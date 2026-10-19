document.addEventListener("DOMContentLoaded", () => {
    const msgs = document.querySelectorAll(".flash-message");
    const container = document.getElementById("flash-container");

    msgs.forEach(msg => {

        // Garante que todas as mensagens vão para o container fixo
        if (container) container.appendChild(msg);

        // Evita aparecer gigante antes do JS
        msg.style.visibility = "visible";

        // Animação de entrada
        setTimeout(() => msg.classList.add("show"), 50);

        // Some depois de 3s
        setTimeout(() => {
            msg.classList.remove("show");

            // Remove depois do fade-out
            setTimeout(() => msg.remove(), 400);
        }, 3000);
    });
});


// Mantém menu ativo (caso exista sidebar)
const links = document.querySelectorAll('.sidebar a');
const currentPath = window.location.pathname;

links.forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});
