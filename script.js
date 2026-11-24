(function () {
  "use strict";

  var KEY = "theme";
  var root = document.documentElement;
  var button = document.getElementById("theme-toggle");

  function systemPreference() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function currentTheme() {
    return root.dataset.theme === "dark" || root.dataset.theme === "light"
      ? root.dataset.theme
      : systemPreference();
  }

  function apply(theme) {
    var value = theme === "dark" ? "dark" : "light";
    root.dataset.theme = value;
    root.style.colorScheme = value;
    if (button) {
      var isDark = value === "dark";
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      button.setAttribute(
        "aria-label",
        isDark ? "Cambiar a tema claro" : "Cambiar a tema oscuro"
      );
    }
  }

  var saved = null;
  try {
    saved = localStorage.getItem(KEY);
  } catch (error) {
    saved = null;
  }

  apply(saved === "dark" || saved === "light" ? saved : systemPreference());

  if (button) {
    button.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      try {
        localStorage.setItem(KEY, next);
      } catch (error) {
        /* ignore */
      }
      apply(next);
    });
  }

  var media = window.matchMedia("(prefers-color-scheme: dark)");
  var onChange = function (event) {
    var stored = null;
    try {
      stored = localStorage.getItem(KEY);
    } catch (error) {
      stored = null;
    }
    if (stored !== "dark" && stored !== "light") {
      apply(event.matches ? "dark" : "light");
    }
  };

  if (typeof media.addEventListener === "function") {
    media.addEventListener("change", onChange);
  } else if (typeof media.addListener === "function") {
    media.addListener(onChange);
  }
})();
