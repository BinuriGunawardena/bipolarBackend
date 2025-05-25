import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests

# cred = credentials.Certificate("serviceaccountkey.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")

if service_account_json:
    cred_dict = json.loads(service_account_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    raise Exception("GOOGLE_SERVICE_ACCOUNT environment variable is missing.")


# Initialize Firebase
db = firestore.client()

def store_prediction(user_id, collection_name, prediction_type, input_data, emotion):
    """Store prediction result in Firestore."""
    doc_ref = db.collection('users').document(user_id).collection(collection_name).document()
    doc_ref.set({
        'user_id': user_id,
        'type': prediction_type,
        'input': input_data if prediction_type == 'text' else None,
        'emotion': emotion,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    # try:
    #     user_ref = db.collection('users').document(user_id)
    #     emotions = {}

    #     # Get latest emotions
    #     collections = {
    #         'text_emotions': 'text_emotion',
    #         'audio_emotions': 'audio_emotion',
    #         'Video_emotions': 'video_emotion'
    #     }

    #     for col, key in collections.items():
    #         docs = user_ref.collection(col).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    #         for doc in docs:
    #             emotions[key] = doc.to_dict().get('emotion')

    #     # Get latest steps from activityData
    #     activity_docs = user_ref.collection('activityData').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    #     steps = None
    #     for doc in activity_docs:
    #         steps = doc.to_dict().get('steps')
    #         break

    #     # Convert steps to activity level
    #     if steps is not None:
    #         if steps < 10:
    #             activity_level = "Low"
    #         elif 10 <= steps <= 30:
    #             activity_level = "Average"
    #         else:
    #             activity_level = "High"
    #     else:
    #         activity_level = None

    #     # Only call API if all values are available
    #     required_keys = ['text_emotion', 'audio_emotion', 'video_emotion']
    #     if all(key in emotions for key in required_keys) and activity_level:
    #         payload = {
    #             'userID': user_id,
    #             'text_emotion': emotions['text_emotion'],
    #             'audio_emotion': emotions['audio_emotion'],
    #             'video_emotion': emotions['video_emotion'],
    #             'activity': activity_level
    #         }

    #         print("Triggering bipolar stage prediction with payload:", payload)

    #         response = requests.post('https://mybipolarapp.loca.lt/api/v1/predict_bipolar_stage', json=payload)

    #         if response.status_code == 200:
    #             print("[✓] Bipolar stage predicted:", response.json())
    #         else:
    #             print(f"[×] Prediction API error: {response.status_code} - {response.text}")

    # except Exception as e:
    #     print(f"[!] Error triggering bipolar stage prediction: {e}")

    try:
        user_ref = db.collection('users').document(user_id)
        emotions = {}

        # Subcollections for emotion types
        collections = {
            'text_emotions': 'text_emotion',
            'audio_emotions': 'audio_emotion',
            'Video_emotions': 'video_emotion'  # Case-sensitive match to your DB
        }

        # Fetch latest emotions, default to "Neutral" if not found
        for col, key in collections.items():
            docs = user_ref.collection(col).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in docs:
                emotions[key] = doc.to_dict().get('emotion')
            if key not in emotions:
                emotions[key] = "Neutral"

        # Fetch latest step count from activityData and convert to activity level
        activity_docs = user_ref.collection('activityData').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
        steps = None
        for doc in activity_docs:
            steps = doc.to_dict().get('steps')
            break

        # Convert steps → activity level
        if steps is not None:
            if steps < 10:
                activity_level = "Low"
            elif 10 <= steps <= 30:
                activity_level = "Average"
            else:
                activity_level = "High"
        else:
            activity_level = "Low"

        # Build payload for bipolar stage prediction
        payload = {
            'userID': user_id,
            'text_emotion': emotions['text_emotion'],
            'audio_emotion': emotions['audio_emotion'],
            'video_emotion': emotions['video_emotion'],
            'activity': activity_level
        }

        print("Triggering bipolar stage prediction with payload:", payload)

        response = requests.post(
            'https://mybipolarapp.loca.lt/api/v1/predict_bipolar_stage',
            json=payload,
            timeout=10
        )

        print("Response:", response.status_code, response.text)

        if response.status_code == 200:
            print("[✓] Bipolar stage predicted:", response.json())
        else:
            print(f"[×] Prediction API failed: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as req_err:
        print(f"[!] Network error calling bipolar API: {req_err}")

    except Exception as e:
        print(f"[!] Unexpected error triggering bipolar prediction: {e}")