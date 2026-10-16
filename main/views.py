from django.shortcuts import render , redirect
from django.http import HttpResponse , HttpResponseRedirect , JsonResponse , FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from models.classifiers import (predict_malaria, predict_liverD, predict_heartD, predict_alzheimer, 
predict_diabetes, predict_cancerB, predict_glaucoma, predict_covid, predict_brain, localizeTumor, predict_disease, extract_symptoms_and_days_from_text)
from models.transcribe import get_text
import os
import re
import cv2
import json
import base64
import random
import time
import boto3
import numpy as np
import uuid
from PIL import Image

def save_and_validate_image(uploaded_file, target_size=None, mode="RGB"):
    """
    Validates uploaded medical image, sanitizes the filename with a unique UUID,
    saves it safely under MEDIA_ROOT, and returns (PIL.Image, file_path, saved_name).
    Raises ValueError on invalid format, size limit violation, or corrupted data.
    """
    if not uploaded_file:
        raise ValueError("No file uploaded.")
    
    # 1. Validate file size (max 20MB)
    if uploaded_file.size > 20 * 1024 * 1024:
        raise ValueError("Uploaded image exceeds the maximum allowed limit of 20MB.")

    # 2. Validate file extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.dcm'):
        raise ValueError("Invalid file format. Please upload a standard medical image (JPG, PNG, WEBP).")

    # 3. Sanitize filename using UUID to prevent collisions and directory traversal
    safe_name = f"{uuid.uuid4().hex}{ext}"
    fss = FileSystemStorage()
    saved_name = fss.save(safe_name, uploaded_file)
    file_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, saved_name))

    # 4. Verify image integrity with PIL
    try:
        with Image.open(file_path) as img_check:
            img_check.verify()
        
        # Re-open verified image for processing and load into memory
        with Image.open(file_path) as img_open:
            pil_img = img_open.convert(mode) if mode else img_open.copy()
            if target_size:
                pil_img = pil_img.resize(target_size)
            pil_img.load()
        return pil_img, file_path, saved_name
    except Exception as e:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise ValueError(f"Corrupted or unreadable image data: {str(e)}")

# Create your views here
def front(request):
    return render(request , 'front/index.html')

def bmiCalc(request):
    return render(request , 'bmi/bmi-calculator.html')

def is_json_requested(request):
    accept = request.headers.get('Accept', '')
    x_req = request.headers.get('X-Requested-With', '')
    return (
        'application/json' in accept
        or x_req == 'XMLHttpRequest'
        or request.content_type == 'application/json'
    )

def heart(request):
    return render(request , 'heart/index.html')

def heartPred(request):
    if request.method == 'POST':
        features = list(request.POST.dict().values())[1:]
        features = list(map(float , features))
        pred, confidence = predict_heartD(np.array([features]))
        if is_json_requested(request):
            return JsonResponse({
                'status': 'success',
                'modality': 'cardiovascular',
                'pred': pred,
                'confidence': confidence,
                'risk_level': 'Elevated' if pred == 1 else 'Low'
            })
        context = {
            'pred': pred,
            'confidence': confidence
        }
        return render(request , 'heart/output.html' , context)
    
    else:
        return redirect('heart-disease-view')

def diabetes(request):
    return render(request , 'diabetes/index.html')

def diabetesPred(request):
    if request.method == 'POST':
        features = list(request.POST.dict().values())[1:]
        pred, confidence = predict_diabetes(np.array([features]))
        if is_json_requested(request):
            return JsonResponse({
                'status': 'success',
                'modality': 'diabetes',
                'pred': pred,
                'confidence': confidence,
                'risk_level': 'Elevated' if pred == 1 else 'Low'
            })
        context = {
            'pred': pred,
            'confidence': confidence
        }
        return render(request , 'diabetes/output.html' , context)
    
    else:
        return redirect('diabetes-view')

def liver(request):
    return render(request , 'liver/index.html')

def liverPred(request):
    if request.method == 'POST':
        features = list(request.POST.dict().values())[1:]
        out_features = request.POST.dict()
        pred, confidence = predict_liverD(np.array([features]))
        if is_json_requested(request):
            return JsonResponse({
                'status': 'success',
                'modality': 'liver_function',
                'pred': pred,
                'confidence': confidence,
                'risk_level': 'Elevated' if pred == 1 else 'Low'
            })
        context = {
            'pred': pred,
            'confidence': confidence,
            'out_features': out_features
        }
        return render(request , 'liver/page2.html' , context)
    
    else:
        return redirect('liver-view')

