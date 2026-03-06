function setupSocket() {
  if (typeof io === 'undefined') {
    return;
  }
  const socket = io();

  socket.on('price_change', (payload) => {
    (payload.items || []).forEach((item) => {
      const productId = item.id;
      const price = item.price;

      document.querySelectorAll(`[data-product-id="${productId}"] .js-price, .js-price[data-product-id="${productId}"]`).forEach((node) => {
        node.textContent = price;
      });
    });
  });

  ['001', '002', '003', '004'].forEach((code) => {
    socket.on(`low_stock_${code}`, (payload) => {
      const panel = document.querySelector('#notification-panel');
      if (!panel || panel.dataset.storeId !== code) {
        return;
      }
      (payload.items || []).forEach((item) => {
        const li = document.createElement('li');
        li.textContent = `Low stock: ${item.refProduct} on ${item.refShelf} (shelfCount=${item.shelfCount})`;
        panel.prepend(li);
      });
    });
  });
}

async function fillAvailableShelves(select) {
  const storeId = select.dataset.storeId;
  const productId = select.dataset.productId;
  const response = await fetch(`/api/stores/${encodeURIComponent(storeId)}/available-shelves?product_id=${encodeURIComponent(productId)}`);
  const items = await response.json();
  select.innerHTML = '';
  if (!items.length) {
    select.innerHTML = '<option value="">No available shelf</option>';
    return;
  }
  items.forEach((shelf) => {
    const option = document.createElement('option');
    option.value = shelf.id;
    option.textContent = `${shelf.name} (${shelf.id})`;
    select.appendChild(option);
  });
}

async function fillAvailableProducts(select) {
  const shelfId = select.dataset.shelfId;
  const response = await fetch(`/api/shelves/${encodeURIComponent(shelfId)}/available-products`);
  const items = await response.json();
  select.innerHTML = '';
  if (!items.length) {
    select.innerHTML = '<option value="">No available product</option>';
    return;
  }
  items.forEach((product) => {
    const option = document.createElement('option');
    option.value = product.id;
    option.textContent = `${product.name} (${product.id})`;
    select.appendChild(option);
  });
}

function setupDynamicSelects() {
  document.querySelectorAll('.js-available-shelves').forEach((select) => {
    fillAvailableShelves(select);
  });

  document.querySelectorAll('.js-available-products').forEach((select) => {
    fillAvailableProducts(select);
  });
}

function setupFormValidation() {
  document.querySelectorAll('form[novalidate]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        form.classList.add('has-errors');
      }
    });
  });
}

function setupProgressBars() {
  document.querySelectorAll('.progress-bar[data-progress]').forEach((node) => {
    const raw = Number(node.dataset.progress || '0');
    const bounded = Math.max(0, Math.min(100, raw));
    node.style.width = `${bounded}%`;
  });
}

function loadStylesheetOnce(href) {
  if (document.querySelector(`link[data-dynamic-style="${href}"]`)) {
    return;
  }
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = href;
  link.dataset.dynamicStyle = href;
  document.head.appendChild(link);
}

function loadScriptOnce(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[data-dynamic-script="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.dataset.dynamicScript = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Cannot load script: ${src}`));
    document.body.appendChild(script);
  });
}

async function ensureLeafletLoaded() {
  if (typeof L !== 'undefined') {
    return true;
  }

  loadStylesheetOnce('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css');

  const scriptSources = [
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js',
  ];

  for (const src of scriptSources) {
    try {
      await loadScriptOnce(src);
      if (typeof L !== 'undefined') {
        return true;
      }
    } catch (error) {
      console.warn(error);
    }
  }

  return typeof L !== 'undefined';
}

function renderStoresLeafletMap(mapNode, stores) {
  if (mapNode.dataset.mapReady === 'true') {
    return;
  }

  const map = L.map(mapNode, {
    scrollWheelZoom: true,
    zoomControl: true,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  const storeMarkerIcon = L.divIcon({
    className: 'store-marker-wrap',
    html: '<span class="store-marker-dot" aria-hidden="true"></span>',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -10],
  });

  const bounds = [];

  stores.forEach((store) => {
    const coords = store?.location?.coordinates;
    const hasCoords = Array.isArray(coords) && coords.length === 2;
    if (!hasCoords) {
      return;
    }

    const lon = Number(coords[0]);
    const lat = Number(coords[1]);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return;
    }

    const marker = L.marker([lat, lon], { icon: storeMarkerIcon }).addTo(map);
    const detailUrl = `/stores/${encodeURIComponent(store.id || '')}`;

    const popup = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = store.name || 'Store';
    popup.appendChild(title);

    if (store?.address?.addressLocality) {
      popup.appendChild(document.createElement('br'));
      const locality = document.createElement('small');
      locality.textContent = store.address.addressLocality;
      popup.appendChild(locality);
    }

    popup.appendChild(document.createElement('br'));
    const link = document.createElement('a');
    link.href = detailUrl;
    link.textContent = 'View details';
    popup.appendChild(link);

    marker.bindPopup(popup);
    bounds.push([lat, lon]);
  });

  if (!bounds.length) {
    map.setView([52.5, 13.4], 12);
    mapNode.dataset.mapReady = 'true';
    return;
  }

  if (bounds.length === 1) {
    map.setView(bounds[0], 14);
    mapNode.dataset.mapReady = 'true';
    return;
  }

  map.fitBounds(bounds, { padding: [28, 28] });

  mapNode.dataset.mapReady = 'true';
}

async function setupStoresLeafletMap() {
  const mapNode = document.querySelector('#stores-leaflet-map');
  const storesNode = document.querySelector('#stores-map-data');
  if (!mapNode || !storesNode) {
    return;
  }

  let stores = [];
  try {
    stores = JSON.parse(storesNode.textContent || '[]');
  } catch (error) {
    console.error('Cannot parse stores map payload', error);
    return;
  }

  const loaded = await ensureLeafletLoaded();
  if (!loaded || typeof L === 'undefined') {
    mapNode.innerHTML = '<p class="map-load-error">Map cannot be loaded right now. Please check your network and reload the page.</p>';
    return;
  }

  renderStoresLeafletMap(mapNode, stores);
}

function initPage() {
  setupSocket();
  setupDynamicSelects();
  setupFormValidation();
  setupProgressBars();
  setupStoresLeafletMap();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPage);
} else {
  initPage();
}
