// Browser boundary for the catalog facade.
// Everything here is intentionally stateless: no localStorage, no cookies.

export function read_params() {
  const params = new URLSearchParams(window.location.search);
  return {
    course: params.get("c") || "",
    query: params.get("q") || "",
    kind: params.get("kind") || "",
  };
}

export function replace_url(course, query, kind) {
  const params = new URLSearchParams();
  if (course) params.set("c", course);
  if (query) params.set("q", query);
  if (kind) params.set("kind", kind);
  const search = params.toString();
  const url = window.location.pathname + (search ? "?" + search : "");
  window.history.replaceState(null, "", url);
}

export function mod_key() {
  return /Mac|iPhone|iPad|iPod/.test(navigator.platform) ? "⌘K" : "Ctrl K";
}

export function focus_search() {
  const element = document.getElementById("search-trigger");
  if (element) element.focus();
}

export function focus_palette() {
  const element = document.getElementById("palette-input");
  if (element) {
    element.focus();
    element.select();
  }
}

export function register_shortcut(callback) {
  window.addEventListener("keydown", (event) => {
    const target = event.target;
    const typing =
      target &&
      (target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable);
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      callback();
      return;
    }
    if (event.key === "/" && !typing) {
      event.preventDefault();
      callback();
    }
  });
}

export function scroll_detail_top() {
  const detail = document.querySelector(".detail");
  if (detail) detail.scrollTop = 0;
  window.scrollTo(0, 0);
}

export function scroll_active(index) {
  const element = document.getElementById("palette-item-" + index);
  if (element) element.scrollIntoView({ block: "nearest" });
}

export function navigate(href) {
  window.location.assign(href);
}

export function copy_page_link() {
  write_clipboard(window.location.href);
}

export function copy_course_link(slug) {
  const url = new URL("courses/" + slug + "/", window.location.href);
  write_clipboard(url.href);
}

function write_clipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text);
    return;
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  try {
    document.execCommand("copy");
  } catch (_error) {
    // Clipboard is best-effort; the fallback is only for insecure contexts.
  }
  area.remove();
}

export function open_external(url) {
  window.open(url, "_blank", "noopener");
}

export function open_issue(repo, title, body) {
  const url =
    repo +
    "/issues/new?title=" +
    encodeURIComponent(title) +
    "&body=" +
    encodeURIComponent(body);
  window.open(url, "_blank", "noopener");
}

export function print_page() {
  window.print();
}

export function register_pop(callback) {
  window.addEventListener("popstate", callback);
}