def cancer(request):
    return render(request , 'cancer/cancer.html')

def cancerPred(request):
    if request.method == 'POST':
        raw_features = list(request.POST.dict().values())[1:]
        features = [float(f) for f in raw_features if str(f).replace('.', '', 1).replace('-', '', 1).isdigit()]
        pred, confidence = predict_cancerB(np.array([features]))
        if is_json_requested(request):
            return JsonResponse({
                'status': 'success',
                'modality': 'breast_cancer',
                'pred': pred,
                'confidence': confidence,
                'risk_level': 'High' if pred in ('M', 'm') else 'Low',
                'features': features
            })
        context = {
            'pred': pred,
            'confidence': confidence,
            'features': features
        }
        return render(request , 'cancer/output.html' , context)
    
    else:
        return redirect('cancer-view')

@csrf_exempt
def alzheimerPred(request):
    if request.method == 'POST':
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        try:
            img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(224, 224), mode="RGB")
            base_name, _ = os.path.splitext(file_path)
            cam_out_path = base_name + "_camViz.jpg"
            label, cam_path, confidence = predict_alzheimer(img, file_path, cam_out_path)

            with open(cam_path, "rb") as img2str:
                converted_string = base64.b64encode(img2str.read()).decode('utf-8')

            context = {
                'file_url': cam_path,
                'label': label,
                'confidence': confidence,
                'photo': converted_string
            }
            return JsonResponse(context)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Inference error: {str(e)}"}, status=500)
    else:
        return render(request , 'alzheimer/Alzheimer.html')

@csrf_exempt
def covidPred(request):
    if request.method == 'POST':
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        try:
            img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(299, 299), mode="L")
            base_name, _ = os.path.splitext(file_path)
            cam_out_path = base_name + "_camViz.jpg"
            label, cam_path, confidence = predict_covid(img, file_path, cam_out_path)

            with open(cam_path, "rb") as img2str:
                converted_string = base64.b64encode(img2str.read()).decode('utf-8')

            context = {
                'file_url': cam_path,
                'label': label,
                'confidence': confidence,
                'photo': converted_string
            }
            return JsonResponse(context)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Inference error: {str(e)}"}, status=500)
    else:
        return render(request, 'Covid/Covid.html')

@csrf_exempt
def brainPred(request):
    if request.method == 'POST':
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        try:
            pil_img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(224, 224), mode="RGB")
            base_name, _ = os.path.splitext(file_path)
            cam_out_path = base_name + "_camViz.jpg"

            label, confidence = predict_brain(pil_img, img_path=file_path, cam_path=cam_out_path)

            display_path = cam_out_path if os.path.exists(cam_out_path) else file_path

            with open(display_path, "rb") as img2str:
                converted_string = base64.b64encode(img2str.read()).decode('utf-8')

            context = {
                'file_url': display_path,
                'label': label,
                'confidence': confidence,
                'photo': converted_string
            }
            return JsonResponse(context)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Inference error: {str(e)}"}, status=500)
    else:
        return render(request, 'brain/BrainTumor.html')

@csrf_exempt
def malariaPred(request):
    if request.method == 'POST':
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        try:
            img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(100, 100), mode="RGB")
            label, confidence = predict_malaria(img)
            context = {
                'label': label,
                'confidence': confidence,
            }
            return JsonResponse(context)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Inference error: {str(e)}"}, status=500)
    else:
        return render(request, 'Malaria/Malaria.html')

@csrf_exempt
def glaucomaPred(request):
    if request.method == 'POST':
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        try:
            img, file_path, saved_name = save_and_validate_image(request.FILES['image'], target_size=(300, 300), mode="RGB")
            label, confidence = predict_glaucoma(img)
            context = {
                'label': label,
                'confidence': confidence,
            }
            return JsonResponse(context)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Inference error: {str(e)}"}, status=500)
    else:
        return render(request, 'glaucoma/index.html')

