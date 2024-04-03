import base64
import io
import json
import os
import threading
import time
import tkinter
import tkinter.messagebox
import customtkinter
import matplotlib.pyplot as plt
import openai
import gridfs
import qrcode
import requests
from bson import ObjectId
from camera_handler import CameraHandler
from CTkMessagebox import CTkMessagebox
from io import BytesIO
from PIL import Image, ImageTk
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import string
import numpy as np
import random
import nltk
from nltk.corpus import wordnet
from PIL import Image, ImageTk


# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("dark-blue")
global Canvas_image
Canvas_image = None
document_id_to_update = None
global device_id
device_id = None
mongo_client: MongoClient = MongoClient(
    "")
database: Database = mongo_client.get_database("moodCraftAI")
collection: Collection = database.get_collection("settings")
dalle_e_api_key = ""


class ImageGeneratorUI(customtkinter.CTk):
    def __init__(self, app):

        super().__init__()
        self.app = app
        self.last_processed_doc_id = None
        db_thread = threading.Thread(target=self.monitor_db_for_changes)
        photos_thread = threading.Thread(target=self.monitor_photos_collection)
        db_thread.daemon = True
        photos_thread.daemon = True
        db_thread.start()
        photos_thread.start()
        self.is_generating_image = False
        self.background_image = Image.open('Moodcraft.jpg')

    

        # Resize the QR Code Image

        # Add a boolean attribute to track the sidebar state
        self.is_sidebar_visible = True

        self.title("MoodCraft AI")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create canvas with the background image
        self.canvas = customtkinter.CTkCanvas(self)
        self.canvas_background = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        self.canvas.grid(row=0, column=1, rowspan=3, sticky="nsew")

        # Bind the configure event of the canvas to the resize_background function
        self.canvas.bind("<Configure>", self.resize_background)

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=80)
        self.tabview.grid(row=0, column=0, padx=(
            20, 10), pady=(20, 0), sticky="nsew")
        self.tabview.add("MoodCraft AI")
        self.tabview.add("Generate")
       # self.tabview.add("Settings")

        self.tabview.tab("MoodCraft AI").grid_columnconfigure(
            0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Generate").grid_columnconfigure(0, weight=1)

      #  self.tabview.tab("Settings").grid_columnconfigure(0, weight=1)

        # In the __init__ method of ImageGeneratorUI class
        self.antonym_toggle = customtkinter.CTkSwitch(self.tabview.tab("Generate"),
                                                      text="Antonym Mode",
                                                      command=self.antonym_toggle_event)
        self.antonym_toggle.grid(row=8, column=0, padx=20, pady=(10, 10))
        self.antonym_mode = False  # To track the state of the toggle

        # create main entry and button ------------------------------------------------------------------------------------------------ TAB 1
        self.sidebar_button_1 = customtkinter.CTkButton(
            self.tabview.tab("MoodCraft AI"), command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        background_color = "#ffffff"  # Replace with the color of your app's background

        # Create and place the toggle sidebar button
        self.toggle_sidebar_button = customtkinter.CTkButton(
            self,
            command=self.toggle_sidebar,
            text="<", width=4, height=4,fg_color="transparent"
        )
        self.toggle_sidebar_button.grid(row=2, column=0 )
        self.toggle_sidebar_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
       
        # Place the button in a fixed location
        self.toggle_sidebar_button.grid(row=1, column=0)

        

        # Create a label for the 4-digit number
        self.number_label = customtkinter.CTkLabel(self.tabview.tab("MoodCraft AI"),
                                                   text="0000",
                                                   font=("Helvetica", 20))  # Example font size 20
        self.number_label.grid(row=3, column=0, padx=5, pady=5)

        self.update_number()

         # Change to the actual URL when deployed
        web_app_url = "http://127.0.0.1:5000/"

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=1,
        )
        # When you generate the device_id, ensure it is URL-encoded if it includes '#'
        device_id_encoded = device_id.replace("#", "%23")
        web_app_url_with_device_id = f"{web_app_url}?device_id={device_id_encoded}"


        qr.add_data(web_app_url_with_device_id)
        print(web_app_url_with_device_id)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="Black", back_color="White")
        qr_photo = ImageTk.PhotoImage(qr_img)


        self.qr_label = customtkinter.CTkLabel(
            self.tabview.tab("MoodCraft AI"), image=qr_photo)
        self.qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
        # Adjust row and column as needed
        self.qr_label.grid(row=4, column=0, padx=0, pady=0)

        # ----------------------------------------------------------------------------------------------------------------------------- TAB 2

        self.entry = customtkinter.CTkEntry(self.tabview.tab(
            "Generate"), placeholder_text="Please enter a prompt",)
        self.entry.grid(row=0, column=0, pady=(5, 5), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(
            self.tabview.tab("Generate"), fg_color="transparent", text="Generate", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.startgen)
        self.main_button_1.grid(row=1, column=0, padx=(
            20, 20), pady=(5, 5), sticky="nsew")

        self.optionmenu_artStyle = customtkinter.CTkOptionMenu(self.tabview.tab("Generate"), dynamic_resizing=False,
                                                       values=["Abstract", "Realistic", "Cartoon", "3D Illustration", "Flat Art", "Watercolor", "Oil Painting", "Sketch", "Pixel Art", "Surrealism", "Pop Art", "Minimalist"])
        self.optionmenu_artStyle.grid(row=2, column=0, padx=20, pady=(20, 10))
        self.optionmenu_artStyle.set("Abstract")  # Set "Abstract" as the default selection


        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Generate"), text="Set Dalle-E API Key",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=3, column=0, padx=20, pady=(10, 10))

        # Add camera timer control elements
        self.camera_timer_options = customtkinter.CTkOptionMenu(self.tabview.tab("Generate"),
                                                                values=["1 Minute", "5 Minutes", "1 Hour",
                                                                        "5 Hours", "1 Day", "1 Week", "1 Month"])
        self.camera_timer_options.grid(row=4, column=0, padx=20, pady=(10, 10))

        self.camera_toggle_button = customtkinter.CTkButton(
            self.tabview.tab("Generate"), text="Start Camera", fg_color="green", command=self.toggle_camera)
        self.camera_toggle_button.grid(row=5, column=0, padx=20, pady=(10, 10))
        self.camera_active = False  # To track the camera state

        self.protocol("WM_DELETE_WINDOW", self.on_close)

# set default values ---------------------------------------------------------------------------------------------------------------------
        self.sidebar_button_1.configure(
            text="Toogle Camera")
# ------------------------------------------------------------------------- METHODS -------------------------------------------------------------------------
        db_thread = threading.Thread(target=self.monitor_db_for_changes)
        db_thread.daemon = True
        db_thread.start()
    
    def resize_background(self, event):
        # Resize the background image to the new size of the canvas
        new_width = event.width
        new_height = event.height
        self.background_image = self.background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.itemconfig(self.canvas_background, image=self.background_photo)

    def toggle_camera(self):
        if self.camera_active:
            self.stop_camera()
            self.camera_toggle_button.configure(
                text="Start Camera", fg_color="green")
            self.camera_active = False
        else:
            self.start_camera()
            self.camera_toggle_button.configure(
                text="Stop Camera", fg_color="red")
            self.camera_active = True

    def handle_camera_timer(self, action):
        # Convert the selected time to seconds
        time_dict = {
            "1 Minute": 60, "5 Minutes": 300, "1 Hour": 3600,
            "5 Hours": 18000, "1 Day": 86400, "1 Week": 604800, "1 Month": 2592000
        }
        self.selected_time_seconds = time_dict.get(
            self.camera_timer_options.get(), 60)

        if action == "start":
            if not hasattr(self, 'camera_timer') or not self.camera_timer.is_alive():
                self.camera_timer = threading.Timer(
                    self.selected_time_seconds, self.timer_callback)
                self.camera_timer.start()
        elif action == "stop":
            if hasattr(self, 'camera_timer'):
                self.camera_timer.cancel()

    def timer_callback(self):
        self.app.camera_handler.open_camera()
        # Reset the timer
        self.camera_timer = threading.Timer(
            self.selected_time_seconds, self.timer_callback)
        self.camera_timer.start()

    def start_camera(self):
        self.handle_camera_timer("start")

    def stop_camera(self):
        self.handle_camera_timer("stop")

    def on_close(self):
        # Stop camera and timer before closing
        self.stop_camera()
        self.destroy()

    def antonym_toggle_event(self):
        self.antonym_mode = not self.antonym_mode
    

    def monitor_photos_collection(self):
        global device_id
        photos_collection = database.get_collection("photos")
        with photos_collection.watch() as stream:
            for change in stream:
                try:
                    if change['operationType'] == 'insert':
                        # Directly use 'fullDocument' for 'insert' operations
                        new_device_id = change['fullDocument'].get('device_id')
                        new_image_id = change['fullDocument'].get('image_id')

                        if new_device_id == device_id:
                            self.update_canvas_with_image_id(new_image_id)

                    elif change['operationType'] == 'update':
                        # For 'update' operations, fetch the document using its '_id'
                        updated_doc_id = change['documentKey']['_id']
                        updated_doc = photos_collection.find_one({"_id": updated_doc_id})
                        
                        if updated_doc and updated_doc.get('device_id') == device_id:
                            new_image_id = updated_doc.get('image_id')
                            self.update_canvas_with_image_id(new_image_id)

                    time.sleep(10)

                except Exception as e:
                    print(f"Error in monitoring photos collection: {e}")

    def monitor_db_for_changes(self):
        global document_id_to_update, device_id  # Ensure device_id is accessible globally
        with collection.watch() as stream:
            for change in stream:
                if change['operationType'] == 'insert':
                    new_doc_id = change['documentKey']['_id']

                    # Safely access 'device_id', 'prompt', 'style', 'dalle_key', and 'mood' keys
                    new_device_id = change['fullDocument'].get('device_id')
                    new_prompt = change['fullDocument'].get('prompt')
                    new_art_style = change['fullDocument'].get('style')
                    new_dalle_id = change['fullDocument'].get('dalle_key', '')  # Optional, default to empty string
                    new_mood = change['fullDocument'].get('mood', '')  # Optional, handle as empty string if not present

                    # Check if the device_id from the document matches the current device_id
                    if new_device_id == device_id:
                        # Only process if this is a new document and device_id matches
                        if new_doc_id != self.last_processed_doc_id:
                            self.last_processed_doc_id = new_doc_id

                            # Ensure new_prompt is not None and new_art_style is not an empty string before proceeding
                            if new_prompt and new_art_style:
                                document_id_to_update = new_doc_id
                                # Check if new_mood is not an empty string or None explicitly (though get() method defaults to '' if not found)
                                if new_mood:
                                    image_prompt = f"Generate me an image with the prompt \"{new_prompt}\", depicting the style \"{new_art_style}\" and showing the emotion \"{new_mood}\" in abstract."
                                else:
                                    # Corrected the f-string syntax for the case without new_mood
                                    image_prompt = f"Generate me an image with the prompt \"{new_prompt}\""

                                # Call the method to process the image generation with the formulated prompt
                                self.update_prompt_and_generate_image(image_prompt, new_art_style)
                            else:
                                print("Document missing required fields: 'prompt' is empty or 'style' is empty")
                    else:
                        print("Device ID does not match")

                    time.sleep(10)


    def update_canvas_with_image_id(self, image_id_str):
        global Canvas_image
        try:
            # Connect to the Database and GridFS
            db = mongo_client.get_database("moodCraftAI")
            fs = gridfs.GridFS(db)
            
            # Convert the image_id string to ObjectId
            image_id = ObjectId(image_id_str)
            Canvas_image = image_id
            # Fetch the image using its ObjectId
            image_data = fs.get(image_id).read()

            # Convert the image data to a format that Tkinter can use
            image = Image.open(BytesIO(image_data))
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Resize the image using LANCZOS (formerly ANTIALIAS)
            photo = ImageTk.PhotoImage(image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS))
            
            # Display the image on the canvas
            self.canvas.image = photo  # Keep a reference to avoid garbage collection
            self.canvas.create_image(0, 0, anchor="nw", image=photo)

        except Exception as e:
            print(f"Error updating canvas with new image: {e}")

    def update_prompt_and_generate_image(self, new_prompt, new_art_style):
        # Update the prompt in the Tkinter Entry widget
        self.entry.delete(0, 'end')
        self.entry.insert(0, new_prompt)
        self.optionmenu_artStyle.set(new_art_style)

        print(self.optionmenu_artStyle)

        # Trigger image generation
        self.app.ui.after(0, self.startgen)

