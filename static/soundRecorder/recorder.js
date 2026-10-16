/**
 * DiagnoAI - Dual-Method Clinical Symptom AI & Voice Dictation Engine
 * Complete Rebuild v6.0
 */

// ==========================================
// 1. DATASET VOCABULARY & ALIASES
// ==========================================

const ALL_SYMPTOMS = [
    "abdominal_pain", "abnormal_menstruation", "acidity", "acute_liver_failure",
    "altered_sensorium", "anxiety", "back_pain", "belly_pain", "blackheads",
    "bladder_discomfort", "blister", "bloody_stool", "blurred_and_distorted_vision",
    "breathlessness", "brittle_nails", "bruising", "burning_micturition",
    "chest_pain", "chills", "cold_hands_and_feets", "coma", "congestion",
    "constipation", "continuous_feel_of_urine", "continuous_sneezing", "cough",
    "cramps", "dark_urine", "dehydration", "depression", "diarrhoea", "dizziness",
    "drying_and_tingling_lips", "enlarged_thyroid", "excessive_hunger", "extra_marital_contacts",
    "fabric_rash", "family_history", "fast_heart_rate", "fatigue", "fluid_overload",
    "foul_smell_of_urine", "frequent_urination", "headache", "high_fever", "hip_joint_pain",
    "history_of_alcohol_consumption", "indigestion", "inflammatory_nails", "internal_itching",
    "irregular_sugar_level", "irritability", "irritation_in_anus", "itching", "joint_pain",
    "knee_pain", "lack_of_concentration", "lethargy", "loss_of_appetite", "loss_of_balance",
    "loss_of_smell", "loss_of_taste", "malaise", "mild_fever", "mood_swings",
    "movement_stiffness", "mucoid_sputum", "muscle_pain", "muscle_wasting",
    "muscle_weakness", "nausea", "neck_pain", "nodal_skin_eruptions", "obesity",
    "pain_behind_the_eyes", "pain_during_bowel_movements", "pain_in_anal_region",
    "painful_walking", "palpitations", "passage_of_gases", "patches_in_throat",
    "phlegm", "polyuria", "prominent_veins_on_calf", "puffy_face_and_eyes",
    "pus_filled_pimples", "receiving_blood_transfusion", "receiving_unsterile_injections",
    "red_sore_around_nose", "red_spots_over_body", "redness_of_eyes", "restlessness",
    "runny_nose", "rusty_sputum", "scabbing", "shivering", "silver_like_dusting",
    "sinus_pressure", "skin_peeling", "skin_rash", "slurred_speech", "small_dents_in_nails",
    "spinning_movements", "spotting_urination", "stiff_neck", "stomach_bleeding",
    "stomach_pain", "sunken_eyes", "sweating", "swelled_lymph_nodes", "swelling_joints",
    "swelling_of_stomach", "swollen_blood_vessels", "swollen_extremities", "swollen_legs",
    "throat_irritation", "toxic_look_(typhos)", "ulcers_on_tongue", "unsteadiness",
    "visual_disturbances", "vomiting", "watering_from_eyes", "weakness_in_limbs",
    "weakness_of_one_body_side", "weight_gain", "weight_loss", "wheezing",
    "yellow_crust_ooze", "yellow_urine", "yellowing_of_eyes", "yellowish_skin"
];

const SYMPTOM_ALIASES = {
    "fever": "high_fever",
    "high fever": "high_fever",
    "mild fever": "mild_fever",
    "low grade fever": "mild_fever",
    "temperature": "high_fever",
    "pyrexia": "high_fever",
    "cold": "continuous_sneezing",
    "sneezing": "continuous_sneezing",
    "sneeze": "continuous_sneezing",
    "runny nose": "runny_nose",
    "running nose": "runny_nose",
    "sore throat": "throat_irritation",
    "throat pain": "throat_irritation",
    "throat irritation": "throat_irritation",
    "cough": "cough",
    "coughing": "cough",
    "dry cough": "cough",
    "wet cough": "cough",
    "headache": "headache",
    "head ache": "headache",
    "migraine": "headache",
    "chills": "chills",
    "shivering": "shivering",
    "body pain": "muscle_pain",
    "body ache": "muscle_pain",
    "muscle pain": "muscle_pain",
    "joint pain": "joint_pain",
    "joint ache": "joint_pain",
    "knee pain": "knee_pain",
    "back pain": "back_pain",
    "back ache": "back_pain",
    "stomach pain": "stomach_pain",
    "stomach ache": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "belly pain": "belly_pain",
    "loose motion": "diarrhoea",
    "loose motions": "diarrhoea",
    "diarrhea": "diarrhoea",
    "diarrhoea": "diarrhoea",
    "vomit": "vomiting",
    "vomiting": "vomiting",
    "throwing up": "vomiting",
    "nausea": "nausea",
    "nauseous": "nausea",
    "gas": "acidity",
    "acidity": "acidity",
    "heartburn": "acidity",
    "acid reflux": "acidity",
    "indigestion": "indigestion",
    "constipation": "constipation",
    "chest pain": "chest_pain",
    "breathlessness": "breathlessness",
    "shortness of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "fatigue": "fatigue",
    "tired": "fatigue",
    "tiredness": "fatigue",
    "exhaustion": "fatigue",
    "weakness": "weakness_in_limbs",
    "dizziness": "dizziness",
    "dizzy": "dizziness",
    "vertigo": "dizziness",
    "sweating": "sweating",
    "skin rash": "skin_rash",
    "rash": "skin_rash",
    "rashes": "skin_rash",
    "itching": "itching",
    "itchy": "itching",
    "itch": "itching",
    "dark urine": "dark_urine",
    "yellow urine": "yellow_urine",
    "yellow eyes": "yellowing_of_eyes",
    "yellow skin": "yellowish_skin",
    "jaundice": "yellowing_of_eyes",
    "loss of appetite": "loss_of_appetite",
    "loss of smell": "loss_of_smell",
    "loss of taste": "loss_of_taste",
    "fast heart rate": "fast_heart_rate",
    "rapid heartbeat": "fast_heart_rate",
    "palpitations": "palpitations",
    "swollen legs": "swollen_legs",
    "swollen lymph nodes": "swelled_lymph_nodes",
    "sinus pain": "sinus_pressure",
    "sinus pressure": "sinus_pressure",
    "blurred vision": "blurred_and_distorted_vision",
    "burning urination": "burning_micturition",
    "frequent urination": "polyuria",
    "weight loss": "weight_loss",
    "weight gain": "weight_gain",
    "anxiety": "anxiety",
    "depression": "depression",
    "wheezing": "wheezing"
};

