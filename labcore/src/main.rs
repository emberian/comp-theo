// labcore -- zero-dependency RL engine for the Computational Theology labs.
//
// Python (numpy) generates worlds + spectral features and serialises them;
// this binary runs ALL the reinforcement-learning training loops natively
// and in parallel (std::thread, no external crates), returning metrics.
// It is a faithful port of the lab3 (tabular) / lab4 (linear-FA) agents:
// cost-to-go Q/V, gamma=1, prioritized replay (= the consequencer), and
// the four mechanisms vow / forgive / variety / grace.
//
// Protocol (stdin):
//   line 1 : path to a world file
//   line k : "<seed> <mode> <vow> <forgive> <variety> <grace> <ep> <cap>"
//            mode = 0 tabular, 1 linear-FA;  flags 0/1
// Output (stdout): one "<success> <capture>" line per spec, in order.
//
// World file (text):
//   N GOOD DIM
//   for s in 0..N:  deg v1 c1 v2 c2 ...
//   DEMON m  n1 n2 ...
//   ESCAPE gate exit_to
//   if DIM>0:  N*DIM whitespace floats (row-major feature matrix)

use std::io::{self, Read, Write};
use std::sync::Arc;

// ---- fast deterministic RNG: splitmix64 -> xoshiro256** -------------------
struct Rng {
    s: [u64; 4],
}
impl Rng {
    fn new(seed: u64) -> Self {
        let mut z = seed.wrapping_add(0x9E3779B97F4A7C15);
        let mut sm = || {
            z = z.wrapping_add(0x9E3779B97F4A7C15);
            let mut x = z;
            x = (x ^ (x >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
            x = (x ^ (x >> 27)).wrapping_mul(0x94D049BB133111EB);
            x ^ (x >> 31)
        };
        Rng { s: [sm(), sm(), sm(), sm()] }
    }
    #[inline]
    fn next_u64(&mut self) -> u64 {
        let r = self.s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        r
    }
    #[inline]
    fn f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / (1u64 << 53) as f64)
    }
    #[inline]
    fn below(&mut self, n: usize) -> usize {
        (self.f64() * n as f64) as usize % n.max(1)
    }
    #[inline]
    fn range(&mut self, lo: usize, hi: usize) -> usize {
        lo + self.below((hi - lo).max(1))
    }
}

struct World {
    n: usize,
    good: usize,
    dim: usize,
    adj: Vec<Vec<(u32, f64)>>,
    demon: Vec<bool>,
    demon_sorted: Vec<usize>,
    gate: usize,
    exit_to: usize,
    feats: Vec<f64>, // n*dim, row-major
}

fn parse_world(path: &str) -> World {
    let txt = std::fs::read_to_string(path).expect("world file");
    let mut it = txt.split_whitespace();
    let mut nx = || it.next().unwrap();
    let n: usize = nx().parse().unwrap();
    let good: usize = nx().parse().unwrap();
    let dim: usize = nx().parse().unwrap();
    let mut adj = Vec::with_capacity(n);
    for _ in 0..n {
        let deg: usize = nx().parse().unwrap();
        let mut e = Vec::with_capacity(deg);
        for _ in 0..deg {
            let v: u32 = nx().parse().unwrap();
            let c: f64 = nx().parse().unwrap();
            e.push((v, c));
        }
        adj.push(e);
    }
    assert_eq!(nx(), "DEMON");
    let m: usize = nx().parse().unwrap();
    let mut demon = vec![false; n];
    let mut demon_sorted = Vec::with_capacity(m);
    for _ in 0..m {
        let d: usize = nx().parse().unwrap();
        demon[d] = true;
        demon_sorted.push(d);
    }
    demon_sorted.sort_unstable();
    assert_eq!(nx(), "ESCAPE");
    let gate: usize = nx().parse().unwrap();
    let exit_to: usize = nx().parse().unwrap();
    let mut feats = Vec::new();
    if dim > 0 {
        feats.reserve(n * dim);
        for _ in 0..n * dim {
            feats.push(nx().parse::<f64>().unwrap());
        }
    }
    World { n, good, dim, adj, demon, demon_sorted, gate, exit_to, feats }
}

