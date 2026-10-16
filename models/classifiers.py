import os
import cv2
import csv
import json
import pickle
import re
import h5py
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from PIL import Image
from models.utils import *

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

import tensorflow as tf
from tensorflow.keras.models import load_model , model_from_json
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import img_to_array , array_to_img , load_img

_cached_models = {}

def get_alzheimer_model():
    if 'alzheimer' not in _cached_models:
        _cached_models['alzheimer'] = load_model("models/alzheimer-model.h5")
    return _cached_models['alzheimer']

def get_covid_model():
    if 'covid' not in _cached_models:
        _cached_models['covid'] = load_model("models/covid-model.h5")
    return _cached_models['covid']

def get_malaria_model():
    if 'malaria' not in _cached_models:
        _cached_models['malaria'] = load_model("models/malaria-model.h5")
    return _cached_models['malaria']

def get_brain_model():
    if 'brain' not in _cached_models:
        _cached_models['brain'] = load_model("models/brain_model.h5")
    return _cached_models['brain']

def get_glaucoma_model():
    if 'glaucoma' not in _cached_models:
        try:
            _cached_models['glaucoma'] = load_model("models/gl_model.h5", compile=False)
        except Exception:
            # Memory-safe loader bypassing optimizer tensors
            h5_path = "models/gl_model.h5"
            with h5py.File(h5_path, 'r') as f:
                cfg = f.attrs['model_config']
                if isinstance(cfg, bytes):
                    cfg = cfg.decode('utf-8')
            model = model_from_json(cfg)
            with h5py.File(h5_path, 'r') as f:
                weight_group = f['model_weights']
                for layer in model.layers:
                    name = layer.name
                    if name in weight_group:
                        g = weight_group[name]
                        weight_names = g.attrs.get('weight_names')
                        if weight_names is not None and len(weight_names) > 0:
                            layer_weights = []
                            subgroup = g[name] if name in g else g
                            for wn in weight_names:
                                if isinstance(wn, bytes):
                                    wn = wn.decode('utf-8')
                                var_name = wn.split('/')[-1]
                                ds = subgroup[var_name]
                                layer_weights.append(np.array(ds))
                            if layer_weights:
                                layer.set_weights(layer_weights)
                                del layer_weights
            _cached_models['glaucoma'] = model
    return _cached_models['glaucoma']

def get_diabetes_model():
    if 'diabetes' not in _cached_models:
        with open('models/diabetes-model.pkl', 'rb') as file:
            _cached_models['diabetes'] = pickle.load(file)
    return _cached_models['diabetes']

def get_heart_model():
    if 'heart' not in _cached_models:
        with open('models/heart-model.pkl', 'rb') as file:
            _cached_models['heart'] = pickle.load(file)
    return _cached_models['heart']

def get_cancer_model():
    if 'cancer' not in _cached_models:
        with open('models/cancer-model.pkl', 'rb') as file:
            _cached_models['cancer'] = pickle.load(file)
    return _cached_models['cancer']

def get_liver_model():
    if 'liver' not in _cached_models:
        with open('models/liver-model.pkl', 'rb') as file:
            _cached_models['liver'] = pickle.load(file)
    return _cached_models['liver']

def get_unet_classifier():
    if 'unet' not in _cached_models:
        unet_model = DynamicUNet([16, 32, 64, 128, 256])
        unet_clf = BrainTumorClassifier(unet_model)
        unet_clf.restore_model("models/brain_tumor_segmentor.pt")
        _cached_models['unet'] = unet_clf
    return _cached_models['unet']

def localizeTumor(img, out_path, pred_label='Pituitary Tumor'):
    if isinstance(img, str):
        with Image.open(img) as opened:
            pil_img = opened.convert("RGB")
    elif isinstance(img, Image.Image):
        pil_img = img.convert("RGB")
    else:
        pil_img = Image.fromarray(np.uint8(img)).convert("RGB")

    w, h = pil_img.size
    rgb_arr = np.array(pil_img)
    mask = None

    # 1. Try UNet segmentor with sensitive threshold
    try:
        gray_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)
        unet_clf = get_unet_classifier()
        unet_mask = unet_clf.predict({"image": gray_arr}, threshold=0.35)
        if unet_mask is not None and unet_mask.sum() > 30:
            mask = unet_mask
    except Exception:
        mask = None

    # 2. If UNet mask is sparse or missed, compute DenseNet attention hotspot
    if mask is None or mask.sum() < 30:
        try:
            m = get_brain_model()
            img_224 = np.expand_dims(np.array(pil_img.resize((224, 224)), dtype=np.float32) / 255.0, axis=0)
            heatmap = make_gradcam_heatmap(img_224, m, 'conv5_block32_concat')
            hmap_full = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
            hmap_full = np.clip(hmap_full, 0, 1.0)
            th = max(0.40, float(np.percentile(hmap_full[hmap_full > 0.1], 75)) if (hmap_full > 0.1).any() else 0.40)
            mask = (hmap_full >= th).astype(np.uint8)
        except Exception:
            mask = np.zeros((h, w), dtype=np.uint8)

    overlay = rgb_arr.copy()
    overlay[mask == 1] = [230, 30, 30]

    blended = cv2.addWeighted(overlay, 0.75, rgb_arr, 0.25, 0)
    result = np.where(mask[:, :, np.newaxis] == 1, blended, rgb_arr)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(result, contours, -1, (255, 20, 20), 2)

    localized_img = Image.fromarray(result.astype(np.uint8))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    localized_img.save(out_path)
    return out_path

def predict_diabetes(features):
    model = get_diabetes_model()
    pred = int(model.predict(features)[0])
    probs = model.predict_proba(features)[0]
    confidence = round(float(probs[pred]) * 100, 1)
    return pred, confidence

def predict_heartD(features):
    model = get_heart_model()
    if hasattr(features, 'shape') and len(features.shape) == 2 and features.shape[1] > 11:
        features = features[:, :11]
    pred = int(model.predict(features)[0])
    probs = model.predict_proba(features)[0]
    confidence = round(float(probs[pred]) * 100, 1)
    return pred, confidence

def predict_cancerB(features):
    model = get_cancer_model()
    pred = str(model.predict(features)[0])
    df = float(model.decision_function(features)[0])
    prob_m = 1.0 / (1.0 + np.exp(-df))
    confidence = round(float(prob_m if pred in ('M', 'm') else (1.0 - prob_m)) * 100, 1)
    return pred, confidence

