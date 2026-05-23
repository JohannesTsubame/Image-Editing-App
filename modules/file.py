from tkinter import filedialog, messagebox
from PIL import Image
import customtkinter as ctk


def open_image(app):

    file_path = filedialog.askopenfilename(
        title="Open Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")])

    if not file_path:
        return

    app.current_image_path = file_path

    app.image = Image.open(file_path)

    app.original_img = app.image.copy()

    display_image = app.image.copy()
    display_image.thumbnail((1000, 700))

    app.ctk_image = ctk.CTkImage(
        light_image=display_image,
        dark_image=display_image,
        size=display_image.size
    )

    app.image_label.configure(
        image=app.ctk_image,
        text=""
    )

def save(app):
    if not hasattr(app, "image"):
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png", 
        filetypes=[
            ("PNG Files", "*.png"), 
            ("JPEG Files", "*.jpg"), 
            ("BMP Files", "*.bmp"),
            ("All Files", "*.*")])
    
    if not file_path:
        return
    
    app.image.save(file_path)
    app.current_image_path = file_path
    