import os
from bson.objectid import ObjectId
import bson
from dotenv import load_dotenv
# Import jsonify here
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, session
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import gridfs
from datetime import timedelta ,timedelta ,datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from tensorflow.keras.models import load_model
import numpy as np
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import random
import nltk
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.responses import HTMLResponse
import json


lemmatizer = WordNetLemmatizer()

model = load_model(r'C:\Users\Anti coding club\Downloads\moodcraft_ai_0.1.0.h5')
words = pickle.load(open(r'C:\Users\Anti coding club\Downloads\words.pkl', 'rb'))
classes = pickle.load(open(r'C:\Users\Anti coding club\Downloads\classes.pkl', 'rb'))
intents = json.load(open('intents.json', 'r'))


# access your MongoDB Atlas cluster
load_dotenv()
connection_string: str = os.environ.get("CONNECTION_STRING")
mongo_client: MongoClient = MongoClient(connection_string)

database: Database = mongo_client.get_database("moodCraftAI")
collection: Collection = database.get_collection("settings")


# instantiating a new object with 'name'
app: Flask = Flask(__name__)
app.secret_key = 'MoodCraft AI'  # Change this to a random secret key
app.permanent_session_lifetime = timedelta(minutes=4)  # Sets the session lifetime



@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route("/chat")
def chat():
    return render_template('chat.html')

@app.route('/')
def index():
    device_id = request.args.get('device_id', None)

    # Check if 'device_id' is present in the request
    if device_id:
        session['device_id'] = device_id  # Store device_id in session
        session['timestamp'] = datetime.now().timestamp()  # Store current timestamp
        session.permanent = True  # Make the session permanent to use the app's lifetime setting
    else:
        # Check if the session has expired
        session_timestamp = session.get('timestamp')
        if session_timestamp:
            current_timestamp = datetime.now().timestamp()
            # Calculate the time difference in seconds
            time_diff = current_timestamp - session_timestamp
            if time_diff > app.permanent_session_lifetime.total_seconds():
                # Session has expired, clear the 'device_id' from session
                session.pop('device_id', None)
                session.pop('timestamp', None)

    # Redirect to a different page or render a template as needed
    return render_template('index.html', device_id=session.get('device_id'))


@app.route('/prompts', methods=["GET", "POST"])
def prompt():
    if request.method == 'POST':
        # Retrieve form data
        prompt = request.form['prompt']  # Prompt, required
        device_id = request.form['deviceId']  # Device ID, required
        art_style = request.form['style']  # Art Style, required
        include_dalle_id = 'dalleKey' in request.form  # Check if DALL-E ID is included
        dalle_id = request.form.get('dalleKey', '') if include_dalle_id else ''  # DALL-E ID, optional
        include_mood = 'mood' in request.form  # Check if Mood is included
        mood = request.form.get('mood', '') if include_mood else ''  # Mood, optional

        # Insert new record into collection in MongoDB
        collection.insert_one({
            "device_id": device_id,
            "dalle_key": dalle_id,
            "prompt": prompt,
            "style": art_style,
            "mood": mood  # Only insert mood if it's provided
        })

        return redirect(url_for('confirmation', prompt=prompt))

    else:
        device_id_query = session.get('device_id', None)  # Use session device_id if available

        prompts = prompts = list(collection.find())
        novels = [{"prompt": p.get("prompt"), "image_id": str(p.get("art"))} for p in prompts]

        return render_template('gallery.html', novels=novels, device_id_query=device_id_query)

@app.route('/confirmation/<prompt>')
def confirmation(prompt):
    return render_template('confirmation.html', prompt=prompt)


@app.route('/image/<image_id>')
def serve_image(image_id):
    mongo_client = MongoClient(connection_string)
    db = mongo_client.get_database("moodCraftAI")
    # If you need to fetch additional data from settings collection
    # associated_data = settings_collection.find_one({'image_field': ObjectId(image_id)})
    # You can use associated_data as needed
    fs = gridfs.GridFS(db)  # Initialize GridFS with the database object
    try:
        file = fs.get(ObjectId(image_id))
        return Response(file.read(), mimetype='image/png')
    except gridfs.errors.NoFile:
        return 'Image not found', 404


@app.route('/update_canvas', methods=["POST"])
def update_canvas():
    device_id = request.form['deviceId']
    image_id = request.form['imageId']
    
    
    photos_collection = mongo_client.get_database("moodCraftAI").get_collection("photos")
    photos_collection.update_one(
        {"device_id": device_id},
        {"$set": {"image_id": image_id}},
        upsert=True
    )

    # Instead of returning a JSON message, render an HTML template
    return render_template('update_canvas_success.html', device_id=device_id, image_id=image_id)


@app.post("/get_response")
def chat_response():  # If you're using standard Flask, this should not be async
    data = request.get_json()  # Get data from request body
    if not data or 'sentence' not in data:
        raise HTTPException(status_code=400, detail="Empty sentence provided.")

    sentence = data['sentence']
    try:
        # Assuming clean_up_sentence is a function that processes the sentence
        cleaned_sentence = clean_up_sentence(sentence)
        # Assuming get_response is a function that generates a response based on the cleaned sentence
        response = get_response(' '.join(cleaned_sentence))  # Example of how you might use the cleaned sentence
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def clean_up_sentence(sentence):
    sentence_words = word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    p = bag_of_words(sentence)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(sentence):
    intent = predict_class(sentence)[0]['intent']
    for i in intents['intents']:
        if i['tag'] == intent:
            result = random.choice(i['responses'])
            break
    return result



if __name__ == '__main__':   
    app.run(host='0.0.0.0', debug=True, port=5000)
