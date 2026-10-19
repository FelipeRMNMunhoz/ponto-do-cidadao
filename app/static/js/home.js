document.addEventListener('DOMContentLoaded', function () {
    // --------------------------
    // SweetAlert - Mensagens flash
    // --------------------------
    const flashedMessagesData = document.body.getAttribute('data-flashed-messages');
    const flashedMessages = flashedMessagesData ? JSON.parse(flashedMessagesData) : [];

    const hasSuccess = flashedMessages.some(msg => Array.isArray(msg) && msg[0] === 'success');

    if (hasSuccess) {
        Swal.fire({
            title: 'Obrigado!',
            text: 'Seu formulário foi enviado com sucesso.',
            icon: 'success',
            showConfirmButton: true,
            timer: 3000,
            timerProgressBar: true,
            showCloseButton: true,
            customClass: {
                popup: 'swal-dark-popup',
                title: 'swal-dark-title',
                content: 'swal-dark-content',
                confirmButton: 'swal-dark-btn',
                closeButton: 'swal-dark-close-btn'
            }
        }).then(() => {
            if (window.history.replaceState) {
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        });
    }

    // --------------------------
    // Carrossel de vídeos
    // --------------------------
    const videos = document.querySelectorAll('.carousel-wrapper video');
    const dots = document.querySelectorAll('.carousel-dots .dot');

    if (videos.length > 0 && dots.length > 0) {
        let currentSlide = 0;

        // Remove loop de todos os vídeos e pausa-os
        videos.forEach(video => {
            video.loop = false;
            video.pause();
        });

        // Função para mostrar slide
        function showSlide(index) {
            // Remove active do vídeo atual
            videos[currentSlide].classList.remove('active');
            videos[currentSlide].pause();
            dots[currentSlide].classList.remove('active');

            // Mostra o próximo vídeo
            currentSlide = index;
            videos[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
            videos[currentSlide].play().catch(() => {});
        }

        // Inicializa o primeiro vídeo
        showSlide(0);

        // Quando o vídeo termina, vai para o próximo
        videos.forEach((video, index) => {
            video.addEventListener('ended', () => {
                let nextSlide = (index + 1) % videos.length; // volta ao primeiro depois do último
                showSlide(nextSlide);
            });
        });

        // Clique nos dots para trocar manualmente
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                showSlide(index);
            });
        });
    }
});
