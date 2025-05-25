import os
from flask import Flask, request
import json
from apscheduler.schedulers.background import BackgroundScheduler
from routes import predict_text, predict_audio, predict_bipolar_stage, scheduled_bipolar_prediction

app = Flask(__name__)

@app.route('/api/v1/predict_text', methods=['POST'])
def predict_text_emotion():
    return predict_text(request.json)
    
@app.route('/api/v1/predict_audio', methods=['POST'])
def predict_audio_emotion():
    return predict_audio(request)

@app.route('/api/v1/predict_bipolar_stage', methods=['POST'])
def predict_bipolar_stage_emotion():
    return predict_bipolar_stage(request.json)
    
@app.route('/')
def hello_world():
    return 'BIPOLAR DISORDER PREDICTION SYSTEM'

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_bipolar_prediction, 'interval', minutes=1)
scheduler.start()
print("Scheduler started")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
