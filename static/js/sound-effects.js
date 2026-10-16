/**
 * DiagnoAI Cyber-Clinical Audio FX System
 * High-performance, zero-latency Web Audio API synthesizer for interactive UI feedback.
 */

(function () {
    'use strict';

    let audioCtx = null;
    let isSoundEnabled = localStorage.getItem('diagnoai_sound_enabled') !== 'false'; // Default to true

    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    // Initialize AudioContext on first user interaction (browser autoplay policy)
    function initOnInteraction() {
        getAudioContext();
        window.removeEventListener('click', initOnInteraction);
        window.removeEventListener('keydown', initOnInteraction);
        window.removeEventListener('touchstart', initOnInteraction);
    }
    window.addEventListener('click', initOnInteraction, { once: true });
    window.addEventListener('keydown', initOnInteraction, { once: true });
    window.addEventListener('touchstart', initOnInteraction, { once: true });

    // --- Sound Synthesis Functions ---

    /**
     * Subtle ethereal blip on hover
     */
    function playHoverSound() {
        if (!isSoundEnabled) return;
        const ctx = getAudioContext();
        if (!ctx) return;

        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1100, ctx.currentTime + 0.035);

            gain.gain.setValueAtTime(0.018, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.035);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.035);
        } catch (e) {}
    }

    /**
     * Crisp modern tactile click
     */
    function playClickSound() {
        if (!isSoundEnabled) return;
        const ctx = getAudioContext();
        if (!ctx) return;

        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(540, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.045);

            gain.gain.setValueAtTime(0.04, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.045);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.045);
        } catch (e) {}
    }

    /**
     * Melodic dual-tone chime on switch/toggle/accordion/tab
     */
    function playToggleSound(state = true) {
        if (!isSoundEnabled) return;
        const ctx = getAudioContext();
        if (!ctx) return;

        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            const now = ctx.currentTime;

            if (state) {
                // Rising chime (activation)
                osc.frequency.setValueAtTime(440, now);
                osc.frequency.exponentialRampToValueAtTime(740, now + 0.065);
            } else {
                // Falling chime (deactivation)
                osc.frequency.setValueAtTime(740, now);
                osc.frequency.exponentialRampToValueAtTime(440, now + 0.065);
            }

            gain.gain.setValueAtTime(0.035, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.065);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start(now);
            osc.stop(now + 0.065);
        } catch (e) {}
    }

    /**
     * Uplifting diagnostic completion chord
     */
    function playSuccessSound() {
        if (!isSoundEnabled) return;
        const ctx = getAudioContext();
        if (!ctx) return;

        try {
            const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
            const now = ctx.currentTime;

            notes.forEach((freq, idx) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                const start = now + idx * 0.045;
                const dur = 0.22;

                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, start);

                gain.gain.setValueAtTime(0.03, start);
                gain.gain.exponentialRampToValueAtTime(0.0001, start + dur);

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.start(start);
                osc.stop(start + dur);
            });
        } catch (e) {}
    }

    /**
     * Throttle hover sounds so rapid mouse movements are pleasant
     */
    let lastHoverTime = 0;
    function throttledHover() {
        const now = Date.now();
        if (now - lastHoverTime > 60) {
            lastHoverTime = now;
            playHoverSound();
        }
    }

    // --- Global Event Listeners ---
    document.addEventListener('DOMContentLoaded', () => {
        // 1. Hover Listener Delegation
        const hoverSelector = `
            .btn-diagno,
            .diagno-nav-link,
            .diagno-dropdown-item,
            .symptom-chip-preset,
            .diagno-feature-card,
            .diagno-tech-badge,
            .diagno-mobile-toggle,
            .btn-close,
            .nav-link,
            .accordion-button,
            button,
            input[type="submit"],
            input[type="button"],
            .card[onclick],
            [data-bs-toggle]
        `;

        document.body.addEventListener('mouseover', (e) => {
            const target = e.target.closest(hoverSelector);
            if (target) {
                throttledHover();
            }
        });

        // 2. Click Listener Delegation
        const clickSelector = `
            .btn-diagno,
            .diagno-dropdown-item,
            .symptom-chip-preset,
            .diagno-nav-link,
            .btn-close,
            button,
            input[type="submit"],
            input[type="button"],
            a.btn,
            .modal-footer button
        `;

        document.body.addEventListener('click', (e) => {
            const target = e.target.closest(clickSelector);
            if (target) {
                if (!target.classList.contains('disabled')) {
                    playClickSound();
                }
            }
        });

        // 3. Toggle & Switch Listener Delegation
        document.body.addEventListener('change', (e) => {
            const target = e.target;
            if (target.matches('input[type="checkbox"], input[type="radio"], select, .form-check-input, .form-switch input')) {
                playToggleSound(target.checked !== false);
            }
        });

        // Accordion click handling
        document.body.addEventListener('click', (e) => {
            const accBtn = e.target.closest('.accordion-button');
            if (accBtn) {
                const isCollapsed = accBtn.classList.contains('collapsed');
                playToggleSound(!isCollapsed);
            }
        });

        // Sound Toggle Button Handler
        const toggleBtn = document.getElementById('diagnoSoundToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                toggleSound();
            });
        }

        updateSoundToggleUI();
    });

    function toggleSound() {
        isSoundEnabled = !isSoundEnabled;
        localStorage.setItem('diagnoai_sound_enabled', isSoundEnabled ? 'true' : 'false');
        updateSoundToggleUI();
        if (isSoundEnabled) {
            playSuccessSound();
        }
    }

    function updateSoundToggleUI() {
        const toggleBtn = document.getElementById('diagnoSoundToggle');
        if (toggleBtn) {
            if (isSoundEnabled) {
                toggleBtn.innerHTML = '<i data-lucide="volume-2" style="width: 18px; height: 18px; color: var(--cyan-600);"></i>';
                toggleBtn.setAttribute('title', 'Sound Effects: Active (Click to Mute)');
            } else {
                toggleBtn.innerHTML = '<i data-lucide="volume-x" style="width: 18px; height: 18px; color: var(--text-muted);"></i>';
                toggleBtn.setAttribute('title', 'Sound Effects: Muted (Click to Unmute)');
            }
            if (window.lucide) {
                lucide.createIcons();
            }
        }
    }

    // Export Global API
    window.DiagnoSound = {
        hover: playHoverSound,
        click: playClickSound,
        toggle: playToggleSound,
        success: playSuccessSound,
        toggleMute: toggleSound,
        isEnabled: () => isSoundEnabled,
    };
})();
