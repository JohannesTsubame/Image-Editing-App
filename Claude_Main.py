"""
PhotoCraft - A Photoshop Clone built with Python, CustomTkinter & Pillow
Features: Layers, Drawing Tools, Filters, Adjustments, Selection, Text, Undo/Redo
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont, ImageOps
import numpy as np
import os
import sys
import copy
import math

# ─── Theme ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Constants ───────────────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 900, 650
BG_COLOR = "#1a1a2e"
PANEL_COLOR = "#16213e"
TOOLBAR_COLOR = "#0f3460"
ACCENT = "#e94560"
ACCENT2 = "#533483"
TEXT_COLOR = "#eaeaea"


# ─── Layer ───────────────────────────────────────────────────────────────────
class Layer:
    def __init__(self, name, width, height, mode="RGBA"):
        self.name = name
        self.visible = True
        self.opacity = 1.0
        self.blend_mode = "normal"
        self.image = Image.new(mode, (width, height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def refresh_draw(self):
        self.draw = ImageDraw.Draw(self.image)


# ─── History ─────────────────────────────────────────────────────────────────
class History:
    def __init__(self, max_steps=30):
        self.states = []
        self.current = -1
        self.max_steps = max_steps

    def push(self, layers):
        # Remove redo history
        self.states = self.states[: self.current + 1]
        snapshot = [(l.name, l.visible, l.opacity, l.image.copy()) for l in layers]
        self.states.append(snapshot)
        if len(self.states) > self.max_steps:
            self.states.pop(0)
        self.current = len(self.states) - 1

    def undo(self):
        if self.current > 0:
            self.current -= 1
            return self.states[self.current]
        return None

    def redo(self):
        if self.current < len(self.states) - 1:
            self.current += 1
            return self.states[self.current]
        return None


# ─── Main App ────────────────────────────────────────────────────────────────
class PhotoCraft(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PhotoCraft – Professional Image Editor")
        self.geometry("1400x900")
        self.minsize(1200, 750)
        self.configure(fg_color=BG_COLOR)

        # State
        self.layers: list[Layer] = []
        self.active_layer_idx = 0
        self.canvas_width = CANVAS_W
        self.canvas_height = CANVAS_H
        self.zoom = 1.0
        self.tool = "brush"
        self.primary_color = (0, 0, 0, 255)
        self.secondary_color = (255, 255, 255, 255)
        self.brush_size = 10
        self.eraser_size = 20
        self.shape_fill = False
        self.text_font_size = 24
        self.last_x = self.last_y = None
        self.drawing = False
        self.selection_rect = None
        self.sel_start = None
        self.history = History()
        self.pan_start = None
        self.canvas_offset = [0, 0]
        self.eyedropper_active = False

        # Build UI
        self._build_menu()
        self._build_ui()
        self._new_document()
        self.bind_shortcuts()

    # ─── Menu ────────────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self, bg=PANEL_COLOR, fg=TEXT_COLOR,
                          activebackground=TOOLBAR_COLOR, activeforeground=ACCENT,
                          bd=0, relief="flat")
        self.configure(menu=menubar)

        # File
        file_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                            activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New…          Ctrl+N", command=self.new_document_dialog)
        file_menu.add_command(label="Open…         Ctrl+O", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Save As…      Ctrl+S", command=self.save_image)
        file_menu.add_command(label="Export Flat…  Ctrl+E", command=self.export_flat)
        file_menu.add_separator()
        file_menu.add_command(label="Quit           Ctrl+Q", command=self.quit)

        # Edit
        edit_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                            activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo  Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo  Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Layer", command=self.clear_layer)
        edit_menu.add_command(label="Fill with Primary Color", command=self.fill_layer)
        edit_menu.add_separator()
        edit_menu.add_command(label="Flatten Image", command=self.flatten_image)

        # Image
        image_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                             activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="Image", menu=image_menu)
        adj_menu = tk.Menu(image_menu, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                           activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        image_menu.add_cascade(label="Adjustments", menu=adj_menu)
        adj_menu.add_command(label="Brightness/Contrast…", command=self.adjust_brightness_contrast)
        adj_menu.add_command(label="Hue/Saturation…", command=self.adjust_hue_saturation)
        adj_menu.add_command(label="Color Balance…", command=self.adjust_color_balance)
        adj_menu.add_command(label="Levels…", command=self.adjust_levels)
        adj_menu.add_separator()
        adj_menu.add_command(label="Grayscale", command=self.to_grayscale)
        adj_menu.add_command(label="Invert", command=self.invert_colors)
        adj_menu.add_command(label="Sepia Tone", command=self.sepia)
        image_menu.add_separator()
        image_menu.add_command(label="Flip Horizontal", command=lambda: self.flip("h"))
        image_menu.add_command(label="Flip Vertical", command=lambda: self.flip("v"))
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_layer(90))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_layer(-90))

        # Filter
        filter_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                              activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="Filter", menu=filter_menu)
        blur_menu = tk.Menu(filter_menu, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                            activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        filter_menu.add_cascade(label="Blur", menu=blur_menu)
        blur_menu.add_command(label="Gaussian Blur…", command=self.gaussian_blur)
        blur_menu.add_command(label="Box Blur…", command=self.box_blur)
        blur_menu.add_command(label="Motion Blur…", command=self.motion_blur)
        sharp_menu = tk.Menu(filter_menu, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                             activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        filter_menu.add_cascade(label="Sharpen", menu=sharp_menu)
        sharp_menu.add_command(label="Sharpen", command=lambda: self.apply_filter(ImageFilter.SHARPEN))
        sharp_menu.add_command(label="Unsharp Mask…", command=self.unsharp_mask)
        filter_menu.add_separator()
        filter_menu.add_command(label="Emboss", command=lambda: self.apply_filter(ImageFilter.EMBOSS))
        filter_menu.add_command(label="Edge Detect", command=lambda: self.apply_filter(ImageFilter.FIND_EDGES))
        filter_menu.add_command(label="Smooth", command=lambda: self.apply_filter(ImageFilter.SMOOTH_MORE))
        filter_menu.add_command(label="Contour", command=lambda: self.apply_filter(ImageFilter.CONTOUR))
        filter_menu.add_separator()
        filter_menu.add_command(label="Pixelate…", command=self.pixelate)
        filter_menu.add_command(label="Vignette", command=self.vignette)
        filter_menu.add_command(label="Noise…", command=self.add_noise)

        # Layer
        layer_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                             activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="Layer", menu=layer_menu)
        layer_menu.add_command(label="New Layer", command=self.add_layer)
        layer_menu.add_command(label="Duplicate Layer", command=self.duplicate_layer)
        layer_menu.add_command(label="Delete Layer", command=self.delete_layer)
        layer_menu.add_separator()
        layer_menu.add_command(label="Merge Down", command=self.merge_down)
        layer_menu.add_command(label="Flatten All Layers", command=self.flatten_image)

        # View
        view_menu = tk.Menu(menubar, tearoff=0, bg=PANEL_COLOR, fg=TEXT_COLOR,
                            activebackground=TOOLBAR_COLOR, activeforeground=ACCENT)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In   Ctrl++", command=lambda: self.zoom_canvas(1.2))
        view_menu.add_command(label="Zoom Out  Ctrl+-", command=lambda: self.zoom_canvas(0.8))
        view_menu.add_command(label="Fit to Window", command=self.zoom_fit)
        view_menu.add_command(label="100%", command=self.zoom_100)

    # ─── UI Layout ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Top toolbar
        self.top_bar = ctk.CTkFrame(self, height=46, fg_color=TOOLBAR_COLOR, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self._build_top_bar()

        # Main content
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Left toolbar
        self.left_bar = ctk.CTkFrame(self.main_frame, width=52, fg_color=PANEL_COLOR, corner_radius=0)
        self.left_bar.pack(fill="y", side="left")
        self.left_bar.pack_propagate(False)
        self._build_left_toolbar()

        # Right panels
        self.right_panel = ctk.CTkFrame(self.main_frame, width=230, fg_color=PANEL_COLOR, corner_radius=0)
        self.right_panel.pack(fill="y", side="right")
        self.right_panel.pack_propagate(False)
        self._build_right_panel()

        # Canvas area (center)
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=0)
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="#2a2a2a",
            cursor="crosshair",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Canvas bindings
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_drag)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Status bar
        self.status_bar = ctk.CTkFrame(self, height=26, fg_color="#0a0a1a", corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", text_color="#888",
                                          font=ctk.CTkFont(size=11))
        self.status_label.pack(side="left", padx=10)
        self.coord_label = ctk.CTkLabel(self.status_bar, text="X: 0  Y: 0", text_color="#888",
                                         font=ctk.CTkFont(size=11))
        self.coord_label.pack(side="right", padx=10)

    def _build_top_bar(self):
        # Logo
        logo = ctk.CTkLabel(self.top_bar, text=" ✦ PhotoCraft",
                             font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
                             text_color=ACCENT)
        logo.pack(side="left", padx=14)

        sep = ctk.CTkFrame(self.top_bar, width=1, height=30, fg_color="#ffffff")
        sep.pack(side="left", padx=8)

        # Context options (dynamic per tool) – we'll show brush size, opacity
        ctk.CTkLabel(self.top_bar, text="Size:", text_color=TEXT_COLOR,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 2))
        self.size_var = ctk.StringVar(value="10")
        self.size_entry = ctk.CTkEntry(self.top_bar, width=48, textvariable=self.size_var,
                                        font=ctk.CTkFont(size=12))
        self.size_entry.pack(side="left", padx=2)
        self.size_entry.bind("<Return>", self._update_brush_size)

        ctk.CTkLabel(self.top_bar, text="Opacity:", text_color=TEXT_COLOR,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(12, 2))
        self.opacity_slider = ctk.CTkSlider(self.top_bar, from_=0, to=100, width=100,
                                             button_color=ACCENT, progress_color=ACCENT2)
        self.opacity_slider.set(100)
        self.opacity_slider.pack(side="left", padx=4)

        self.opacity_label = ctk.CTkLabel(self.top_bar, text="100%", text_color=TEXT_COLOR,
                                           font=ctk.CTkFont(size=12), width=36)
        self.opacity_label.pack(side="left")
        self.opacity_slider.configure(command=self._on_opacity_change)

        sep2 = ctk.CTkFrame(self.top_bar, width=1, height=30, fg_color="#ffffff")
        sep2.pack(side="left", padx=8)

        # Fill toggle for shapes
        self.fill_var = tk.BooleanVar(value=False)
        self.fill_check = ctk.CTkCheckBox(self.top_bar, text="Fill Shape", variable=self.fill_var,
                                           text_color=TEXT_COLOR, font=ctk.CTkFont(size=12),
                                           fg_color=ACCENT, hover_color=ACCENT2)
        self.fill_check.pack(side="left", padx=8)

        sep3 = ctk.CTkFrame(self.top_bar, width=1, height=30, fg_color="#ffffff")
        sep3.pack(side="left", padx=8)

        # Font size for text
        ctk.CTkLabel(self.top_bar, text="Font Size:", text_color=TEXT_COLOR,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(4, 2))
        self.font_size_var = ctk.StringVar(value="24")
        self.font_entry = ctk.CTkEntry(self.top_bar, width=44, textvariable=self.font_size_var,
                                        font=ctk.CTkFont(size=12))
        self.font_entry.pack(side="left", padx=2)

        # Zoom display
        self.zoom_label = ctk.CTkLabel(self.top_bar, text="100%", text_color=ACCENT,
                                        font=ctk.CTkFont(size=12, weight="bold"))
        self.zoom_label.pack(side="right", padx=14)
        ctk.CTkLabel(self.top_bar, text="Zoom:", text_color=TEXT_COLOR,
                     font=ctk.CTkFont(size=12)).pack(side="right", padx=2)

    def _build_left_toolbar(self):
        tools = [
            ("✏️", "brush", "Brush (B)"),
            ("⬜", "eraser", "Eraser (E)"),
            ("🪣", "fill", "Fill/Paint Bucket (G)"),
            ("💧", "eyedropper", "Eyedropper (I)"),
            ("🔲", "rect", "Rectangle (R)"),
            ("⭕", "ellipse", "Ellipse (O)"),
            ("📏", "line", "Line (L)"),
            ("✂️", "selection", "Selection (S)"),
            ("T", "text", "Text (T)"),
            ("✋", "pan", "Pan (Space)"),
            ("🔍", "zoom_in", "Zoom In (+)"),
            ("🔍", "zoom_out", "Zoom Out (-)"),
        ]
        self.tool_buttons = {}
        pad = 4
        for emoji, tool_name, tooltip in tools:
            btn = ctk.CTkButton(
                self.left_bar,
                text=emoji if tool_name != "zoom_out" else "🔎",
                width=44, height=38,
                font=ctk.CTkFont(size=16),
                fg_color=TOOLBAR_COLOR if tool_name != self.tool else ACCENT,
                hover_color=ACCENT2,
                command=lambda t=tool_name: self.set_tool(t),
                corner_radius=6,
            )
            btn.pack(pady=(pad, 0), padx=4)
            self.tool_buttons[tool_name] = btn

        # Color swatches
        sep = ctk.CTkFrame(self.left_bar, height=1, fg_color="#ffffff")
        sep.pack(fill="x", padx=4, pady=8)

        color_frame = ctk.CTkFrame(self.left_bar, fg_color="transparent")
        color_frame.pack(pady=4, padx=4)

        # Secondary (background) color
        self.sec_color_btn = tk.Button(
            color_frame, bg="#ffffff", width=3, height=1,
            relief="flat", bd=2, cursor="hand2",
            command=self.pick_secondary_color
        )
        self.sec_color_btn.place(x=16, y=16) if False else None
        self.sec_color_btn.grid(row=0, column=1, padx=1, pady=1, sticky="se")

        # Primary (foreground) color
        self.pri_color_btn = tk.Button(
            color_frame, bg="#000000", width=3, height=1,
            relief="flat", bd=2, cursor="hand2",
            command=self.pick_primary_color
        )
        self.pri_color_btn.grid(row=0, column=0, padx=1, pady=1, sticky="nw")

        # Swap button
        swap_btn = ctk.CTkButton(color_frame, text="⇄", width=24, height=18,
                                  font=ctk.CTkFont(size=11),
                                  fg_color=TOOLBAR_COLOR, hover_color=ACCENT2,
                                  command=self.swap_colors)
        swap_btn.grid(row=1, column=0, columnspan=2, pady=(2, 0))

        # Reset
        reset_btn = ctk.CTkButton(color_frame, text="↺", width=24, height=18,
                                   font=ctk.CTkFont(size=11),
                                   fg_color=TOOLBAR_COLOR, hover_color=ACCENT2,
                                   command=self.reset_colors)
        reset_btn.grid(row=2, column=0, columnspan=2, pady=(2, 0))

    def _build_right_panel(self):
        # Layers section
        layers_header = ctk.CTkFrame(self.right_panel, fg_color=TOOLBAR_COLOR, height=32, corner_radius=0)
        layers_header.pack(fill="x")
        layers_header.pack_propagate(False)
        ctk.CTkLabel(layers_header, text="LAYERS", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=ACCENT).pack(side="left", padx=8)

        # Layer buttons
        layer_btns = ctk.CTkFrame(self.right_panel, fg_color=PANEL_COLOR, height=32, corner_radius=0)
        layer_btns.pack(fill="x")
        for text, cmd in [("＋", self.add_layer), ("🗑", self.delete_layer),
                          ("⧉", self.duplicate_layer), ("↓", self.merge_down)]:
            ctk.CTkButton(layer_btns, text=text, width=44, height=28,
                          font=ctk.CTkFont(size=14),
                          fg_color=TOOLBAR_COLOR, hover_color=ACCENT2,
                          command=cmd).pack(side="left", padx=2, pady=2)

        # Layer list
        self.layer_list_frame = ctk.CTkScrollableFrame(
            self.right_panel, height=200, fg_color="#0e1428", corner_radius=0
        )
        self.layer_list_frame.pack(fill="x")

        sep = ctk.CTkFrame(self.right_panel, height=1, fg_color=TOOLBAR_COLOR)
        sep.pack(fill="x", pady=4)

        # Opacity for active layer
        ctk.CTkLabel(self.right_panel, text="Layer Opacity",
                     font=ctk.CTkFont(size=11), text_color="#aaa").pack(anchor="w", padx=8)
        self.layer_opacity_slider = ctk.CTkSlider(
            self.right_panel, from_=0, to=100,
            button_color=ACCENT, progress_color=ACCENT2,
            command=self._on_layer_opacity_change
        )
        self.layer_opacity_slider.set(100)
        self.layer_opacity_slider.pack(fill="x", padx=8, pady=(2, 8))

        sep2 = ctk.CTkFrame(self.right_panel, height=1, fg_color=TOOLBAR_COLOR)
        sep2.pack(fill="x", pady=4)

        # Histogram / Info
        info_header = ctk.CTkFrame(self.right_panel, fg_color=TOOLBAR_COLOR, height=28, corner_radius=0)
        info_header.pack(fill="x")
        ctk.CTkLabel(info_header, text="INFO", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=ACCENT).pack(side="left", padx=8)

        self.info_canvas = tk.Canvas(self.right_panel, height=80, bg="#0e1428",
                                      highlightthickness=0)
        self.info_canvas.pack(fill="x", padx=4, pady=4)

        self.info_label = ctk.CTkLabel(self.right_panel, text="Size: 0×0\nLayers: 0",
                                        font=ctk.CTkFont(size=11), text_color="#aaa",
                                        justify="left")
        self.info_label.pack(anchor="w", padx=8, pady=4)

        sep3 = ctk.CTkFrame(self.right_panel, height=1, fg_color=TOOLBAR_COLOR)
        sep3.pack(fill="x", pady=4)

        # Quick filters
        qf_header = ctk.CTkFrame(self.right_panel, fg_color=TOOLBAR_COLOR, height=28, corner_radius=0)
        qf_header.pack(fill="x")
        ctk.CTkLabel(qf_header, text="QUICK FILTERS", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=ACCENT).pack(side="left", padx=8)

        qf_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        qf_frame.pack(fill="x", padx=4, pady=4)

        quick_filters = [
            ("Blur", lambda: self.apply_filter(ImageFilter.GaussianBlur(2))),
            ("Sharpen", lambda: self.apply_filter(ImageFilter.SHARPEN)),
            ("Emboss", lambda: self.apply_filter(ImageFilter.EMBOSS)),
            ("Edges", lambda: self.apply_filter(ImageFilter.FIND_EDGES)),
            ("Grayscale", self.to_grayscale),
            ("Invert", self.invert_colors),
            ("Sepia", self.sepia),
            ("Vignette", self.vignette),
        ]
        for i, (label, cmd) in enumerate(quick_filters):
            btn = ctk.CTkButton(qf_frame, text=label, width=100, height=26,
                                font=ctk.CTkFont(size=11),
                                fg_color=TOOLBAR_COLOR, hover_color=ACCENT,
                                command=cmd)
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")
        qf_frame.columnconfigure(0, weight=1)
        qf_frame.columnconfigure(1, weight=1)

    # ─── Document ────────────────────────────────────────────────────────
    def _new_document(self, w=CANVAS_W, h=CANVAS_H):
        self.canvas_width = w
        self.canvas_height = h
        self.layers = []
        self.active_layer_idx = 0

        # Background layer
        bg = Layer("Background", w, h)
        bg.image.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)))
        bg.refresh_draw()
        self.layers.append(bg)

        # Default layer
        layer1 = Layer("Layer 1", w, h)
        self.layers.append(layer1)
        self.active_layer_idx = 1

        self.history = History()
        self.history.push(self.layers)
        self.canvas_offset = [0, 0]
        self.zoom = 1.0
        self._update_layer_panel()
        self.render()
        self.update_info()

    def new_document_dialog(self):
        dlg = NewDocDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            w, h = dlg.result
            self._new_document(w, h)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif"),
                       ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
            self._new_document(img.width, img.height)
            self.layers[0].image.paste(img)
            self.layers[0].refresh_draw()
            self.history.push(self.layers)
            self.render()
            self.update_info()
            self.status("Opened: " + os.path.basename(path))
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def save_image(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            flat = self._flatten()
            ext = os.path.splitext(path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                flat = flat.convert("RGB")
            flat.save(path)
            self.status("Saved: " + os.path.basename(path))
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def export_flat(self):
        self.save_image()

    # ─── Rendering ───────────────────────────────────────────────────────
    def _flatten(self) -> Image.Image:
        result = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 255))
        for layer in self.layers:
            if layer.visible:
                overlay = layer.image.copy()
                if layer.opacity < 1.0:
                    r, g, b, a = overlay.split()
                    a = a.point(lambda x: int(x * layer.opacity))
                    overlay = Image.merge("RGBA", (r, g, b, a))
                result = Image.alpha_composite(result, overlay)
        return result

    def render(self):
        flat = self._flatten()
        w = int(self.canvas_width * self.zoom)
        h = int(self.canvas_height * self.zoom)
        display = flat.resize((w, h), Image.LANCZOS if self.zoom < 1 else Image.NEAREST)

        self._tk_image = ctk.CTkImage(display, size=(w, h))

        self.canvas.delete("image")
        cx = self.canvas.winfo_width() // 2 + self.canvas_offset[0]
        cy = self.canvas.winfo_height() // 2 + self.canvas_offset[1]
        self.canvas.create_image(cx, cy, image=self._tk_image._light_image, anchor="center", tags="image")
        self.canvas.tag_lower("image")

        # Draw selection rect
        if self.selection_rect:
            x1, y1, x2, y2 = self.selection_rect
            self.canvas.delete("selection")
            sx1, sy1 = self._layer_to_canvas(x1, y1)
            sx2, sy2 = self._layer_to_canvas(x2, y2)
            self.canvas.create_rectangle(sx1, sy1, sx2, sy2,
                                          outline=ACCENT, width=2, dash=(6, 4),
                                          tags="selection")

    def _layer_to_canvas(self, lx, ly):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        cx = cw // 2 + self.canvas_offset[0] - int(self.canvas_width * self.zoom) // 2
        cy = ch // 2 + self.canvas_offset[1] - int(self.canvas_height * self.zoom) // 2
        return cx + int(lx * self.zoom), cy + int(ly * self.zoom)

    def _canvas_to_layer(self, sx, sy):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        cx = cw // 2 + self.canvas_offset[0] - int(self.canvas_width * self.zoom) // 2
        cy = ch // 2 + self.canvas_offset[1] - int(self.canvas_height * self.zoom) // 2
        lx = (sx - cx) / self.zoom
        ly = (sy - cy) / self.zoom
        return lx, ly

    # ─── Tools ───────────────────────────────────────────────────────────
    def on_mouse_down(self, event):
        lx, ly = self._canvas_to_layer(event.x, event.y)
        if self.tool == "pan":
            self.pan_start = (event.x, event.y)
            return
        if self.tool == "eyedropper":
            self._pick_color(lx, ly)
            return
        if self.tool == "zoom_in":
            self.zoom_canvas(1.25)
            return
        if self.tool == "zoom_out":
            self.zoom_canvas(0.8)
            return
        if self.tool == "fill":
            self._push_history()
            self._flood_fill(int(lx), int(ly))
            self.render()
            return
        if self.tool == "text":
            self._add_text(int(lx), int(ly))
            return
        if self.tool == "selection":
            self.sel_start = (int(lx), int(ly))
            self.selection_rect = None
            return

        self.drawing = True
        self.last_x, self.last_y = lx, ly
        self._push_history()

        if self.tool in ("rect", "ellipse", "line"):
            self._shape_start = (int(lx), int(ly))
            self._shape_preview = self.layers[self.active_layer_idx].image.copy()

    def on_mouse_drag(self, event):
        lx, ly = self._canvas_to_layer(event.x, event.y)

        if self.tool == "pan" and self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas_offset[0] += dx
            self.canvas_offset[1] += dy
            self.pan_start = (event.x, event.y)
            self.render()
            return

        if self.tool == "selection" and self.sel_start:
            x1, y1 = self.sel_start
            x2, y2 = int(lx), int(ly)
            self.selection_rect = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            self.render()
            return

        if not self.drawing:
            return

        layer = self.layers[self.active_layer_idx]
        opacity_val = self.opacity_slider.get() / 100.0
        size = self.brush_size

        if self.tool == "brush":
            if self.last_x is not None:
                color = (*self.primary_color[:3], int(self.primary_color[3] * opacity_val))
                self._draw_line(layer, self.last_x, self.last_y, lx, ly, size, color)
        elif self.tool == "eraser":
            if self.last_x is not None:
                self._draw_line(layer, self.last_x, self.last_y, lx, ly,
                                self.eraser_size, (0, 0, 0, 0), erase=True)
        elif self.tool in ("rect", "ellipse", "line"):
            # Preview
            layer.image = self._shape_preview.copy()
            layer.refresh_draw()
            x1, y1 = self._shape_start
            x2, y2 = int(lx), int(ly)
            fill_c = (*self.primary_color[:3], int(255 * opacity_val)) if self.fill_var.get() else None
            outline_c = (*self.primary_color[:3], int(255 * opacity_val))
            lw = max(1, int(size / 4))
            if self.tool == "rect":
                layer.draw.rectangle([x1, y1, x2, y2], fill=fill_c, outline=outline_c, width=lw)
            elif self.tool == "ellipse":
                layer.draw.ellipse([x1, y1, x2, y2], fill=fill_c, outline=outline_c, width=lw)
            elif self.tool == "line":
                layer.draw.line([x1, y1, x2, y2], fill=outline_c, width=lw)

        self.last_x, self.last_y = lx, ly
        self.render()

    def on_mouse_up(self, event):
        self.drawing = False
        self.last_x = self.last_y = None
        self.pan_start = None
        if self.tool in ("rect", "ellipse", "line"):
            self._shape_preview = None

    def on_mouse_move(self, event):
        lx, ly = self._canvas_to_layer(event.x, event.y)
        xi, yi = int(lx), int(ly)
        self.coord_label.configure(text=f"X: {xi}  Y: {yi}")

    def _draw_line(self, layer, x1, y1, x2, y2, size, color, erase=False):
        if erase:
            # Draw transparent circle
            overlay = Image.new("RGBA", layer.image.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(overlay)
            r = size // 2
            for t in np.linspace(0, 1, max(1, int(math.hypot(x2 - x1, y2 - y1))) + 1):
                cx = int(x1 + (x2 - x1) * t)
                cy = int(y1 + (y2 - y1) * t)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, 255))
            # Apply erase mask
            r_ch, g_ch, b_ch, a_ch = layer.image.split()
            erase_mask = overlay.split()[3]
            a_ch = Image.fromarray(
                np.clip(np.array(a_ch).astype(int) - np.array(erase_mask).astype(int), 0, 255).astype(np.uint8)
            )
            layer.image = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))
        else:
            r = size // 2
            steps = max(1, int(math.hypot(x2 - x1, y2 - y1)))
            for i in range(steps + 1):
                t = i / steps
                cx = int(x1 + (x2 - x1) * t)
                cy = int(y1 + (y2 - y1) * t)
                layer.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        layer.refresh_draw()

    def _flood_fill(self, x, y, tolerance=30):
        layer = self.layers[self.active_layer_idx]
        img_arr = np.array(layer.image, dtype=np.int32)
        h, w = img_arr.shape[:2]
        if x < 0 or x >= w or y < 0 or y >= h:
            return
        target = img_arr[y, x].copy()
        fill = np.array(self.primary_color, dtype=np.int32)

        def color_match(c):
            return np.all(np.abs(c - target) <= tolerance)

        visited = np.zeros((h, w), dtype=bool)
        stack = [(x, y)]
        while stack:
            px, py = stack.pop()
            if px < 0 or px >= w or py < 0 or py >= h:
                continue
            if visited[py, px]:
                continue
            if not color_match(img_arr[py, px]):
                continue
            visited[py, px] = True
            img_arr[py, px] = fill
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                stack.append((px + dx, py + dy))
        layer.image = Image.fromarray(img_arr.astype(np.uint8), "RGBA")
        layer.refresh_draw()

    def _pick_color(self, lx, ly):
        xi, yi = int(lx), int(ly)
        flat = self._flatten()
        if 0 <= xi < flat.width and 0 <= yi < flat.height:
            pixel = flat.getpixel((xi, yi))
            self.primary_color = pixel[:4] if len(pixel) >= 4 else (*pixel[:3], 255)
            self._update_color_buttons()
            self.status(f"Eyedropper: RGBA{self.primary_color}")

    def _add_text(self, x, y):
        text = simpledialog.askstring("Add Text", "Enter text:", parent=self)
        if not text:
            return
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        try:
            size = int(self.font_size_var.get())
        except Exception:
            size = 24
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except Exception:
            font = ImageFont.load_default()
        color = (*self.primary_color[:3], int(self.primary_color[3] * self.opacity_slider.get() / 100))
        layer.draw.text((x, y), text, fill=color, font=font)
        layer.refresh_draw()
        self.render()

    # ─── Filters & Adjustments ───────────────────────────────────────────
    def apply_filter(self, filt):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        layer.image = layer.image.filter(filt)
        layer.refresh_draw()
        self.render()
        self.status("Filter applied")

    def gaussian_blur(self):
        r = simpledialog.askfloat("Gaussian Blur", "Radius (0.1–20):", initialvalue=2.0,
                                   minvalue=0.1, maxvalue=20, parent=self)
        if r:
            self.apply_filter(ImageFilter.GaussianBlur(r))

    def box_blur(self):
        r = simpledialog.askfloat("Box Blur", "Radius:", initialvalue=2.0, parent=self)
        if r:
            self.apply_filter(ImageFilter.BoxBlur(r))

    def motion_blur(self):
        size = simpledialog.askinteger("Motion Blur", "Size (3–50):", initialvalue=10,
                                        minvalue=3, maxvalue=50, parent=self)
        if size:
            kernel_data = [0] * (size * size)
            for i in range(size):
                kernel_data[i * size + i] = 1
            self.apply_filter(ImageFilter.Kernel((size, size), kernel_data, scale=size))

    def unsharp_mask(self):
        r = simpledialog.askfloat("Unsharp Mask", "Radius:", initialvalue=2.0, parent=self)
        if r:
            self.apply_filter(ImageFilter.UnsharpMask(radius=r, percent=150, threshold=3))

    def pixelate(self):
        block = simpledialog.askinteger("Pixelate", "Block size (2–50):", initialvalue=10,
                                         minvalue=2, maxvalue=50, parent=self)
        if not block:
            return
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        w, h = layer.image.size
        small = layer.image.resize((max(1, w // block), max(1, h // block)), Image.NEAREST)
        layer.image = small.resize((w, h), Image.NEAREST)
        layer.refresh_draw()
        self.render()

    def vignette(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        w, h = layer.image.size
        vign = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vign)
        steps = 60
        for i in range(steps):
            alpha = int(180 * (i / steps) ** 2)
            margin = int((steps - i) * max(w, h) / (2 * steps))
            draw.ellipse([margin, margin, w - margin, h - margin],
                         outline=(0, 0, 0, alpha), width=max(1, max(w, h) // (2 * steps)))
        vign_blur = vign.filter(ImageFilter.GaussianBlur(max(w, h) // 10))
        layer.image = Image.alpha_composite(layer.image, vign_blur)
        layer.refresh_draw()
        self.render()

    def add_noise(self):
        amount = simpledialog.askinteger("Add Noise", "Amount (1–100):", initialvalue=20,
                                          minvalue=1, maxvalue=100, parent=self)
        if not amount:
            return
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        arr = np.array(layer.image, dtype=np.float32)
        noise = np.random.normal(0, amount, arr[:, :, :3].shape)
        arr[:, :, :3] = np.clip(arr[:, :, :3] + noise, 0, 255)
        layer.image = Image.fromarray(arr.astype(np.uint8), "RGBA")
        layer.refresh_draw()
        self.render()

    def to_grayscale(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        gray = ImageOps.grayscale(layer.image)
        layer.image = gray.convert("RGBA")
        layer.refresh_draw()
        self.render()

    def invert_colors(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        r, g, b, a = layer.image.split()
        inv = Image.merge("RGBA", (ImageOps.invert(r), ImageOps.invert(g),
                                    ImageOps.invert(b), a))
        layer.image = inv
        layer.refresh_draw()
        self.render()

    def sepia(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        arr = np.array(layer.image.convert("RGB"), dtype=np.float32)
        r = np.clip(arr[:, :, 0] * 0.393 + arr[:, :, 1] * 0.769 + arr[:, :, 2] * 0.189, 0, 255)
        g = np.clip(arr[:, :, 0] * 0.349 + arr[:, :, 1] * 0.686 + arr[:, :, 2] * 0.168, 0, 255)
        b = np.clip(arr[:, :, 0] * 0.272 + arr[:, :, 1] * 0.534 + arr[:, :, 2] * 0.131, 0, 255)
        sepia_arr = np.stack([r, g, b], axis=2).astype(np.uint8)
        _, _, _, alpha = layer.image.split()
        result = Image.fromarray(sepia_arr, "RGB").convert("RGBA")
        result.putalpha(alpha)
        layer.image = result
        layer.refresh_draw()
        self.render()

    def flip(self, direction):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        if direction == "h":
            layer.image = ImageOps.mirror(layer.image)
        else:
            layer.image = ImageOps.flip(layer.image)
        layer.refresh_draw()
        self.render()

    def rotate_layer(self, angle):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        layer.image = layer.image.rotate(-angle, expand=False)
        layer.refresh_draw()
        self.render()

    def adjust_brightness_contrast(self):
        AdjustDialog(self, "Brightness / Contrast",
                     [("Brightness", -100, 100, 0), ("Contrast", -100, 100, 0)],
                     self._apply_brightness_contrast)

    def _apply_brightness_contrast(self, vals):
        b, c = vals
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        enh_b = ImageEnhance.Brightness(layer.image)
        img = enh_b.enhance(1 + b / 100)
        enh_c = ImageEnhance.Contrast(img)
        layer.image = enh_c.enhance(1 + c / 100)
        layer.refresh_draw()
        self.render()

    def adjust_hue_saturation(self):
        AdjustDialog(self, "Hue / Saturation",
                     [("Saturation", -100, 100, 0), ("Color", 0, 100, 50)],
                     self._apply_saturation)

    def _apply_saturation(self, vals):
        s, _ = vals
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        enh = ImageEnhance.Color(layer.image)
        layer.image = enh.enhance(max(0, 1 + s / 100))
        layer.refresh_draw()
        self.render()

    def adjust_color_balance(self):
        AdjustDialog(self, "Color Balance",
                     [("Red", -100, 100, 0), ("Green", -100, 100, 0), ("Blue", -100, 100, 0)],
                     self._apply_color_balance)

    def _apply_color_balance(self, vals):
        rv, gv, bv = vals
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        arr = np.array(layer.image, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + rv * 2.55, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + gv * 2.55, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + bv * 2.55, 0, 255)
        layer.image = Image.fromarray(arr.astype(np.uint8), "RGBA")
        layer.refresh_draw()
        self.render()

    def adjust_levels(self):
        AdjustDialog(self, "Levels",
                     [("Black Point", 0, 255, 0), ("White Point", 0, 255, 255),
                      ("Gamma", 10, 300, 100)],
                     self._apply_levels)

    def _apply_levels(self, vals):
        black, white, gamma_int = vals
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        gamma = gamma_int / 100.0
        arr = np.array(layer.image, dtype=np.float32)
        scale = white - black
        if scale == 0:
            return
        arr[:, :, :3] = np.clip((arr[:, :, :3] - black) / scale * 255, 0, 255)
        arr[:, :, :3] = np.clip(255 * (arr[:, :, :3] / 255) ** (1 / gamma), 0, 255)
        layer.image = Image.fromarray(arr.astype(np.uint8), "RGBA")
        layer.refresh_draw()
        self.render()

    # ─── Layers Management ───────────────────────────────────────────────
    def add_layer(self):
        name = f"Layer {len(self.layers)}"
        layer = Layer(name, self.canvas_width, self.canvas_height)
        self.layers.append(layer)
        self.active_layer_idx = len(self.layers) - 1
        self._push_history()
        self._update_layer_panel()
        self.render()

    def delete_layer(self):
        if len(self.layers) <= 1:
            messagebox.showwarning("Delete Layer", "Cannot delete the last layer.")
            return
        del self.layers[self.active_layer_idx]
        self.active_layer_idx = max(0, self.active_layer_idx - 1)
        self._push_history()
        self._update_layer_panel()
        self.render()

    def duplicate_layer(self):
        src = self.layers[self.active_layer_idx]
        new_layer = Layer(src.name + " copy", self.canvas_width, self.canvas_height)
        new_layer.image = src.image.copy()
        new_layer.refresh_draw()
        new_layer.visible = src.visible
        new_layer.opacity = src.opacity
        self.layers.insert(self.active_layer_idx + 1, new_layer)
        self.active_layer_idx += 1
        self._push_history()
        self._update_layer_panel()
        self.render()

    def merge_down(self):
        if self.active_layer_idx == 0:
            messagebox.showwarning("Merge Down", "Cannot merge below the bottom layer.")
            return
        top = self.layers[self.active_layer_idx]
        bottom = self.layers[self.active_layer_idx - 1]
        merged = Image.alpha_composite(bottom.image, top.image)
        bottom.image = merged
        bottom.refresh_draw()
        del self.layers[self.active_layer_idx]
        self.active_layer_idx -= 1
        self._push_history()
        self._update_layer_panel()
        self.render()

    def flatten_image(self):
        flat = self._flatten()
        bg = Layer("Background", self.canvas_width, self.canvas_height)
        bg.image = flat
        bg.refresh_draw()
        self.layers = [bg]
        self.active_layer_idx = 0
        self._push_history()
        self._update_layer_panel()
        self.render()

    def clear_layer(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        layer.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        layer.refresh_draw()
        self.render()

    def fill_layer(self):
        self._push_history()
        layer = self.layers[self.active_layer_idx]
        layer.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), self.primary_color)
        layer.refresh_draw()
        self.render()

    def _update_layer_panel(self):
        for w in self.layer_list_frame.winfo_children():
            w.destroy()
        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            row = ctk.CTkFrame(self.layer_list_frame,
                               fg_color=ACCENT2 if i == self.active_layer_idx else "#1a1f35",
                               corner_radius=4)
            row.pack(fill="x", pady=1, padx=2)

            # Visibility toggle
            vis_text = "👁" if layer.visible else "🚫"
            vis_btn = ctk.CTkButton(row, text=vis_text, width=28, height=28,
                                     font=ctk.CTkFont(size=12),
                                     fg_color="transparent", hover_color=TOOLBAR_COLOR,
                                     command=lambda idx=i: self._toggle_layer_visibility(idx))
            vis_btn.pack(side="left", padx=2)

            # Thumbnail
            thumb_size = (28, 28)
            thumb = layer.image.copy().resize(thumb_size, Image.LANCZOS)
            # Checkerboard bg
            checker = Image.new("RGBA", thumb_size, (200, 200, 200, 255))
            for ty in range(0, thumb_size[1], 7):
                for tx in range(0, thumb_size[0], 7):
                    if (tx // 7 + ty // 7) % 2 == 0:
                        for py in range(ty, min(ty + 7, thumb_size[1])):
                            for px in range(tx, min(tx + 7, thumb_size[0])):
                                checker.putpixel((px, py), (150, 150, 150, 255))
            combined = Image.alpha_composite(checker, thumb)
            tk_thumb = ctk.CTkImage(combined, size=thumb_size)
            thumb_lbl = ctk.CTkLabel(row, image=tk_thumb, text="")
            thumb_lbl.image = tk_thumb
            thumb_lbl.pack(side="left", padx=2)

            # Name
            name_lbl = ctk.CTkLabel(row, text=layer.name,
                                     font=ctk.CTkFont(size=11),
                                     text_color=TEXT_COLOR, anchor="w")
            name_lbl.pack(side="left", padx=4, fill="x", expand=True)

            # Make clickable
            for widget in [row, name_lbl]:
                widget.bind("<Button-1>", lambda e, idx=i: self._select_layer(idx))

        self.update_info()

    def _select_layer(self, idx):
        self.active_layer_idx = idx
        self.layer_opacity_slider.set(self.layers[idx].opacity * 100)
        self._update_layer_panel()

    def _toggle_layer_visibility(self, idx):
        self.layers[idx].visible = not self.layers[idx].visible
        self._update_layer_panel()
        self.render()

    def _on_layer_opacity_change(self, val):
        self.layers[self.active_layer_idx].opacity = val / 100
        self.render()

    # ─── Colors ──────────────────────────────────────────────────────────
    def pick_primary_color(self):
        color = colorchooser.askcolor(
            color=f"#{self.primary_color[0]:02x}{self.primary_color[1]:02x}{self.primary_color[2]:02x}",
            parent=self, title="Primary Color"
        )
        if color[0]:
            r, g, b = [int(c) for c in color[0]]
            self.primary_color = (r, g, b, 255)
            self._update_color_buttons()

    def pick_secondary_color(self):
        color = colorchooser.askcolor(
            color=f"#{self.secondary_color[0]:02x}{self.secondary_color[1]:02x}{self.secondary_color[2]:02x}",
            parent=self, title="Secondary Color"
        )
        if color[0]:
            r, g, b = [int(c) for c in color[0]]
            self.secondary_color = (r, g, b, 255)
            self._update_color_buttons()

    def swap_colors(self):
        self.primary_color, self.secondary_color = self.secondary_color, self.primary_color
        self._update_color_buttons()

    def reset_colors(self):
        self.primary_color = (0, 0, 0, 255)
        self.secondary_color = (255, 255, 255, 255)
        self._update_color_buttons()

    def _update_color_buttons(self):
        r, g, b = self.primary_color[:3]
        self.pri_color_btn.configure(bg=f"#{r:02x}{g:02x}{b:02x}")
        r, g, b = self.secondary_color[:3]
        self.sec_color_btn.configure(bg=f"#{r:02x}{g:02x}{b:02x}")

    # ─── Zoom & Pan ──────────────────────────────────────────────────────
    def zoom_canvas(self, factor):
        self.zoom = max(0.1, min(16.0, self.zoom * factor))
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self.render()

    def zoom_fit(self):
        cw = self.canvas.winfo_width() or 900
        ch = self.canvas.winfo_height() or 650
        zx = cw / self.canvas_width
        zy = ch / self.canvas_height
        self.zoom = min(zx, zy) * 0.9
        self.canvas_offset = [0, 0]
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self.render()

    def zoom_100(self):
        self.zoom = 1.0
        self.canvas_offset = [0, 0]
        self.zoom_label.configure(text="100%")
        self.render()

    def on_pan_start(self, event):
        self.pan_start = (event.x, event.y)

    def on_pan_drag(self, event):
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas_offset[0] += dx
            self.canvas_offset[1] += dy
            self.pan_start = (event.x, event.y)
            self.render()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_canvas(1.1)
        else:
            self.zoom_canvas(0.9)

    def on_canvas_configure(self, event):
        self.render()

    # ─── Tool Selection ──────────────────────────────────────────────────
    def set_tool(self, tool):
        self.tool = tool
        for name, btn in self.tool_buttons.items():
            btn.configure(fg_color=ACCENT if name == tool else TOOLBAR_COLOR)
        # Update brush size from entry
        self._update_brush_size()
        # Set cursor
        cursors = {
            "brush": "pencil", "eraser": "circle", "fill": "spraycan",
            "eyedropper": "crosshair", "rect": "crosshair", "ellipse": "crosshair",
            "line": "crosshair", "selection": "crosshair", "text": "xterm",
            "pan": "fleur", "zoom_in": "plus", "zoom_out": "plus"
        }
        self.canvas.configure(cursor=cursors.get(tool, "crosshair"))
        self.status(f"Tool: {tool.replace('_', ' ').title()}")

    def _update_brush_size(self, event=None):
        try:
            s = int(self.size_var.get())
            self.brush_size = max(1, min(200, s))
            self.eraser_size = self.brush_size * 2
        except Exception:
            pass

    def _on_opacity_change(self, val):
        self.opacity_label.configure(text=f"{int(val)}%")

    # ─── Undo/Redo ───────────────────────────────────────────────────────
    def _push_history(self):
        self.history.push(self.layers)

    def undo(self):
        state = self.history.undo()
        if state:
            self._restore_state(state)
        else:
            self.status("Nothing to undo")

    def redo(self):
        state = self.history.redo()
        if state:
            self._restore_state(state)
        else:
            self.status("Nothing to redo")

    def _restore_state(self, state):
        self.layers = []
        for name, vis, opacity, img in state:
            l = Layer(name, img.width, img.height)
            l.image = img.copy()
            l.visible = vis
            l.opacity = opacity
            l.refresh_draw()
            self.layers.append(l)
        self.active_layer_idx = min(self.active_layer_idx, len(self.layers) - 1)
        self._update_layer_panel()
        self.render()

    # ─── Shortcuts ───────────────────────────────────────────────────────
    def bind_shortcuts(self):
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-s>", lambda e: self.save_image())
        self.bind("<Control-o>", lambda e: self.open_image())
        self.bind("<Control-n>", lambda e: self.new_document_dialog())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-equal>", lambda e: self.zoom_canvas(1.2))
        self.bind("<Control-minus>", lambda e: self.zoom_canvas(0.8))
        self.bind("<Control-0>", lambda e: self.zoom_fit())
        self.bind("<Control-1>", lambda e: self.zoom_100())
        self.bind("b", lambda e: self.set_tool("brush"))
        self.bind("e", lambda e: self.set_tool("eraser"))
        self.bind("g", lambda e: self.set_tool("fill"))
        self.bind("i", lambda e: self.set_tool("eyedropper"))
        self.bind("r", lambda e: self.set_tool("rect"))
        self.bind("o", lambda e: self.set_tool("ellipse"))
        self.bind("l", lambda e: self.set_tool("line"))
        self.bind("s", lambda e: self.set_tool("selection"))
        self.bind("t", lambda e: self.set_tool("text"))
        self.bind("<space>", lambda e: self.set_tool("pan"))

    # ─── Info / Status ───────────────────────────────────────────────────
    def update_info(self):
        self.info_label.configure(
            text=f"Size: {self.canvas_width}×{self.canvas_height}\n"
                 f"Layers: {len(self.layers)}\n"
                 f"Active: {self.layers[self.active_layer_idx].name if self.layers else '—'}"
        )
        # Draw simple histogram
        self._draw_histogram()

    def _draw_histogram(self):
        ic = self.info_canvas
        ic.delete("all")
        w, h = 222, 80
        if not self.layers:
            return
        try:
            layer = self.layers[self.active_layer_idx]
            arr = np.array(layer.image.convert("L"), dtype=np.float32).flatten()
            hist, _ = np.histogram(arr, bins=64, range=(0, 256))
            if hist.max() == 0:
                return
            hist_norm = hist / hist.max()
            bar_w = w / 64
            for i, val in enumerate(hist_norm):
                x0 = i * bar_w
                y0 = h - int(val * (h - 4)) - 2
                ic.create_rectangle(x0, y0, x0 + bar_w - 1, h - 2,
                                     fill="#4a7fcb", outline="")
        except Exception:
            pass

    def status(self, msg: str):
        self.status_label.configure(text=msg)


# ─── New Document Dialog ──────────────────────────────────────────────────────
class NewDocDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Document")
        self.geometry("340x230")
        self.resizable(False, False)
        self.result = None
        self.configure(fg_color=BG_COLOR)
        self.grab_set()

        ctk.CTkLabel(self, text="New Document", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=ACCENT).pack(pady=(20, 10))

        frame = ctk.CTkFrame(self, fg_color=PANEL_COLOR)
        frame.pack(padx=20, fill="x")

        ctk.CTkLabel(frame, text="Width:", text_color=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.w_var = ctk.StringVar(value="900")
        ctk.CTkEntry(frame, textvariable=self.w_var, width=100).grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(frame, text="Height:", text_color=TEXT_COLOR).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.h_var = ctk.StringVar(value="650")
        ctk.CTkEntry(frame, textvariable=self.h_var, width=100).grid(row=1, column=1, padx=10, pady=8)

        # Presets
        presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        presets_frame.pack(pady=6)
        for label, w, h in [("HD", 1280, 720), ("Full HD", 1920, 1080), ("Square", 1000, 1000)]:
            ctk.CTkButton(presets_frame, text=label, width=80, height=26,
                          fg_color=TOOLBAR_COLOR, hover_color=ACCENT2,
                          font=ctk.CTkFont(size=11),
                          command=lambda ww=w, hh=h: (self.w_var.set(str(ww)), self.h_var.set(str(hh)))
                          ).pack(side="left", padx=3)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Create", fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._ok).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color=TOOLBAR_COLOR, hover_color="#444",
                      command=self.destroy).pack(side="left", padx=6)

    def _ok(self):
        try:
            w = int(self.w_var.get())
            h = int(self.h_var.get())
            if w < 1 or h < 1:
                raise ValueError
            self.result = (w, h)
        except Exception:
            messagebox.showerror("Invalid", "Please enter valid positive integers.", parent=self)
            return
        self.destroy()


# ─── Adjustment Dialog ────────────────────────────────────────────────────────
class AdjustDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, sliders, callback):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.callback = callback
        self.slider_vars = []
        self.grab_set()

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=ACCENT).pack(pady=(16, 8))

        frame = ctk.CTkFrame(self, fg_color=PANEL_COLOR)
        frame.pack(padx=20, fill="x", pady=4)

        for i, (label, from_, to, default) in enumerate(sliders):
            ctk.CTkLabel(frame, text=f"{label}:", text_color=TEXT_COLOR,
                         font=ctk.CTkFont(size=12)).grid(row=i, column=0, padx=10, pady=6, sticky="w")
            var = ctk.DoubleVar(value=default)
            sl = ctk.CTkSlider(frame, from_=from_, to=to, variable=var,
                               button_color=ACCENT, progress_color=ACCENT2, width=200)
            sl.grid(row=i, column=1, padx=8, pady=6)
            lbl = ctk.CTkLabel(frame, text=str(default), text_color=TEXT_COLOR,
                               font=ctk.CTkFont(size=11), width=40)
            lbl.grid(row=i, column=2, padx=4)
            var.trace_add("write", lambda *_, v=var, l=lbl: l.configure(text=f"{v.get():.0f}"))
            self.slider_vars.append(var)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="Apply", fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._apply).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color=TOOLBAR_COLOR,
                      command=self.destroy).pack(side="left", padx=6)

        width = 380
        height = 80 + len(sliders) * 50 + 80
        self.geometry(f"{width}x{height}")

    def _apply(self):
        vals = [v.get() for v in self.slider_vars]
        self.callback(vals)
        self.destroy()


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PhotoCraft()
    app.mainloop()
