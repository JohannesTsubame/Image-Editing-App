from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from modules import edit

def open_image(app):
    file_path = filedialog.askopenfilename(
        title="Open Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")])

    if not file_path:
        return

    app.current_image_path = file_path

    app.image = Image.open(file_path)

    app.original_img = app.image.copy()

    edit.initialize_effects(app)

    display_image = app.image.copy()
    display_image.thumbnail((1000, 700))

    app.tk_image = ImageTk.PhotoImage(display_image)

    app.canvas.delete("all")

    app.root.update_idletasks()

    canvas_width = app.canvas.winfo_width()
    canvas_height = app.canvas.winfo_height()

    app.canvas.create_image(
        canvas_width // 2,
        canvas_height // 2,
        anchor="center",
        image=app.tk_image
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
    