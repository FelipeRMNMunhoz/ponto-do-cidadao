"use strict";
document.querySelectorAll(".add-form").forEach(form => {
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    if (button.disabled || !form.reportValidity()) return;
    button.disabled = true;
    button.textContent = "Adicionando…";
    try {
      const data = await PontoAPI.post(form.action, {quantity: form.elements.quantity.value});
      PontoAPI.message(data.message, "success");
      PontoAPI.changed(data, "catalog");
    } catch (error) { PontoAPI.message(error.message); }
    finally { button.disabled = false; button.textContent = "Adicionar ao carrinho"; }
  });
});
