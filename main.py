import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editing App (Kelompok 10)")
        self.root.geomatry("1920x1080")
        self.root.configure(bg="#e6f7ff")
        
        self.original_img = None
        self.image = None
        self.image_tk = None

    def load_img(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif")])

        if file_path:
            self.original_img = Image.open(file_path)
            self.image = self.original_img.copy()
            self.display_img()

    def display_img(self):
        if self.image == None:
            return
        
        aspect_ratio = self.image.width / self.image.height
        new_width = 600
        new_height = int(new_height/aspect_ratio)

        self.image_tk = ImageTk.PhotoImage(self.image.resize((new_width, new_height, Image.LANCZ0S)))
        self.image_label.config(image=self.image_tk)

    def apply_filter(self, filter_type):
        if self.image:
            self.image = self.image.filter(filter_type)
            self.display_img()

    def reset(self):
        if self.original_img:
            self.image = self.original_img.copy()
            self.display_img()

    def save(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")])

            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Succes", "Image Saved")

    def create_widgets(self):
        self.load_btn = tk.Button(self.root)