"use strict";
(() => {
  const checkout = document.getElementById("checkout");
  if (!checkout) return;
  let busy = false;
  function bounds() {
    checkout.querySelectorAll(".checkout-item").forEach(item => {
      const qty = Number(item.querySelector(".qty-value").textContent);
      item.querySelector(".minus").disabled = busy || qty <= 1;
      item.querySelector(".plus").disabled = busy || qty >= Number(item.dataset.limit);
      item.querySelector(".remove-item").disabled = busy;
    });
    const pay = document.getElementById("pay-btn");
    if (pay) pay.disabled = busy;
    checkout.setAttribute("aria-busy", String(busy));
  }
  function apply(data) {
    if (!Array.isArray(data.items)) return;
    if (data.cart_count === 0) {window.location.assign("/doacoes#catalogo"); return;}
    checkout.querySelectorAll(".checkout-item").forEach(item => {
      const row = data.items.find(value => String(value.id) === item.dataset.id);
      if (!row) {item.remove(); return;}
      item.querySelector(".qty-value").textContent = row.quantity;
      item.querySelector(".item-price").textContent = row.subtotal;
      item.querySelector(".item-seller").textContent = row.unit_price + " por unidade";
      item.dataset.limit = row.limit;
    });
    document.getElementById("subtotal-value").textContent = data.total;
    document.getElementById("total-value").textContent = data.total;
  }
  checkout.addEventListener("click", async event => {
    const button = event.target.closest(".checkout-item .qty-btn, .checkout-item .remove-item");
    if (!button || button.disabled || busy) return;
    event.preventDefault();
    const item = button.closest(".checkout-item");
    const qty = button.classList.contains("remove-item") ? 0 : Number(item.querySelector(".qty-value").textContent) + (button.classList.contains("plus") ? 1 : -1);
    busy = true; bounds();
    try {
      const data = await PontoAPI.post("/update_cart", {product_id: item.dataset.id, qty});
      apply(data);
      PontoAPI.changed(data, "checkout");
    } catch (error) {if (error.data) apply(error.data); PontoAPI.message(error.message);}
    finally {
      busy = false; bounds();
      const focus = button.isConnected && !button.disabled ? button : checkout.querySelector(".qty-btn:not(:disabled),.remove-item,.back-link");
      focus?.focus();
    }
  });
  document.addEventListener("cart:changed", event => {
    if (event.detail.source === "drawer") {apply(event.detail); bounds();}
  });
  document.getElementById("pay-btn")?.addEventListener("click", async event => {
    event.preventDefault(); if (busy) return;
    busy = true; bounds();
    try {const data = await PontoAPI.post("/pagamento"); window.location.assign(data.url);}
    catch (error) {PontoAPI.message(error.message);}
    finally {busy = false; bounds();}
  });
})();
