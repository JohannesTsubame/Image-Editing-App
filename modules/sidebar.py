import customtkinter as ctk
from modules import edit, filter_

def refresh_sidebar(app):
    for widget in app.sidebar_upper.winfo_children():
        widget.destroy()

def update_slider(app, value, label, func):
    label.configure(text=f"{value*100-100:.0f}")

    func(app, value)

def update_slider_hue(app, value, label):
    label.configure(text=int(value))

    edit.hue(app, value)

def update_slider_rot(app, value, label, func):
    label.configure(text=f"{int(value)}°")

    func(app, value)

def update_slider_gray(app, value, label, func):
    label.configure(text=int(value))

    func(app, value)

def apply_effect(app, func):
    func(app)

def apply_resize(app, width, height):
    w, h = int(width), int(height)

    edit.resize(app, w, h)

def enable_crop(app):
    app.canvas.bind(
        "<Button-1>",
        lambda event:
            start_crop(app, event)
    )
    app.canvas.bind(
        "<B1-Motion>",
        lambda event:
            draw_crop(app, event)
    )
    app.canvas.bind(
        "<ButtonRelease-1>",
        lambda event:
            finish_crop(app, event)
    )

def start_crop(app, event):
    app.crop_start_x = event.x
    app.crop_start_y = event.y

    if app.crop_rect:
        app.canvas.delete(app.crop_rect)

    app.crop_rect = app.canvas.create_rectangle(
        event.x,
        event.y,
        event.x,
        event.y,
        outline="red",
        width=2
    )

def draw_crop(app, event):
    app.canvas.coords(
        app.crop_rect,
        app.crop_start_x,
        app.crop_start_y,
        event.x,
        event.y
    )

def finish_crop(app, event):
    x1 = app.crop_start_x
    y1 = app.crop_start_y

    x2 = event.x
    y2 = event.y

    left = min(x1, x2)
    top = min(y1, y2)

    right = max(x1, x2)
    bottom = max(y1, y2)

    display_w = app.display_width
    display_h = app.display_height

    original_w = app.image.width
    original_h = app.image.height

    scale_x = original_w / display_w
    scale_y = original_h / display_h

    left = int((left - app.image_x) * scale_x)
    top = int((top - app.image_y) * scale_y)

    right = int((right - app.image_x) * scale_x)
    bottom = int((bottom - app.image_y) * scale_y)

    left = max(0, left)
    top = max(0, top)

    right = min(original_w, right)
    bottom = min(original_h, bottom)

    edit.crop(
        app,
        left,
        top,
        right,
        bottom
    )

    app.canvas.delete(app.crop_rect)
    app.crop_rect = None

def color_sidebar(app):
    refresh_sidebar(app)

    title = ctk.CTkLabel(app.sidebar_upper,
                         text="Color",
                         font=("Inter", 30, "bold"))
    title.pack(pady=(20, 10))

    #Hue
    hue_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    hue_row.pack(fill="x", padx=20, pady=(0, 10))

    hue_name_label =  ctk.CTkLabel(hue_row, text="Hue")
    hue_name_label.pack(side="left")

    hue_value_label = ctk.CTkLabel(hue_row, text="0")
    hue_value_label.pack(side="right")

    hue_slide = ctk.CTkSlider(app.sidebar_upper, 
                              from_=-180,
                              to=180,
                              command=lambda value:
                                      update_slider_hue(app, value, hue_value_label),
                              fg_color="#AAAAAA",
                              progress_color="#732828",
                              button_color="#ff5353",
                              button_hover_color="#b33a3a")
    hue_slide.set(0)
    hue_slide.pack(fill="x", padx=20)

    #Saturation
    saturation_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    saturation_row.pack(fill="x", padx=20, pady=(20, 0))

    saturation_name_label = ctk.CTkLabel(saturation_row, text="Saturation")
    saturation_name_label.pack(side="left")

    saturation_value_label = ctk.CTkLabel(saturation_row, text="0")
    saturation_value_label.pack(side="right")

    saturation_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=2,
                                     command=lambda value:
                                             update_slider(app, value,saturation_value_label,edit.saturation),
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

    #Grayscale
    grayscale_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    grayscale_row.pack(fill="x", padx=20, pady=(20, 0))

    grayscale_name_label = ctk.CTkLabel(grayscale_row, text="grayscale")
    grayscale_name_label.pack(side="left")

    grayscale_value_label = ctk.CTkLabel(grayscale_row, text="0")
    grayscale_value_label.pack(side="right")

    grayscale_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=255,
                                     command=lambda value:
                                             update_slider_gray(
                                                 app, 
                                                 value,
                                                 grayscale_value_label,
                                                 edit.grayscale),
                                     fg_color="#AAAAAA",
                                     progress_color="#732828",
                                     button_color="#ff5353",
                                     button_hover_color="#b33a3a")
    grayscale_slide.set(128)
    grayscale_slide.pack(fill="x", padx=20)

    #Invert 
    invert_button = ctk.CTkButton(app.sidebar_upper,
                                  command=lambda: apply_effect(app, edit.invert),
                                  text="Invert",
                                  fg_color="#bb2e1e",
                                  hover_color="#474e9f",
                                  text_color="#FFFFFF")
    invert_button.pack(padx=20, pady=(20, 0), fill="x")

