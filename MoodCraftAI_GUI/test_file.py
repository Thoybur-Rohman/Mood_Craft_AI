from pymongo import MongoClient
import gridfs
from PIL import Image
import io
import base64

class YourClass:
    def save_image_to_mongodb(self, image_bytes, filename, movie_info):
        try:
            # Convert the image bytes to a PNG format
            try:
                image = Image.open(io.BytesIO(image_bytes))
                with io.BytesIO() as png_io:
                    image.save(png_io, format="PNG")
                    png_bytes = png_io.getvalue()
            except IOError:
                raise Exception("Unable to convert image to PNG - may be invalid image data")

            # Connect to MongoDB
            connection = MongoClient("mongodb+srv://new_years:AuMBHvQmKC5XFtTl@cluster0.6swbq.mongodb.net/")

            # Connect to the Database where the images will be stored.
            database = connection['MoodCraftAi-db']
            fs = gridfs.GridFS(database)

            # Store the PNG image in GridFS
            image_id = fs.put(png_bytes, filename=filename)

            # Update the movie_info with the image reference
            movie_info['poster'] = str(image_id)

            # Create and insert the movie document
            movie_document = {
                "imdbId": movie_info['imdbId'],
                "title": movie_info['title'],
                "releaseDate": movie_info['releaseDate'],
                "trailerLink": movie_info['trailerLink'],
                "genres": movie_info['genres'],
                "poster": movie_info['poster'],
                "backdrops": movie_info['backdrops'],
                "reviewIds": movie_info['reviewIds']
            }
            movies_collection = database['Movies']
            movies_collection.insert_one(movie_document)

            print(f"Image '{filename}' and associated data saved to MongoDB successfully.")

        except Exception as e:
            print(f"Error saving image to MongoDB: {str(e)}")


# Example usage
your_instance = YourClass()
# Your image bytes here
image_bytes = b'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'  # Replace with actual image bytes
image = base64.b64decode(image_bytes)
filename = 'example_movie_poster.png'
movie_info = {
    "imdbId": "tt1234568",
    "title": "Test Movie Title",
    "releaseDate": "2024-01-01",
    "trailerLink": "https://example.com/trailer",
    "genres": ["Fantasy", "Drama", "Mystery"],
    "backdrops": ["https://example.com/backdrop1.jpg", "https://example.com/backdrop2.jpg"],
    "reviewIds": []
}
your_instance.save_image_to_mongodb(image, filename, movie_info)


