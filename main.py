import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageColor, ImageOps
import modules.color as color
import modules.rotate as rotate

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editing App (Kelompok 10)")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#5a5a5a")
        
        self.original_img = None
        self.image = None
        self.image_tk = None

        self.create_widgets()

    def load_img(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])

        if file_path:
            self.original_img = Image.open(file_path)
            self.image = self.original_img.copy()
            self.display_img()

    def display_img(self):
        if self.image == None:
            return
        
        aspect_ratio = self.image.width / self.image.height
        new_width = 600
        new_height = int(new_width/aspect_ratio)

        self.image_tk = ImageTk.PhotoImage(self.image.resize((new_width, new_height), Image.LANCZOS))
        self.image_label.config(image=self.image_tk)

    def apply_filter(self, filter_type):
        if self.image:
            self.image = self.image.filter(filter_type)
            self.display_img()

    def grayscale(self):
        if self.image:
            self.image = color.grey_scale(self.image)
            self.display_img()
    
    def apply_rotate(self, value):
        if self.image:

            try:
                value = int(value)
            except ValueError:
                messagebox.showerror("Error", "Invalid rotation angle")
                return

            self.image = self.image.rotate(value, expand=True)
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
        self.load_btn = tk.Button(self.root, text="Load Image", command=self.load_img, bg="#007bff", fg="white", font=("Arial", 12), padx=10, pady=5)

        self.load_btn.pack(pady=10)

        self.image_label = tk.Label(self.root, bg="#5a5a5a")
        self.image_label.pack(pady=10)

        self.filters_frame = tk.Frame(self.root, bg="#5a5a5a")
        self.filters_frame.pack(pady=10)

        filters = [
            ("Blur", ImageFilter.BLUR),
            ("Countour", ImageFilter.CONTOUR),
            ("Edge Enchance", ImageFilter.EDGE_ENHANCE),
            ("Emboss", ImageFilter.EMBOSS),
            ("Sharpen", ImageFilter.SHARPEN),
            ("Smooth", ImageFilter.SMOOTH),
        ]

        for filter_name, filter_type in filters:
            tk.Button(self.filters_frame, 
                      text=filter_name,
                      command=lambda ft=filter_type: self.apply_filter(ft),
                      bg = "#e8e8e8", 
                      fg="black", 
                      font=("Arial", 10), 
                      padx=10, pady=5).pack(side="left", padx=10, pady=5)
        
        #Grayscale Button
        tk.Button(
                    self.filters_frame,
                    text="Grayscale",
                    command=self.grayscale,
                    bg="#e8e8e8",
                    fg="black",
                    font=("Arial", 10),
                    padx=10,
                    pady=5
                ).pack(side="left", padx=10, pady=5)
        
        #Rotate Button
        self.rotate_value = tk.Spinbox(root, from_=0, to=360)
        self.rotate_value.pack(side="left", padx=10, pady=5)
        tk.Button(
                    self.filters_frame,
                    text="Rotate",
                    command=self.apply_rotate(self.rotate_value.get()),
                    bg="#e8e8e8",
                    fg="black",
                    font=("Arial", 10),
                    padx=10,
                    pady=5
                ).pack(side="left", padx=10, pady=5)
        

            
        self.buttons_frame = tk.Frame(self.root, bg="#5a5a5a")
        self.buttons_frame.pack(pady=20)

        self.reset_button = tk.Button(self.buttons_frame, 
                                      text = "Reset Image", 
                                      command = self.reset, 
                                      bg = "#28a745", 
                                      fg="white", 
                                      font=("Arial", 10), 
                                      padx=10, 
                                      pady=5)
        self.reset_button.pack(side="left", padx=10)

        self.save_button = tk.Button(self.buttons_frame, 
                                      text = "Save Image", 
                                      command = self.save, 
                                      bg = "#28a745", 
                                      fg="white", 
                                      font=("Arial", 10), 
                                      padx=10, 
                                      pady=5)
        self.save_button.pack(side="left", padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
        

