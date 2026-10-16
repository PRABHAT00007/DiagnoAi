import os
import json
import base64
import time
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from models.classifiers import (
    predict_heartD,
    predict_diabetes,
    predict_cancerB,
    predict_liverD,
    predict_alzheimer,
    predict_covid,
    predict_brain,
    predict_glaucoma,
    predict_malaria,
    localizeTumor,
    predict_disease
)
from main.views import save_and_validate_image

def _parse_payload(request):
    """Safely extracts dictionary from either JSON body or form POST."""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return None
    return request.POST.dict()

@require_http_methods(["GET"])
def api_health(request):
    """Health check endpoint for DiagnoAI API."""
    return JsonResponse({
        "status": "healthy",
        "service": "DiagnoAI Clinical Diagnostic API",
        "version": "1.0.0",
        "timestamp": int(time.time()),
        "modalities": [
            "cardiovascular", "diabetes", "breast_cancer", "liver_function",
            "alzheimer_mri", "covid_cxr", "brain_tumor_mri", "glaucoma_fundus",
            "malaria_smear", "symptom_analyzer"
        ]
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_heart(request):
    """REST API: Heart Disease Risk Assessment."""
    data = _parse_payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body provided."}, status=400)
    
    feature_vals = [v for k, v in data.items() if k not in ('csrfmiddlewaretoken',)]
    if len(feature_vals) < 11:
        return JsonResponse({
            "error": f"Expected at least 11 cardiac parameters, received {len(feature_vals)}.",
            "required_fields": ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope"]
        }, status=400)
    
    try:
        features = np.array([list(map(float, feature_vals[:13]))])
        pred, confidence = predict_heartD(features)
        return JsonResponse({
            "status": "success",
            "modality": "cardiovascular",
            "prediction": pred,
            "confidence": confidence,
            "risk_level": "Elevated" if pred == 1 else "Low",
            "diagnosis": "Elevated Cardiovascular Risk Detected" if pred == 1 else "Normal Cardiac Profile (Low Risk)",
            "recommendations": [
                "Schedule a 12-lead ECG and Echocardiogram with a Cardiologist." if pred == 1 else "Maintain routine annual cardiovascular checkups.",
                "Monitor daily resting blood pressure and adopt a low-sodium Mediterranean diet.",
                "Avoid unmonitored high-intensity cardiac strain if symptomatic." if pred == 1 else "Engage in 150 minutes of weekly aerobic exercise."
            ]
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid parameter data types: {str(e)}"}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_diabetes(request):
    """REST API: Diabetes Metabolic Risk Assessment."""
    data = _parse_payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body provided."}, status=400)
    
    feature_vals = [v for k, v in data.items() if k not in ('csrfmiddlewaretoken',)]
    if len(feature_vals) < 8:
        return JsonResponse({
            "error": f"Expected 8 metabolic parameters, received {len(feature_vals)}.",
            "required_fields": ["pregnancies", "glucose", "blood_pressure", "skin_thickness", "insulin", "bmi", "pedigree", "age"]
        }, status=400)
    
    try:
        features = np.array([list(map(float, feature_vals[:8]))])
        pred, confidence = predict_diabetes(features)
        return JsonResponse({
            "status": "success",
            "modality": "diabetes",
            "prediction": pred,
            "confidence": confidence,
            "risk_level": "Elevated" if pred == 1 else "Low",
            "diagnosis": "Elevated Diabetes Risk Detected" if pred == 1 else "Healthy Glycemic Profile (Low Risk)",
            "recommendations": [
                "Consult an Endocrinologist for an HbA1c glycated hemoglobin laboratory test." if pred == 1 else "Maintain healthy dietary habits with complex fibers.",
                "Adopt a low-glycemic nutrition plan, minimizing refined sugars and simple carbs.",
                "Incorporate 30 minutes of moderate daily exercise to enhance insulin sensitivity."
            ]
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid parameter data types: {str(e)}"}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_cancer(request):
    """REST API: Breast Cancer Biopsy Classification."""
    data = _parse_payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body provided."}, status=400)
    
    feature_vals = [v for k, v in data.items() if k not in ('csrfmiddlewaretoken',)]
    if len(feature_vals) < 30:
        return JsonResponse({
            "error": f"Expected 30 cell nucleus morphometric parameters, received {len(feature_vals)}."
        }, status=400)
    
    try:
        features = np.array([list(map(float, feature_vals[:30]))])
        pred, confidence = predict_cancerB(features)
        is_malignant = pred in ('M', 'm')
        return JsonResponse({
            "status": "success",
            "modality": "breast_cancer",
            "prediction": "Malignant" if is_malignant else "Benign",
            "confidence": confidence,
            "risk_level": "High" if is_malignant else "Low",
            "diagnosis": "Malignant Classification Detected" if is_malignant else "Benign Cellular Characteristics",
            "recommendations": [
                "Schedule an urgent consultation with an Oncologist for core-needle biopsy." if is_malignant else "Continue routine scheduled mammographic surveillance.",
                "Perform diagnostic contrast-enhanced breast MRI and 3D digital mammography." if is_malignant else "Perform monthly breast self-examinations."
            ]
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid parameter data types: {str(e)}"}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_liver(request):
    """REST API: Liver Function Assessment."""
    data = _parse_payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body provided."}, status=400)
    
    feature_vals = [v for k, v in data.items() if k not in ('csrfmiddlewaretoken',)]
    if len(feature_vals) < 10:
        return JsonResponse({
            "error": f"Expected 10 liver panel parameters, received {len(feature_vals)}.",
            "required_fields": ["age", "gender", "total_bilirubin", "direct_bilirubin", "alkaline_phosphatase", "alamine_aminotransferase", "aspartate_aminotransferase", "total_proteins", "albumin", "albumin_globulin_ratio"]
        }, status=400)
    
    try:
        features = np.array([list(map(float, feature_vals[:10]))])
        pred, confidence = predict_liverD(features)
        return JsonResponse({
            "status": "success",
            "modality": "liver_function",
            "prediction": pred,
            "confidence": confidence,
            "risk_level": "Elevated" if pred == 1 else "Low",
            "diagnosis": "Elevated Hepatic Risk Detected" if pred == 1 else "Healthy Liver Function (Normal Profile)",
            "recommendations": [
                "Schedule a comprehensive abdominal ultrasound and viral hepatitis panel." if pred == 1 else "Maintain adequate hydration and balanced nutrition.",
                "Refrain from all alcohol intake and consult a physician before consuming NSAIDs." if pred == 1 else "Continue routine annual metabolic health checkups."
            ]
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid parameter data types: {str(e)}"}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_alzheimer(request):
    """REST API: Alzheimer MRI Neuroimaging Analysis & Grad-CAM."""
    if not request.FILES.get('image'):
        return JsonResponse({'error': 'No image file uploaded.'}, status=400)
    try:
        img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(224, 224), mode="RGB")
        base_name, _ = os.path.splitext(file_path)
        cam_out_path = base_name + "_camViz.jpg"
        label, cam_path, confidence = predict_alzheimer(img, file_path, cam_out_path)

        with open(cam_path, "rb") as img2str:
            cam_base64 = base64.b64encode(img2str.read()).decode('utf-8')

        return JsonResponse({
            "status": "success",
            "modality": "alzheimer_mri",
            "label": label,
            "confidence": confidence,
            "visualization": cam_base64
        })
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Inference failure: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_covid(request):
    """REST API: Covid-19 & Pulmonary CXR Radiograph Screening."""
    if not request.FILES.get('image'):
        return JsonResponse({'error': 'No image file uploaded.'}, status=400)
    try:
        img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(299, 299), mode="L")
        base_name, _ = os.path.splitext(file_path)
        cam_out_path = base_name + "_camViz.jpg"
        label, cam_path, confidence = predict_covid(img, file_path, cam_out_path)

        with open(cam_path, "rb") as img2str:
            cam_base64 = base64.b64encode(img2str.read()).decode('utf-8')

        return JsonResponse({
            "status": "success",
            "modality": "covid_cxr",
            "label": label,
            "confidence": confidence,
            "visualization": cam_base64
        })
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Inference failure: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_brain(request):
    """REST API: Brain MRI Tumor Classification & UNet Localization."""
    if not request.FILES.get('image'):
        return JsonResponse({'error': 'No image file uploaded.'}, status=400)
    try:
        pil_img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=None, mode="RGB")
        resized_img = pil_img.resize((224, 224))
        label, confidence = predict_brain(resized_img)

        if label == "No Tumor":
            display_path = file_path
        else:
            base_name, _ = os.path.splitext(file_path)
            out_path = base_name + "_tumorLoc.jpg"
            try:
                display_path = localizeTumor(file_path, out_path)
            except Exception as loc_err:
                print(f"API Tumor localization warning: {loc_err}")
                display_path = file_path

        with open(display_path, "rb") as img2str:
            seg_base64 = base64.b64encode(img2str.read()).decode('utf-8')

        return JsonResponse({
            "status": "success",
            "modality": "brain_tumor_mri",
            "label": label,
            "confidence": confidence,
            "visualization": seg_base64
        })
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Inference failure: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_glaucoma(request):
    """REST API: Glaucoma Retinal Fundus Screening."""
    if not request.FILES.get('image'):
        return JsonResponse({'error': 'No image file uploaded.'}, status=400)
    try:
        img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(300, 300), mode="RGB")
        label, confidence = predict_glaucoma(img)
        return JsonResponse({
            "status": "success",
            "modality": "glaucoma_fundus",
            "label": label,
            "confidence": confidence
        })
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Inference failure: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_malaria(request):
    """REST API: Malaria Blood Smear Cell Screening."""
    if not request.FILES.get('image'):
        return JsonResponse({'error': 'No image file uploaded.'}, status=400)
    try:
        img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(100, 100), mode="RGB")
        label, confidence = predict_malaria(img)
        return JsonResponse({
            "status": "success",
            "modality": "malaria_smear",
            "label": label,
            "confidence": confidence
        })
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Inference failure: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_symptoms(request):
    """REST API: Multi-Symptom Disease Diagnosis & Probability Engine."""
    data = _parse_payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body provided."}, status=400)
    
    if isinstance(data.get('symptoms'), list):
        user_symptoms = [str(s).strip() for s in data['symptoms'] if str(s).strip()]
    else:
        user_symptoms = [v.strip() for k, v in data.items() if k.startswith('symptoms') and str(v).strip()]
        if not user_symptoms:
            user_symptoms = [v.strip() for k, v in data.items() if k not in ('csrfmiddlewaretoken', 'days') and str(v).strip()]
    
    try:
        days = int(data.get('days', 5))
    except (ValueError, TypeError):
        days = 5
    
    advice, output = predict_disease(user_symptoms, days)
    return JsonResponse({
        "status": "success",
        "modality": "symptom_analyzer",
        "advice": advice,
        "results": output
    })