def predict_liverD(features):
    model = get_liver_model()
    pred = int(model.predict(features)[0])
    probs = model.predict_proba(features)[0]
    confidence = round(float(probs[pred]) * 100, 1)
    return pred, confidence

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    grad_model = tf.keras.models.Model([model.inputs], [model.get_layer(last_conv_layer_name).output, model.output])
    model.layers[-1].activation = None

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]
        
    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    
    return heatmap.numpy()

def save_and_display_gradcam(img_path, heatmap, cam_path, alpha=0.9):
    img = load_img(img_path)
    img = img_to_array(img)

    heatmap = np.uint8(255 * heatmap)
    jet = cm.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]
    jet_heatmap = array_to_img(jet_heatmap)
    
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = img_to_array(jet_heatmap)

    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = array_to_img(superimposed_img)

    superimposed_img.save(cam_path)

def predict_alzheimer(img, img_path, cam_path):
    img = np.asarray(img, dtype=np.float32) / 255.0
    img = img.reshape((1, *img.shape))
    m = get_alzheimer_model()
    class2label = {0: 'Mild Demented', 1: 'Moderate Demented', 2: 'Non Demented', 3: 'Very Mild Demented'}
    raw_preds = m.predict(img)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred = class2label[pred_idx]
    confidence = round(float(raw_preds[pred_idx]) * 100, 1)

    heatmap = make_gradcam_heatmap(img, m, 'block5_pool')
    save_and_display_gradcam(img_path, heatmap, cam_path, alpha=0.9)
    return pred, cam_path, confidence

def predict_covid(img, img_path, cam_path):
    if isinstance(img, Image.Image):
        img = img.convert("L").resize((299, 299))
        img = np.asarray(img, dtype=np.float32) / 255.0
    elif isinstance(img, np.ndarray):
        if img.ndim == 3 and img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = img.astype(np.float32) / 255.0
    
    if img.ndim == 2:
        img = img.reshape((1, 299, 299, 1))
    elif img.ndim == 3 and img.shape[0] != 1:
        img = img.reshape((1, *img.shape))
    elif img.ndim == 3 and img.shape[-1] != 1:
        img = img[:, :, :, :1]

    m = get_covid_model()
    class2label = {0: 'Covid Infected', 1: 'Lung Opacity', 2: 'Healthy', 3: 'Viral Pneumonia'}
    raw_preds = m.predict(img)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred = class2label[pred_idx]
    confidence = round(float(raw_preds[pred_idx]) * 100, 1)

    heatmap = make_gradcam_heatmap(img, m, 'conv2d_18')
    save_and_display_gradcam(img_path, heatmap, cam_path, alpha=0.9)
    return pred, cam_path, confidence

def predict_brain(img, img_path=None, cam_path=None):
    if isinstance(img, Image.Image):
        img_rgb = img.convert("RGB")
    elif isinstance(img, str):
        with Image.open(img) as opened:
            img_rgb = opened.convert("RGB")
    else:
        img_rgb = Image.fromarray(np.uint8(img)).convert("RGB")

    w, h = img_rgb.size
    img_np = np.array(img_rgb)
    img_arr = np.asarray(img_rgb.resize((224, 224)), dtype=np.float32) / 255.0
    if img_arr.ndim == 3:
        img_input = np.expand_dims(img_arr, axis=0)
    else:
        img_input = img_arr

    m = get_brain_model()
    class2label = {0: 'No Tumor', 1: 'Pituitary Tumor', 2: 'Meningioma Tumor', 3: 'Glioma Tumor'}
    raw_preds = m.predict(img_input)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred = class2label[pred_idx]
    confidence = round(float(raw_preds[pred_idx]) * 100, 1)

    if cam_path:
        heatmap = make_gradcam_heatmap(img_input, m, 'conv5_block32_concat', pred_index=pred_idx)
        hmap_full = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
        hmap_full = np.clip(hmap_full, 0, 1.0)

        # When a tumor is present (Pituitary, Meningioma, Glioma), fuse with UNet tumor segmentor to ensure the tumor lesion is vividly highlighted in RED
        if pred_idx > 0:
            try:
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                unet_clf = get_unet_classifier()
                unet_mask = unet_clf.predict({"image": gray}, threshold=0.25)
                if unet_mask is not None and unet_mask.sum() > 20:
                    unet_smooth = cv2.GaussianBlur(unet_mask.astype(np.float32), (15, 15), 0)
                    if unet_smooth.max() > 0:
                        unet_smooth = unet_smooth / unet_smooth.max()
                    hmap_full = np.maximum(hmap_full * 0.7, unet_smooth * 1.0)
                    hmap_full = np.clip(hmap_full, 0, 1.0)
            except Exception:
                pass

        jet = cm.get_cmap("jet")
        jet_colors = (jet(np.arange(256))[:, :3] * 255).astype(np.uint8)
        heatmap_idx = (hmap_full * 255).astype(np.uint8)
        color_cam = jet_colors[heatmap_idx]

        alpha_map = np.clip(hmap_full * 0.85, 0.15, 0.85)[:, :, np.newaxis]
        blended = (alpha_map * color_cam + (1.0 - alpha_map) * img_np).astype(np.uint8)

        out_img = Image.fromarray(blended)
        os.makedirs(os.path.dirname(os.path.abspath(cam_path)), exist_ok=True)
        out_img.save(cam_path)

    return pred, confidence

def predict_glaucoma(img):
    img = np.asarray(img, dtype=np.float32) / 255.0
    img = img.reshape((1, *img.shape))
    m = get_glaucoma_model()
    class2label = {0: 'Glaucoma Negative', 1: 'Glaucoma Positive'}
    raw_preds = m.predict(img)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred = class2label[pred_idx]
    confidence = round(float(raw_preds[pred_idx]) * 100, 1)
    return pred, confidence

def predict_malaria(img):
    img = np.asarray(img, dtype=np.float32)
    img = img.reshape((1, *img.shape))
    m = get_malaria_model()
    class2label = {0: 'Parasitic', 1: 'Unaffected'}
    raw_preds = m.predict(img)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred = class2label[pred_idx]
    confidence = round(float(raw_preds[pred_idx]) * 100, 1)
    return pred, confidence 


