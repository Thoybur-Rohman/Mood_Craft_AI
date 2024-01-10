import qrcode
import tkinter as tk
from PIL import Image, ImageTk

# URL of your web application for MongoDB Key input
web_app_url = "https://github.com/Thoybur-Rohman?tab=overview&from=2023-01-01&to=2023-01-01"  # Change to the actual URL when deployed

# Generate QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(web_app_url)
qr.make(fit=True)

img = qr.make_image(fill='black', back_color='white')
img.save("mongodb_key_qr.png")

# Tkinter GUI
root = tk.Tk()
root.title("Settings QR Code")

image = Image.open("mongodb_key_qr.png")
photo = ImageTk.PhotoImage(image)

label = tk.Label(root, image=photo)
label.image = photo  # keep a reference!
label.pack()

root.mainloop()
