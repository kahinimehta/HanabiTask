import os
from PIL import Image, ImageDraw, ImageChops
import numpy as np

# --- SETUP ---
save_dir = "/Users/mehtaka/Desktop/Columbia/Nuttida_Lab/Collaboration_Code/Shapes"
os.makedirs(save_dir, exist_ok=True)

colors = {
    "yellow": (255, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "orange": (255, 165, 0)
}

positions = ["up", "down", "left", "right"]
canvas_size = (400, 400)
shape_size = 80

# --- POSITION COORDINATES ---
def get_coords(position, size):
    w, h = size
    margin = 40
    mid_w, mid_h = w // 2, h // 2
    if position == "up":
        return (mid_w, margin)
    elif position == "down":
        return (mid_w, h - margin)
    elif position == "left":
        return (margin, mid_h)
    elif position == "right":
        return (w - margin, mid_h)

# --- DRAW SQUARE ---
def draw_square(draw, x, y, color, s):
    r = s // 2
    draw.rectangle([x - r, y - r, x + r, y + r], fill=color)

# --- RENDER SHAPE PATCH ---
def render_square_patch(color_rgb, s, rotation_deg=0):
    patch_dim = int(s * 2)
    patch = Image.new("RGBA", (patch_dim, patch_dim), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch)
    cx, cy = patch_dim // 2, patch_dim // 2
    r = s // 2
    fill = (*color_rgb, 255)
    d.rectangle([cx - r, cy - r, cx + r, cy + r], fill=fill)
    if rotation_deg != 0:
        patch = patch.rotate(rotation_deg, expand=True, resample=Image.BICUBIC)
    return patch

# --- CROP RELEVANT EDGE ---
def crop_edge(img, position):
    bg = Image.new(img.mode, img.size, "white")
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if not bbox:
        return img
    left, top, right, bottom = bbox
    w, h = img.size
    if position == "up":
        return img.crop((0, top, w, h))
    elif position == "down":
        return img.crop((0, 0, w, bottom))
    elif position == "left":
        return img.crop((left, 0, w, h))
    elif position == "right":
        return img.crop((0, 0, right, h))
    else:
        return img

# --- MAIN LOOP ---
stimuli = []
for color_name, color_rgb in colors.items():
    for pos in positions:
        img = Image.new("RGB", canvas_size, "white")
        draw = ImageDraw.Draw(img)
        x, y = get_coords(pos, canvas_size)
        draw_square(draw, x, y, color_rgb, shape_size)
        img = crop_edge(img, pos)
        fname = f"{save_dir}/{color_name}_{pos}_square.png"
        img.save(fname)
        stimuli.append(fname)

# --- ROTATED (slightly offset) ---
offset = 20
for f in stimuli:
    color_name, pos, _ = os.path.basename(f).replace(".png", "").split("_")
    base = Image.new("RGB", canvas_size, "white")
    x, y = get_coords(pos, canvas_size)
    if pos == "up":
        y += offset
    elif pos == "down":
        y -= offset
    elif pos == "left":
        x += offset
    elif pos == "right":
        x -= offset
    patch = render_square_patch(colors[color_name], shape_size, rotation_deg=45)
    px, py = patch.size
    top_left = (int(round(x - px / 2)), int(round(y - py / 2)))
    base.paste(patch, top_left, patch)
    base = crop_edge(base, pos)
    rotated_name = f.replace(".png", "_rotated.png")
    base.save(rotated_name)

print("✅ 32 stimuli generated (16 base + 16 rotated, squares only, trimmed on relevant edge)")
