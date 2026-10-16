from django.urls import path, include
from main import views
from main import api_views

urlpatterns = [
    path('' , views.front , name = 'index'),
    path('know-your-disease/' , views.symptomsDis , name = 'know-your-disease'),
    path('know-your-disease' , views.symptomsDis),

    path('calculate-bmi/' , views.bmiCalc , name = 'bmi-calculator'),

    path('alzheimer/' , views.alzheimerPred , name = 'alzheimer-predict'),

    path('cancer/' , views.cancer , name = 'cancer-view'),
    path('cancer-prediction/' , views.cancerPred , name = 'cancer-predict'),

    path('brain-tumor/' , views.brainPred , name = 'brain-tumor-predict'),

    path('covid/' , views.covidPred , name = 'covid-predict'),

    path('diabetes/' , views.diabetes , name = 'diabetes-view'),
    path('diabetes-prediction/' , views.diabetesPred , name = 'diabetes-predict'),

    path('glaucoma/' , views.glaucomaPred , name = 'glaucoma-predict'),

    path('heart-disease/' , views.heart , name = 'heart-disease-view'),
    path('heart-disease-prediction/' , views.heartPred , name = 'heart-disease-predict'),

    path('liver/' , views.liver , name = 'liver-view'),
    path('liver-prediction/' , views.liverPred , name = 'liver-predict'),

    path('malaria/' , views.malariaPred , name = 'malaria-predict'),

    # --- DiagnoAI REST API v1 Endpoints ---
    path('api/v1/health/', api_views.api_health, name='api-v1-health'),
    path('api/v1/heart/', api_views.api_heart, name='api-v1-heart'),
    path('api/v1/diabetes/', api_views.api_diabetes, name='api-v1-diabetes'),
    path('api/v1/cancer/', api_views.api_cancer, name='api-v1-cancer'),
    path('api/v1/liver/', api_views.api_liver, name='api-v1-liver'),
    path('api/v1/alzheimer/', api_views.api_alzheimer, name='api-v1-alzheimer'),
    path('api/v1/covid/', api_views.api_covid, name='api-v1-covid'),
    path('api/v1/brain-tumor/', api_views.api_brain, name='api-v1-brain'),
    path('api/v1/glaucoma/', api_views.api_glaucoma, name='api-v1-glaucoma'),
    path('api/v1/malaria/', api_views.api_malaria, name='api-v1-malaria'),
    path('api/v1/symptoms/', api_views.api_symptoms, name='api-v1-symptoms'),
]