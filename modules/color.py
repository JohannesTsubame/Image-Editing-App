from PIL import ImageColor, ImageOps

def grey_scale(img):
    img_gray = ImageOps.grayscale(img)
    return img_gray

