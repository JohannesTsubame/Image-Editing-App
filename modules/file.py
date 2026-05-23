import tkinter as tk

def load_img(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])

        if file_path:
            self.original_img = tk.Image.open(file_path)
            self.image = self.original_img.copy()
            self.display_img()
    
def display_img(self):
    if self.image == None:
        return
    
    aspect_ratio = self.image.width / self.image.height
    new_width = 600
    new_height = int(new_width/aspect_ratio)

    self.image_tk = tk.ImageTk.PhotoImage(self.image.resize((new_width, new_height), tk.Image.LANCZOS))
    self.image_label.config(image=self.image_tk)