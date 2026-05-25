from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from modules import edit, sidebar

def open_image(app):
    file_path = filedialog.askopenfilename(
        title="Open Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")
        ]
    )

    if not file_path:
        return

    app.current_image_path = file_path

    app.original_img = Image.open(file_path).convert("RGB")

    app.image = app.original_img.copy()

    edit.initialize_effects(app)

    app.crop_start_x = 0
    app.crop_start_y = 0
    app.crop_rect = None

    app.canvas.delete("all")

    if hasattr(app, "canvas_image"):
        del app.canvas_image

    edit.refresh_image(app)

    if app.active_menu == "Color":
        sidebar.color_sidebar(app)

    elif app.active_menu == "Reshape":
        sidebar.reshape_sidebar(app)

    elif app.active_menu == "Filter":
        sidebar.filter_sidebar(app)

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
    