const ORGAN_CATEGORIES = {
    head: [
        "headache", "dizziness", "blurred_and_distorted_vision", "loss_of_smell",
        "loss_of_taste", "sinus_pressure", "runny_nose", "continuous_sneezing",
        "throat_irritation", "anxiety", "depression", "altered_sensorium",
        "pain_behind_the_eyes", "redness_of_eyes", "stiff_neck"
    ],
    chest: [
        "chest_pain", "breathlessness", "cough", "phlegm", "fast_heart_rate",
        "palpitations", "wheezing", "sweating", "chills", "high_fever",
        "mild_fever", "mucoid_sputum"
    ],
    abdomen: [
        "stomach_pain", "abdominal_pain", "acidity", "indigestion", "vomiting",
        "nausea", "loss_of_appetite", "diarrhoea", "constipation", "dark_urine",
        "yellowing_of_eyes", "yellowish_skin", "belly_pain", "passage_of_gases"
    ],
    joints: [
        "joint_pain", "swelling_joints", "knee_pain", "back_pain", "neck_pain",
        "muscle_pain", "muscle_weakness", "weakness_in_limbs", "movement_stiffness",
        "hip_joint_pain", "cramps"
    ],
    skin: [
        "skin_rash", "itching", "yellowish_skin", "blister", "nodal_skin_eruptions",
        "sweating", "blackheads", "pus_filled_pimples", "red_spots_over_body",
        "skin_peeling", "scabbing"
    ],
    all: [
        "high_fever", "mild_fever", "headache", "cough", "fatigue", "chills",
        "joint_pain", "chest_pain", "breathlessness", "vomiting", "nausea",
        "stomach_pain", "diarrhoea", "skin_rash", "itching", "dizziness",
        "loss_of_appetite", "sweating", "throat_irritation", "runny_nose",
        "acidity", "constipation"
    ]
};

// ==========================================
// 2. STATE MANAGEMENT
// ==========================================

let selectedSymptoms = new Set();
let latestVoiceTranscriptText = '';
let isVoiceRecording = false;
let speechRecognizer = null;
let visualizerAnimFrame = null;
let latestDiagnosisResult = null;

function formatSymptomName(sym) {
    if (!sym) return '';
    return String(sym)
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

function resolveCanonical(input) {
    if (!input) return null;
    const clean = String(input).trim().toLowerCase();
    const underscore = clean.replace(/\s+/g, '_');
    const space = clean.replace(/_/g, ' ');

    if (ALL_SYMPTOMS.includes(underscore)) return underscore;
    if (ALL_SYMPTOMS.includes(clean)) return clean;

    if (SYMPTOM_ALIASES[space]) return SYMPTOM_ALIASES[space];
    if (SYMPTOM_ALIASES[underscore]) return SYMPTOM_ALIASES[underscore];
    if (SYMPTOM_ALIASES[clean]) return SYMPTOM_ALIASES[clean];

    const exact = ALL_SYMPTOMS.find(s => s === underscore || s.replace(/_/g, ' ') === space);
    if (exact) return exact;

    const starts = ALL_SYMPTOMS.find(s => s.startsWith(underscore + '_') || s.startsWith(underscore));
    if (starts) return starts;

    return underscore;
}

function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input && input.value) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

// ==========================================
// 3. METHOD A: TOKENIZER LOGIC
// ==========================================

function addSymptom(name) {
    if (!name) return;
    const resolved = resolveCanonical(name);
    if (!resolved) return;

    if (selectedSymptoms.has(resolved)) {
        if (window.DiagnoToast) DiagnoToast.info(`"${formatSymptomName(resolved)}" is already added.`, 'Already Selected');
        return;
    }

    selectedSymptoms.add(resolved);
    renderAllTokens();
    updateVoiceChipsUI();

    const searchInput = document.getElementById('symptomSearchInput');
    if (searchInput) searchInput.value = '';
    hideAutocompleteDropdown();

    if (window.DiagnoToast) {
        DiagnoToast.success(`Added: ${formatSymptomName(resolved)}`, 'Symptom Added');
    }
}