# ------------------------------------------------------------------------PTOGRESSBAR--------------------------------------------------------------------------

    def startgen(self, emotion=None):
        if self.is_generating_image:
            return  # Exit the function if an image is already being generated

        self.is_generating_image = True  # Set the flag to True to indicate the process has started

        self.progressbar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", indeterminate_speed=3, mode="indeterminate", width=950)
        self.progressbar.grid(row=2, column=1, padx=5, pady=5)
        self.progressbar.start()

        # Start image generation in a separate thread
        thread = threading.Thread(target=self.threaded_image_generation, args=(emotion,))
        thread.start()


    def threaded_image_generation(self, emotion=None):
        try:
            # Image generation logic
            if emotion is not None:
                self.generate_image_from_emotion(emotion)
            else:
                self.generate_image_from_emotion()
        finally:
            # Schedule the stop_progressbar method to run on the main thread
            self.app.ui.after(0, self.stop_progressbar)

    def stop_progressbar(self):
        self.progressbar.stop()
        self.progressbar.grid_forget()
        self.is_generating_image = False  # Reset the flag when the process is completed


 # -------------------------------------------------------------------------Toggll SideBar----------------------------------------------------------------------------------

    def toggle_sidebar(self):
        # Toggle the state
        self.is_sidebar_visible = not self.is_sidebar_visible

        # Show or hide the sidebar based on the state
        if self.is_sidebar_visible:
            self.tabview.grid()
            self.toggle_sidebar_button.configure(text="<", fg_color="transparent",width=3, height=3,)
            # Ensure tabview column does not expand
            self.grid_columnconfigure(0, weight=0)
            # Reset the canvas to its original column
            self.canvas.grid(column=1)
            self.resize_after_toogle()

        else:
            self.tabview.grid_remove()
            # Expand canvas to cover tabview's column
            self.canvas.grid(column=0, columnspan=2)
            self.toggle_sidebar_button.configure(width=1, height=1,text=">", fg_color="transparent")
            # Place the button to toggle the sidebar
            self.toggle_sidebar_button.grid(row=2, column=0)
            self.resize_after_toogle()
    # Function to generate image from detected emotion

