/* Community Resource Map — Leaflet + OpenStreetMap
   Reads config from #map data-* attributes and loads pins from the JSON API
   using the same query string as the current page filters. */
(function () {
  "use strict";

  var el = document.getElementById("map");
  if (!el || typeof L === "undefined") return;

  var lat = parseFloat(el.dataset.lat) || 39.7392;
  var lng = parseFloat(el.dataset.lng) || -104.9903;
  var zoom = parseInt(el.dataset.zoom, 10) || 12;
  var apiUrl = el.dataset.apiUrl;

  var map = L.map(el, { scrollWheelZoom: false }).setView([lat, lng], zoom);

  // OpenStreetMap standard tiles. Attribution is required by the OSM license.
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Enable scroll zoom only after the user clicks the map (avoids hijacking page scroll).
  map.on("focus", function () { map.scrollWheelZoom.enable(); });
  map.on("blur", function () { map.scrollWheelZoom.disable(); });

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function coloredIcon(color) {
    return L.divIcon({
      className: "crm-pin",
      html:
        '<span style="display:inline-block;width:18px;height:18px;border-radius:50%;' +
        "background:" + (color || "#2f7d5b") +
        ';border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.4)"></span>',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  }

  fetch(apiUrl, { headers: { Accept: "application/json" } })
    .then(function (r) {
      if (!r.ok) throw new Error("Network error");
      return r.json();
    })
    .then(function (data) {
      var features = (data && data.features) || [];
      if (!features.length) return;

      var markers = [];
      features.forEach(function (f) {
        var c = f.geometry.coordinates; // [lng, lat]
        var p = f.properties;
        var marker = L.marker([c[1], c[0]], { icon: coloredIcon(p.color) });
        var popup =
          '<strong>' + escapeHtml(p.name) + "</strong><br>" +
          '<span style="color:#6b6259">' + escapeHtml(p.category) +
          (p.is_free ? " · Free" : "") + "</span><br>" +
          (p.address ? escapeHtml(p.address) + "<br>" : "") +
          '<a href="' + escapeHtml(p.url) + '">View details</a>';
        marker.bindPopup(popup);
        marker.addTo(map);
        markers.push(marker);
      });

      if (markers.length) {
        var group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.15));
      }
    })
    .catch(function () {
      el.insertAdjacentHTML(
        "afterend",
        '<p class="resource-meta mt-2">Map data could not load. The list below still works.</p>'
      );
    });
})();