function removeSymptom(name) {
    if (!name) return;
    const resolved = resolveCanonical(name) || name;
    selectedSymptoms.delete(resolved);
    selectedSymptoms.delete(String(name).trim().toLowerCase().replace(/\s+/g, '_'));
    selectedSymptoms.delete(String(name).trim().toLowerCase());

    renderAllTokens();
    updateVoiceChipsUI();

    if (window.DiagnoToast) {
        DiagnoToast.info(`Removed: ${formatSymptomName(resolved)}`, 'Symptom Removed');
    }
}

function toggleSymptom(name) {
    if (!name) return;
    const resolved = resolveCanonical(name) || name;
    if (selectedSymptoms.has(resolved)) {
        removeSymptom(resolved);
    } else {
        addSymptom(resolved);
    }
}

function clearAllSymptoms() {
    selectedSymptoms.clear();
    renderAllTokens();
    updateVoiceChipsUI();

    const resultsCard = document.getElementById('resultsAccordionCard');
    if (resultsCard) resultsCard.style.display = 'none';

    if (window.DiagnoToast) {
        DiagnoToast.info('All symptoms cleared.', 'Reset');
    }
}

function renderAllTokens() {
    const container = document.getElementById('selectedTokensContainer');
    const analyzeBtn = document.getElementById('analyzeSymptomsBtn');
    const clearBtn = document.getElementById('clearAllSymptomsBtn');
    const countBadge = document.getElementById('symptomCountBadge');

    // 1. Update quick preset chips visual active states
    document.querySelectorAll('.symptom-chip-preset').forEach(chip => {
        const sym = chip.getAttribute('data-sym');
        if (!sym) return;
        const resolved = resolveCanonical(sym);
        const isActive = selectedSymptoms.has(resolved) || selectedSymptoms.has(sym);

        if (isActive) {
            chip.classList.add('active');
            chip.innerHTML = `<i data-lucide="check" style="width: 12px; height: 12px;"></i> ${formatSymptomName(sym)}`;
        } else {
            chip.classList.remove('active');
            chip.innerHTML = `<i data-lucide="plus" style="width: 12px; height: 12px;"></i> ${formatSymptomName(sym)}`;
        }
    });

    // 2. Update count badge & clear button
    if (countBadge) {
        countBadge.textContent = `${selectedSymptoms.size} Selected`;
        countBadge.style.display = selectedSymptoms.size > 0 ? 'inline-block' : 'none';
    }
    if (clearBtn) {
        clearBtn.style.display = selectedSymptoms.size > 0 ? 'inline-flex' : 'none';
    }

    // 3. Update Analyze Symptoms button state
    if (analyzeBtn) {
        if (selectedSymptoms.size > 0) {
            analyzeBtn.removeAttribute('disabled');
            analyzeBtn.classList.remove('disabled');
        } else {
            analyzeBtn.setAttribute('disabled', 'true');
            analyzeBtn.classList.add('disabled');
        }
    }

    // 4. Render tokens in container
    if (!container) return;
    container.innerHTML = '';

    if (selectedSymptoms.size === 0) {
        container.innerHTML = `
            <div class="text-muted text-center py-4 w-100" style="font-size: 0.88rem; pointer-events: none;">
                <i data-lucide="plus-circle" style="width: 20px; height: 20px; display: block; margin: 0 auto 0.35rem; color: #94a3b8;"></i>
                No symptoms added yet. Click quick chips above, search, or dictate on the right.
            </div>
        `;
    } else {
        selectedSymptoms.forEach(sym => {
            const token = document.createElement('div');
            token.className = 'diagno-symptom-chip';
            token.innerHTML = `
                <span>${formatSymptomName(sym)}</span>
                <button type="button" class="btn-remove-token" aria-label="Remove ${formatSymptomName(sym)}" title="Remove">&times;</button>
            `;
            token.querySelector('.btn-remove-token').onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                removeSymptom(sym);
            };
            container.appendChild(token);
        });
    }

    if (window.lucide) lucide.createIcons();
}

function populateSymptomDropdown() {
    const select = document.getElementById('symptomSelectDropdown');
    if (!select) return;

    // Clear existing options except placeholder
    select.innerHTML = '<option value="" disabled selected>-- Choose a symptom to add (140+ dataset items) --</option>';

    // Sort symptoms alphabetically by display name
    const sorted = [...ALL_SYMPTOMS].sort((a, b) => {
        const nameA = formatSymptomName(a).toLowerCase();
        const nameB = formatSymptomName(b).toLowerCase();
        return nameA.localeCompare(nameB);
    });

    sorted.forEach(sym => {
        const opt = document.createElement('option');
        opt.value = sym;
        opt.textContent = formatSymptomName(sym);
        select.appendChild(opt);
    });
}

function onSymptomDropdownSelect(selectEl) {
    if (!selectEl || !selectEl.value) return;
    const val = selectEl.value;
    addSymptom(val);
    selectEl.selectedIndex = 0;
}

function addSelectedFromDropdown() {
    const select = document.getElementById('symptomSelectDropdown');
    if (!select || !select.value) {
        if (window.DiagnoToast) DiagnoToast.warning('Please select a symptom from the dropdown list.', 'No Symptom Selected');
        return;
    }
    const val = select.value;
    addSymptom(val);
    select.selectedIndex = 0;
}

function setDurationDays(days) {
    const input = document.getElementById('durationDaysInput');
    if (input) input.value = days;

    document.querySelectorAll('.duration-pill').forEach(pill => {
        pill.classList.remove('active');
        if (pill.getAttribute('data-days') == days) {
            pill.classList.add('active');
        }
    });
}

