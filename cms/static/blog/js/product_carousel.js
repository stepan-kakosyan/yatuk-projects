(function () {
    function initCarousel(carousel) {
        var track = carousel.querySelector('[data-carousel-track]');
        var prev = carousel.querySelector('[data-carousel-prev]');
        var next = carousel.querySelector('[data-carousel-next]');

        if (!track || !prev || !next) {
            return;
        }

        var step = function () {
            return Math.max(track.clientWidth * 0.8, 240);
        };

        prev.addEventListener('click', function () {
            track.scrollBy({ left: -step(), behavior: 'smooth' });
        });

        next.addEventListener('click', function () {
            track.scrollBy({ left: step(), behavior: 'smooth' });
        });
    }

    function mount() {
        var carousels = document.querySelectorAll('[data-blog-carousel]');
        carousels.forEach(initCarousel);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mount);
    } else {
        mount();
    }
})();
