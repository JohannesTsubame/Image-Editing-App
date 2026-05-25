from modules import edit

def blur(app, value):
    app.effects["blur"] = float(value)
    edit.render_effects(app)

def smooth(app, value):
    app.effects["smooth"] = int(value)
    edit.render_effects(app)

def sharpen(app, value):
    app.effects["sharpen"] = float(value)
    edit.render_effects(app)

def edge_enhance(app, value):
    app.effects["edge_enhance"] = int(value)
    edit.render_effects(app)
