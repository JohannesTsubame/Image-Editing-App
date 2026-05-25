from PIL import ImageEnhance, ImageOps, ImageTk, Image
import numpy as np

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

def initialize_effects(app):
    app.effects = {
        "hue": 0,
        "saturation": 1.0,
        "brightness": 1.0,
        "contrast": 1.0,
        "grayscale": False,
        "grayscale_threshold": 128,
        "invert": False,
        "rotation": 0,
        "flip_horizontal": False,
        "flip_vertical": False,
        "resize": None,
        "crop": None,

        #Filters
        "blur": 0,
        "smooth": 0,
        "sharpen": 0,
        "edge_enhance": 0,
    }

def render_effects(app):
    if app.original_img is None:
        return

    image = app.original_img.copy().convert("RGB")

    hue_value = app.effects["hue"]

    if hue_value != 0:
        hsv_image = image.convert("HSV")
        hsv_array = np.array(hsv_image)

        h = hsv_array[:, :, 0].astype(np.int16)

        shift = int((hue_value / 360) * 255)

        h = (h + shift) % 255

        hsv_array[:, :, 0] = h.astype(np.uint8)

        image = Image.fromarray(
            hsv_array,
            "HSV"
        ).convert("RGB")

    image = ImageEnhance.Color(image).enhance(
        app.effects["saturation"]
    )
    image = ImageEnhance.Brightness(image).enhance(
        app.effects["brightness"]
    )
    image = ImageEnhance.Contrast(image).enhance(
        app.effects["contrast"]
    )

    if app.effects["grayscale"]:
        gray = image.convert("L")
        threshold = app.effects["grayscale_threshold"]
        bw = gray.point(
            lambda x: 255 if x > threshold else 0,
            mode="1"
        )
        image = bw.convert("RGB")

    if app.effects["invert"]:
        image = ImageOps.invert(image)

    rotation = app.effects["rotation"]

    if rotation != 0:
        image = image.rotate(
            -rotation,
            expand=True
        )

    if app.effects["flip_horizontal"]:
        image = ImageOps.mirror(image)

    if app.effects["flip_vertical"]:
        image = ImageOps.flip(image)

    resize = app.effects["resize"]

    if resize is not None:
        image = image.resize(resize)
    
    crop = app.effects["crop"]

    if crop is not None:
        image = image.crop(crop)
    app.image = image

    refresh_image(app)


def hue(app, value):
    app.effects["hue"] = value
    render_effects(app)


def saturation(app, value):
    app.effects["saturation"] = float(value)
    render_effects(app)


def brightness(app, value):
    app.effects["brightness"] = float(value)
    render_effects(app)


def contrast(app, value):
    app.effects["contrast"] = float(value)
    render_effects(app)


def grayscale(app, enabled):
    app.effects["grayscale"] = enabled
    render_effects(app)

def grayscale_threshold(app, value):
    app.effects["grayscale_threshold"] = int(value)

    if app.effects["grayscale"]:
        render_effects(app)

def remove_grayscale(app):
    app.effects["grayscale"] = False
    render_effects(app)


def invert(app):
    app.effects["invert"] = not app.effects["invert"]
    render_effects(app)


def rotate(app, value):
    app.effects["rotation"] = float(value)
    render_effects(app)


def rotate_left(app):
    app.effects["rotation"] -= 90
    render_effects(app)


def rotate_right(app):
    app.effects["rotation"] += 90
    render_effects(app)


def flip_horizontal(app):
    app.effects["flip_horizontal"] = (
        not app.effects["flip_horizontal"]
    )
    render_effects(app)


def flip_vertical(app):
    app.effects["flip_vertical"] = (
        not app.effects["flip_vertical"]
    )
    render_effects(app)


def resize(app, w, h):
    app.effects["resize"] = (int(w), int(h))
    render_effects(app)


def crop(app, left, top, right, bottom):
    app.effects["crop"] = (
        left,
        top,
        right,
        bottom
    )
    render_effects(app)


def apply_changes(app):
    app.original_img = app.image.copy()
    initialize_effects(app)