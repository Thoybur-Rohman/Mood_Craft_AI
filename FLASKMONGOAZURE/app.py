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
                            <button class="btn btn-sm btn-info btn-preview" data-toggle="modal" data-target="#previewModal" data-image-id="{novel["image_id"]}">Preview</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
            for novel in novels
        ])

    # Generate the main page with the gallery
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prompts Gallery</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
        <style>
            body {{
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .container {{
                padding: 20px;
                max-width: 1200px;
                margin: auto;
            }}
            .sticky-button {{
                position: sticky;
                top: 20px;
                z-index: 1;
            }}
            .search-bar {{
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .search-input {{
                flex-grow: 1;
                margin-right: 10px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                outline: none;
            }}
            .search-button {{
                white-space: nowrap;
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                background-color: #007bff;
                color: #fff;
                border-radius: 5px;
                cursor: pointer;
            }}
            .search-button:hover {{
                background-color: #0056b3;
            }}
            .loading {{
                text-align: center;
                margin-top: 20px;
            }}
            .card {{
                border-radius: 10px;
                overflow: hidden;
                transition: transform 0.3s ease;
                margin-bottom: 20px;
            }}
            .card:hover {{
                transform: scale(1.03);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }}
            .card-img-top {{
                height: 250px;
                object-fit: cover;
            }}
            .card-title {{
                font-size: 1.1em;
                margin-top: 10px;
            }}
            @media (max-width: 576px) {{
                .search-input, .search-button {{
                    width: 100%;
                    margin: 5px 0;
                }}
            }}
            .image-hover:hover {{
                transform: scale(1.1);
                transition: transform 0.3s ease;
            }}
            .loading-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }} 
            .image-caption {{
            position: absolute;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            color: #fff;
            width: 100%;
            text-align: center;
            padding: 5px;
            display: none;
            }}
            .card:hover .image-caption {{
                display: block;
            }}
                                           
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="text-center my-4">Prompts Gallery</h2>
            
            <!-- Sticky Back Button -->
            <a href="/" class="btn btn-secondary sticky-button" id="backButton">Back</a>
            
            <div class="search-bar">
                <form action="/prompts" method="get" class="form-inline">
                    <input type="text" name="device_id" class="form-control search-input" placeholder="Enter Device ID" value="{device_id_query}">
                    <button type="submit" class="btn btn-primary search-button">Search</button>
                </form>
            </div>
            
            <div id="loadingOverlay" class="loading-overlay">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
            
            <div class="row" id="gallery">
                {gallery_content}
            </div>
        </div>

        <!-- Modal for Image Preview -->
        <div class="modal fade" id="previewModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-body">
                        <img class="modal-image img-fluid" src="" alt="Preview">
                    </div>
                </div>
            </div>
        </div>

        <!-- JavaScript to handle the sticky back button, image preview, and loading indicator -->
         <script>
            document.addEventListener("DOMContentLoaded", function() {{
                updatePreviewButtons();
                document.querySelector(".loading").style.display = "none";
            }});

            function updatePreviewButtons() {{
                var previewButtons = document.querySelectorAll(".btn-preview");
                var modalImage = document.querySelector(".modal-image");

                previewButtons.forEach(function(button) {{
                    button.addEventListener("click", function() {{
                        var imageId = button.getAttribute("data-image-id");
                        modalImage.setAttribute("src", "/image/" + imageId);
                    }});
                }});
            }};
             // Enhanced Image Loading
            window.onload = function() {{
            document.getElementById("loadingOverlay").style.display = "none";
             }};
            
        </script>
    </body>
    </html>
    ''')


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
