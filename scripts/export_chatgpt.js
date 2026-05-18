/* Export a full ChatGPT conversation to JSON + Markdown.
 *
 * HOW TO USE
 *  1. Open the conversation in your browser (logged in):
 *       https://chatgpt.com/c/6a05f3fe-966c-8328-a69c-b413425e3e38
 *  2. Open DevTools console (Cmd+Opt+J on macOS Chrome).
 *  3. Paste this whole file, press Enter.
 *  4. Two files download: conversation.json (raw, full fidelity, includes
 *     image asset pointers) and conversation.md (readable transcript).
 *
 * It uses chatgpt.com/backend-api, the same API the web UI uses, with your
 * own session token — nothing leaves your browser.
 */
(async () => {
  const id = (location.pathname.match(/\/c\/([0-9a-f-]+)/) || [])[1]
    || prompt("Conversation id?", "6a05f3fe-966c-8328-a69c-b413425e3e38");

  const sess = await fetch("/api/auth/session").then(r => r.json());
  const token = sess.accessToken;
  if (!token) throw new Error("Not logged in / no accessToken");

  const conv = await fetch(`/backend-api/conversation/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(r => {
    if (!r.ok) throw new Error(`conversation fetch ${r.status}`);
    return r.json();
  });

  // Walk the active branch: climb from current_node to root, then reverse.
  const map = conv.mapping;
  const path = [];
  for (let n = conv.current_node; n; n = map[n] && map[n].parent) {
    if (map[n]) path.push(map[n]);
  }
  path.reverse();

  const lines = [`# ${conv.title || id}`, ""];
  for (const node of path) {
    const m = node.message;
    if (!m || !m.content) continue;
    const role = m.author && m.author.role;
    if (role === "system" || role === "tool") continue;
    const c = m.content;
    let text = "";
    if (c.content_type === "text") {
      text = (c.parts || []).join("\n");
    } else if (c.content_type === "multimodal_text") {
      text = (c.parts || [])
        .map(p => (typeof p === "string"
          ? p
          : `\n_[${p.content_type || "asset"}: ${p.asset_pointer || ""}]_\n`))
        .join("\n");
    } else if (c.parts) {
      text = c.parts.join("\n");
    } else {
      text = JSON.stringify(c);
    }
    if (!text.trim()) continue;
    lines.push(`\n\n## ${role === "user" ? "User" : "Assistant"}\n`, text);
  }

  const dl = (name, data, type) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([data], { type }));
    a.download = name;
    a.click();
  };
  dl("conversation.json", JSON.stringify(conv, null, 2), "application/json");
  dl("conversation.md", lines.join("\n"), "text/markdown");
  console.log(`Exported ${path.length} nodes from "${conv.title}"`);
})();