struct Spec {
    seed: u64,
    fa: bool,
    vow: bool,
    forgive: bool,
    variety: bool,
    grace: bool,
    episodes: usize,
    cap: usize,
}

// weighted index sample (prio^0.6), with replacement
fn wsample(rng: &mut Rng, prio: &[f64], out: &mut [usize]) {
    let mut cum = vec![0.0f64; prio.len()];
    let mut acc = 0.0;
    for (i, p) in prio.iter().enumerate() {
        acc += p.powf(0.6);
        cum[i] = acc;
    }
    for o in out.iter_mut() {
        let r = rng.f64() * acc;
        // binary search
        let mut lo = 0usize;
        let mut hi = cum.len() - 1;
        while lo < hi {
            let mid = (lo + hi) / 2;
            if cum[mid] < r {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        *o = lo;
    }
}

fn argmin(v: &[f64]) -> usize {
    let mut bi = 0;
    let mut bv = v[0];
    for (i, &x) in v.iter().enumerate().skip(1) {
        if x < bv {
            bv = x;
            bi = i;
        }
    }
    bi
}

fn run(w: &World, sp: &Spec) -> (f64, f64) {
    let mut rng = Rng::new(sp.seed);
    let n = w.n;
    let good = w.good;
    let mut adj = w.adj.clone(); // grace may append
    // learner state
    let tabular = !sp.fa;
    let mut q: Vec<Vec<f64>> = if tabular {
        adj.iter().map(|e| vec![0.0; e.len()]).collect()
    } else {
        Vec::new()
    };
    let mut wt: Vec<f64> = if sp.fa { vec![0.0; w.dim] } else { Vec::new() };
    let alpha = if tabular { 0.5 } else { 0.02 };
    let eps_env = 0.12;
    let mut visits = vec![1.0f64; n];
    let mut buf: Vec<(usize, usize, f64, usize)> = Vec::new();
    let mut prio: Vec<f64> = Vec::new();
    let mut vow_b = 0.0f64;
    let mut graced = false;
    let grace_ep = rng.range(sp.episodes / 4, sp.episodes / 2);

    let vfn = |wt: &[f64], s: usize| -> f64 {
        let mut acc = 0.0;
        let base = s * w.dim;
        for k in 0..w.dim {
            acc += wt[k] * w.feats[base + k];
        }
        acc
    };

    let mut succ = vec![0.0f64; sp.episodes];
    let mut capt = vec![0.0f64; sp.episodes];

    for ep in 0..sp.episodes {
        if sp.grace && ep == grace_ep && !graced && !w.demon_sorted.is_empty()
        {
            let gnode = w.demon_sorted[w.demon_sorted.len() / 2];
            adj[gnode].push((good as u32, 1.2));
            if tabular {
                q[gnode].push(0.0);
            }
            graced = true;
        }
        let eps = (0.5 * 0.99f64.powi(ep as i32)).max(0.05);
        let mut s = 0usize;
        let mut steps = 0usize;
        let mut ind = 0usize;
        while s != good && steps < sp.cap {
            visits[s] += 1.0;
            if w.demon[s] {
                ind += 1;
            }
            let nb = &adj[s];
            let dgr = nb.len();
            // action values
            let mut qv = vec![0.0f64; dgr];
            for (i, &(v, c)) in nb.iter().enumerate() {
                qv[i] = if tabular {
                    q[s][i]
                } else {
                    c + if v as usize == good { 0.0 }
                    else { vfn(&wt, v as usize) }
                };
                if sp.variety {
                    qv[i] -= 2.5 / visits[v as usize].sqrt();
                }
            }
            if sp.vow && s == w.gate {
                for (i, &(v, _)) in nb.iter().enumerate() {
                    if v as usize == w.exit_to {
                        qv[i] -= vow_b;
                    }
                }
            }
            let a = if rng.f64() < eps {
                rng.below(dgr)
            } else {
                argmin(&qv)
            };
            let (tgt_v, ac) = nb[a];
            let s2 = if rng.f64() < eps_env {
                adj[s][rng.below(dgr)].0 as usize
            } else {
                tgt_v as usize
            };
            let g = ac + 0.02;
            // TD update + surprise
            let d;
            if tabular {
                let boot = if s2 == good { 0.0 } else {
                    q[s2].iter().cloned().fold(f64::INFINITY, f64::min)
                };
                let target = g + boot;
                d = (target - q[s][a]).abs();
                q[s][a] += alpha * (target - q[s][a]);
            } else {
                let vs = vfn(&wt, s);
                let target =
                    g + if s2 == good { 0.0 } else { vfn(&wt, s2) };
                let delta = target - vs;
                d = delta.abs();
                let base = s * w.dim;
                for k in 0..w.dim {
                    wt[k] += alpha * delta * w.feats[base + k];
                }
            }
            buf.push((s, a, g, s2));
            prio.push(d + 1e-3);
            if buf.len() > 4000 {
                buf.remove(0);
                prio.remove(0);
            }
            if sp.forgive && d > 6.0 {
                *prio.last_mut().unwrap() = 1e-3;
            }
            s = s2;
            steps += 1;
        }
        // replay (= consequencer)
        if buf.len() >= 24 {
            let mut idx = [0usize; 24];
            wsample(&mut rng, &prio, &mut idx);
            for &i in idx.iter() {
                let (bs, ba, bg, bs2) = buf[i];
                let nd;
                if tabular {
                    let boot = if bs2 == good { 0.0 } else {
                        q[bs2].iter().cloned().fold(f64::INFINITY, f64::min)
                    };
                    let tgt = bg + boot;
                    nd = (tgt - q[bs][ba]).abs();
                    q[bs][ba] += alpha * (tgt - q[bs][ba]);
                } else {
                    let vs = vfn(&wt, bs);
                    let tgt = bg
                        + if bs2 == good { 0.0 } else { vfn(&wt, bs2) };
                    let delta = tgt - vs;
                    nd = delta.abs();
                    let base = bs * w.dim;
                    for k in 0..w.dim {
                        wt[k] += alpha * delta * w.feats[base + k];
                    }
                }
                prio[i] = nd + 1e-3;
            }
        }
        if sp.vow {
            if tabular {
                vow_b = 8.0 * 0.96; // lab3: reset-then-decay each episode
            } else {
                vow_b = (8.0 + 0.96 * vow_b) * 0.96; // lab4: accumulating
            }
        }
        succ[ep] = if s == good { 1.0 } else { 0.0 };
        capt[ep] = ind as f64 / steps.max(1) as f64;
    }
    let tail = (sp.episodes / 5).max(10);
    let m = |v: &[f64]| {
        let t = &v[v.len() - tail..];
        t.iter().sum::<f64>() / t.len() as f64
    };
    (m(&succ), m(&capt))
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut lines = input.lines();
    let world_path = lines.next().unwrap().trim().to_string();
    let world = Arc::new(parse_world(&world_path));
    let specs: Vec<Spec> = lines
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let p: Vec<&str> = l.split_whitespace().collect();
            Spec {
                seed: p[0].parse().unwrap(),
                fa: p[1] == "1",
                vow: p[2] == "1",
                forgive: p[3] == "1",
                variety: p[4] == "1",
                grace: p[5] == "1",
                episodes: p[6].parse().unwrap(),
                cap: p[7].parse().unwrap(),
            }
        })
        .collect();

    let nthreads = std::thread::available_parallelism()
        .map(|x| x.get())
        .unwrap_or(4);
    let mut out = vec![(0.0f64, 0.0f64); specs.len()];
    let chunk = (specs.len() + nthreads - 1) / nthreads.max(1);
    std::thread::scope(|sc| {
        for (ti, slot) in out.chunks_mut(chunk.max(1)).enumerate() {
            let w = Arc::clone(&world);
            let sl = &specs[ti * chunk..(ti * chunk + slot.len())];
            sc.spawn(move || {
                for (o, sp) in slot.iter_mut().zip(sl.iter()) {
                    *o = run(&w, sp);
                }
            });
        }
    });
    let mut o = String::new();
    for (s, c) in out {
        o.push_str(&format!("{:.6} {:.6}\n", s, c));
    }
    io::stdout().write_all(o.as_bytes()).unwrap();
}
