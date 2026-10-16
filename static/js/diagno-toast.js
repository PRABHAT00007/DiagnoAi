/**
 * DiagnoAI Modern Glassmorphic Toast Notification Engine
 * Non-blocking, stackable notifications with sound integration.
 */

(function () {
    'use strict';

    let toastContainer = null;

    function getContainer() {
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'diagno-toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 99999;
                display: flex;
                flex-direction: column;
                gap: 12px;
                pointer-events: none;
                max-width: 420px;
                width: calc(100% - 48px);
            `;
            document.body.appendChild(toastContainer);
        }
        return toastContainer;
    }

    const toastIcons = {
        success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
        error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
        info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
        warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`
    };

    function showToast({ title = '', message = '', type = 'info', duration = 4000 }) {
        const container = getContainer();
        const toast = document.createElement('div');
        toast.className = `diagno-toast diagno-toast-${type}`;
        toast.style.cssText = `
            pointer-events: auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#06b6d4'};
            border-radius: 12px;
            padding: 14px 18px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: flex-start;
            gap: 12px;
            transform: translateX(100%);
            opacity: 0;
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease;
            position: relative;
            overflow: hidden;
            font-family: inherit;
        `;

        if (document.documentElement.getAttribute('data-theme') === 'dark') {
            toast.style.background = 'rgba(15, 23, 42, 0.92)';
            toast.style.borderColor = 'rgba(51, 65, 85, 0.8)';
            toast.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.5)';
        }

        const iconHtml = toastIcons[type] || toastIcons.info;

        toast.innerHTML = `
            <div style="flex-shrink: 0; margin-top: 2px;">${iconHtml}</div>
            <div style="flex: 1; min-width: 0;">
                ${title ? `<div style="font-weight: 700; font-size: 0.92rem; color: var(--text-primary); margin-bottom: 2px;">${title}</div>` : ''}
                <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.4;">${message}</div>
            </div>
            <button class="diagno-toast-close" style="background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 0; font-size: 1.2rem; line-height: 1; flex-shrink: 0;" aria-label="Close">&times;</button>
            <div class="diagno-toast-progress" style="position: absolute; bottom: 0; left: 0; height: 3px; background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#06b6d4'}; width: 100%; transform-origin: left; transition: transform ${duration}ms linear;"></div>
        `;

        container.appendChild(toast);

        // Sound FX
        if (window.DiagnoSound) {
            if (type === 'success') window.DiagnoSound.success();
            else if (type === 'error') window.DiagnoSound.toggle(false);
            else window.DiagnoSound.click();
        }

        // Animate in
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
            const progressBar = toast.querySelector('.diagno-toast-progress');
            if (progressBar) {
                requestAnimationFrame(() => {
                    progressBar.style.transform = 'scaleX(0)';
                });
            }
        });

        // Dismiss handlers
        let dismissTimer = setTimeout(dismiss, duration);

        function dismiss() {
            toast.style.transform = 'translateX(110%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 350);
        }

        toast.querySelector('.diagno-toast-close').addEventListener('click', () => {
            clearTimeout(dismissTimer);
            dismiss();
        });
    }

    window.DiagnoToast = {
        show: showToast,
        success: (msg, title = 'Success') => showToast({ title, message: msg, type: 'success' }),
        error: (msg, title = 'Attention Required') => showToast({ title, message: msg, type: 'error' }),
        info: (msg, title = 'Information') => showToast({ title, message: msg, type: 'info' }),
        warning: (msg, title = 'Warning') => showToast({ title, message: msg, type: 'warning' })
    };
})();
