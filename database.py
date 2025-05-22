import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

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