function initSearchListeners() {
    const searchInput = document.getElementById('symptomSearchInput');
    const dropdown = document.getElementById('symptomDropdown');
    if (!searchInput || !dropdown) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query.length < 1) {
            hideAutocompleteDropdown();
            return;
        }

        const querySpace = query.replace(/_/g, ' ');
        const matches = ALL_SYMPTOMS.filter(s => {
            const sClean = s.toLowerCase();
            const sSpace = sClean.replace(/_/g, ' ');
            return sClean.includes(query) || sSpace.includes(querySpace);
        }).slice(0, 10);

        dropdown.innerHTML = '';

        if (matches.length > 0) {
            matches.forEach(m => {
                const item = document.createElement('div');
                item.className = 'symptom-dropdown-item';
                item.innerHTML = `
                    <i data-lucide="plus" style="width: 14px; height: 14px; color: var(--primary-600);"></i>
                    <span>${formatSymptomName(m)}</span>
                `;
                item.onclick = (ev) => {
                    ev.preventDefault();
                    addSymptom(m);
                };
                dropdown.appendChild(item);
            });
        } else {
            const item = document.createElement('div');
            item.className = 'symptom-dropdown-item';
            item.innerHTML = `
                <i data-lucide="plus-circle" style="width: 14px; height: 14px; color: var(--emerald-600);"></i>
                <span>Add Custom: "<strong>${query}</strong>"</span>
            `;
            item.onclick = (ev) => {
                ev.preventDefault();
                addSymptom(query);
            };
            dropdown.appendChild(item);
        }

        dropdown.style.display = 'block';
        if (window.lucide) lucide.createIcons();
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) addSymptom(query);
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            hideAutocompleteDropdown();
        }
    });
}

function hideAutocompleteDropdown() {
    const dropdown = document.getElementById('symptomDropdown');
    if (dropdown) dropdown.style.display = 'none';
}

// ==========================================
// 4. METHOD B: VOICE DICTATION LOGIC
// ==========================================

function toggleVoiceRecording() {
    if (isVoiceRecording) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

function startVoiceRecording() {
    isVoiceRecording = true;

    // 1. Instant UI update
    const mic = document.getElementById('micIconCircle');
    if (mic) mic.classList.add('recording');

    const voiceStatus = document.getElementById('voiceStatus');
    if (voiceStatus) voiceStatus.textContent = "Listening... Speak your symptoms and duration";

    const startBtn = document.getElementById('startVoiceBtn');
    if (startBtn) {
        startBtn.innerHTML = '<i data-lucide="square" style="width: 16px; height: 16px;"></i> <span>Stop Recording</span>';
        startBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        startBtn.style.boxShadow = '0 4px 14px rgba(220, 38, 38, 0.35)';
    }

    const clearVoiceBtn = document.getElementById('clearVoiceCardBtn');
    const clearControlsBtn = document.getElementById('clearVoiceControlsBtn');
    if (clearVoiceBtn) clearVoiceBtn.style.display = 'inline-flex';
    if (clearControlsBtn) {
        clearControlsBtn.classList.remove('disabled');
        clearControlsBtn.removeAttribute('disabled');
    }

    startWaveformAnimation();
    if (window.lucide) lucide.createIcons();

    if (window.DiagnoToast) {
        DiagnoToast.info("Microphone listening... Speak symptoms naturally.", "Voice Recording Started");
    }

    // 2. Start Web Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        try {
            if (speechRecognizer) {
                try { speechRecognizer.abort(); } catch(e) {}
            }
            speechRecognizer = new SpeechRecognition();
            speechRecognizer.continuous = true;
            speechRecognizer.interimResults = true;
            speechRecognizer.lang = 'en-US';

            speechRecognizer.onresult = (event) => {
                let full = '';
                for (let i = 0; i < event.results.length; ++i) {
                    full += event.results[i][0].transcript + ' ';
                }
                const text = full.trim();
                if (text) {
                    latestVoiceTranscriptText = text;
                    const textarea = document.getElementById('voiceLiveTranscript');
                    if (textarea) textarea.value = text;
                    parseSymptomsFromSpeech(text);
                }
            };

            speechRecognizer.onerror = (e) => {
                console.warn("Speech recognition notice:", e.error);
            };

            speechRecognizer.onend = () => {
                if (isVoiceRecording && speechRecognizer) {
                    try { speechRecognizer.start(); } catch(e) {}
                }
            };

            speechRecognizer.start();
        } catch(err) {
            console.warn("Speech recognizer start error:", err);
        }
    }
}

function stopVoiceRecording() {
    isVoiceRecording = false;

    const mic = document.getElementById('micIconCircle');
    if (mic) mic.classList.remove('recording');

    const startBtn = document.getElementById('startVoiceBtn');
    if (startBtn) {
        startBtn.innerHTML = '<i data-lucide="mic" style="width: 16px; height: 16px;"></i> <span>Start Recording</span>';
        startBtn.style.background = '';
        startBtn.style.boxShadow = '';
    }

    const voiceStatus = document.getElementById('voiceStatus');
    if (voiceStatus) {
        voiceStatus.textContent = selectedSymptoms.size > 0 
            ? `${selectedSymptoms.size} Symptom(s) Detected & Ready` 
            : "Voice Processing Complete";
    }

    if (speechRecognizer) {
        try { speechRecognizer.stop(); } catch(e) {}
    }

    stopWaveformAnimation();
    updateVoiceChipsUI();
    if (window.lucide) lucide.createIcons();

    if (selectedSymptoms.size > 0 && window.DiagnoToast) {
        DiagnoToast.success(`Identified: ${Array.from(selectedSymptoms).map(formatSymptomName).join(', ')}`, 'Voice Capture Complete');
    }
}

