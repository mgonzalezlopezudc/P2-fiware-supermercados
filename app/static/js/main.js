const I18N = window.I18N || {};

function t(key, params = {}) {
  const template = I18N[key] || key;
  return Object.entries(params).reduce(
    (acc, [name, value]) => acc.replaceAll(`{${name}}`, String(value)),
    String(template),
  );
}

function shortEntityId(value) {
  if (!value || typeof value !== 'string') {
    return value || '';
  }
  const parts = value.split(':');
  return parts[parts.length - 1] || value;
}

function ensureToastRoot() {
  let root = document.querySelector('#global-toast-root');
  if (root) {
    return root;
  }

  root = document.createElement('div');
  root.id = 'global-toast-root';
  root.className = 'global-toast-root';
  root.setAttribute('aria-live', 'polite');
  root.setAttribute('aria-atomic', 'false');
  document.body.appendChild(root);
  return root;
}

function showToast(message, tone = 'info') {
  const root = ensureToastRoot();
  const toast = document.createElement('div');
  toast.className = `global-toast ${tone}`;
  toast.textContent = message;
  root.appendChild(toast);

  window.setTimeout(() => {
    toast.classList.add('is-hiding');
    window.setTimeout(() => {
      toast.remove();
    }, 220);
  }, 4500);
}

function setupSocket() {
  if (typeof io === 'undefined') {
    return;
  }
  const socket = io();

  socket.on('connect_error', () => {
    showToast(t('realtime_connection_issue'), 'error');
  });

  socket.on('price_change', (payload) => {
    (payload.items || []).forEach((item) => {
      const productId = item.id;
      const price = item.price;

      document
        .querySelectorAll(`[data-product-id="${productId}"] .js-price, .js-price[data-product-id="${productId}"]`)
        .forEach((node) => {
          node.textContent = price;
        });

      if (productId && price !== undefined) {
        showToast(
          t('price_updated', { product_id: shortEntityId(productId), price }),
          'info',
        );
      }
    });
  });

  ['001', '002', '003', '004'].forEach((code) => {
    socket.on(`low_stock_${code}`, (payload) => {
      const items = payload.items || [];
      items.forEach((item) => {
        const productLabel = shortEntityId(item.refProduct || t('unknown'));
        const shelfLabel = shortEntityId(item.refShelf || t('unknown'));
        showToast(
          t('low_stock', {
            store_code: code,
            product_label: productLabel,
            shelf_label: shelfLabel,
            count: item.shelfCount,
          }),
          'warning',
        );
      });

      const panel = document.querySelector('#notification-panel');
      if (!panel || panel.dataset.storeId !== code) {
        return;
      }
      items.forEach((item) => {
        const li = document.createElement('li');
        li.textContent = t('low_stock_panel', {
          product: shortEntityId(item.refProduct || t('unknown')),
          shelf: shortEntityId(item.refShelf || t('unknown')),
          count: item.shelfCount,
        });
        panel.prepend(li);
      });
    });
  });
}

async function fillAvailableShelves(select) {
  const storeId = select.dataset.storeId;
  const productId = select.dataset.productId;
  const response = await fetch(
    `/api/stores/${encodeURIComponent(storeId)}/available-shelves?product_id=${encodeURIComponent(productId)}`,
  );
  const items = await response.json();
  select.innerHTML = '';
  if (!items.length) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = t('no_available_shelf');
    select.appendChild(option);
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
    const option = document.createElement('option');
    option.value = '';
    option.textContent = t('no_available_product');
    select.appendChild(option);
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
    title.textContent = store.name || t('store_fallback');
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
    link.textContent = t('view_details');
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
    console.error(t('map_payload_parse_error'), error);
    return;
  }

  const loaded = await ensureLeafletLoaded();
  if (!loaded || typeof L === 'undefined') {
    mapNode.innerHTML = `<p class="map-load-error">${t('map_load_error')}</p>`;
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
