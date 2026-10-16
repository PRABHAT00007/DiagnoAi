import pandas as pd
import json
import random
import time
import boto3
from decouple import config
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Accessing the environment variables stored in .env file
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_KEY = config('AWS_SECRET_KEY', default='')

MY_REGION = config('MY_REGION', default='us-east-1')
BUCKET_NAME = config('BUCKET_NAME', default='')

LANG_CODE = 'en-AU'

# For each transcription call, create a random job name
def random_job_name():
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
    LOWERCASE_CHAR = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q','r', 's', 't', 'u', 'v', 'w', 'x', 'y','z']
    UPPERCASE_CHAR = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q','R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y','Z']

    COMBINED_LIST = DIGITS + UPPERCASE_CHAR + LOWERCASE_CHAR
    temp_name = ""

    for x in range(10):
        temp_name += random.choice(COMBINED_LIST)

    return str(temp_name)

def get_text(file_path , file_name):
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_KEY or not BUCKET_NAME:
        return "Audio transcription requires AWS S3 and Transcribe configuration."

    try:
        s3 = boto3.resource(
            service_name="s3",
            region_name=MY_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        s3.Bucket(BUCKET_NAME).upload_file(Filename=file_path, Key=file_name)

        transcribe = boto3.Session(
            region_name=MY_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_KEY
        ).client("transcribe")  

        file_format = "webm"
        job_uri = f"s3://{BUCKET_NAME}/{file_name}"
        job_name = random_job_name()             

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=file_format,
            LanguageCode=LANG_CODE
        )

        max_wait_seconds = 120
        elapsed = 0
        while elapsed < max_wait_seconds:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)
            elapsed += 5

        if job_status == "COMPLETED":
            data = pd.read_json(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            text = data['results']['transcripts'][0]['transcript']
        else:
            text = ""

        try:
            s3.Bucket(BUCKET_NAME).objects.filter(Prefix=file_name).delete()
        except Exception:
            pass

        return text
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
