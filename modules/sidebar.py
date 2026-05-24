import customtkinter as ctk
from modules import edit  

def refresh_sidebar(app):
    for widget in app.sidebar_upper.winfo_children():
        widget.destroy()

def update_slider(app, value, label, func):
    label.configure(text=f"{value*100-100:.0f}")

    func(app, value)

def color_sidebar(app):
    refresh_sidebar(app)

    title = ctk.CTkLabel(app.sidebar_upper,
                         text="Color",
                         font=("Inter", 24, "bold"))
    title.pack(pady=(20, 10))

    saturation_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    saturation_row.pack(fill="x", padx=20, pady=(0, 10))

    #Saturation
    saturation_name_label = ctk.CTkLabel(saturation_row, text="Saturation")
    saturation_name_label.pack(side="left")

    saturation_value_label = ctk.CTkLabel(saturation_row, text="0")
    saturation_value_label.pack(side="right")

    saturation_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=2,
                                     command=lambda value:
                                             update_slider(
                                                 app, 
                                                 value,
                                                 saturation_value_label,
                                                 edit.saturation),
                                     fg_color="#AAAAAA",
                                     progress_color="#732828",
                                     button_color="#ff5353",
                                     button_hover_color="#b33a3a")
    saturation_slide.set(1)
    saturation_slide.pack(fill="x", padx=20)

    #Brightness
    brightness_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    brightness_row.pack(fill="x", padx=20, pady=(20, 0))

    brightness_name_label = ctk.CTkLabel(brightness_row, text="Brightness")
    brightness_name_label.pack(side="left")

    brightness_value_label = ctk.CTkLabel(brightness_row, text="0")
    brightness_value_label.pack(side="right")

    brightness_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=2,
                                     command=lambda value:
                                             update_slider(
                                                 app, 
                                                 value,
                                                 brightness_value_label,
                                                 edit.brightness),
                                     fg_color="#AAAAAA",
                                     progress_color="#732828",
                                     button_color="#ff5353",
                                     button_hover_color="#b33a3a")
    brightness_slide.set(1)
    brightness_slide.pack(fill="x", padx=20)

    #Contrast
    contrast_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    contrast_row.pack(fill="x", padx=20, pady=(20, 0))

    contrast_name_label = ctk.CTkLabel(contrast_row, text="Contrast")
    contrast_name_label.pack(side="left")

    contrast_value_label = ctk.CTkLabel(contrast_row, text="0")
    contrast_value_label.pack(side="right")

    contrast_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=2,
                                     command=lambda value:
                                             update_slider(
                                                 app, 
                                                 value,
                                                 contrast_value_label,
                                                 edit.contrast),
                                     fg_color="#AAAAAA",
                                     progress_color="#732828",
                                     button_color="#ff5353",
                                     button_hover_color="#b33a3a")
    contrast_slide.set(1)
    contrast_slide.pack(fill="x", padx=20)

    #RGB
    RGB_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    RGB_row.pack(fill="x", padx=20, pady=(20, 0))
    