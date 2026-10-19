"use strict";
(() => {
  let pending = Promise.resolve();
  async function send(url, values) {
    let response;
    try {
      response = await fetch(url, {
        method: "POST",
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content},
        body: new URLSearchParams(values)
      });
    } catch {
      throw new Error("Não foi possível conectar. Confira sua conexão e tente novamente.");
    }
    const data = await response.json().catch(() => ({message: "Não foi possível concluir. Atualize a página e tente novamente."}));
    if (response.status === 401 && data.status === "redirect") {
      window.location.assign(data.url);
      throw new Error("Entre na sua conta para continuar.");
    }
    if (Number.isInteger(data.cart_count)) {
      document.querySelectorAll("[data-cart-count]").forEach(el => {el.textContent = data.cart_count;});
      document.querySelectorAll(".open-cart").forEach(el => {el.setAttribute("aria-label", `Carrinho de contribuições, ${data.cart_count} itens`);});
    }
    if (!response.ok || data.status !== "success") {
      const error = new Error(data.message || "Não foi possível concluir. Tente novamente.");
      error.data = data;
      throw error;
    }
    return data;
  }
  window.PontoAPI = {
    post(url, values = {}) {
      // Finish each mutation before sending another cookie-backed cart update.
      const request = pending.then(() => send(url, values));
      pending = request.catch(() => {});
      return request;
    },
    changed(data, source) {
      document.dispatchEvent(new CustomEvent("cart:changed", {detail: {...data, source}}));
    },
    message(text, category = "error") {
      const container = document.getElementById("flash-container");
      if (!container) return;
      const notice = document.createElement("div");
      notice.className = `flash-message ${category}`;
      notice.setAttribute("role", category === "error" ? "alert" : "status");
      notice.textContent = text;
      container.replaceChildren(notice);
      requestAnimationFrame(() => notice.classList.add("show"));
      setTimeout(() => notice.remove(), 5000);
    }
  };
})();
