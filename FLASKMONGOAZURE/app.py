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

# book = {"book": "Harry Potter" , "pages": "123"}
# collection.insert_one(book)

# instantiating a new object with 'name'
app: Flask = Flask(__name__)


@app.route('/')
def index():
    prompts = list(collection.find({}, {"_id": 0, "key": 1, "prompt": 1}))
    # Generate table rows
    table_rows = ''.join(
        [f'<tr><td>{prompt["key"]}</td><td>{prompt["prompt"]}</td></tr>' for prompt in prompts])
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoodCraftAI Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f0f0f8;
            font-family: 'Arial', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .navbar-custom {
            background-color: #33495e;
            border-bottom: 3px solid #f0ad4e;
        }
        .navbar-custom .navbar-brand,
        .navbar-custom .navbar-nav .nav-link {
            color: #fff;
        }
        .navbar-custom .navbar-brand:hover,
        .navbar-custom .navbar-nav .nav-link:hover {
            color: #f0ad4e;
        }
        .container-main {
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .form-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 500px;
        }
        .footer {
            background-color: #33495e;
            color: white;
            text-align: center;
            padding: 20px 0;
        }
        .btn-custom {
            background-color: #5cb85c;
            color: white;
            border: none;
        }
        .btn-custom:hover {
            background-color: #4cae4c;
            color: white;
        }

        @media (max-width: 768px) {
            .form-container {
                padding: 15px;
            }
            .navbar-custom .navbar-nav .nav-link {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand" href="/">MoodCraftAI Dashboard</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item"><a class="nav-link" href="/prompts">Prompts</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-main">
        <div class="form-container">
            <h2 class="text-center">Welcome to MoodCraftAI</h2>
            <form action="/prompts" method="POST">
    <div class="form-group">
        <label for="key">Dalle API Key (optional):</label>
        <input type="text" class="form-control" id="key" name="key">
    </div>
    <div class="form-group">
        <label for="prompt">Prompt:</label>
        <input type="text" class="form-control" id="prompt" name="prompt" required>
    </div>
    <div class="form-group">
        <label for="style">Style:</label>
        <select class="form-control" id="style" name="style" required>
            <option value="Realistic">Realistic</option>
            <option value="Cartoon">Cartoon</option>
            <option value="3D Illustration">3D Illustration</option>
            <option value="Flat Art">Flat Art</option>
        </select>
    </div>
    <button type="submit" class="btn btn-custom btn-block">Submit</button>
</form>
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <span>MoodCraftAI Dashboard &copy; 2024</span>
        </div>
    </footer>
    <script>
    function vote(imageId, action) {
        fetch(`/${action}/${imageId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(`${action === 'upvote' ? 'Upvoted' : 'Liked'}! Total: ${data.count}`);
        });
    }
    </script>

    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.0.0/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>

    '''


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
                    padding: 40px 0;
                }}
                .card-img-top {{
                    width: 100%;
                    height: auto;
                    box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.5s;
                }}
                .card-img-top:hover {{
                    transform: scale(1.05);
                }}
                .zoom-image {{
                    overflow: hidden;
                    position: relative;
                }}
                .btn-download, .btn-copy {{
                    transition: background-color 0.3s;
                }}
                .btn-download:hover, .btn-copy:hover {{
                    background-color: #007bff;
                    color: #fff;
                }}
                .go-back-button {{
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    z-index: 1000;
                    background-color: #007bff;
                    color: #fff;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                }}
                .go-back-button:hover {{
                    background-color: #0056b3;
                }}
                .prompt-text {{
                    font-size: 16px;
                    text-align: center;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <a href="/" class="btn btn-primary go-back-button">Go Back</a>
            <div class="container">
                <h2 class="text-center">Art Gallery</h2>
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