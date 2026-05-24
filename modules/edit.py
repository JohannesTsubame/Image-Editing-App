from PIL import ImageEnhance, ImageOps, ImageFilter
import customtkinter as ctk

def refresh_image(app):
    display = app.image.copy()
    display.thumbnail((1000, 700))

    app.ctk_image = ctk.CTkImage(
        light_image=display,
        dark_image=display,
        size=display.size
    )

    # app.image_label.configure(
    #     image=app.ctk_image,
    #     text=""
    # )

def brightness(app, value):
    enhancer = ImageEnhance.Brightness(app.original_img)
    app.image = enhancer.enhance(float(value))
    refresh_image(app)

def saturation(app, value):
    enhancer = ImageEnhance.Color(app.original_img)
    app.image = enhancer.enhance(float(value))
    refresh_image(app)

def contrast(app, value):
    enhancer = ImageEnhance.Contrast(app.original_img)
    app.image = enhancer.enhance(float(value))
    refresh_image(app)

def grayscale(app):
    app.image = ImageOps.grayscale(app.original_img)
    refresh_image(app)

def invert(app):
    app.image = ImageOps.invert(app.original_img.convert("RGB"))
    refresh_image(app)

def rgb(app, r, g, b):
    image = app.original_img.convert("RGB")
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            pr, pg, pb = pixels[x, y]

            pr = min(255, int(pr * r))
            pg = min(255, int(pg * g))
            pb = min(255, int(pb * b))

            pixels[x, y] = (pr, pg, pb)
    app.image = image

    refresh_image(app)

def scale(app, factor):
    width, height = app.original_img.size
    new_size = (int(width * factor), 
                int(height * factor))
    app.image = app.original_img.resize(new_size)

    refresh_image(app)

def crop(app, left, top, right, bottom):
    app.image = app.original_img.crop((left, top, right, bottom))
    refresh_image(app)