# ------------------------------------------------------------------------Generate Image--------------------------------------------------------------------------

    def generate_image_from_emotion(self, emotion=None):

        global Canvas_image
        try:
            # Securely get your API key
            openai.api_key = dalle_e_api_key

            if emotion is None:
                user_prompt = self.entry.get()
                user_prompt = self.get_antonym(user_prompt)
            else:
                user_prompt = emotion
                if self.antonym_mode:
                    # Convert emotion to its antonym
                    user_prompt = self.get_antonym(user_prompt)

            user_prompt += " in style: " + self.optionmenu_artStyle.get()
            print(user_prompt)
            self.entry.delete(0, 'end')
            # Assuming OpenAI API has an endpoint for image generation (fictional in this context)
            response = openai.images.generate(
                model="dall-e-3",
                prompt=user_prompt,
                n=1,
                quality="hd",
                size="1024x1024"
            )

            print(response)

            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                Canvas_image = image_url

                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_bytes = image_response.content
                    self.save_image_to_mongodb(image_bytes, user_prompt)
                    # Download and display the image
                    self.download_and_display_image(image_url)

        except Exception as e:
            print("An error occurred:", e)

# ------------------------------------------------------------------------Display Image--------------------------------------------------------------------------
    def download_and_display_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # This will raise an exception for HTTP errors

            # Convert the response content into a BytesIO object
            image_bytes_io = BytesIO(response.content)

            # Display the image
            self.display_image(image_bytes_io)
        except Exception as e:
            print(f"Error downloading or displaying the image: {e}")

    def display_image(self, image_bytes_io):
        try:
            image = Image.open(image_bytes_io)

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Resize the image to match the canvas size
            photo = ImageTk.PhotoImage(image.resize(
                (canvas_width, canvas_height), Image.LANCZOS))
            self.canvas.image = photo  # Keep a reference.
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
        except Exception as e:
            print(f"Error in displaying the image: {e}")

    def open_input_dialog_event(self):
        global dalle_e_api_key
        dialog = customtkinter.CTkInputDialog(
            text="Type in a number:", title="CTkInputDialog")

        # Assuming the dialog is blocking and waits for user input
        dialog.wait_window()  # This waits for the dialog to close

        # After the dialog is closed, get the input
        dalle_e_api_key = dialog.get_input()
        print("CTkInputDialog:", dalle_e_api_key)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        self.app.camera_handler.open_camera()

    def generate(self):
        user_prompt = self.entry.get()
        category = f"{user_prompt} emotion"
        self.app.camera_handler.display_image(category)

     # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    def resize_after_toogle(self):
        global Canvas_image

        # Check if the image URL is valid
        if not Canvas_image:
            print("Canvas_image is empty or invalid.")
            return

        # Allow the UI to update its layout
        self.update_idletasks()
        if isinstance(Canvas_image, str) and Canvas_image.startswith('http'):
            # Start a background thread for downloading and processing the image
            thread = threading.Thread(target=self.process_image, args=(Canvas_image,), daemon=True)
            thread.start()
        else:
        # Assume it's an image ID for GridFS, update the canvas directly
            print(Canvas_image)
            self.update_canvas_with_image_id(Canvas_image)


    def process_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()

            image_bytes_io = BytesIO(response.content)
            image = Image.open(image_bytes_io)

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Use a faster resizing algorithm (lower quality but faster)
            resized_image = image.resize((canvas_width, canvas_height), Image.NEAREST)

            # Process the image data and prepare for Tkinter
            self.prepare_image_for_tkinter(resized_image)
        except Exception as e:
            print(f"Error in processing the image: {e}")

    def prepare_image_for_tkinter(self, resized_image):
        # Convert the resized image to a format that can be used in Tkinter
        image_tk = ImageTk.PhotoImage(resized_image)

        # Schedule the update_canvas method to run on the main thread
        self.canvas.after(0, lambda: self.update_canvas(image_tk))

    def update_canvas(self, photo):
        try:
            # Keep a reference to the PhotoImage object
            self.canvas_image_reference = photo
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
        except Exception as e:
            print(f"Error in updating the canvas: {e}")


    # -----------------------------------------------------------------------------------------------------------------------------------------------------------

    def save_image_to_mongodb(self, image_bytes, filename):
        global document_id_to_update
        global device_id
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
            connection = MongoClient(
                "mongodb+srv://MoodCraftAi:MoodCraftAi@moodcraftai.uygfyac.mongodb.net/?retryWrites=true&w=majority")

            # Connect to the Database where the images will be stored.
            database = connection['moodCraftAI']
            fs = gridfs.GridFS(database)

            # Store the PNG image in GridFS
            image_id = fs.put(png_bytes, filename=filename, collection='generated_images')

            settings_collection = database['settings']
            if document_id_to_update is not None:
                # Update existing document
                settings_collection.update_one(
                    {"_id": ObjectId(document_id_to_update)},
                    {"$set": {"art": image_id, "device_id": device_id}})
            else:
                # Upsert: Update if exists, insert if not
                new_id = ObjectId()  # Generating a new ObjectId
                update = {
                    "$setOnInsert": {
                        "_id": new_id,
                        "dalle_key": "",  # Set default values
                        "prompt": filename,
                        "style": "Generted from Moodcraft",
                        "art": image_id
                    },
                    "$set": {
                        "device_id": device_id
                    }
                }
                settings_collection.update_one({"device_id": device_id}, update, upsert=True)

            print(f"Image '{filename}' and associated data saved to MongoDB successfully.")

        except Exception as e:
            print(f"Error saving image to MongoDB: {str(e)}")


    def generate_random_id_np(self, length=10):
        """
        Generates a random string of specified length using NumPy.

        :param length: The length of the random string. Default is 10.
        :return: A random string of letters and digits.
        """
        # Create a sequence of all letters (uppercase and lowercase) and digits
        characters = string.ascii_letters + string.digits

        # Use NumPy's random.choice to select 'length' characters
        random_id = ''.join(np.random.choice(list(characters), size=length))

        return random_id

    def update_number(self):
        global device_id

        # Generate a random mix of 7 uppercase, lowercase letters, and digits
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=7))

        # Prepend '#' to make it 8 characters in total
        new_device_id = f"#{random_chars}"

        device_id = new_device_id
        print(device_id)
        # Update the label
        self.number_label.configure(text="Id: " + new_device_id)

        # Schedule the next update after 2 days (2 days * 24 hours * 60 minutes * 60 seconds)
        threading.Timer(172800, self.update_number).start()

    def get_antonym(self, word):
        antonyms = []
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                if l.antonyms():
                    antonyms.append(l.antonyms()[0].name())
        # Return the first antonym or the word itself
        return antonyms[0] if antonyms else word
