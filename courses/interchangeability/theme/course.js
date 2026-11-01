// Injected into every page of this book by mdbook.
// Adds the only cross-site affordance: a link back to the catalog.
// It is a plain relative link; nothing is stored anywhere.

// The site stores nothing on the reader's device. mdbook itself remembers the
// sidebar and theme in localStorage; drop those two writes so the promise also
// holds inside a book.
(function () {
  try {
    var originalSet = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (key === "mdbook-theme" || key === "mdbook-sidebar") return;
      return originalSet.call(this, key, value);
    };

    // Ignore any theme left on the device: the book follows the system
    // preference, the same way the facade does.
    var originalGet = Storage.prototype.getItem;
    Storage.prototype.getItem = function (key) {
      if (key === "mdbook-theme") return null;
      return originalGet.call(this, key);
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

// 折叠的课件原文在打印/存 PDF 前全部展开，纸面上不缺内容。
window.addEventListener("beforeprint", function () {
  document.querySelectorAll("details").forEach(function (el) {
    el.open = true;
  });
});