_symptom_engine = None

CLINICAL_ANCHORS = {
    'COVID-19': {
        'primary': ['loss_of_smell', 'loss_of_taste', 'cough', 'high_fever', 'breathlessness', 'dry_hacking_cough'],
        'secondary': ['fatigue', 'throat_irritation', 'muscle_pain', 'headache']
    },
    'Influenza': {
        'primary': ['high_fever', 'chills', 'muscle_pain', 'headache', 'sweating', 'severe_exhaustion'],
        'secondary': ['fatigue', 'cough', 'runny_nose', 'malaise']
    },
    'Common Cold': {
        'primary': ['continuous_sneezing', 'runny_nose', 'congestion', 'mild_fever'],
        'secondary': ['throat_irritation', 'cough', 'chills']
    },
    'Allergic Rhinitis': {
        'primary': ['continuous_sneezing', 'runny_nose', 'eye_itching', 'watering_from_eyes'],
        'secondary': ['congestion', 'throat_irritation', 'sinus_pressure', 'post_nasal_drip']
    },
    'Allergy': {
        'primary': ['continuous_sneezing', 'shivering', 'chills', 'watering_from_eyes'],
        'secondary': ['itching', 'skin_rash']
    },
    'Malaria': {
        'primary': ['chills', 'high_fever', 'sweating', 'vomiting', 'headache'],
        'secondary': ['nausea', 'muscle_pain', 'diarrhoea']
    },
    'Dengue': {
        'primary': ['high_fever', 'pain_behind_the_eyes', 'joint_pain', 'back_pain', 'skin_rash'],
        'secondary': ['chills', 'vomiting', 'loss_of_appetite', 'purple_spots_on_skin']
    },
    'Typhoid': {
        'primary': ['high_fever', 'abdominal_pain', 'constipation', 'headache', 'toxic_look_(typhos)'],
        'secondary': ['chills', 'vomiting', 'fatigue', 'dry_coated_tongue']
    },
    'Tuberculosis': {
        'primary': ['cough', 'blood_in_sputum', 'weight_loss', 'night_sweats', 'high_fever'],
        'secondary': ['fatigue', 'chills', 'loss_of_appetite', 'phlegm']
    },
    'Chicken pox': {
        'primary': ['itching', 'skin_rash', 'fatigue', 'lethargy', 'high_fever', 'red_spots_over_body'],
        'secondary': ['headache', 'loss_of_appetite', 'mild_fever']
    },
    'Strep Throat': {
        'primary': ['throat_irritation', 'painful_swallowing', 'patches_in_throat', 'swelled_lymph_nodes'],
        'secondary': ['high_fever', 'headache']
    },
    'Pneumonia': {
        'primary': ['high_fever', 'chills', 'cough', 'breathlessness', 'chest_pain', 'rusty_sputum'],
        'secondary': ['fast_heart_rate', 'fatigue', 'phlegm']
    },
    'Acute Bronchitis': {
        'primary': ['cough', 'phlegm', 'chest_pain', 'wheezing', 'mild_fever'],
        'secondary': ['fatigue', 'throat_irritation']
    },
    'Bronchial Asthma': {
        'primary': ['breathlessness', 'cough', 'wheezing', 'chest_tightness'],
        'secondary': ['chest_pain', 'fatigue']
    },
    'Sinusitis': {
        'primary': ['sinus_pressure', 'headache', 'congestion', 'facial_pain', 'post_nasal_drip'],
        'secondary': ['runny_nose', 'throat_irritation']
    },
    'GERD': {
        'primary': ['acidity', 'ulcers_on_tongue', 'stomach_pain', 'chest_pain', 'heartburn'],
        'secondary': ['vomiting', 'cough']
    },
    'Peptic ulcer diseae': {
        'primary': ['vomiting', 'loss_of_appetite', 'abdominal_pain', 'passage_of_gases', 'indigestion'],
        'secondary': ['stomach_pain', 'nausea']
    },
    'Gastritis': {
        'primary': ['acidity', 'stomach_pain', 'indigestion', 'nausea', 'bloating'],
        'secondary': ['loss_of_appetite', 'vomiting']
    },
    'Food Poisoning': {
        'primary': ['vomiting', 'diarrhoea', 'stomach_pain', 'cramps'],
        'secondary': ['nausea', 'dehydration']
    },
    'Gastroenteritis': {
        'primary': ['vomiting', 'sunken_eyes', 'dehydration', 'diarrhoea'],
        'secondary': ['stomach_pain', 'nausea']
    },
    'Appendicitis': {
        'primary': ['sharp_abdominal_pain', 'belly_pain', 'nausea', 'vomiting', 'right_lower_quadrant_pain'],
        'secondary': ['loss_of_appetite', 'constipation']
    },
    'Kidney Stones': {
        'primary': ['back_pain', 'sharp_abdominal_pain', 'burning_micturition', 'blood_in_urine', 'flank_pain'],
        'secondary': ['spotting_urination', 'nausea']
    },
    'Urinary tract infection': {
        'primary': ['burning_micturition', 'bladder_discomfort', 'foul_smell_of_urine', 'continuous_feel_of_urine'],
        'secondary': ['skin_rash']
    },
    'Diabetes': {
        'primary': ['polyuria', 'increased_appetite', 'excessive_hunger', 'irregular_sugar_level', 'weight_loss', 'excessive_thirst'],
        'secondary': ['fatigue', 'lethargy']
    },
    'Heart attack': {
        'primary': ['chest_pain', 'breathlessness', 'sweating', 'vomiting', 'substernal_chest_pain'],
        'secondary': ['palpitations', 'fast_heart_rate']
    },
    'Hypertension': {
        'primary': ['headache', 'chest_pain', 'dizziness', 'loss_of_balance', 'lack_of_concentration'],
        'secondary': ['palpitations']
    },
    'Panic Disorder': {
        'primary': ['palpitations', 'fast_heart_rate', 'chest_pain', 'breathlessness', 'anxiety', 'dizziness'],
        'secondary': ['sweating', 'shivering', 'tremors']
    },
    'Iron Deficiency Anemia': {
        'primary': ['fatigue', 'lethargy', 'dizziness', 'pale_skin', 'cold_hands_and_feets'],
        'secondary': ['breathlessness', 'brittle_nails']
    },
    'Osteoarthristis': {
        'primary': ['joint_pain', 'knee_pain', 'hip_joint_pain', 'swelling_joints', 'painful_walking'],
        'secondary': ['neck_pain']
    },
    'Arthritis': {
        'primary': ['joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness'],
        'secondary': ['painful_walking']
    },
    'Gout': {
        'primary': ['joint_pain', 'swelling_joints', 'joint_swelling', 'knee_pain', 'big_toe_joint_pain'],
        'secondary': ['movement_stiffness', 'painful_walking']
    },
    'Cervical spondylosis': {
        'primary': ['back_pain', 'weakness_in_limbs', 'neck_pain', 'dizziness', 'loss_of_balance'],
        'secondary': ['movement_stiffness']
    },
    'Jaundice': {
        'primary': ['yellowish_skin', 'dark_urine', 'yellowing_of_eyes', 'loss_of_appetite', 'itching', 'vomiting'],
        'secondary': ['fatigue', 'weight_loss', 'abdominal_pain', 'high_fever']
    },
    'Chronic cholestasis': {
        'primary': ['itching', 'vomiting', 'yellowish_skin', 'nausea', 'loss_of_appetite'],
        'secondary': ['abdominal_pain', 'yellowing_of_eyes']
    },
    'Alcoholic hepatitis': {
        'primary': ['vomiting', 'yellowish_skin', 'abdominal_pain', 'swelling_of_stomach', 'distention_of_abdomen'],
        'secondary': ['fluid_overload']
    },
    'Hepatitis A': {
        'primary': ['joint_pain', 'vomiting', 'yellowish_skin', 'dark_urine', 'loss_of_appetite', 'diarrhoea', 'mild_fever'],
        'secondary': ['muscle_pain', 'nausea', 'yellowing_of_eyes']
    },
    'Hepatitis B': {
        'primary': ['itching', 'fatigue', 'lethargy', 'yellowish_skin', 'dark_urine', 'loss_of_appetite'],
        'secondary': ['yellowing_of_eyes']
    },
    'Hepatitis C': {
        'primary': ['fatigue', 'yellowish_skin', 'nausea', 'loss_of_appetite', 'yellowing_of_eyes'],
        'secondary': ['dark_urine']
    },
    'Hepatitis D': {
        'primary': ['joint_pain', 'vomiting', 'fatigue', 'yellowish_skin', 'dark_urine'],
        'secondary': ['loss_of_appetite', 'yellowing_of_eyes']
    },
    'Hepatitis E': {
        'primary': ['joint_pain', 'vomiting', 'fatigue', 'high_fever', 'yellowish_skin', 'dark_urine'],
        'secondary': ['nausea', 'loss_of_appetite']
    },
    'Hypothyroidism': {
        'primary': ['fatigue', 'weight_gain', 'cold_hands_and_feets', 'mood_swings', 'lethargy', 'puffy_face_and_eyes', 'enlarged_thyroid'],
        'secondary': ['dizziness', 'brittle_nails']
    },
    'Hyperthyroidism': {
        'primary': ['fatigue', 'mood_swings', 'weight_loss', 'restlessness', 'sweating', 'diarrhoea', 'fast_heart_rate', 'excessive_hunger'],
        'secondary': ['muscle_weakness']
    },
    'Hypoglycemia': {
        'primary': ['vomiting', 'fatigue', 'anxiety', 'sweating', 'headache', 'nausea', 'blurred_and_distorted_vision', 'excessive_hunger', 'slurred_speech', 'palpitations'],
        'secondary': ['dizziness']
    },
    'Varicose veins': {
        'primary': ['cramps', 'bruising', 'swollen_legs', 'swollen_blood_vessels', 'prominent_veins_on_calf'],
        'secondary': ['fatigue']
    },
    'Eczema': {
        'primary': ['itching', 'skin_rash', 'skin_peeling', 'blister', 'dry_cracked_scaly_skin'],
        'secondary': ['dischromic_patches']
    },
    'Psoriasis': {
        'primary': ['skin_rash', 'joint_pain', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails'],
        'secondary': ['itching']
    },
    'Impetigo': {
        'primary': ['skin_rash', 'high_fever', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'],
        'secondary': ['itching']
    },
    'Fungal infection': {
        'primary': ['itching', 'skin_rash', 'nodal_skin_eruptions', 'dischromic_patches'],
        'secondary': ['skin_peeling']
    },
    'Acne': {
        'primary': ['skin_rash', 'pus_filled_pimples', 'blackheads', 'scurring'],
        'secondary': ['itching']
    },
    'Drug Reaction': {
        'primary': ['itching', 'skin_rash', 'stomach_pain', 'burning_micturition', 'spotting_urination'],
        'secondary': ['skin_peeling']
    },
    'Migraine': {
        'primary': ['headache', 'throbbing_headache', 'sensitivity_to_light', 'sensitivity_to_sound', 'visual_disturbances', 'stiff_neck', 'irritability'],
        'secondary': ['nausea', 'vomiting', 'blurred_and_distorted_vision']
    },
    '(vertigo) Paroymsal  Positional Vertigo': {
        'primary': ['vomiting', 'headache', 'nausea', 'spinning_movements', 'loss_of_balance', 'unsteadiness'],
        'secondary': ['dizziness']
    },
    'Paralysis (brain hemorrhage)': {
        'primary': ['vomiting', 'headache', 'weakness_of_one_body_side', 'altered_sensorium'],
        'secondary': ['loss_of_balance']
    },
    'Conjunctivitis': {
        'primary': ['redness_of_eyes', 'watering_from_eyes', 'eye_itching', 'burning_eyes'],
        'secondary': ['blurred_and_distorted_vision']
    },
    'AIDS': {
        'primary': ['muscle_wasting', 'patches_in_throat', 'high_fever', 'extra_marital_contacts'],
        'secondary': ['fatigue']
    },
    'Dimorphic hemmorhoids(piles)': {
        'primary': ['constipation', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus'],
        'secondary': ['passage_of_gases']
    },
    'Irritable Bowel Syndrome': {
        'primary': ['abdominal_pain', 'stomach_pain', 'passage_of_gases', 'bloating', 'cramps'],
        'secondary': ['diarrhoea', 'constipation']
    }
}

def get_symptom_engine():
    global _symptom_engine
    if _symptom_engine is None:
        training_df = pd.read_csv('models/training.csv')
        training_df['prognosis'] = training_df['prognosis'].str.strip()
        symptom_cols = [c.strip() for c in training_df.columns[:-1]]
        training_df.columns = symptom_cols + ['prognosis']

        X = training_df[symptom_cols]
        y = training_df['prognosis']
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        rf_clf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y_encoded)
        nb_clf = MultinomialNB().fit(X, y_encoded)

        symptoms_dict = {col: i for i, col in enumerate(symptom_cols)}
        symptoms_norm_dict = {col.lower().replace(" ", "").replace("_", "").replace("-", ""): col for col in symptom_cols}

        # Build automated profiles from training.csv means + merge anchors
        disease_profiles = {}
        for disease in y.unique():
            subset = training_df[training_df['prognosis'] == disease][symptom_cols]
            freq = subset.mean()
            high_freq = list(freq[freq >= 0.50].index)
            med_freq = list(freq[(freq >= 0.15) & (freq < 0.50)].index)
            disease_profiles[disease] = {
                'primary': high_freq,
                'secondary': med_freq
            }

        for k, v in CLINICAL_ANCHORS.items():
            matching_k = None
            for d in disease_profiles:
                if d.lower() == k.lower() or d.lower().replace(' ', '') == k.lower().replace(' ', ''):
                    matching_k = d
                    break
            if matching_k:
                prim_clean = [s.strip().lower().replace(' ', '_') for s in v.get('primary', [])]
                sec_clean = [s.strip().lower().replace(' ', '_') for s in v.get('secondary', [])]
                disease_profiles[matching_k]['primary'] = list(set(disease_profiles[matching_k]['primary'] + prim_clean))
                disease_profiles[matching_k]['secondary'] = list(set(disease_profiles[matching_k]['secondary'] + sec_clean))
            else:
                disease_profiles[k] = {
                    'primary': [s.strip().lower().replace(' ', '_') for s in v.get('primary', [])],
                    'secondary': [s.strip().lower().replace(' ', '_') for s in v.get('secondary', [])]
                }

        description_dict = {}
        with open('models/symptom_description.csv', 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    k = row[0].strip()
                    description_dict[k] = row[1].strip()
                    description_dict[k.lower()] = row[1].strip()

        severity_dict = {}
        with open('models/symptom_severity.csv', 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[1].strip().isdigit():
                    k = row[0].strip()
                    severity_dict[k] = int(row[1].strip())
                    severity_dict[k.replace('_', ' ')] = int(row[1].strip())
                    severity_dict[k.replace(' ', '_')] = int(row[1].strip())

        precautions_dict = {}
        with open('models/symptom_precaution.csv', 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                if len(row) >= 5:
                    k = row[0].strip()
                    prec = [row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip()]
                    precautions_dict[k] = prec
                    precautions_dict[k.lower()] = prec

        _symptom_engine = {
            'rf_clf': rf_clf,
            'nb_clf': nb_clf,
            'le': le,
            'cols': symptom_cols,
            'symptoms_dict': symptoms_dict,
            'symptoms_norm_dict': symptoms_norm_dict,
            'disease_profiles': disease_profiles,
            'description_dict': description_dict,
            'severity_dict': severity_dict,
            'precautions_dict': precautions_dict,
        }
    return _symptom_engine

_symptom_aliases = {
    # Fever & Systemic
    'fever': 'high_fever',
    'feverish': 'high_fever',
    'high fever': 'high_fever',
    'high_fever': 'high_fever',
    'mild fever': 'mild_fever',
    'mild_fever': 'mild_fever',
    'temperature': 'high_fever',
    'pyrexia': 'high_fever',
    'chills': 'chills',
    'shivering': 'shivering',
    'feeling cold': 'chills',
    'sweating': 'sweating',
    'sweats': 'sweating',
    'night sweats': 'night_sweats',
    'night_sweats': 'night_sweats',
    'fatigue': 'fatigue',
    'tired': 'fatigue',
    'tiredness': 'fatigue',
    'exhaustion': 'fatigue',
    'exhausted': 'fatigue',
    'lethargy': 'lethargy',
    'malaise': 'malaise',
    'weakness': 'weakness_in_limbs',
    'weakness in limbs': 'weakness_in_limbs',
    'weakness_in_limbs': 'weakness_in_limbs',
    'muscle weakness': 'muscle_weakness',
    'muscle_weakness': 'muscle_weakness',
    'pale skin': 'pale_skin',
    'pale_skin': 'pale_skin',
    'paleness': 'pale_skin',
    'pallor': 'pale_skin',

    # Respiratory & ENT
    'cold': 'continuous_sneezing',
    'common cold': 'continuous_sneezing',
    'sneezing': 'continuous_sneezing',
    'sneeze': 'continuous_sneezing',
    'sneezes': 'continuous_sneezing',
    'continuous sneezing': 'continuous_sneezing',
    'continuous_sneezing': 'continuous_sneezing',
    'runny nose': 'runny_nose',
    'runny_nose': 'runny_nose',
    'running nose': 'runny_nose',
    'stuffy nose': 'congestion',
    'blocked nose': 'congestion',
    'congestion': 'congestion',
    'nasal congestion': 'congestion',
    'post nasal drip': 'post_nasal_drip',
    'post_nasal_drip': 'post_nasal_drip',
    'sinus pressure': 'sinus_pressure',
    'sinus_pressure': 'sinus_pressure',
    'sinus pain': 'sinus_pressure',
    'facial pain': 'facial_pain',
    'facial_pain': 'facial_pain',
    'cough': 'cough',
    'coughing': 'cough',
    'coughs': 'cough',
    'dry cough': 'cough',
    'wet cough': 'cough',
    'phlegm': 'phlegm',
    'sputum': 'phlegm',
    'mucus': 'phlegm',
    'blood in sputum': 'blood_in_sputum',
    'blood_in_sputum': 'blood_in_sputum',
    'breathlessness': 'breathlessness',
    'shortness of breath': 'breathlessness',
    'difficulty breathing': 'breathlessness',
    'breathless': 'breathlessness',
    'wheezing': 'wheezing',
    'wheeze': 'wheezing',
    'sore throat': 'throat_irritation',
    'throat pain': 'throat_irritation',
    'throat irritation': 'throat_irritation',
    'throat_irritation': 'throat_irritation',
    'patches in throat': 'patches_in_throat',
    'patches_in_throat': 'patches_in_throat',
    'painful swallowing': 'painful_swallowing',
    'painful_swallowing': 'painful_swallowing',
    'difficulty swallowing': 'painful_swallowing',
    'dysphagia': 'painful_swallowing',
    'loss of smell': 'loss_of_smell',
    'loss_of_smell': 'loss_of_smell',
    'lost sense of smell': 'loss_of_smell',
    'lost my sense of smell': 'loss_of_smell',
    'lost smell': 'loss_of_smell',
    'lost my smell': 'loss_of_smell',
    'cannot smell': 'loss_of_smell',
    'cant smell': 'loss_of_smell',
    'no smell': 'loss_of_smell',
    'anosmia': 'loss_of_smell',
    'loss of taste': 'loss_of_taste',
    'loss_of_taste': 'loss_of_taste',
    'lost sense of taste': 'loss_of_taste',
    'lost my sense of taste': 'loss_of_taste',
    'lost taste': 'loss_of_taste',
    'lost my taste': 'loss_of_taste',
    'cannot taste': 'loss_of_taste',
    'cant taste': 'loss_of_taste',
    'no taste': 'loss_of_taste',
    'ageusia': 'loss_of_taste',
    'swelled lymph nodes': 'swelled_lymph_nodes',
    'swelled_lymph_nodes': 'swelled_lymph_nodes',
    'swollen lymph nodes': 'swelled_lymph_nodes',
    'swollen glands': 'swelled_lymph_nodes',

    # Head, Eyes & Neuro
    'headache': 'headache',
    'head ache': 'headache',
    'headaches': 'headache',
    'throbbing headache': 'headache',
    'throbbing_headache': 'headache',
    'throbbing temple headache': 'headache',
    'sensitivity to light': 'visual_disturbances',
    'sensitivity_to_light': 'visual_disturbances',
    'photophobia': 'visual_disturbances',
    'sensitivity to sound': 'irritability',
    'sensitivity_to_sound': 'irritability',
    'phonophobia': 'irritability',
    'migraine': 'headache',
    'dizziness': 'dizziness',
    'dizzy': 'dizziness',
    'lightheaded': 'dizziness',
    'vertigo': 'dizziness',
    'spinning movements': 'spinning_movements',
    'spinning_movements': 'spinning_movements',
    'loss of balance': 'loss_of_balance',
    'loss_of_balance': 'loss_of_balance',
    'unsteadiness': 'unsteadiness',
    'confusion': 'confusion',
    'disorientation': 'confusion',
    'disoriented': 'confusion',
    'tremors': 'tremors',
    'tremor': 'tremors',
    'shaking hands': 'tremors',
    'trembling': 'tremors',
    'tingling sensation': 'tingling_sensation',
    'tingling_sensation': 'tingling_sensation',
    'numbness': 'tingling_sensation',
    'redness of eyes': 'redness_of_eyes',
    'redness_of_eyes': 'redness_of_eyes',
    'red eyes': 'redness_of_eyes',
    'watering from eyes': 'watering_from_eyes',
    'watering_from_eyes': 'watering_from_eyes',
    'watery eyes': 'watering_from_eyes',
    'eye itching': 'eye_itching',
    'eye_itching': 'eye_itching',
    'itchy eyes': 'eye_itching',
    'burning eyes': 'burning_eyes',
    'burning_eyes': 'burning_eyes',
    'pain behind the eyes': 'pain_behind_the_eyes',
    'pain_behind_the_eyes': 'pain_behind_the_eyes',
    'blurred and distorted vision': 'blurred_and_distorted_vision',
    'blurred_and_distorted_vision': 'blurred_and_distorted_vision',
    'yellowing of eyes': 'yellowing_of_eyes',
    'yellowing_of_eyes': 'yellowing_of_eyes',
    'yellow eyes': 'yellowing_of_eyes',

    # Gastrointestinal & Abdomen
    'stomach pain': 'stomach_pain',
    'stomach_pain': 'stomach_pain',
    'stomach ache': 'stomach_pain',
    'tummy ache': 'stomach_pain',
    'abdominal pain': 'abdominal_pain',
    'abdominal_pain': 'abdominal_pain',
    'sharp abdominal pain': 'sharp_abdominal_pain',
    'sharp_abdominal_pain': 'sharp_abdominal_pain',
    'flank pain': 'sharp_abdominal_pain',
    'belly pain': 'belly_pain',
    'belly_pain': 'belly_pain',
    'bloating': 'bloating',
    'passage of gases': 'passage_of_gases',
    'passage_of_gases': 'passage_of_gases',
    'gas': 'passage_of_gases',
    'acidity': 'acidity',
    'heartburn': 'acidity',
    'acid reflux': 'acidity',
    'indigestion': 'indigestion',
    'nausea': 'nausea',
    'nauseous': 'nausea',
    'vomiting': 'vomiting',
    'vomit': 'vomiting',
    'throwing up': 'vomiting',
    'diarrhea': 'diarrhoea',
    'diarrhoea': 'diarrhoea',
    'loose motion': 'diarrhoea',
    'loose motions': 'diarrhoea',
    'constipation': 'constipation',
    'cramps': 'cramps',
    'stomach cramps': 'cramps',
    'abdominal cramps': 'cramps',
    'loss of appetite': 'loss_of_appetite',
    'loss_of_appetite': 'loss_of_appetite',
    'ulcers on tongue': 'ulcers_on_tongue',
    'ulcers_on_tongue': 'ulcers_on_tongue',
    'yellowish skin': 'yellowish_skin',
    'yellowish_skin': 'yellowish_skin',
    'jaundice': 'yellowish_skin',
    'dark urine': 'dark_urine',
    'dark_urine': 'dark_urine',
    'yellow urine': 'yellow_urine',
    'yellow_urine': 'yellow_urine',
    'bloody stool': 'bloody_stool',
    'bloody_stool': 'bloody_stool',

    # Urinary & Renal
    'burning micturition': 'burning_micturition',
    'burning_micturition': 'burning_micturition',
    'painful urination': 'burning_micturition',
    'burning urination': 'burning_micturition',
    'blood in urine': 'blood_in_urine',
    'blood_in_urine': 'blood_in_urine',
    'hematuria': 'blood_in_urine',
    'spotting urination': 'spotting_urination',
    'spotting_urination': 'spotting_urination',
    'bladder discomfort': 'bladder_discomfort',
    'bladder_discomfort': 'bladder_discomfort',
    'foul smell of urine': 'foul_smell_of_urine',
    'foul_smell_of_urine': 'foul_smell_of_urine',
    'continuous feel of urine': 'continuous_feel_of_urine',
    'continuous_feel_of_urine': 'continuous_feel_of_urine',
    'frequent urination': 'polyuria',
    'polyuria': 'polyuria',

    # Cardiovascular & Thoracic
    'chest pain': 'chest_pain',
    'chest_pain': 'chest_pain',
    'chest tightness': 'chest_pain',
    'palpitations': 'palpitations',
    'fast heart rate': 'fast_heart_rate',
    'fast_heart_rate': 'fast_heart_rate',
    'racing heart': 'fast_heart_rate',

    # Musculoskeletal & Joints
    'body pain': 'muscle_pain',
    'body ache': 'muscle_pain',
    'muscle pain': 'muscle_pain',
    'muscle_pain': 'muscle_pain',
    'muscle ache': 'muscle_pain',
    'joint pain': 'joint_pain',
    'joint_pain': 'joint_pain',
    'joint ache': 'joint_pain',
    'joints pain': 'joint_pain',
    'joint swelling': 'joint_swelling',
    'joint_swelling': 'joint_swelling',
    'swelling joints': 'swelling_joints',
    'swelling_joints': 'swelling_joints',
    'swollen joints': 'swelling_joints',
    'knee pain': 'knee_pain',
    'knee_pain': 'knee_pain',
    'hip joint pain': 'hip_joint_pain',
    'hip_joint_pain': 'hip_joint_pain',
    'back pain': 'back_pain',
    'back_pain': 'back_pain',
    'backache': 'back_pain',
    'neck pain': 'neck_pain',
    'neck_pain': 'neck_pain',
    'stiff neck': 'stiff_neck',
    'stiff_neck': 'stiff_neck',
    'movement stiffness': 'movement_stiffness',
    'movement_stiffness': 'movement_stiffness',
    'painful walking': 'painful_walking',
    'painful_walking': 'painful_walking',
    'swollen legs': 'swollen_legs',
    'swollen_legs': 'swollen_legs',
    'cold hands and feets': 'cold_hands_and_feets',
    'cold_hands_and_feets': 'cold_hands_and_feets',

    # Skin & Allergies
    'itching': 'itching',
    'itchy': 'itching',
    'skin rash': 'skin_rash',
    'skin_rash': 'skin_rash',
    'rash': 'skin_rash',
    'rashes': 'skin_rash',
    'nodal skin eruptions': 'nodal_skin_eruptions',
    'nodal_skin_eruptions': 'nodal_skin_eruptions',
    'skin peeling': 'skin_peeling',
    'skin_peeling': 'skin_peeling',
    'blister': 'blister',
    'blisters': 'blister',
    'dischromic patches': 'dischromic_patches',
    'dischromic_patches': 'dischromic_patches',
    'red spots over body': 'red_spots_over_body',
    'red_spots_over_body': 'red_spots_over_body',
    'brittle nails': 'brittle_nails',
    'brittle_nails': 'brittle_nails',
    'pus filled pimples': 'pus_filled_pimples',
    'pus_filled_pimples': 'pus_filled_pimples',
    'blackheads': 'blackheads',

    # Metabolic & Psychological
    'anxiety': 'anxiety',
    'depression': 'depression',
    'restlessness': 'restlessness',
    'weight loss': 'weight_loss',
    'weight_loss': 'weight_loss',
    'weight gain': 'weight_gain',
    'weight_gain': 'weight_gain',
    'increased appetite': 'increased_appetite',
    'increased_appetite': 'increased_appetite',
    'excessive hunger': 'excessive_hunger',
    'excessive_hunger': 'excessive_hunger',
    'irregular sugar level': 'irregular_sugar_level',
    'irregular_sugar_level': 'irregular_sugar_level',
    'dehydration': 'dehydration',
}

def resolve_symptom_name(user_sym, engine=None):
    if engine is None:
        engine = get_symptom_engine()
    raw = str(user_sym).lower().strip().replace("-", " ")
    if not raw:
        return None

    # 1. Check exact match
    if raw in engine['symptoms_dict']:
        return raw

    # 2. Check underscore normalized
    with_underscore = raw.replace(" ", "_")
    if with_underscore in engine['symptoms_dict']:
        return with_underscore

    # 3. Check space normalized
    with_space = raw.replace("_", " ")
    if with_space in engine['symptoms_dict']:
        return with_space

    # 4. Check aliases
    if raw in _symptom_aliases:
        alias_target = _symptom_aliases[raw]
        if alias_target in engine['symptoms_dict']:
            return alias_target
    if with_underscore in _symptom_aliases:
        alias_target = _symptom_aliases[with_underscore]
        if alias_target in engine['symptoms_dict']:
            return alias_target
    if with_space in _symptom_aliases:
        alias_target = _symptom_aliases[with_space]
        if alias_target in engine['symptoms_dict']:
            return alias_target

    # 5. Normalized alphanumeric match
    norm = raw.replace(" ", "").replace("_", "")
    if norm in engine['symptoms_norm_dict']:
        return engine['symptoms_norm_dict'][norm]

    # 6. Substring match against columns
    for col in engine['cols']:
        col_clean = col.lower().replace("_", " ")
        if raw == col_clean or raw in col_clean or col_clean in raw:
            return col
        col_under = col.lower()
        if with_underscore == col_under or with_underscore in col_under or col_under in with_underscore:
            return col

    return None

def extract_symptoms_and_days_from_text(text, engine=None):
    if engine is None:
        engine = get_symptom_engine()
    if not text:
        return [], 5

    raw_text = str(text).lower()
    extracted_symptoms = []

    # 1. Extract days duration if mentioned
    days = 5
    num_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'fourteen': 14, 'a week': 7, 'one week': 7, 'two weeks': 14
    }
    match_days = re.search(r'(?:for|since|past|over|around)?\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|fourteen)\s*days?', raw_text)
    if match_days:
        val = match_days.group(1)
        days = num_words.get(val, int(val) if val.isdigit() else 5)
    elif 'week' in raw_text:
        if 'two weeks' in raw_text or '2 weeks' in raw_text:
            days = 14
        else:
            days = 7
    elif 'yesterday' in raw_text or 'today' in raw_text:
        days = 1

    # 2. Check alias phrases first
    sorted_aliases = sorted(_symptom_aliases.keys(), key=lambda x: len(x), reverse=True)
    matched_canonical = set()

    for alias in sorted_aliases:
        pattern = r'\b' + re.escape(alias.replace('_', ' ')) + r'\b'
        if re.search(pattern, raw_text, re.IGNORECASE):
            canonical = _symptom_aliases[alias]
            if canonical in engine['symptoms_dict'] and canonical not in matched_canonical:
                matched_canonical.add(canonical)
                extracted_symptoms.append(canonical)

    # 3. Check direct columns
    for col in engine['cols']:
        if col not in matched_canonical:
            pattern = r'\b' + re.escape(col.lower().replace('_', ' ')) + r'\b'
            if re.search(pattern, raw_text, re.IGNORECASE):
                matched_canonical.add(col)
                extracted_symptoms.append(col)

    return extracted_symptoms, days

def predict_disease(user_symptoms, days=5):
    engine = get_symptom_engine()
    input_vector = np.zeros(len(engine['symptoms_dict']))
    matched_symptoms = []
    total_severity = 0
    red_flag_detected = False

    red_flags = {
        'chest_pain', 'substernal_chest_pain', 'breathlessness', 'blood_in_sputum',
        'blood_in_urine', 'bloody_stool', 'sharp_abdominal_pain', 'altered_sensorium',
        'coma', 'loss_of_smell', 'fast_heart_rate', 'yellowish_skin', 'yellowing_of_eyes',
        'seizures', 'slurred_speech', 'cyanosis'
    }

    for item in user_symptoms:
        resolved = resolve_symptom_name(item, engine)
        if resolved and resolved not in matched_symptoms:
            matched_symptoms.append(resolved)
            input_vector[engine['symptoms_dict'][resolved]] = 1
            sev = engine['severity_dict'].get(resolved, 3)
            total_severity += sev
            if resolved in red_flags or resolved.replace('_', ' ') in red_flags:
                red_flag_detected = True

    if not matched_symptoms:
        return "No specific recognized clinical symptoms matched. Please specify common symptoms such as fever, cough, fatigue, headache, chills, or joint pain.", {}

    # 1. Random Forest Probabilities
    rf_probs = engine['rf_clf'].predict_proba([input_vector])[0]

    # 2. Multinomial Naive Bayes Probabilities
    nb_probs = engine['nb_clf'].predict_proba([input_vector])[0]

    # 3. Clinical Pathognomonic Anchor Score
    clinical_scores = np.zeros(len(engine['le'].classes_))
    matched_set = {s.strip().lower().replace(' ', '_') for s in matched_symptoms}
    matched_set_all = matched_set | {s.replace('_', ' ') for s in matched_set}

    for i, disease in enumerate(engine['le'].classes_):
        prof = engine['disease_profiles'].get(disease, {'primary': [], 'secondary': []})
        prim = {s.strip().lower().replace(' ', '_') for s in prof.get('primary', [])} | {s.strip().lower().replace('_', ' ') for s in prof.get('primary', [])}
        sec = {s.strip().lower().replace(' ', '_') for s in prof.get('secondary', [])} | {s.strip().lower().replace('_', ' ') for s in prof.get('secondary', [])}

        prim_matches = len(matched_set_all & prim)
        sec_matches = len(matched_set_all & sec)
        total_matches = prim_matches + sec_matches

        if total_matches > 0:
            user_precision = total_matches / max(len(matched_set), 1)
            core_recall = prim_matches / max(len(prim), 1)
            score = (prim_matches * 5.5 + sec_matches * 1.5) * (user_precision ** 0.8) * (1.0 + 0.6 * core_recall)
            clinical_scores[i] = score

    if clinical_scores.sum() > 0:
        clinical_probs = clinical_scores / clinical_scores.sum()
    else:
        clinical_probs = np.ones(len(engine['le'].classes_)) / len(engine['le'].classes_)

    # Hybrid Ensemble Scoring
    if len(matched_symptoms) <= 2:
        final_probs = 0.68 * clinical_probs + 0.18 * nb_probs + 0.14 * rf_probs
    else:
        final_probs = 0.48 * clinical_probs + 0.28 * rf_probs + 0.24 * nb_probs

    top_indices = np.argsort(final_probs)[::-1][:3]
    top_probs = final_probs[top_indices]

    if top_probs.sum() > 0:
        top_probs_norm = (top_probs / top_probs.sum()) * 100
    else:
        top_probs_norm = np.array([55.0, 30.0, 15.0])

    top_diseases = engine['le'].inverse_transform(top_indices)

    # Clinical Triage Advice Logic
    triage_score = ((total_severity * max(days, 1)) / (len(matched_symptoms) + 1))
    if red_flag_detected or triage_score > 12 or days >= 7:
        advice = "Elevated clinical risk detected. You should consult a physician or medical professional promptly for comprehensive examination."
    elif triage_score > 7 or days >= 4:
        advice = "Moderate clinical concern. The condition is currently manageable, but if symptoms persist or worsen, please seek medical evaluation."
    else:
        advice = "The situation is manageable at present with rest and symptomatic precautions. If symptoms persist beyond a few days, please consult a healthcare provider."

    output = {}
    for idx, dis, prob in zip(top_indices, top_diseases, top_probs_norm):
        prob_percent = round(float(prob), 1)
        desc = engine['description_dict'].get(dis) or engine['description_dict'].get(dis.lower()) or "Clinical description currently being updated."
        prec = engine['precautions_dict'].get(dis) or engine['precautions_dict'].get(dis.lower()) or ["Rest adequately", "Stay hydrated", "Consult a physician if symptoms worsen", "Monitor vitals"]
        output[dis] = {
            'desc': desc,
            'prec': prec,
            'probability': prob_percent
        }

    return advice, output
