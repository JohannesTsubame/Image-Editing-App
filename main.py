import tkinter as tk
import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editing App (Kelompok 10)")
        self.root.geometry("1920x1080")
        self.root.configure(fg_color="#fafafa")

        self.original_img = None
        self.image = None
        self.image_tk = None

        self.create_header(root)

        self.create_menu(root)

        self.create_layout(root)

    def create_header(self, root):
        top_frame = ctk.CTkFrame(self.root, fg_color="#fafafa")
        top_frame.pack(fill="x", pady=10)

        self.label = ctk.CTkLabel(top_frame,
                                  text="Editing App",
                                  fg_color="transparent",
                                  font=("Inter", 40, "bold"))
        self.label.pack(side="left", padx=15)

    def menu_selected(self, dropdown, placeholder):
        dropdown.set(placeholder)

    def create_menu(self, root):
        top_frame = ctk.CTkFrame(self.root, fg_color="#fafafa", border_color="#000000", border_width=1, corner_radius=0)
        top_frame.pack(fill="x")

        file_options = ["New",
                        "Open",
                        "Save",
                        "Save As"]
        
        self.file_menu = ctk.CTkOptionMenu(top_frame, 
                                           command=lambda placeholder:
                                                   self.menu_selected(self.file_menu, "📂 File"),
                                           values=file_options,
                                           fg_color="#fafafa", 
                                           button_color="#fafafa",
                                           button_hover_color="#bababa",
                                           font=("Inter", 16),
                                           height=20,
                                           width=70,
                                           text_color="#000000")
        self.file_menu.set("📂 File")
        self.file_menu.pack(side="left", pady=3, padx=5)

        edit_options = ["Color", 
                        "Crop", 
                        "Resize"]
        
        self.edit_menu = ctk.CTkOptionMenu(top_frame, 
                                           command=lambda placeholder:
                                                   self.menu_selected(self.edit_menu, "✎ Edit"),
                                           values=edit_options,
                                           fg_color="#fafafa", 
                                           button_color="#fafafa",
                                           button_hover_color="#bababa",
                                           font=("Inter", 16),
                                           height=20,
                                           width=70,
                                           text_color="#000000")
        self.edit_menu.set("✎ Edit")
        self.edit_menu.pack(side="left", pady=3, padx=5)

        filter_options = ["Blur",
                          "Sharpen",
                          "Contour",
                          "Enhance",
                          "Emboss",
                          "Smooth"]
        
        self.filter_menu = ctk.CTkOptionMenu(top_frame, 
                                           command=lambda placeholder:
                                                   self.menu_selected(self.filter_menu, "⚙ Filter"),
                                           values=filter_options,
                                           fg_color="#fafafa", 
                                           button_color="#fafafa",
                                           button_hover_color="#bababa",
                                           font=("Inter", 16),
                                           height=20,
                                           width=70,
                                           text_color="#000000")
        self.filter_menu.set("⚙ Filter")
        self.filter_menu.pack(side="left", pady=3, padx=5)


        buttons = ["⟳ Reset",
                   "↩️ Undo",
                   "↪️ Redo"]
        
        for btn in buttons:
            self.button = ctk.CTkButton(top_frame,
                                        text=btn,
                                        fg_color="#fafafa", 
                                        font=("Inter", 16),
                                        text_color="#000000",
                                        hover_color="#bababa",
                                        height=20,
                                        width=70,)
            self.button.pack(side="left", pady=3, padx=5)
    
    def create_layout(self, root):

        # MAIN CONTENT AREA
        self.content_frame = ctk.CTkFrame(self.root,
                                          fg_color="#d3d3d3",
                                          corner_radius=0)

        self.content_frame.pack(fill="both", expand=True)

        # LEFT IMAGE AREA
        self.image_frame = ctk.CTkFrame(self.content_frame,
                                        fg_color="#cfcfcf",
                                        corner_radius=0)

        self.image_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # RIGHT SIDEBAR
        self.sidebar_frame = ctk.CTkFrame(self.content_frame,
                                          width=250,
                                          fg_color="#efefef",
                                          corner_radius=0)
        self.sidebar_frame.pack(side="right" ,fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.border = ctk.CTkFrame(self.sidebar_frame,
                                   width=1,
                                   fg_color="black",
                                   corner_radius=0,
                                   border_color="#000000",
                                   border_width=1)

        self.border.pack(side="left", fill="y")

        self.label = ctk.CTkLabel(self.sidebar_frame,
                                  text="Placeholder",
                                  font=("Inter", 20))

        self.label.pack(pady=30)

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


if __name__ == "__main__":
    root = ctk.CTk()
    app = ImageApp(root)
    root.mainloop()