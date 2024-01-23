import os
from bson.objectid import ObjectId
import bson
from dotenv import load_dotenv
# Import jsonify here
from flask import Flask, render_template, request, Response, jsonify , redirect, url_for,render_template_string
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
        prompts = list(collection.find())
        novels = []
        for title in prompts:
            book_prompt = title.get("prompt")
            # Replace with your actual field name for the GridFS image ID
            image_id = title.get("art")
            novels.insert(0, {"prompt": book_prompt, "image_id": image_id})

        # Generate HTML content for the gallery
        gallery_content = ''.join([
        f'''
        <div class="col-md-4">
            <div class="card mb-4 shadow-sm">
                <div class="zoom-image">
                    <img src="/image/{novel["image_id"]}" class="card-img-top" alt="Image">
                </div>
                <div class="card-body">
                    <p class="card-text">{novel["prompt"]}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="btn-group">                
                            <a href="/image/{novel["image_id"]}" class="btn btn-sm btn-outline-secondary btn-download" download="Image_{novel["image_id"]}">Download</a>
                            <button type="button" class="btn btn-sm btn-outline-secondary btn-copy" onclick="copyToClipboard('/image/{novel["image_id"]}')">Copy Link</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        for novel in novels
    ])

        # Generate the main page with the gallery
        main_page = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prompts Gallery</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
            <style>
                body {{
                    background-color: #f0f0f8;
                    font-family: 'Arial', sans-serif;
                }}

                .container {{
                    padding: 20px;
                }}

                .card {{
                    border: none;
                    border-radius: 10px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    transition: transform 0.3s ease-in-out;
                }}

                .card:hover {{
                    transform: scale(1.05);
                }}

                .card-img-top {{
                    width: 100%;
                    height: auto;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }}

                .card-body {{
                    padding: 1.5rem;
                }}

                .btn-download, .btn-copy {{
                    background-color: #007bff;
                    color: #fff;
                    transition: background-color 0.3s;
                    border: none;
                    border-radius: 5px;
                    margin-right: 10px;
                    padding: 8px 20px;
                }}

                .btn-download:hover, .btn-copy:hover {{
                    background-color: #0056b3;
                }}

                /* Updated Go Back Button */
                .go-back-button {{
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    z-index: 1000;
                    background-color: #007bff;
                    color: #fff;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    text-decoration: none;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    transition: background-color 0.3s, transform 0.3s;
                }}

                .go-back-button:hover {{
                    background-color: #0056b3;
                    transform: scale(1.05);
                }}

                /* Responsive Styles */
                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}

                    .card-body {{
                        padding: 1rem;
                    }}

                    .go-back-button {{
                        top: 10px;
                        left: 10px;
                        font-size: 16px;
                        padding: 10px 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <a href="/" class="btn btn-primary go-back-button">Go Back</a>
            <div class="container">
                <h2>Prompts Gallery</h2>
                <div class="row">
                    {gallery_content}
                </div>
            </div>
        </body>
        <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text);
                alert("Link copied to clipboard");
            }}
        </script>
        </html>
        '''


        return main_page
    

@app.route('/confirmation/<prompt>')
def confirmation(prompt):
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prompt Confirmation</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    text-align: center;
                    color: #333;
                }
                .container {
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                h2 {
                    color: #5cb85c;
                }
                p {
                    font-size: 16px;
                    line-height: 1.6;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #5cb85c;
                    color: white;
                    border-radius: 5px;
                    text-decoration: none;
                    transition: background-color 0.3s ease;
                }
                a:hover {
                    background-color: #4cae4c;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Prompt Added Successfully</h2>
                <p>The following prompt has been successfully added:</p>
                <p><strong>{{ prompt }}</strong></p>
                <a href="/">Add another prompt</a>
            </div>
        </body>
        </html>
    ''', prompt=prompt)


@app.route('/image/<image_id>')
def serve_image(image_id):
    mongo_client = MongoClient(connection_string)
    db = mongo_client.get_database("moodCraftAI")
    settings_collection = db.get_collection(
        "settings")  # Access the settings collection

    # If you need to fetch additional data from settings collection
    # associated_data = settings_collection.find_one({'image_field': ObjectId(image_id)})
    # You can use associated_data as needed

    fs = gridfs.GridFS(db)  # Initialize GridFS with the database object

    try:
        file = fs.get(ObjectId(image_id))
        return Response(file.read(), mimetype='image/png')
    except gridfs.errors.NoFile:
        return 'Image not found', 404







if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)