@csrf_exempt
def symptomsDis(request):
    if request.method == 'POST':
        try:
            # 1. Parse JSON payload if sent
            data = {}
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except Exception:
                    data = {}

            user_symptoms = []
            days = None
            transcript_text = ""

            if data:
                transcript_text = data.get('transcript', '') or data.get('speech_text', '') or data.get('text', '')
                if 'symptoms' in data:
                    sym_val = data['symptoms']
                    if isinstance(sym_val, list):
                        user_symptoms.extend([str(s).strip() for s in sym_val if str(s).strip()])
                    elif isinstance(sym_val, str):
                        sym_val_str = sym_val.strip()
                        if sym_val_str.startswith('[') and sym_val_str.endswith(']'):
                            try:
                                parsed_list = json.loads(sym_val_str)
                                if isinstance(parsed_list, list):
                                    user_symptoms.extend([str(s).strip() for s in parsed_list if str(s).strip()])
                            except Exception:
                                user_symptoms.extend([s.strip() for s in sym_val_str.split(',') if s.strip()])
                        elif ',' in sym_val_str:
                            user_symptoms.extend([s.strip() for s in sym_val_str.split(',') if s.strip()])
                        elif sym_val_str:
                            user_symptoms.append(sym_val_str)
                else:
                    user_symptoms.extend([str(v).strip() for k, v in data.items() if k not in ('csrfmiddlewaretoken', 'days', 'transcript', 'speech_text', 'text') and str(v).strip()])
                
                if 'days' in data and str(data['days']).isdigit():
                    days = int(data['days'])
            else:
                post_data = request.POST
                transcript_text = post_data.get('transcript', '') or post_data.get('speech_text', '') or post_data.get('text', '')
                
                # Extract from getlist('symptoms')
                raw_symptoms_list = post_data.getlist('symptoms')
                for raw_val in raw_symptoms_list:
                    raw_val = str(raw_val).strip()
                    if not raw_val:
                        continue
                    if raw_val.startswith('[') and raw_val.endswith(']'):
                        try:
                            parsed_list = json.loads(raw_val)
                            if isinstance(parsed_list, list):
                                for s in parsed_list:
                                    if str(s).strip() and str(s).strip() not in user_symptoms:
                                        user_symptoms.append(str(s).strip())
                                continue
                        except Exception:
                            pass
                    if ',' in raw_val:
                        for s in raw_val.split(','):
                            s_clean = s.strip()
                            if s_clean and s_clean not in user_symptoms:
                                user_symptoms.append(s_clean)
                        continue
                    if raw_val not in user_symptoms:
                        user_symptoms.append(raw_val)



                # Extract from symptoms0, symptoms1, etc.
                for k, v in post_data.items():
                    if k.startswith('symptoms') and k != 'symptoms' and v.strip():
                        if v.strip() not in user_symptoms:
                            user_symptoms.append(v.strip())

                # Fallback if other keys are used
                if not user_symptoms:
                    for k, v in post_data.items():
                        if k not in ('csrfmiddlewaretoken', 'days', 'transcript', 'speech_text', 'text') and v.strip():
                            user_symptoms.append(v.strip())

                if 'days' in post_data and str(post_data.get('days')).isdigit():
                    days = int(post_data.get('days'))

            # 2. Extract symptoms & duration from transcript if speech text was provided
            if transcript_text:
                speech_syms, speech_days = extract_symptoms_and_days_from_text(transcript_text)
                for s in speech_syms:
                    if s not in user_symptoms:
                        user_symptoms.append(s)
                if days is None:
                    days = speech_days

            # 3. Check for audio attachment fallback
            if 'audio' in request.FILES:
                try:
                    audio_data = request.FILES["audio"]
                    fss = FileSystemStorage()
                    file_name = audio_data.name + ".webm"
                    fss.save(file_name, audio_data)
                    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    text = get_text(file_path, file_name)
                    if text and "Audio transcription requires" not in text:
                        audio_syms, audio_days = extract_symptoms_and_days_from_text(text)
                        for s in audio_syms:
                            if s not in user_symptoms:
                                user_symptoms.append(s)
                        if days is None:
                            days = audio_days
                except Exception:
                    pass

            if days is None or days <= 0:
                days = 5

            advice, output = predict_disease(user_symptoms, days)
            context = {
                "status": "success",
                "recognized_symptoms": user_symptoms,
                "days": days,
                "advice": advice,
                "output": output,
                "results": output
            }
            return JsonResponse(context)
        except Exception as err:
            return JsonResponse({"status": "error", "error": str(err)}, status=500)
    else:
        return render(request, 'soundRecorder/recorder.html')
