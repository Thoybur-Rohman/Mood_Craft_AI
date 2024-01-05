import tkinter as tk
from image_generator_ui import ImageGeneratorUI
from camera_handler import CameraHandler

class ImageGeneratorApp:
    def __init__(self):
        self.camera_handler = CameraHandler(self)
        self.ui = ImageGeneratorUI(self)

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = ImageGeneratorApp()
    app.run()
