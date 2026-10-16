/**
 * DiagnoAI Drag-and-Drop Dropzone & Live Image Preview
 * Provides smooth drag-over visual feedback, file format validation, and instant base64 preview.
 */

(function () {
    'use strict';

    function initDropzones() {
        const dropzones = document.querySelectorAll('.diagno-dropzone');

        dropzones.forEach((dropzone) => {
            if (dropzone.dataset.dropzoneInitialized === 'true') return;
            dropzone.dataset.dropzoneInitialized = 'true';

            const input = dropzone.querySelector('input[type="file"]');
            const previewContainer = dropzone.querySelector('.dropzone-preview');
            const placeholder = dropzone.querySelector('.dropzone-placeholder');
            const fileNameDisplay = dropzone.querySelector('.dropzone-filename');
            const clearBtn = dropzone.querySelector('.dropzone-clear-btn');
            const submitBtn = dropzone.closest('form')?.querySelector('button[type="submit"], input[type="submit"]');

            if (!input) return;

            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
                dropzone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            // Highlight dropzone on dragover
            ['dragenter', 'dragover'].forEach((eventName) => {
                dropzone.addEventListener(eventName, () => {
                    dropzone.classList.add('drag-active');
                }, false);
            });

            ['dragleave', 'drop'].forEach((eventName) => {
                dropzone.addEventListener(eventName, () => {
                    dropzone.classList.remove('drag-active');
                }, false);
            });

            // Handle dropped files
            dropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files && files.length > 0) {
                    input.files = files;
                    handleFiles(files[0]);
                }
            });

            // Handle file input change
            input.addEventListener('change', (e) => {
                if (input.files && input.files.length > 0) {
                    handleFiles(input.files[0]);
                }
            });

            function handleFiles(file) {
                if (!file.type.startsWith('image/')) {
                    if (window.DiagnoToast) {
                        DiagnoToast.error('Please upload a valid medical image file (.jpg, .jpeg, .png, .dicom).', 'Invalid File Type');
                    }
                    return;
                }

                if (file.size > 15 * 1024 * 1024) {
                    if (window.DiagnoToast) {
                        DiagnoToast.error('Medical scan file size must be less than 15MB.', 'File Too Large');
                    }
                    return;
                }

                const reader = new FileReader();
                reader.onload = (e) => {
                    if (previewContainer) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 280px; border-radius: var(--radius-md); object-fit: contain; box-shadow: var(--shadow-md);">`;
                        previewContainer.classList.remove('d-none');
                    }
                    if (placeholder) placeholder.classList.add('d-none');
                    if (fileNameDisplay) {
                        fileNameDisplay.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                        fileNameDisplay.classList.remove('d-none');
                    }
                    if (clearBtn) clearBtn.classList.remove('d-none');
                    if (submitBtn) submitBtn.classList.remove('disabled');

                    if (window.DiagnoToast) {
                        DiagnoToast.info(`Uploaded: ${file.name}`, 'Scan Ready');
                    }
                };
                reader.readAsDataURL(file);
            }

            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    input.value = '';
                    if (previewContainer) {
                        previewContainer.innerHTML = '';
                        previewContainer.classList.add('d-none');
                    }
                    if (placeholder) placeholder.classList.remove('d-none');
                    if (fileNameDisplay) {
                        fileNameDisplay.textContent = '';
                        fileNameDisplay.classList.add('d-none');
                    }
                    clearBtn.classList.add('d-none');
                });
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initDropzones);
    window.initDiagnoDropzones = initDropzones;
})();
