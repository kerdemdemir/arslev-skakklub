/* Årslev Skakklub — små forbedringer, ingen afhængigheder. */
(function () {
  "use strict";

  /* ---------- Mobilmenu ---------- */
  var burger = document.getElementById("burger");
  var links = document.getElementById("navLinks");
  if (burger && links) {
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!open));
      burger.setAttribute("aria-label", open ? "Åbn menu" : "Luk menu");
      links.classList.toggle("open", !open);
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        links.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
        burger.focus();
      }
    });
  }

  /* ---------- Skygge under sticky header ---------- */
  var header = document.getElementById("siteHeader");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Bløde indtoninger ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length) {
    if (!("IntersectionObserver" in window) ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      reveals.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      reveals.forEach(function (el, i) {
        el.style.transitionDelay = (Math.min(i, 5) * 55) + "ms";
        io.observe(el);
      });
    }
  }

  /* ---------- Næste klubaften ---------- */
  var MONTHS = ["januar", "februar", "marts", "april", "maj", "juni",
                "juli", "august", "september", "oktober", "november", "december"];
  var DAYS = ["søndag", "mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag"];

  function fmt(iso) {
    var d = new Date(iso + "T19:00:00");
    return DAYS[d.getDay()] + " den " + d.getDate() + ". " + MONTHS[d.getMonth()] +
           " " + d.getFullYear() + " kl. 19.00";
  }

  var today = new Date(); today.setHours(0, 0, 0, 0);
  var events = window.AARSLEV_EVENTS || [];
  var next = null;
  for (var i = 0; i < events.length; i++) {
    if (new Date(events[i].d + "T23:59:59") >= today) { next = events[i]; break; }
  }

  var strip = document.getElementById("nextup");
  if (strip && next) {
    document.getElementById("nextEvent").textContent = next.t;
    var days = Math.round((new Date(next.d + "T19:00:00") - today) / 86400000);
    var rel = days <= 0 ? "i aften" : days === 1 ? "i morgen" : "om " + days + " dage";
    document.getElementById("nextDate").textContent = fmt(next.d) + " · " + rel;
    strip.hidden = false;
  }

  /* ---------- Markér fortid/næste i kalendertabeller ---------- */
  document.querySelectorAll("tr[data-date]").forEach(function (tr) {
    var d = new Date(tr.getAttribute("data-date") + "T23:59:59");
    if (d < today) tr.classList.add("is-past");
    else if (next && tr.getAttribute("data-date") === next.d) tr.classList.add("is-next");
  });
})();
