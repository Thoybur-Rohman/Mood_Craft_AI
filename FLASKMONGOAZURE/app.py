import os
from bson.objectid import ObjectId
import bson
from dotenv import load_dotenv
# Import jsonify here
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, render_template_string
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import gridfs


# access your MongoDB Atlas cluster
load_dotenv()
connection_string: str = os.environ.get("CONNECTION_STRING")
mongo_client: MongoClient = MongoClient(connection_string)

database: Database = mongo_client.get_database("moodCraftAI")
collection: Collection = database.get_collection("settings")


# instantiating a new object with 'name'
app: Flask = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/prompts', methods=["GET", "POST"])
def prompt():
    if request.method == 'POST':
        # Retrieve form data
        prompt = request.form['prompt']  # Prompt, required
        device_id = request.form['deviceId']  # Device ID, required
        art_style = request.form['style']  # Art Style, required

        # DALL-E ID is optional, check if it's provided
        dalle_id = request.form.get('dalleKey', '')

        # Insert new record into collection in MongoDB
        collection.insert_one({
            "device_id": device_id,
            "dalle_key": dalle_id,
            "prompt": prompt,
            "style": art_style
        })

        return redirect(url_for('confirmation', prompt=prompt))

    elif request.method == 'GET':
        device_id_query = request.args.get('device_id', '')

        if device_id_query:
            prompts = list(collection.find({"device_id": device_id_query}))
        else:
            prompts = list(collection.find())

        novels = []
        for title in prompts:
            prompt = title.get("prompt")
            # Replace with your actual field name for the GridFS image ID
            image_id = title.get("art")
            novels.insert(0, {"prompt": prompt, "image_id": image_id})

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
    return jsonify({"message": "Canvas updated successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
