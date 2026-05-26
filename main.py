import tkinter as tk
import customtkinter as ctk
from PIL import Image
from modules import file, edit, sidebar

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
        self.active_menu = None

        #History Var
        self.undo_stack = []
        self.redo_stack = []

        #Crop Var
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_rect = None

        self.create_header(root)
        self.create_menu(root)
        self.create_layout(root)

    def create_header(self, root):
        top_frame = ctk.CTkFrame(self.root, fg_color="#fafafa")
        top_frame.pack(fill="x", pady=10)

        self.label = ctk.CTkLabel(top_frame,
                                  text="Editing App Kelompok 10",
                                  fg_color="transparent",
                                  font=("Inter", 40, "bold"))
        self.label.pack(side="left", padx=15)

        team = {"Junaidi" : 3865,
                "Azizi" : 3874,
                "Pratama" : 3748,
                "Jonathan" : 3844,}

        for name, nim in team.items():
            self.kelompok = ctk.CTkLabel(
                top_frame,
                text=f"{name} ({nim})",
                font=("Inter", 20)
            )
            self.kelompok.pack(side="right", padx=10)

    def file_action(self, choice):
        self.file_menu.set("🗀 File")

        if choice == "Open":
            file.open_image(self)
        elif choice == "Save":
            file.save(self)

    def edit_action(self, choice):
        self.edit_menu.set("✎ Edit")

        self.active_menu = choice

        if choice == "Color":
            sidebar.color_sidebar(self)
        elif choice == "Reshape":
            sidebar.reshape_sidebar(self)

    def filter_action(self):
        self.active_menu = "Filter"
        sidebar.filter_sidebar(self)

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
        self.file_menu.set("🗀 File")
        self.file_menu.pack(side="left", pady=3, padx=5)

        #Edit
        edit_options = ["Color", "Reshape"]
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
        self.filter_btn = ctk.CTkButton(
            top_frame,
            text="⚙ Filter",
            command=self.filter_action,
            fg_color="#fafafa", 
            hover_color="#bababa",
            font=("Inter", 16),
            height=20,
            width=70,
            text_color="#000000")
        
        self.filter_btn.pack(side="left", pady=3, padx=5)

        filter_options = ["Blur",
                          "Sharpen",
                          "Enhance",
                          "Smooth"]

        buttons = [("⊕ Zoom In", edit.zoom_in),
                   ("⊖ Zoom Out", edit.zoom_out),
                   ("⟳ Reset", edit.reset),
                   ("↪ Redo", edit.redo),
                   ("↩ Undo", edit.undo),
                   ]

        for btn, command in buttons:
            if btn == "⟳ Reset":
                txt_clr = "#ef3030"
            else:
                txt_clr = "#000000"
            self.button = ctk.CTkButton(top_frame,
                                        text=btn,
                                        command=lambda cmd=command:
                                            cmd(self) if cmd else None,
                                        fg_color="#fafafa", 
                                        font=("Inter", 16),
                                        text_color=txt_clr,
                                        hover_color="#bababa",
                                        height=20,
                                        width=70,)
            self.button.pack(side="right", pady=3, padx=5)
    
    def create_layout(self, root):
        self.content_frame = ctk.CTkFrame(self.root,
                                          fg_color="#d3d3d3",
                                          corner_radius=0)

        self.content_frame.pack(fill="both", expand=True)

        #Image Area
        self.image_frame = ctk.CTkFrame(self.content_frame,
                                        fg_color="#cfcfcf",
                                        corner_radius=0)

        self.image_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            self.image_frame,

            bg="#cfcfcf",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        #Slider Bar
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

        #Upper Part
        self.sidebar_upper = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_upper.pack(fill="both", expand=True)

        # #Bottom Part
        # self.sidebar_bottom = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent", height=70)
        # self.sidebar_bottom.pack(side="bottom", fill="x")
        # self.sidebar_bottom.pack_propagate(False)

        # self.apply_btn = ctk.CTkButton(self.sidebar_bottom, 
        #                                text="Apply",
        #                                fg_color="#ff5353",
        #                                hover_color="#b33a3a",
        #                                font=("Inter", 20, "bold"),
        #                                height=40,
        #                                width=200,
        #                                corner_radius=20)
        # self.apply_btn.pack(pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ImageApp(root)
    root.mainloop()