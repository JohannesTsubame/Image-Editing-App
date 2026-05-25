from PIL import ImageEnhance, ImageOps, ImageFilter, ImageTk, Image
import customtkinter as ctk
import colorsys

def refresh_image(app): 
    if app.image is None:
        return

    display = app.image.copy()
    display.thumbnail((1000, 700))

    app.display_width = display.width
    app.display_height = display.height

    app.tk_image = ImageTk.PhotoImage(display)

    canvas_width = app.canvas.winfo_width()
    canvas_height = app.canvas.winfo_height()

    center_x = canvas_width // 2
    center_y = canvas_height // 2

    app.image_x = center_x - (display.width // 2)
    app.image_y = center_y - (display.height // 2)

    if not hasattr(app, "canvas_image"):
        app.canvas_image = app.canvas.create_image(
            center_x,
            center_y,
            anchor="center",
            image=app.tk_image
        )
    else:
        app.canvas.itemconfig(
            app.canvas_image,
            image=app.tk_image
        )

        app.canvas.coords(
            app.canvas_image,
            center_x,
            center_y
        )

def render_effects(app):
    if app.image is None:
        return
    image = app.original_img.copy()

    blur = app.effects["blur"]
    if blur > 0:
        image = image.filter(
            ImageFilter.GaussianBlur(radius=blur)
        )

    smooth = app.effects["smooth"]
    if smooth > 0:
        image = image.filter(ImageFilter.SMOOTH_MORE)

    sharpen = app.effects["sharpen"]
    if sharpen > 0:
        image = ImageEnhance.Sharpness(image).enhance(
            1 + sharpen
        )

    edge_enhance = app.effects["edge_enhance"]
    if edge_enhance > 0:
        image = image.filter(
            ImageFilter.EDGE_ENHANCE_MORE
        )

    app.image = image

    refresh_image(app)

def blur(app, value):
    app.effects["blur"] = float(value)
    render_effects(app)

def smooth(app, value):
    app.effects["smooth"] = int(value)
    render_effects(app)

def sharpen(app, value):
    app.effects["sharpen"] = float(value)
    render_effects(app)

def edge_enhance(app, value):
    app.effects["edge_enhance"] = int(value)
    render_effects(app)