function clearVoiceDictation() {
    isVoiceRecording = false;
    if (speechRecognizer) {
        try { speechRecognizer.abort(); } catch(e) {}
    }
    stopWaveformAnimation();

    latestVoiceTranscriptText = '';
    const textarea = document.getElementById('voiceLiveTranscript');
    if (textarea) textarea.value = '';

    const mic = document.getElementById('micIconCircle');
    if (mic) mic.classList.remove('recording');

    const voiceStatus = document.getElementById('voiceStatus');
    if (voiceStatus) voiceStatus.textContent = "Ready to Record";

    const startBtn = document.getElementById('startVoiceBtn');
    if (startBtn) {
        startBtn.innerHTML = '<i data-lucide="mic" style="width: 16px; height: 16px;"></i> <span>Start Recording</span>';
        startBtn.style.background = '';
        startBtn.style.boxShadow = '';
    }

    const clearVoiceBtn = document.getElementById('clearVoiceCardBtn');
    const clearControlsBtn = document.getElementById('clearVoiceControlsBtn');
    if (clearVoiceBtn) clearVoiceBtn.style.display = 'none';
    if (clearControlsBtn) {
        clearControlsBtn.classList.add('disabled');
        clearControlsBtn.setAttribute('disabled', 'true');
    }

    selectedSymptoms.clear();
    renderAllTokens();
    updateVoiceChipsUI();

    const resultsCard = document.getElementById('resultsAccordionCard');
    if (resultsCard) resultsCard.style.display = 'none';

    if (window.DiagnoToast) {
        DiagnoToast.info("Voice transcript and symptoms cleared.", "Reset");
    }
    if (window.lucide) lucide.createIcons();
}

function onVoiceTranscriptInput(val) {
    latestVoiceTranscriptText = val || '';
    if (latestVoiceTranscriptText.trim()) {
        parseSymptomsFromSpeech(latestVoiceTranscriptText.trim());
    }
}

function loadSampleVoiceText(sample) {
    latestVoiceTranscriptText = sample;
    const textarea = document.getElementById('voiceLiveTranscript');
    if (textarea) textarea.value = sample;
    parseSymptomsFromSpeech(sample);

    const clearVoiceBtn = document.getElementById('clearVoiceCardBtn');
    const clearControlsBtn = document.getElementById('clearVoiceControlsBtn');
    if (clearVoiceBtn) clearVoiceBtn.style.display = 'inline-flex';
    if (clearControlsBtn) {
        clearControlsBtn.classList.remove('disabled');
        clearControlsBtn.removeAttribute('disabled');
    }

    if (window.DiagnoToast) {
        DiagnoToast.success("Sample dictation loaded and parsed. Click 'Analyze Spoken Symptoms'.", "Sample Loaded");
    }
}

function parseSymptomsFromSpeech(text) {
    if (!text) return;
    const lower = text.toLowerCase();

    // 1. Duration Extraction
    const daysMatch = lower.match(/(?:for|since|past)?\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|fourteen)\s*days?/);
    if (daysMatch) {
        const wordMap = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, fourteen: 14 };
        const d = wordMap[daysMatch[1]] || parseInt(daysMatch[1], 10);
        if (d) setDurationDays(d);
    }

    // 2. Scan Aliases & Dataset
    let newlyAdded = 0;
    Object.keys(SYMPTOM_ALIASES).forEach(alias => {
        const reg = new RegExp('\\b' + alias + '\\b', 'i');
        if (reg.test(lower)) {
            const canonical = SYMPTOM_ALIASES[alias];
            if (!selectedSymptoms.has(canonical)) {
                selectedSymptoms.add(canonical);
                newlyAdded++;
            }
        }
    });

    ALL_SYMPTOMS.forEach(sym => {
        const phrase = sym.replace(/_/g, ' ');
        const reg = new RegExp('\\b' + phrase + '\\b', 'i');
        if (reg.test(lower)) {
            if (!selectedSymptoms.has(sym)) {
                selectedSymptoms.add(sym);
                newlyAdded++;
            }
        }
    });

    if (newlyAdded > 0) {
        renderAllTokens();
    }
    updateVoiceChipsUI();
}

function updateVoiceChipsUI() {
    const wrap = document.getElementById('voiceDetectedSymptomsWrap');
    const chipsBox = document.getElementById('voiceDetectedChips');
    if (!wrap || !chipsBox) return;

    if (selectedSymptoms.size === 0) {
        wrap.style.display = 'none';
        chipsBox.innerHTML = '';
    } else {
        wrap.style.display = 'block';
        chipsBox.innerHTML = '';
        selectedSymptoms.forEach(s => {
            const badge = document.createElement('span');
            badge.className = 'diagno-badge diagno-badge-blue';
            badge.style.cssText = 'padding: 0.25rem 0.65rem; font-size: 0.78rem; display: inline-flex; align-items: center; gap: 0.25rem;';
            badge.innerHTML = `<i data-lucide="check" style="width: 12px; height: 12px;"></i> ${formatSymptomName(s)}`;
            chipsBox.appendChild(badge);
        });
    }
    if (window.lucide) lucide.createIcons();
}

