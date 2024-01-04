import tkinter as tk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import customtkinter
from camera_handler import CameraHandler
import tkinter
import tkinter.messagebox
from PIL import Image
import json
import io
import base64
import json
from PIL import Image
from io import BytesIO
import json
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from pymongo import MongoClient
import gridfs
import base64

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")


class ImageGeneratorUI(customtkinter.CTk):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.title("AI Image Generator")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

         # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(
            self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=3, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="CustomTkinter", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.is_sidebar_visible = True

         # Add a button to toggle the sidebar
        self.toggle_sidebar_button = customtkinter.CTkButton(
            self, text="Toggle Sidebar", command=self.toggle_sidebar)
        self.toggle_sidebar_button.grid(row=3, column=3)  # Adjust the position as needed




         # create canvas
        self.canvas = customtkinter.CTkCanvas(self, width=512, height=512)
        self.canvas.grid(row=0, column=1, rowspan=3, sticky="nsew")  # Set rowspan to 3




        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=80)
        self.tabview.grid(row=0, column=0, padx=(
            20, 10), pady=(20, 0), sticky="nsew")
        self.tabview.add("MoodCraft AI")
        self.tabview.add("Generate")
        self.tabview.add("Settings")

        self.tabview.tab("MoodCraft AI").grid_columnconfigure(
            0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Generate").grid_columnconfigure(0, weight=1)

        self.tabview.tab("Settings").grid_columnconfigure(0, weight=1)

        # create main entry and button ------------------------------------------------------------------------------------------------ TAB 1 
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("MoodCraft AI"), text="select you generation type")
        self.label_tab_2.grid(row=0, column=0, padx=5, pady=0)

        self.sidebar_button_1 = customtkinter.CTkButton(
            self.tabview.tab("MoodCraft AI"), command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(
            self.tabview.tab("MoodCraft AI"), command=self.sidebar_button_event)
        
        
        # ----------------------------------------------------------------------------------------------------------------------------- TAB 2

        self.entry = customtkinter.CTkEntry(self.tabview.tab("Generate"),placeholder_text="Please enter a prompt",)
        self.entry.grid(row=0, column=0,pady=(5, 5), sticky="nsew")
        
        self.main_button_1 = customtkinter.CTkButton(
            self.tabview.tab("Generate"), fg_color="transparent", text="Generate" ,border_width=2, text_color=("gray10", "#DCE4EE"), command=self.generate_display_image_Deep_AI)
        self.main_button_1.grid(row=1, column=0, padx=(
            20, 20), pady=(5, 5), sticky="nsew")
         
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("Generate"), dynamic_resizing=False,
                                                        values=["Value 1", "Value 2", "Value Long Long Long"])
        self.optionmenu_1.grid(row=2, column=0, padx=20, pady=(20, 10))

        self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("Generate"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        self.combobox_1.grid(row=3, column=0, padx=20, pady=(10, 10))

        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Generate"), text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=4, column=0, padx=20, pady=(10, 10))
        # ------------------------------------------------------------------------------------------------------------------------------ TAB 2
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Settings"), text="CTkLabel on Tab 2")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        # ------------------------------------------------------------------------------------------------------------------------------ TAB 3 

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.tabview.tab("Settings"), text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Settings"), values=[
                                                                       "Light", "Dark", "System"],                                                                  command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(
            row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(
            self.tabview.tab("Settings"), text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Settings"), values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        #-------------------------------------------------------------------------------------------------------------------------------- TAB 3

        # set default values ---------------------------------------------------------------------------------------------------------------------
        self.sidebar_button_1.configure(
            text="Toogle Camera")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")




# ------------------------------------------------------------------------- METHODS ---------------------------------------------------------------------
    def toggle_sidebar(self):
        # Toggle the state
            self.is_sidebar_visible = not self.is_sidebar_visible

        # Show or hide the sidebar based on the state
            if self.is_sidebar_visible:
                self.sidebar_frame.grid()
                self.canvas.grid(columnspan = 1)
                  # Restore the original configuration
            else:
                self.sidebar_frame.grid_remove()
                self.canvas.grid(columnspan = 3)  # Allocate the space to the canvas
 
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(
            text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        self.app.camera_handler.toggle_camera()

    def generate(self):
        user_prompt = self.entry.get()
        category = f"{user_prompt} emotion"
        self.app.camera_handler.display_image(category)

    def generate_display_image_Deep_AI(self, emotion):
        category = emotion
        # Replace with your actual API key
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDM5OTMwMTUsInVzZXJfaWQiOiI2NTkwZGViMzBjNWYzNWIzMThjOTI5NDYifQ.UPTjRrFnubgH9oiMwpTITMky_eG8vdnRnOUgtoKUkKs"

        url1 = "https://api.wizmodel.com/sdapi/v1/txt2img"

        payload = json.dumps({
            "prompt": category,
            "steps": 200
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        response = requests.request(
            "POST", url1, headers=headers, data=payload)
        data = response.json()
        print(response.content)
        image_list = data.get("images", [])
        print(image_list)
        if image_list:
            image_string = image_list[0]

            # Decode the base64-encoded image string
            image_bytes = base64.b64decode(image_string)

            # Save the image to MongoDB using GridFS
            self.save_image_to_mongodb(image_bytes, self.entry.get())

            # Open the image
            image = Image.open(BytesIO(image_bytes))

            # Get the canvas size
            canvas_width = self.app.ui.canvas.winfo_width()
            canvas_height = self.app.ui.canvas.winfo_height()

            # Resize the image to match the canvas size
            photo = ImageTk.PhotoImage(image.resize(
                (canvas_width, canvas_height), resample=Image.LANCZOS))
            self.app.ui.canvas.image = photo
            self.app.ui.canvas.create_image(
                0, 0, anchor="nw", image=self.app.ui.canvas.image)
        else:
            print("Error: No images found in the response.")

    def save_image_to_mongodb(self, image_bytes, filename):
        try:
            # Connect to the server with the hostName and portNumber.
            connection = MongoClient(
                "mongodb+srv://new_years:AuMBHvQmKC5XFtTl@cluster0.6swbq.mongodb.net/")

            # Connect to the Database where the images will be stored.
            database = connection['DB_NAME']

            # Create an object of GridFs for the above database.
            fs = gridfs.GridFS(database)

            # Now store/put the image via GridFs object.
            fs.put(image_bytes, filename=filename)
            print(f"Image '{filename}' saved to MongoDB successfully.")

        except Exception as e:
            print(f"Error saving image to MongoDB: {str(e)}")
