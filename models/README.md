# 🧠 Pre-Trained Model Weights Directory

Due to GitHub's file size limitations (files exceeding 25MB/100MB), the pre-trained neural network weights and tabular classifiers are hosted externally on Google Drive.

---

## 📥 Download Instructions

1. Download all pre-trained model files from the Google Drive link:
   👉 **[Download DiagnoAI Model Weights (Google Drive)](INSERT_YOUR_GDRIVE_LINK_HERE)**

2. Place the downloaded `.h5`, `.pt`, and `.pkl` files directly into this `models/` directory:

| Filename | Type | Size | Modality / Purpose |
| :--- | :--- | :--- | :--- |
| `alzheimer-model.h5` | Keras / TensorFlow | ~1.1 GB | Alzheimer's MRI Staging (4 dementia classes) |
| `brain_model.h5` | Keras / TensorFlow | ~78 MB | Brain Tumor Classifier (Glioma, Meningioma, Pituitary, Normal) |
| `brain_tumor_segmentor.pt` | PyTorch | ~7.8 MB | UNet 512x512 Pixel-Level Brain Tumor Localization |
| `covid-model.h5` | Keras / TensorFlow | ~35 MB | COVID-19 & Viral Pneumonia Chest Radiograph Screening |
| `gl_model.h5` | Keras / TensorFlow | ~2.6 GB | Glaucoma Optic Cup/Disc Retinal Fundus Screening |
| `malaria-model.h5` | Keras / TensorFlow | ~126 MB | Malaria Giemsa-Stained Blood Cell Parasite Classifier |
| `cancer-model.pkl` | Scikit-Learn | ~10 KB | Breast Cancer FNA Cytology Diagnostic Model |
| `diabetes-model.pkl` | Scikit-Learn | ~1.9 MB | Diabetes Mellitus Metabolic Risk Model |
| `heart-model.pkl` | Scikit-Learn | ~2.0 MB | Cardiovascular Disease Risk Scoring Model |
| `liver-model.pkl` | Scikit-Learn | ~6.7 MB | Hepatic / Liver Disease Biochemical Model |

---

## ⚠️ Notes
- The CSV metadata files (`training.csv`, `symptom_description.csv`, `symptom_precaution.csv`, `symptom_severity.csv`) and Python inference code (`classifiers.py`, `transcribe.py`, `utils.py`) are tracked in the repository and already present in this folder.
- Do not rename any of the downloaded weight files, as `models/classifiers.py` loads them by their exact names.
