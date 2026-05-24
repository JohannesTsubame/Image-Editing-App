import tkinter as tk
import customtkinter as ctk
from PIL import Image
from modules import file, edit

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
        self.image_ctk = None

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

    # def menu_selected(self, dropdown, placeholder):
    #     dropdown.set(placeholder)

    def file_action(self, choice):
        self.file_menu.set("📂 File")

        if choice == "Open":
            file.open_image(self)
        elif choice == "Save":
            file.save(self)

        self.file_menu.set("📂 File")  

    def edit_action(self, choice):
        self.edit_menu.set("✎ Edit")

    def filter_action(self, choice):
        self.filter_menu.set("⚙ Filter")


    def create_menu(self, root):
        top_frame = ctk.CTkFrame(self.root, fg_color="#fafafa", border_color="#000000", border_width=1, corner_radius=0)
        top_frame.pack(fill="x")


        #File
        file_options = ["Open",
                        "Save"]
        self.file_menu = ctk.CTkOptionMenu(top_frame, 
                                           command=self.file_action,
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

        #Edit
        edit_options = ["Color", 
                        "Crop", 
                        "Resize"]
        self.edit_menu = ctk.CTkOptionMenu(top_frame, 
                                           command=self.edit_action,
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

        #Filter
        filter_options = ["Blur",
                          "Sharpen",
                          "Contour",
                          "Enhance",
                          "Emboss",
                          "Smooth"]
        self.filter_menu = ctk.CTkOptionMenu(top_frame, 
                                             command=self.filter_action,
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
                   "↪️ Redo",
                   "⊕ Zoom In",
                   "⊖ Zoom Out"]
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

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text=""
        )

        self.image_label.pack(expand=True)

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


if __name__ == "__main__":
    root = ctk.CTk()
    app = ImageApp(root)
    root.mainloop()