def reshape_sidebar(app):
    refresh_sidebar(app)

    title = ctk.CTkLabel(app.sidebar_upper,
                         text="Reshape",
                         font=("Inter", 30, "bold"))
    title.pack(pady=(20, 10))

    #Rotate
    rotate_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    rotate_row.pack(fill="x", padx=20, pady=(20, 0))

    rotate_name_label = ctk.CTkLabel(rotate_row, text="Rotate")
    rotate_name_label.pack(side="left")

    rotate_value_label = ctk.CTkLabel(rotate_row, text="0°")
    rotate_value_label.pack(side="right")

    rotate_slide = ctk.CTkSlider(app.sidebar_upper, 
                                     from_=0,
                                     to=360,
                                     command=lambda value:
                                             update_slider_rot(
                                                 app, 
                                                 value,
                                                 rotate_value_label,
                                                 edit.rotate),
                                     fg_color="#AAAAAA",
                                     progress_color="#732828",
                                     button_color="#ff5353",
                                     button_hover_color="#b33a3a")
    rotate_slide.set(0)
    rotate_slide.pack(fill="x", padx=20)

    rotate_r = ctk.CTkButton(app.sidebar_upper, 
                             text="Rotate Right     ⟳",
                             command=edit.rotate_right,
                             fg_color="#ff5353",
                             hover_color="#b33a3a")
    rotate_r.pack(padx=20, pady=5, fill="x")

    rotate_l = ctk.CTkButton(app.sidebar_upper, 
                             text="Rotate Left     ⟲",
                             command=edit.rotate_left,
                             fg_color="#ff5353",
                             hover_color="#b33a3a")
    rotate_l.pack(padx=20, pady=5, fill="x")

    flip_horizontal = ctk.CTkButton(app.sidebar_upper, 
                             text="Flip Horizontal    ⇋",
                             command=edit.flip_horizontal,
                             fg_color="#ff5353",
                             hover_color="#b33a3a")
    flip_horizontal.pack(padx=20, pady=5, fill="x")

    flip_vertical = ctk.CTkButton(app.sidebar_upper, 
                             text="Flip Vertical     ⇅",
                             command=edit.flip_vertical,
                             fg_color="#ff5353",
                             hover_color="#b33a3a")
    flip_vertical.pack(padx=20, pady=5, fill="x")

    #Resize 
    resize_label = ctk.CTkLabel(app.sidebar_upper, text="Resize")
    resize_label.pack(fill="x", padx=20, pady=(10, 5))

    width_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    width_row.pack(fill="x", padx=20)

    width_label = ctk.CTkLabel(width_row, text="Width   :")
    width_label.pack(padx=10, side="left")

    width_entry = ctk.CTkEntry(width_row)
    width_entry.pack(padx=10, side="right")

    height_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    height_row.pack(fill="x", padx=20)

    height_label = ctk.CTkLabel(height_row, text="Height :")
    height_label.pack(padx=10, pady=10, side="left")

    height_entry = ctk.CTkEntry(height_row)
    height_entry.pack(padx=10, pady=10, side="right")

    resize_btn = ctk.CTkButton(app.sidebar_upper, 
                               text="Resize",
                               command=lambda:
                               apply_resize(app, width_entry.get(), height_entry.get()),
                               fg_color="#ff5353",
                               hover_color="#b33a3a")
    resize_btn.pack(fill="x", padx=20)

    #Crop
    crop_btn = ctk.CTkButton(app.sidebar_upper, 
                             command=lambda:enable_crop(app),
                             text="Crop",
                             fg_color="#ff5353",
                             hover_color="#b33a3a")
    crop_btn.pack(fill="x", padx=20, pady=20)

