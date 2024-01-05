from pymongo import MongoClient
import gridfs
import bson

class YourClass:
    def save_image_to_mongodb(self, image_bytes, filename, movie_info):
        try:
            # Connect to the server with the hostName and portNumber.
            connection = MongoClient("mongodb+srv://new_years:AuMBHvQmKC5XFtTl@cluster0.6swbq.mongodb.net/")

            # Connect to the Database where the images will be stored.
            database = connection['MoodCraftAi-db']

            # Create an object of GridFs for the above database.
            fs = gridfs.GridFS(database)

            # Store the image via GridFs object and get its id.
            image_id = fs.put(image_bytes, filename=filename)

            # Update the 'poster' field in movie_info with the image reference.
            # This could be a URL or an identifier to retrieve the image.
            # For this example, I'm using the GridFS file ID as the reference.
            movie_info['poster'] = str(image_id)

            # Create a document for the movie with additional information.
            movie_document = {
                "imdbId": movie_info['imdbId'],
                "title": movie_info['title'],
                "releaseDate": movie_info['releaseDate'],
                "trailerLink": movie_info['trailerLink'],
                "genres": movie_info['genres'],
                "poster": movie_info['poster'],  # Reference to the stored image file
                "backdrops": movie_info['backdrops'],
                "reviewIds": movie_info['reviewIds']
            }

            # Insert the document into a collection (e.g., 'movies').
            movies_collection = database['Movies']
            movies_collection.insert_one(movie_document)

            print(f"Image '{filename}' and associated data saved to MongoDB successfully.")

        except Exception as e:
            print(f"Error saving image to MongoDB: {str(e)}")

# Example usage
your_instance = YourClass()
image_bytes = b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='  # Your image bytes here
filename = 'example_movie_poster.jpg'
movie_info = {
    "imdbId": "tt1234567",
    "title": "Example Movie Title",
    "releaseDate": "2024-01-01",
    "trailerLink": "https://example.com/trailer",
    "genres": ["Fantasy", "Drama", "Mystery"],
    "backdrops": ["https://example.com/backdrop1.jpg", "https://example.com/backdrop2.jpg"],
    "reviewIds": []
}
your_instance.save_image_to_mongodb(image_bytes, filename, movie_info)
