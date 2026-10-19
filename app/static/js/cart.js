"use strict";
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("cartOverlay");
  const content = document.getElementById("cartContent");
  const panel = overlay?.querySelector(".cart-container");
  if (!overlay || !content) return;
  let opener = null, busy = false, closeTimer;
  const isOpen = () => overlay.classList.contains("open");
  async function refresh() {
    const response = await fetch("/cart_partial", {headers: {"X-Requested-With": "XMLHttpRequest"}});
    if (response.status === 401) {
      const data = await response.json();
      window.location.assign(data.url);
      return;
    }
    if (!response.ok) throw new Error("Não foi possível carregar o carrinho.");
    content.innerHTML = await response.text();
  }
  function close() {
    overlay.classList.remove("open");
    panel.classList.remove("active");
    overlay.setAttribute("aria-hidden", "true");
    closeTimer = setTimeout(() => overlay.classList.add("hidden"), 300);
    document.body.style.overflow = "";
    opener?.focus();
  }
  document.querySelectorAll(".open-cart").forEach(button => {
    button.addEventListener("click", async event => {
      event.preventDefault();
      if (isOpen()) {close(); return;}
      opener = button;
      clearTimeout(closeTimer);
      overlay.classList.remove("hidden");
      overlay.setAttribute("aria-hidden", "false");
      requestAnimationFrame(() => {overlay.classList.add("open"); panel.classList.add("active");});
      document.body.style.overflow = "hidden";
      content.textContent = "Carregando…";
      content.setAttribute("aria-busy", "true");
      try {await refresh(); if (isOpen()) content.querySelector("#closeCart")?.focus();}
      catch (error) {close(); PontoAPI.message(error.message);}
      finally {content.removeAttribute("aria-busy");}
    });
    button.addEventListener("keydown", event => {
      if (event.key === " ") {event.preventDefault(); button.click();}
    });
  });
  async function mutate(url, values, trigger) {
    if (busy) return;
    busy = true;
    const rowId = trigger.closest(".cart-item")?.dataset.id;
    const selector = trigger.matches("input") ? "input[name=qty]" : trigger.classList.contains("plus") ? ".plus" : trigger.classList.contains("minus") ? ".minus" : ".remove-btn";
    const controls = [...content.querySelectorAll("button:not(#closeCart), input")].map(el => [el, el.disabled]);
    controls.forEach(([el]) => {el.disabled = true;});
    content.setAttribute("aria-busy", "true");
    try {
      const data = await PontoAPI.post(url, values);
      await refresh();
      PontoAPI.changed(data, "drawer");
    } catch (error) {
      if (error.data) PontoAPI.changed(error.data, "drawer");
      PontoAPI.message(error.message);
      await refresh().catch(() => {});
    } finally {
      controls.forEach(([el, disabled]) => {if (el.isConnected) el.disabled = disabled;});
      busy = false;
      content.removeAttribute("aria-busy");
      if (isOpen()) {
        const row = [...content.querySelectorAll(".cart-item")].find(el => el.dataset.id === rowId);
        const next = row?.querySelector(selector);
        (next && !next.disabled ? next : row?.querySelector("input") || content.querySelector("#closeCart"))?.focus();
      }
    }
  }
  content.addEventListener("click", event => {
    if (event.target.closest("#closeCart")) {close(); return;}
    const remove = event.target.closest(".remove-btn");
    if (remove) {mutate("/remove/" + remove.dataset.id, {}, remove); return;}
    const button = event.target.closest(".qty-btn");
    if (!button || button.disabled) return;
    const form = button.closest("form"), input = form.elements.qty;
    const qty = Number(input.value) + (button.classList.contains("plus") ? 1 : -1);
    if (qty < 1 || qty > Number(input.max)) return;
    mutate(form.action, {product_id: form.elements.product_id.value, qty}, button);
  });
  function submitQuantity(form, input) {
    if (!input.reportValidity()) return;
    mutate(form.action, {product_id: form.elements.product_id.value, qty: input.value}, input);
  }
  content.addEventListener("submit", event => {event.preventDefault(); submitQuantity(event.target, event.target.elements.qty);});
  content.addEventListener("change", event => {if (event.target.name === "qty") submitQuantity(event.target.form, event.target);});
  content.addEventListener("click", event => {if (event.target.closest('.cart-empty a') && location.pathname === "/doacoes") close();});
  overlay.addEventListener("click", event => {if (event.target === overlay) close();});
  document.addEventListener("cart:changed", event => {
    if (event.detail.source === "catalog" && isOpen() && !busy) refresh().catch(error => PontoAPI.message(error.message));
  });
  document.addEventListener("keydown", event => {
    if (!isOpen()) return;
    if (event.key === "Escape") close();
    if (event.key === "Tab") {
      const targets = [...content.querySelectorAll('button:not(:disabled),input:not(:disabled):not([type=hidden]),a[href]')];
      const first = targets[0], last = targets[targets.length - 1];
      if (event.shiftKey && (document.activeElement === first || !content.contains(document.activeElement))) {event.preventDefault(); last?.focus();}
      else if (!event.shiftKey && (document.activeElement === last || !content.contains(document.activeElement))) {event.preventDefault(); first?.focus();}
    }
  });
});