def filter_sidebar(app):
    refresh_sidebar(app)

    title = ctk.CTkLabel(app.sidebar_upper,
                         text="Filter",
                         font=("Inter", 30, "bold"))
    title.pack(pady=(20, 10))

    #Blur
    blur_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    blur_row.pack(fill="x", padx=20, pady=(20, 0))

    blur_name_label = ctk.CTkLabel(blur_row, text="Blur")
    blur_name_label.pack(side="left")

    blur_value_label = ctk.CTkLabel(blur_row, text="0")
    blur_value_label.pack(side="right")

    blur_slide = ctk.CTkSlider(app.sidebar_upper, 
                               from_=0,
                               to=2,
                               command=lambda value:
                                       update_slider(
                                           app, 
                                           value,
                                           blur_value_label,
                                           filter_.blur),
                               fg_color="#AAAAAA",
                               progress_color="#732828",
                               button_color="#ff5353",
                               button_hover_color="#b33a3a")
    blur_slide.set(1)
    blur_slide.pack(fill="x", padx=20)

    #Smooth
    smooth_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    smooth_row.pack(fill="x", padx=20, pady=(20, 0))

    smooth_name_label = ctk.CTkLabel(smooth_row, text="Smooth")
    smooth_name_label.pack(side="left")

    smooth_value_label = ctk.CTkLabel(smooth_row, text="0")
    smooth_value_label.pack(side="right")

    smooth_slide = ctk.CTkSlider(app.sidebar_upper, 
                               from_=0,
                               to=2,
                               command=lambda value:
                                       update_slider(
                                           app, 
                                           value,
                                           smooth_value_label,
                                           filter_.smooth),
                               fg_color="#AAAAAA",
                               progress_color="#732828",
                               button_color="#ff5353",
                               button_hover_color="#b33a3a")
    smooth_slide.set(1)
    smooth_slide.pack(fill="x", padx=20)

    #Sharpen
    sharpen_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    sharpen_row.pack(fill="x", padx=20, pady=(20, 0))

    sharpen_name_label = ctk.CTkLabel(sharpen_row, text="Sharpen")
    sharpen_name_label.pack(side="left")

    sharpen_value_label = ctk.CTkLabel(sharpen_row, text="0")
    sharpen_value_label.pack(side="right")

    sharpen_slide = ctk.CTkSlider(app.sidebar_upper, 
                               from_=0,
                               to=2,
                               command=lambda value:
                                       update_slider(
                                           app, 
                                           value,
                                           sharpen_value_label,
                                           filter_.sharpen),
                               fg_color="#AAAAAA",
                               progress_color="#732828",
                               button_color="#ff5353",
                               button_hover_color="#b33a3a")
    sharpen_slide.set(1)
    sharpen_slide.pack(fill="x", padx=20)

    #Edge Enchance
    edge_enhance_row = ctk.CTkFrame(app.sidebar_upper, fg_color="transparent")
    edge_enhance_row.pack(fill="x", padx=20, pady=(20, 0))

    edge_enhance_name_label = ctk.CTkLabel(edge_enhance_row, text="Edge Enhance")
    edge_enhance_name_label.pack(side="left")

    edge_enhance_value_label = ctk.CTkLabel(edge_enhance_row, text="0")
    edge_enhance_value_label.pack(side="right")

    edge_enhance_slide = ctk.CTkSlider(app.sidebar_upper, 
                               from_=0,
                               to=2,
                               command=lambda value:
                                       update_slider(
                                           app, 
                                           value,
                                           edge_enhance_value_label,
                                           filter_.edge_enhance),
                               fg_color="#AAAAAA",
                               progress_color="#732828",
                               button_color="#ff5353",
                               button_hover_color="#b33a3a")
    edge_enhance_slide.set(1)
    edge_enhance_slide.pack(fill="x", padx=20)