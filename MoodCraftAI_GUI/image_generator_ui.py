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


# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("dark-blue")
global Canvas_image
Canvas_image = None
global document_id_to_update
global device_id
mongo_client: MongoClient = MongoClient(
    "mongodb+srv://MoodCraftAi:MoodCraftAi@moodcraftai.uygfyac.mongodb.net/?retryWrites=true&w=majority")
database: Database = mongo_client.get_database("moodCraftAI")
collection: Collection = database.get_collection("settings")
dalle_e_api_key = "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"


class ImageGeneratorUI(customtkinter.CTk):
    def __init__(self, app):

        super().__init__()
        self.app = app
        self.last_processed_doc_id = None
        db_thread = threading.Thread(target=self.monitor_db_for_changes)
        db_thread.daemon = True
        db_thread.start()

        # Change to the actual URL when deployed
        web_app_url = "https://moodcraftai.salmonbay-ea017e6c.ukwest.azurecontainerapps.io/"

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        
        qr.add_data(web_app_url)  # Replace with your data
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="Black", back_color="White")
        qr_photo = ImageTk.PhotoImage(qr_img)

        # Resize the QR Code Image
        desired_size = (10, 10)  # Example size, adjust as needed
        qr_img_resized = qr_img.resize(desired_size, Image.Resampling.LANCZOS)

        # Add a boolean attribute to track the sidebar state
        self.is_sidebar_visible = True

        self.title("MoodCraft AI")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create canvas
        self.canvas = customtkinter.CTkCanvas(self, width=512, height=512)
        self.canvas.grid(row=0, column=1, rowspan=3,
                         sticky="nsew")  # Set rowspan to 3

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

        # create main entry and button ------------------------------------------------------------------------------------------------ TAB 1
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab(
            "MoodCraft AI"), text="select you generation type")
        self.label_tab_2.grid(row=0, column=0, padx=5, pady=0)

        self.sidebar_button_1 = customtkinter.CTkButton(
            self.tabview.tab("MoodCraft AI"), command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.toggle_sidebar_button = customtkinter.CTkButton(
            self, text="Toggle Sidebar", command=self.toggle_sidebar)
        # Place the button in a fixed location
        self.toggle_sidebar_button.grid(row=3, column=0)
        
        self.qr_label = customtkinter.CTkLabel(
            self.tabview.tab("MoodCraft AI"), image=qr_photo)
        self.qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
        # Adjust row and column as needed
        self.qr_label.grid(row=2, column=0, padx=0, pady=0)

                # Create a label for the 4-digit number
        self.number_label = customtkinter.CTkLabel(self.tabview.tab("MoodCraft AI"), 
                                           text="0000", 
                                           font=("Helvetica", 20))  # Example font size 20
        self.number_label.grid(row=3, column=0, padx=5, pady=5)

        self.update_number()


        # ----------------------------------------------------------------------------------------------------------------------------- TAB 2

        self.entry = customtkinter.CTkEntry(self.tabview.tab(
            "Generate"), placeholder_text="Please enter a prompt",)
        self.entry.grid(row=0, column=0, pady=(5, 5), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(
            self.tabview.tab("Generate"), fg_color="transparent", text="Generate", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.startgen)
        self.main_button_1.grid(row=1, column=0, padx=(
            20, 20), pady=(5, 5), sticky="nsew")

        self.optionmenu_artStyle = customtkinter.CTkOptionMenu(self.tabview.tab("Generate"), dynamic_resizing=False,
                                                               values=["Realistic", "Cartoon", "3D Illustration", "Flat Art"])
        self.optionmenu_artStyle.grid(row=2, column=0, padx=20, pady=(20, 10))

        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Generate"), text="Set Dalle-E API Key",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=3, column=0, padx=20, pady=(10, 10))




# set default values ---------------------------------------------------------------------------------------------------------------------
        self.sidebar_button_1.configure(
            text="Toogle Camera")
      #  self.appearance_mode_optionemenu.set("Dark")
      #  self.scaling_optionemenu.set("100%")

# ------------------------------------------------------------------------- METHODS -------------------------------------------------------------------------
        db_thread = threading.Thread(target=self.monitor_db_for_changes)
        db_thread.daemon = True
        db_thread.start()

    def monitor_db_for_changes(self):
        global document_id_to_update
        with collection.watch() as stream:
            for change in stream:
                if change['operationType'] == 'insert':
                    new_doc_id = change['documentKey']['_id']

                    # Only process if this is a new document
                    if new_doc_id != self.last_processed_doc_id:
                        self.last_processed_doc_id = new_doc_id

                        # Safely access 'prompt' and 'style' keys
                        new_prompt = change['fullDocument'].get('prompt')
                        new_art_style = change['fullDocument'].get('style')

                        # Ensure both new_prompt and new_art_style are not None before proceeding
                        if new_prompt is not None and new_art_style is not None:
                            document_id_to_update = new_doc_id
                            self.update_prompt_and_generate_image(
                                new_prompt, new_art_style)
                        else:
                            print("Document missing required fields: 'prompt' or 'style'")
                        time.sleep(10)


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
        self.progressbar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", indeterminate_speed=2, mode="indeterminate", width=800)
        self.progressbar.grid(row=3, column=1, padx=20, pady=10)
        self.progressbar.start()

        # Start image generation in a separate thread, checking if emotion is not None
        if emotion is not None:
            thread = threading.Thread(
                target=self.threaded_image_generation, args=(emotion,))
        else:
            thread = threading.Thread(target=self.threaded_image_generation)

        thread.start()

    def threaded_image_generation(self, emotion=None):
        # Check if emotion is None and call generate_image_from_emotion accordingly
        if emotion is not None:
            self.generate_image_from_emotion(emotion)
        else:
            self.generate_image_from_emotion()

        # Schedule the stop_progressbar method to run on the main thread
        self.app.ui.after(0, self.stop_progressbar)

    # Schedule the stop_progressbar method to run on the main thread
        self.app.ui.after(0, self.stop_progressbar)

    def stop_progressbar(self):
        self.progressbar.stop()
        self.progressbar.grid_forget()

 # -------------------------------------------------------------------------Toggll SideBar----------------------------------------------------------------------------------

    def toggle_sidebar(self):
        # Toggle the state
        self.is_sidebar_visible = not self.is_sidebar_visible

        # Show or hide the sidebar based on the state
        if self.is_sidebar_visible:
            self.tabview.grid()
            # Ensure tabview column does not expand
            self.grid_columnconfigure(0, weight=0)
            # Reset the canvas to its original column
            self.canvas.grid(column=1)
            self.resize_after_toogle()

        else:
            self.tabview.grid_remove()
            # Expand canvas to cover tabview's column
            self.canvas.grid(column=0, columnspan=2)
            # Add a button to toggle the sidebar
            self.toggle_sidebar_button.grid(row=3, column=0)
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
            else:
                user_prompt = emotion

            user_prompt += " in style: " + self.optionmenu_artStyle.get()
            print(user_prompt)
            self.entry.delete(0, 'end')
            # Assuming OpenAI API has an endpoint for image generation (fictional in this context)
            response = openai.Image.create(
                model="dall-e-3",
                prompt=user_prompt,
                n=1,
                quality="hd",
                size="1024x1024"
            )

            image_urls = [response['data'][i]['url']
                          for i in range(len(response['data']))]

            for url in image_urls:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                self.save_image_to_mongodb(response.content, user_prompt)
                Canvas_image = response.content  # Store the raw bytes of the image

            # Display the first image
            if image_urls:
                self.display_image(Canvas_image)

        except Exception as e:
            print("An error occurred:", e)

# ------------------------------------------------------------------------Display Image--------------------------------------------------------------------------

    def display_image(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))

            canvas_width = self.app.ui.canvas.winfo_width()
            canvas_height = self.app.ui.canvas.winfo_height()

            # Resize the image to match the canvas size
            photo = ImageTk.PhotoImage(image.resize(
                (canvas_width, canvas_height), resample=Image.LANCZOS))
            self.app.ui.canvas.image = photo
            self.app.ui.canvas.create_image(
                0, 0, anchor="nw", image=self.app.ui.canvas.image)
        except Exception as e:
            print("Error in displaying the image:", e)

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

        try:
            if Canvas_image:
                # Decode the base64-encoded image string
                # image_bytes = base64.b64decode(Canvas_image)
                # image = Image.open(BytesIO(image_bytes))

                # Allow the UI to update its layout
                self.update_idletasks()

                # Get the updated canvas size
                canvas_width = self.app.ui.canvas.winfo_width()
                canvas_height = self.app.ui.canvas.winfo_height()

                image = Image.open(io.BytesIO(Canvas_image))

                canvas_width = self.app.ui.canvas.winfo_width()
                canvas_height = self.app.ui.canvas.winfo_height()

                # Resize the image to match the canvas size
                photo = ImageTk.PhotoImage(image.resize(
                    (canvas_width, canvas_height), resample=Image.LANCZOS))
                self.app.ui.canvas.image = photo
                self.app.ui.canvas.create_image(
                    0, 0, anchor="nw", image=self.app.ui.canvas.image)

            else:
                print("Canvas_image is empty or invalid.")
        except Exception as e:
            print(f"Error in resizing or displaying the image: {e}")

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
                raise Exception(
                    "Unable to convert image to PNG - may be invalid image data")

            # Connect to MongoDB
            connection = MongoClient(
                "mongodb+srv://MoodCraftAi:MoodCraftAi@moodcraftai.uygfyac.mongodb.net/?retryWrites=true&w=majority")

            # Connect to the Database where the images will be stored.
            database = connection['moodCraftAI']
            fs = gridfs.GridFS(database)

            # Store the PNG image in GridFS
            image_id = fs.put(png_bytes, filename=filename,
                              collection='generated_images')

            # Update the movie_info with the image reference
            m = str(image_id)
            random_id_np = self.generate_random_id_np(10)

            # Create and insert the movie document
            generted_art = {
                "imdbId": random_id_np,
                "mood": [],
                "art": str(image_id),
                "reviews": []
            }
            movies_collection = database['Movies']
            movies_collection.insert_one(generted_art)


            settings_collection = database['settings']
            settings_collection.update_one(
            {"_id": ObjectId(document_id_to_update)},
            {"$set": 
             {"art": image_id,
              "device_id": device_id}
             }
        )

            print(
                f"Image '{filename}' and associated data saved to MongoDB successfully.")

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
        # Generate a random 4-digit number
        new_number = f"{random.randint(1000, 9999)}"

        device_id = new_number
        # Update the label
        self.number_label.configure(text="Device Id: " + new_number)
        # Schedule the next update after 2 days (2 days * 24 hours * 60 minutes * 60 seconds)
        threading.Timer(172800, self.update_number).start()
    
# Unussed Code----------------------------------------------------------------------------------------------------------------------------------------------------------

    # def generate_display_image_Deep_AI(self, emotion):
    #     global Canvas_image
    #     category = emotion
    #     # Replace with your actual API key
    #     api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDM5OTMwMTUsInVzZXJfaWQiOiI2NTkwZGViMzBjNWYzNWIzMThjOTI5NDYifQ.UPTjRrFnubgH9oiMwpTITMky_eG8vdnRnOUgtoKUkKs"

    #     url1 = "https://api.wizmodel.com/sdapi/v1/txt2img"

    #     payload = json.dumps({
    #         "prompt": category,
    #         "steps": 200
    #     })

    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': f'Bearer {api_key}'
    #     }
    #     response = requests.request(
    #         "POST", url1, headers=headers, data=payload)
    #     data = response.json()
    #     print(response.content)
    #     image_list = data.get("images", [])
    #     print(image_list)
    #     if image_list:
    #         image_string = image_list[0]
    #         Canvas_image = image_string

    #         # Decode the base64-encoded image string
    #         image_bytes = base64.b64decode(image_string)

    #         # Save the image to MongoDB using GridFS
    #         self.save_image_to_mongodb(image_bytes, self.entry.get())

    #         # Open the image
    #         image = Image.open(BytesIO(image_bytes))

    #         # Get the canvas size
    #         canvas_width = self.app.ui.canvas.winfo_width()
    #         canvas_height = self.app.ui.canvas.winfo_height()

    #         # Resize the image to match the canvas size
    #         photo = ImageTk.PhotoImage(image.resize(
    #             (canvas_width, canvas_height), resample=Image.LANCZOS))
    #         self.app.ui.canvas.image = photo
    #         self.app.ui.canvas.create_image(
    #             0, 1, anchor="nw", image=self.app.ui.canvas.image)
    #     else:
    #         print("Error: No images found in the response.")

        # ------------------------------------------------------------------------------------------------------------------------------ TAB 2
        # self.label_tab_2 = customtkinter.CTkLabel(
        #     self.tabview.tab("Settings"), text="CTkLabel on Tab 2")
        # self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        # ------------------------------------------------------------------------------------------------------------------------------ TAB 3

        # self.appearance_mode_label = customtkinter.CTkLabel(
        #     self.tabview.tab("Settings"), text="Appearance Mode:", anchor="w")
        # self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        # self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Settings"), values=[
        #                                                                "Light", "Dark", "System"],                                                                  command=self.change_appearance_mode_event)
        # self.appearance_mode_optionemenu.grid(
        #     row=6, column=0, padx=20, pady=(10, 10))
        # self.scaling_label = customtkinter.CTkLabel(
        #     self.tabview.tab("Settings"), text="UI Scaling:", anchor="w")
        # self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        # self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Settings"), values=["80%", "90%", "100%", "110%", "120%"],
        #                                                        command=self.change_scaling_event)
        # self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        # -------------------------------------------------------------------------------------------------------------------------------- TAB 3
