/**
 * DiagnoAI Interactive Radiological Split Comparison Slider
 * Provides smooth draggable comparison between Raw Medical Scans and AI Segmentation/Heatmaps.
 */

(function () {
    'use strict';

    function initImageSliders() {
        const containers = document.querySelectorAll('.diagno-slider-container');

        containers.forEach((container) => {
            if (container.dataset.sliderInitialized === 'true') return;
            container.dataset.sliderInitialized = 'true';

            const beforeImage = container.querySelector('.slider-img-before');
            const handle = container.querySelector('.slider-handle');
            const overlay = container.querySelector('.slider-overlay');

            if (!beforeImage || !handle || !overlay) return;

            let isDragging = false;

            function setPosition(xPos) {
                const rect = container.getBoundingClientRect();
                let offsetX = xPos - rect.left;
                if (offsetX < 0) offsetX = 0;
                if (offsetX > rect.width) offsetX = rect.width;

                const percentage = (offsetX / rect.width) * 100;
                handle.style.left = `${percentage}%`;
                overlay.style.width = `${percentage}%`;
            }

            // Mouse Events
            handle.addEventListener('mousedown', (e) => {
                isDragging = true;
                e.preventDefault();
            });

            container.addEventListener('mousedown', (e) => {
                isDragging = true;
                setPosition(e.clientX);
            });

            window.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                setPosition(e.clientX);
            });

            window.addEventListener('mouseup', () => {
                isDragging = false;
            });

            // Touch Events
            handle.addEventListener('touchstart', (e) => {
                isDragging = true;
            }, { passive: true });

            container.addEventListener('touchstart', (e) => {
                isDragging = true;
                if (e.touches[0]) setPosition(e.touches[0].clientX);
            }, { passive: true });

            window.addEventListener('touchmove', (e) => {
                if (!isDragging || !e.touches[0]) return;
                setPosition(e.touches[0].clientX);
            }, { passive: true });

            window.addEventListener('touchend', () => {
                isDragging = false;
            });
        });
    }

    document.addEventListener('DOMContentLoaded', initImageSliders);
    window.initDiagnoSliders = initImageSliders;
})();
