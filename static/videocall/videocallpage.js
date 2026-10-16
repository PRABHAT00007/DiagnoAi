
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function btnenable(event) {
    const target = (event && event.target) ? event.target : event;
    if (!target) return;
    const cardEl = target.closest ? target.closest('.doc-card') : null;
    if (cardEl) {
        const bookBtn = cardEl.querySelector('.btn-book-consult, .btn-diagno');
        if (bookBtn) {
            bookBtn.classList.remove('disabled');
            bookBtn.classList.add('ready');
            bookBtn.removeAttribute('disabled');
        }
    }
    // Backward compatibility for hidden table structure
    if (target.parentElement && target.parentElement.parentElement && target.parentElement.parentElement.nextElementSibling) {
        try {
            target.parentElement.parentElement.nextElementSibling.children[0].classList.remove('disabled');
        } catch(e) {}
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.slot-pill-group input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', btnenable);
        if (radio.checked) {
            btnenable({ target: radio });
        }
    });

    document.querySelectorAll('.slot-label-btn').forEach(label => {
        label.addEventListener('click', function(e) {
            const forId = this.getAttribute('for');
            if (forId) {
                const radio = document.getElementById(forId);
                if (radio) {
                    radio.checked = true;
                    btnenable({ target: radio });
                }
            }
        });
    });
});

function book(event) {
    const isAuth = window.IS_USER_AUTHENTICATED === true;
    const modalBodyEl = document.getElementById('modalBody');
    const modalFooterEl = document.querySelectorAll('.modal-footer')[0];
    const modalTitleEl = document.getElementById('exampleModalLabel');

    let docName = "Specialist";
    let spec = "";
    let selectedSlot = "Right Now";

    // Try finding checked slot in closest card
    const cardEl = event.target.closest('.doc-card');
    if (cardEl) {
        docName = cardEl.getAttribute('data-doctor-name') || (cardEl.querySelector('h5') ? cardEl.querySelector('h5').textContent.trim() : "Specialist");
        const specBadge = cardEl.querySelector('.diagno-badge');
        if (specBadge) spec = specBadge.textContent.trim();

        const checkedRadio = cardEl.querySelector('input[type="radio"]:checked');
        if (checkedRadio) {
            selectedSlot = checkedRadio.value;
        }
    }

    const displayDocName = docName.startsWith('Dr.') ? docName : `Dr. ${docName}`;

    if (!isAuth) {
        // Redirect directly to login page preserving return URL
        const nextUrl = window.location.pathname + window.location.search;
        window.location.href = `/auth/login/?next=${encodeURIComponent(nextUrl || '/auth/book-appointment')}`;
        return;
    }

    // Authenticated User Flow
    modalTitleEl.textContent = "Your Appointment Details";
    const formdata = new FormData();
    formdata.append('doctorName', docName);
    formdata.append('timeSlot', selectedSlot);

    if (selectedSlot === "Right Now") {
        modalFooterEl.classList.add('d-none');
        modalBodyEl.innerHTML = `
            <div class="text-center py-4">
                <div class="loader"></div>
                <h5 style="font-weight: 800; color: var(--text-primary); margin-top: 1rem;">Connecting to ${displayDocName}...</h5>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Connecting to the physician's active telehealth video room.</p>
            </div>
        `;
        showBookingModal();
        setTimeout(() => {
            document.getElementById('modalcross').click();
            document.getElementById('videobtn').classList.remove('d-none');
            if (window.DiagnoToast) {
                DiagnoToast.success(`${displayDocName} accepted your immediate session. Click 'Join Secure Video Consultation Room' below to start.`, 'Consultation Ready');
            }
        }, 1800);
    } else {
        modalFooterEl.classList.remove('d-none');
        modalBodyEl.innerHTML = `
            <div style="background: var(--bg-main); border-radius: var(--radius-md); padding: 1.25rem; margin-bottom: 1rem;">
                <p style="margin-bottom: 0.5rem;"><strong>Doctor:</strong> ${displayDocName}</p>
                <p style="margin-bottom: 0.5rem;"><strong>Specialization:</strong> ${spec || 'Clinical Specialist'}</p>
                <p style="margin-bottom: 0;"><strong>Selected Time Slot:</strong> <span class="diagno-badge diagno-badge-blue">${selectedSlot}</span></p>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0;">A confirmation email with the video consultation link will be dispatched to your registered email.</p>
        `;

        let conbtn = document.getElementById('modalconfirm');
        // Remove existing listeners by cloning
        const newConBtn = conbtn.cloneNode(true);
        conbtn.parentNode.replaceChild(newConBtn, conbtn);

        newConBtn.addEventListener('click', () => {
            axios.post('', formdata, {
                headers: {
                    "Content-Type": 'multipart/form-data',
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            }).then((response) => {
                document.getElementById('modalcross').click();
                document.getElementById('meetingconfirm').click();
                if (window.DiagnoToast) {
                    DiagnoToast.success(`Appointment confirmed with ${displayDocName} for ${selectedSlot}`, 'Booking Scheduled');
                }
            }).catch((error) => {
                console.error(error);
                if (window.DiagnoToast) {
                    DiagnoToast.error('Failed to schedule appointment. Please try again.', 'Booking Error');
                }
            });
        });

        showBookingModal();
    }
}

function showBookingModal() {
    const modalEl = document.getElementById('exampleModal');
    if (modalEl && window.bootstrap) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
}

function videoCall() {
    callFrame = window.DailyIframe.createFrame({
        iframeStyle: {
            position: "fixed",
            width: "40%",
            height: "70%",
            margin: 0,
            padding: 0,
            bottom: 0,
            right: 0,
        },
        showLeaveButton: true,
        showFullscreenButton: true,
    });
    callFrame.join({
        url: "https://apnacheckup.daily.co/SVBqZbAE0tM8BaU9J4at",
    });
    callFrame.on('left-meeting', (event) => {
        console.log(event);
        document.getElementById('aftermeetingModal').click();
        document.getElementById('videobtn').classList.add('d-none');
        if (window.DiagnoToast) {
            DiagnoToast.info('Video consultation session ended.', 'Call Concluded');
        }
    });
}

// Quick Search Helpers & Global Exports
window.btnenable = btnenable;
window.book = book;
window.videoCall = videoCall;
window.quickFilterCity = function(city) {
    const cityInput = document.getElementById('cityID');
    if (cityInput) {
        cityInput.value = city;
        const form = cityInput.closest('form');
        if (form) form.submit();
    }
};

window.quickFilterSpecialty = function(spec) {
    const specSelect = document.getElementById('inputGroupSelect03');
    if (specSelect) {
        specSelect.value = spec;
        const form = specSelect.closest('form');
        if (form) form.submit();
    }
};



