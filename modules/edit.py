from PIL import ImageEnhance, ImageOps, ImageTk, Image, ImageFilter
import numpy as np
import copy

def undo(app):
    if not app.undo_stack:
        return

    current_state = {
        "image": app.image.copy(),
        "original_img": app.original_img.copy(),
        "effects": copy.deepcopy(app.effects)
    }

    app.redo_stack.append(current_state)

    previous_state = app.undo_stack.pop()

    app.image = previous_state["image"]
    app.original_img = previous_state["original_img"]
    app.effects = previous_state["effects"]

    refresh_image(app)
    update_ui_sliders(app)

def redo(app):
    if not app.redo_stack:
        return

    current_state = {
        "image": app.image.copy(),
        "original_img": app.original_img.copy(),
        "effects": copy.deepcopy(app.effects)
    }

    app.undo_stack.append(current_state)

    next_state = app.redo_stack.pop()

    app.image = next_state["image"]
    app.original_img = next_state["original_img"]
    app.effects = next_state["effects"]

    refresh_image(app)
    update_ui_sliders(app)

def reset(app):
    if app.original_img is None:
        return

    save_state(app)

    app.image = app.original_img.copy()

    initialize_effects(app)

    refresh_image(app)
    update_ui_sliders(app)

def save_state(app):
    state = {
        "image": app.image.copy(),
        "original_img": app.original_img.copy(),
        "effects": copy.deepcopy(app.effects)
    }

    app.undo_stack.append(state)

    if len(app.undo_stack) > 20:
        app.undo_stack.pop(0)

    app.redo_stack.clear()

def refresh_image(app):
    if app.image is None:
        return

    display = app.image.copy()

    canvas_width = app.canvas.winfo_width()
    canvas_height = app.canvas.winfo_height()

    img_width = display.width
    img_height = display.height

    fit_scale = min(
        canvas_width / img_width,
        canvas_height / img_height,
        1
    )

    zoom = app.effects["zoom"]

    scale = fit_scale * zoom

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    display = display.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    app.display_width = display.width
    app.display_height = display.height

    app.tk_image = ImageTk.PhotoImage(display)

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
        "zoom" : 1.0,

        #Colors
        "hue": 0,
        "saturation": 1.0,
        "brightness": 1.0,
        "contrast": 1.0,
        "grayscale": False,
        "grayscale_threshold": 128,
        "invert": False,

        #Reshape
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

    #Filters
    blur = app.effects["blur"]
    if blur > 0:
        image = image.filter(
            ImageFilter.GaussianBlur(radius=blur)
        )

    smooth = app.effects["smooth"]
    if smooth > 0:
        image = image.filter(
            ImageFilter.SMOOTH_MORE
        )

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

def zoom_in(app):
    app.effects["zoom"] *= 1.1

    if app.effects["zoom"] > 5:
        app.effects["zoom"] = 5

    refresh_image(app)


def zoom_out(app):
    app.effects["zoom"] *= 0.9

    if app.effects["zoom"] < 0.1:
        app.effects["zoom"] = 0.1

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

def update_ui_sliders(app):
    if hasattr(app, "hue_slide"):
        app.hue_slide.set(app.effects["hue"])

    if hasattr(app, "saturation_slide"):
        app.saturation_slide.set(app.effects["saturation"])

    if hasattr(app, "brightness_slide"):
        app.brightness_slide.set(app.effects["brightness"])

    if hasattr(app, "contrast_slide"):
        app.contrast_slide.set(app.effects["contrast"])

    if hasattr(app, "grayscale_slide"):
        app.grayscale_slide.set(app.effects["grayscale_threshold"])

    if hasattr(app, "rotate_slide"):
        app.rotate_slide.set(app.effects["rotation"])

    if hasattr(app, "blur_slide"):
        app.blur_slide.set(app.effects["blur"])

    if hasattr(app, "smooth_slide"):
        app.smooth_slide.set(app.effects["smooth"])

    if hasattr(app, "sharpen_slide"):
        app.sharpen_slide.set(app.effects["sharpen"])

    if hasattr(app, "edge_enhance_slide"):
        app.edge_enhance_slide.set(app.effects["edge_enhance"])