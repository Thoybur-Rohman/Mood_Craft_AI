from pymongo import MongoClient
import gridfs

# Connect to the server with the hostName and portNumber.
connection = MongoClient("mongodb+srv://new_years:AuMBHvQmKC5XFtTl@cluster0.6swbq.mongodb.net/")

# Connect to the Database where the images will be stored.
database = connection['DB_NAME']


#Create an object of GridFs for the above database.
fs = gridfs.GridFS(database)

#define an image object with the location.
file = "C:\\Users\\Anti coding club\\Pictures\\34013ae5d376f71e56698868447a8c67.jpg"

#Open the image in read-only format.
with open(file, 'rb') as f:
    contents = f.read()

#Now store/put the image via GridFs object.
fs.put(contents, filename="file")