// Real-Time Canvas Waveform Simulation
function startWaveformAnimation() {
    const canvas = document.getElementById('audioWaveformCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let step = 0;
    function draw() {
        if (!isVoiceRecording) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
            return;
        }

        visualizerAnimFrame = requestAnimationFrame(draw);
        step += 0.08;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const bars = 36;
        const barWidth = canvas.width / bars;

        for (let i = 0; i < bars; i++) {
            const h = Math.sin(step + i * 0.35) * (canvas.height * 0.38) + (canvas.height * 0.45);
            const x = i * barWidth;
            const y = (canvas.height - h) / 2;

            const grad = ctx.createLinearGradient(0, canvas.height, 0, 0);
            grad.addColorStop(0, '#06b6d4');
            grad.addColorStop(0.5, '#2563eb');
            grad.addColorStop(1, '#ec4899');

            ctx.fillStyle = grad;
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(x + 2, y, Math.max(barWidth - 4, 3), h, 3);
            } else {
                ctx.rect(x + 2, y, Math.max(barWidth - 4, 3), h);
            }
            ctx.fill();
        }
    }

    draw();
}

function stopWaveformAnimation() {
    if (visualizerAnimFrame) {
        cancelAnimationFrame(visualizerAnimFrame);
        visualizerAnimFrame = null;
    }
    const canvas = document.getElementById('audioWaveformCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
        }
    }
}

// ==========================================
// 5. BACKEND SUBMISSION & DIFFERENTIAL TRIAGE
// ==========================================

function submitSymptomAnalysis() {
    executeTriageRequest('analyzeSymptomsBtn');
}

function submitVoiceAnalysis() {
    const textarea = document.getElementById('voiceLiveTranscript');
    if (textarea && textarea.value.trim()) {
        parseSymptomsFromSpeech(textarea.value.trim());
    }
    executeTriageRequest('sendVoiceBtn');
}

function executeTriageRequest(btnId) {
    if (selectedSymptoms.size === 0) {
        if (window.DiagnoToast) {
            DiagnoToast.warning("Please select, dictate, or type at least one symptom before analyzing.", "No Symptoms Found");
        }
        return;
    }

    const btn = document.getElementById(btnId);
    if (btn) {
        btn.setAttribute('disabled', 'true');
        btn.classList.add('disabled');
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Analyzing Diagnostic Triage...';
    }

    const daysInput = document.getElementById('durationDaysInput');
    const daysVal = daysInput ? daysInput.value || '5' : '5';

    let formData = new FormData();
    formData.append('days', daysVal);

    if (latestVoiceTranscriptText) {
        formData.append('transcript', latestVoiceTranscriptText);
    }

    let count = 0;
    selectedSymptoms.forEach(sym => {
        formData.append(`symptoms${count}`, sym.replace(/_/g, ' '));
        formData.append('symptoms', sym.replace(/_/g, ' '));
        count++;
    });

    axios.post('/know-your-disease/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        if (btn) {
            btn.removeAttribute('disabled');
            btn.classList.remove('disabled');
            btn.innerHTML = `<i data-lucide="activity" style="width: 16px; height: 16px;"></i> <span>${btnId === 'sendVoiceBtn' ? 'Analyze Spoken Symptoms' : 'Re-Analyze Symptoms'}</span>`;
        }

        renderDiagnosisResults(response.data);

        if (window.DiagnoToast) {
            DiagnoToast.success("Diagnostic triage generated successfully.", "Assessment Ready");
        }
    })
    .catch(error => {
        if (btn) {
            btn.removeAttribute('disabled');
            btn.classList.remove('disabled');
            btn.innerHTML = `<i data-lucide="activity" style="width: 16px; height: 16px;"></i> <span>${btnId === 'sendVoiceBtn' ? 'Analyze Spoken Symptoms' : 'Analyze Symptoms'}</span>`;
        }
        console.error("Diagnosis error:", error);
        if (window.DiagnoToast) {
            DiagnoToast.error("Failed to communicate with symptom AI engine.", "Error");
        }
    });
}

function getSpecialistForDisease(disease) {
    const d = String(disease).toLowerCase();
    if (d.includes('heart') || d.includes('hypertension') || d.includes('vascular') || d.includes('paralysis')) return 'Cardiologist';
    if (d.includes('pneumonia') || d.includes('bronchial') || d.includes('tuberculosis') || d.includes('asthma') || d.includes('covid')) return 'Pulmonologist';
    if (d.includes('gerd') || d.includes('peptic') || d.includes('gastro') || d.includes('jaundice') || d.includes('hepatitis') || d.includes('cirrhosis') || d.includes('gastritis')) return 'Gastroenterologist';
    if (d.includes('diabetes') || d.includes('thyroid') || d.includes('hypoglycemia')) return 'Endocrinologist';
    if (d.includes('migraine') || d.includes('vertigo') || d.includes('paralysis') || d.includes('cervical')) return 'Neurologist';
    if (d.includes('arthritis') || d.includes('osteo') || d.includes('spondylosis') || d.includes('gout')) return 'Rheumatologist';
    if (d.includes('acne') || d.includes('fungal') || d.includes('psoriasis') || d.includes('impetigo') || d.includes('eczema')) return 'Dermatologist';
    if (d.includes('urinary') || d.includes('kidney') || d.includes('renal') || d.includes('uti')) return 'Urologist / Nephrologist';
    if (d.includes('malaria') || d.includes('dengue') || d.includes('typhoid') || d.includes('chicken') || d.includes('influenza') || d.includes('strep')) return 'Infectious Disease Specialist';
    return 'General Physician';
}

