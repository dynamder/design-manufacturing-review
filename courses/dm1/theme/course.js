// Injected into every page of this book by mdbook.
// Adds the only cross-site affordance: a link back to the catalog.
// It is a plain relative link; nothing is stored anywhere.

// The site stores nothing on the reader's device. mdbook itself remembers the
// sidebar and theme in localStorage; drop those two writes so the promise also
// holds inside a book.
(function () {
  try {
    var original = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (key === "mdbook-theme" || key === "mdbook-sidebar") return;
      return original.call(this, key, value);
    };
  } catch (_) {}
})();

(function () {
  var link = document.createElement("a");
  link.className = "sn-back";
  link.href = "../../";
  link.textContent = "← 课程资料库";
  link.setAttribute("aria-label", "返回课程资料库");
  document.body.appendChild(link);
})();
