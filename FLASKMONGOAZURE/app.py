import os
from bson.objectid import ObjectId
import bson
from dotenv import load_dotenv
# Import jsonify here
from flask import Flask, render_template, request, Response, jsonify
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
        # CREATE
        key = request.form['key']
        prompt = request.form['prompt']
        art_style = request.form['style']

        # insert new book into books collection in MongoDB
        collection.insert_one(
            {"key": key, "prompt": prompt, "style": art_style})
        return f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Prompt Added</title>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                <style>
                    body {{ 
                        font-family: 'Arial', sans-serif; 
                        background-color: #e9ecef; 
                        margin: 0; 
                        padding-top: 40px; 
                    }}
                    .container {{ 
                        max-width: 600px; 
                        margin: auto; 
                    }}
                    .message-box {{ 
                        background-color: white; 
                        padding: 30px; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.15); 
                        text-align: center; 
                    }}
                    .btn-back {{ 
                        color: white; 
                        background-color: #28a745; 
                        text-decoration: none; 
                        padding: 10px 20px; 
                        border-radius: 5px; 
                        margin-top: 20px; 
                        display: inline-block; 
                    }}
                    .btn-back:hover {{ 
                        background-color: #218838; 
                    }}
                    h2 {{
                        color: #333;
                    }}
                    p {{
                        color: #555;
                        font-size: 1.1rem;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="message-box">
                        <h2>Prompt Added Successfully</h2>
                        <p>The following prompt has been successfully added:</p>
                        <p class="text-success"><strong>"{prompt}"</strong></p>
                        <a href="/" class="btn-back">Go back to the form</a>
                    </div>
                </div>
            </body>
            </html>
            '''
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