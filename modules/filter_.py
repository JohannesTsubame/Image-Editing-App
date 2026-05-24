from PIL import ImageEnhance, ImageOps, ImageFilter
import customtkinter as ctk
import colorsys

def refresh_image(app):
    display = app.image.copy()
    display.thumbnail((1000, 700))

    app.image_ctk = ctk.CTkImage(
        light_image=display,
        dark_image=display,
        size=display.size
    )

    app.tk_image = app.ctk_image._light_image
    app.canvas.delete("all")
    app.canvas.create_image(
        0,
        0,
        anchor="nw",
        image=app.tk_image
    )

def blur():
    ...

def smooth():
    ...

def sharpen():
    ...

def edge_enhance():
    ...
