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

document.addEventListener('DOMContentLoaded', () => {
  setupSocket();
  setupDynamicSelects();
  setupFormValidation();
  setupProgressBars();
});