function renderDiagnosisResults(data) {
    latestDiagnosisResult = data;
    const resultsCard = document.getElementById('resultsAccordionCard');
    const accordionBox = document.getElementById('accordionExample');
    const adviceText = document.getElementById('adviceText');

    if (!resultsCard || !accordionBox) return;

    resultsCard.style.display = 'block';
    accordionBox.innerHTML = '';

    if (adviceText) {
        adviceText.textContent = data.advice || 'Follow clinical precautions and monitor vital signs.';
    }

    const output = data.output || {};
    const entries = Object.entries(output);

    if (entries.length === 0) {
        accordionBox.innerHTML = `
            <div class="alert alert-info" style="border-radius: var(--radius-md);">
                No definitive high-probability match found for the selected combination. Please review your entered symptoms or consult a general physician for comprehensive clinical workup.
            </div>
        `;
    } else {
        entries.forEach(([disease, info], idx) => {
            const isOpen = idx === 0;
            const safeId = disease.replace(/[^a-zA-Z0-9]/g, '');
            const specialist = getSpecialistForDisease(disease);
            const prob = info.probability !== undefined ? info.probability : 50;

            let probBadgeClass = 'diagno-badge-blue';
            if (prob >= 70) probBadgeClass = 'diagno-badge-rose';
            else if (prob >= 40) probBadgeClass = 'diagno-badge-amber';

            const precautionsList = (info.prec || []).map(p => `
                <li class="list-group-item d-flex align-items-center gap-2" style="background: transparent;">
                    <i data-lucide="check-circle-2" style="width: 16px; height: 16px; color: var(--emerald-600); flex-shrink: 0;"></i>
                    <span>${p}</span>
                </li>
            `).join('');

            const item = document.createElement('div');
            item.className = 'accordion-item mb-3';
            item.style.border = '1px solid var(--surface-glass-border)';
            item.style.borderRadius = 'var(--radius-lg)';
            item.style.overflow = 'hidden';

            item.innerHTML = `
                <h2 class="accordion-header" id="heading${safeId}">
                    <button class="accordion-button ${isOpen ? '' : 'collapsed'} d-flex align-items-center" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${safeId}" aria-expanded="${isOpen ? 'true' : 'false'}" aria-controls="collapse${safeId}" style="font-weight: 700; color: var(--text-primary);">
                        <i data-lucide="activity" style="width: 18px; height: 18px; margin-right: 0.6rem; color: var(--primary-600);"></i>
                        <span style="font-size: 1.1rem;">${disease}</span>
                        <div class="d-flex align-items-center gap-2 ms-auto me-3">
                            <span class="diagno-badge ${probBadgeClass}" style="font-size: 0.8rem; font-weight: 700;">${prob}% AI Likelihood</span>
                        </div>
                    </button>
                </h2>
                <div id="collapse${safeId}" class="accordion-collapse collapse ${isOpen ? 'show' : ''}" aria-labelledby="heading${safeId}" data-bs-parent="#accordionExample">
                    <div class="accordion-body" style="background: var(--surface-glass); padding: 1.5rem;">
                        <div class="w-100 mb-3" style="background: rgba(0,0,0,0.06); border-radius: 999px; height: 8px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #2563eb, #06b6d4); height: 100%; width: ${Math.min(prob, 100)}%; border-radius: 999px;"></div>
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <div class="p-3" style="background: var(--surface-card); border-radius: var(--radius-md); border: 1px solid var(--surface-glass-border); height: 100%; display: flex; flex-direction: column;">
                                    <h6 style="font-weight: 800; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
                                        <i data-lucide="file-text" style="width: 16px; height: 16px; color: var(--cyan-600);"></i>
                                        <span>Clinical Pathological Overview</span>
                                    </h6>
                                    <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                                        ${info.desc || 'Comprehensive diagnostic information compiled by DiagnoAI Decision Support Core.'}
                                    </p>
                                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mt-auto pt-2" style="border-top: 1px dashed var(--surface-glass-border);">
                                        <div class="d-flex align-items-center gap-2">
                                            <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">SPECIALIST:</span>
                                            <span class="diagno-badge diagno-badge-purple" style="font-size: 0.8rem;">
                                                <i data-lucide="stethoscope" style="width: 13px; height: 13px;"></i> ${specialist}
                                            </span>
                                        </div>
                                        <a href="/appointment/book-appointment/" class="btn btn-sm btn-outline-primary py-1 px-2" style="font-size: 0.78rem; font-weight: 600; border-radius: var(--radius-full); display: inline-flex; align-items: center; gap: 0.25rem;">
                                            <i data-lucide="calendar-plus" style="width: 12px; height: 12px;"></i> Consult ${specialist}
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="p-3" style="background: var(--surface-card); border-radius: var(--radius-md); border: 1px solid var(--surface-glass-border); height: 100%;">
                                    <h6 style="font-weight: 800; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
                                        <i data-lucide="shield-check" style="width: 16px; height: 16px; color: var(--emerald-600);"></i>
                                        <span>Recommended Clinical Precautions</span>
                                    </h6>
                                    <ul class="list-group list-group-flush">
                                        ${precautionsList}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            accordionBox.appendChild(item);
        });

        // Update top recommended specialist tag in CTA banner
        const topDisease = entries[0][0];
        const topSpecialist = getSpecialistForDisease(topDisease);
        const specialistTag = document.getElementById('consultSpecialistTag');
        if (specialistTag) {
            specialistTag.textContent = topSpecialist;
        }
    }

    if (window.lucide) lucide.createIcons();
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ==========================================
// 6. CLINICAL REPORT MODAL & PRINTING
// ==========================================

function openClinicalReportModal() {
    const docDate = document.getElementById('reportDocDate');
    const docId = document.getElementById('reportDocId');
    const symList = document.getElementById('reportSymptomsList');
    const diffTable = document.getElementById('reportDifferentialTable');
    const precBlock = document.getElementById('reportPrecautionsBlock');

    if (docDate) docDate.textContent = new Date().toLocaleString();
    if (docId) docId.textContent = '#DGN-' + Math.floor(100000 + Math.random() * 900000);

    if (symList) {
        symList.innerHTML = Array.from(selectedSymptoms).map(s => `
            <span class="diagno-badge diagno-badge-blue" style="font-size: 0.8rem;">
                ${formatSymptomName(s)}
            </span>
        `).join('') || '<span class="text-muted">No symptoms recorded.</span>';
    }

    if (diffTable) {
        const output = (latestDiagnosisResult && latestDiagnosisResult.output) ? latestDiagnosisResult.output : {};
        const entries = Object.entries(output);

        if (entries.length === 0) {
            diffTable.innerHTML = '<p class="text-muted mb-0">No differential records available.</p>';
        } else {
            const rows = entries.map(([dis, item]) => {
                const spec = getSpecialistForDisease(dis);
                const prob = item.probability !== undefined ? item.probability : 50;
                let badgeClass = prob >= 70 ? 'diagno-badge-rose' : (prob >= 40 ? 'diagno-badge-amber' : 'diagno-badge-blue');
                return `
                    <tr>
                        <td style="font-weight: 700; color: var(--text-primary);">${dis}</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <span class="diagno-badge ${badgeClass}" style="font-size: 0.75rem;">${prob}%</span>
                                <div style="flex-grow: 1; height: 6px; background: rgba(0,0,0,0.06); border-radius: 99px; overflow: hidden;">
                                    <div style="width: ${prob}%; height: 100%; background: #2563eb;"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="diagno-badge diagno-badge-purple" style="font-size: 0.75rem;">${spec}</span>
                        </td>
                    </tr>
                `;
            }).join('');

            diffTable.innerHTML = `
                <table class="table table-sm table-bordered align-middle mb-0" style="font-size: 0.88rem;">
                    <thead style="background: var(--bg-main);">
                        <tr>
                            <th>Condition / Disease</th>
                            <th>AI Confidence</th>
                            <th>Specialist Referral</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }
    }

    if (precBlock) {
        const output = (latestDiagnosisResult && latestDiagnosisResult.output) ? latestDiagnosisResult.output : {};
        const firstDis = Object.keys(output)[0];
        if (firstDis && output[firstDis]) {
            const prec = output[firstDis].prec || [];
            precBlock.innerHTML = `
                <div class="mb-2"><strong>Primary Condition:</strong> ${firstDis}</div>
                <ul class="mb-2 ps-3" style="font-size: 0.88rem;">
                    ${prec.map(p => `<li>${p}</li>`).join('')}
                </ul>
                <div style="font-size: 0.85rem; color: var(--text-secondary);">
                    <strong>Directive:</strong> ${latestDiagnosisResult.advice || 'Schedule specialist appointment if symptoms persist.'}
                </div>
            `;
        }
    }

    const modalEl = document.getElementById('clinicalReportModal');
    if (modalEl && window.bootstrap) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
        if (window.lucide) lucide.createIcons();
    }
}

function printClinicalReport() {
    window.print();
}

// ==========================================
// 7. GLOBAL EXPORTS & INITIALIZATION
// ==========================================

window.addSymptom = addSymptom;
window.removeSymptom = removeSymptom;
window.toggleSymptom = toggleSymptom;
window.clearAllSymptoms = clearAllSymptoms;
window.setDurationDays = setDurationDays;
window.populateSymptomDropdown = populateSymptomDropdown;
window.onSymptomDropdownSelect = onSymptomDropdownSelect;
window.addSelectedFromDropdown = addSelectedFromDropdown;
window.toggleVoiceRecording = toggleVoiceRecording;
window.startVoiceRecording = startVoiceRecording;
window.stopVoiceRecording = stopVoiceRecording;
window.clearVoiceDictation = clearVoiceDictation;
window.onVoiceTranscriptInput = onVoiceTranscriptInput;
window.loadSampleVoiceText = loadSampleVoiceText;
window.submitSymptomAnalysis = submitSymptomAnalysis;
window.submitVoiceAnalysis = submitVoiceAnalysis;
window.openClinicalReportModal = openClinicalReportModal;
window.printClinicalReport = printClinicalReport;

function initDualSymptomEngine() {
    populateSymptomDropdown();
    initSearchListeners();
    renderAllTokens();
    updateVoiceChipsUI();
    stopWaveformAnimation();

    // Quick chips event delegation
    const quickBox = document.getElementById('quickSymptomChips');
    if (quickBox) {
        quickBox.addEventListener('click', (e) => {
            const chip = e.target.closest('.symptom-chip-preset');
            if (chip) {
                e.preventDefault();
                e.stopPropagation();
                const sym = chip.getAttribute('data-sym');
                if (sym) toggleSymptom(sym);
            }
        });
    }

    if (window.lucide) lucide.createIcons();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDualSymptomEngine);
} else {
    initDualSymptomEngine();
}