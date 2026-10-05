import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent / "preset_sarees"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Curated Authentic Saree Color Palettes
COLOR_THEMES = [
    {"name": "Crimson_Red", "rgb": (185, 28, 28), "zari": (255, 215, 0), "contrast": (250, 240, 200)},
    {"name": "Royal_Blue", "rgb": (24, 76, 160), "zari": (255, 220, 50), "contrast": (240, 245, 255)},
    {"name": "Emerald_Green", "rgb": (20, 110, 50), "zari": (255, 215, 0), "contrast": (230, 255, 230)},
    {"name": "Mustard_Yellow", "rgb": (220, 140, 10), "zari": (255, 235, 120), "contrast": (255, 250, 220)},
    {"name": "Deep_Purple", "rgb": (90, 30, 130), "zari": (255, 215, 0), "contrast": (245, 230, 255)},
    {"name": "Peacock_Teal", "rgb": (10, 120, 130), "zari": (255, 215, 0), "contrast": (210, 250, 250)},
]

def add_fabric_texture(img: Image.Image) -> Image.Image:
    """Adds subtle silk/cotton weave texture to simulate realistic fabric."""
    w, h = img.size
    arr = np.array(img, dtype=np.float32)
    # Weave noise
    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)
    weave = (np.sin(xx * 0.8) * np.cos(yy * 0.8) * 8.0).astype(np.float32)
    # Vignette and fold shadows
    shadow = (np.sin(yy / 35.0) * 12.0).astype(np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + weave + shadow, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + weave + shadow, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + weave + shadow, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def draw_temple_border(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws iconic triangular spires (Temple border/Gopuram) along the border."""
    border_height = 80
    # Base border ribbon
    draw.rectangle([0, h - border_height, w, h], fill=zari_col)
    draw.rectangle([0, h - border_height + 8, w, h - 8], fill=(130, 20, 20))
    # Temple triangles (Kuttu / Temple gopuram)
    spire_width = 32
    spire_height = 42
    for x in range(0, w, spire_width):
        p1 = (x, h - border_height)
        p2 = (x + spire_width // 2, h - border_height - spire_height)
        p3 = (x + spire_width, h - border_height)
        draw.polygon([p1, p2, p3], fill=zari_col)
        # Inner decorative triangle
        ip1 = (x + 6, h - border_height)
        ip2 = (x + spire_width // 2, h - border_height - spire_height + 10)
        ip3 = (x + spire_width - 6, h - border_height)
        draw.polygon([ip1, ip2, ip3], fill=contrast_col)

def draw_peacock_motif(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws stylized Mayil / Peacock motifs across the pallu and body."""
    # Repeat decorative peacocks
    step_x = 90
    step_y = 90
    for y in range(40, h - 30, step_y):
        for x in range(40, w - 30, step_x):
            # Peacock body
            draw.ellipse([x - 12, y - 8, x + 12, y + 20], fill=zari_col)
            # Neck & head
            draw.ellipse([x + 6, y - 22, x + 18, y - 6], fill=zari_col)
            draw.line([x + 8, y - 6, x + 4, y], fill=zari_col, width=4)
            # Beak
            draw.polygon([(x + 18, y - 14), (x + 24, y - 12), (x + 18, y - 10)], fill=contrast_col)
            # Crown feathers
            draw.line([x + 14, y - 22, x + 16, y - 28], fill=contrast_col, width=2)
            draw.line([x + 12, y - 22, x + 10, y - 27], fill=contrast_col, width=2)
            # Ornate Fan/Plumage eyelets
            for deg in range(-120, 20, 30):
                rad = math.radians(deg)
                fx = x - 8 + int(math.cos(rad) * 28)
                fy = y + int(math.sin(rad) * 28)
                draw.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=contrast_col, outline=zari_col, width=2)

def draw_floral_jaal(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws cascading vines, flowers, and foliage net (Jaal)."""
    # Intertwined sinusoidal vines
    for offset_y in range(-50, h + 50, 70):
        points = []
        for x in range(0, w + 10, 8):
            y = offset_y + int(math.sin(x / 25.0) * 22)
            points.append((x, y))
        draw.line(points, fill=zari_col, width=3)
        # Petals & rosettes along the vine
        for px, py in points[::6]:
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                pet_x = px + int(math.cos(rad) * 9)
                pet_y = py + int(math.sin(rad) * 9)
                draw.ellipse([pet_x - 3, pet_y - 3, pet_x + 3, pet_y + 3], fill=contrast_col)
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=zari_col)

def draw_paisley(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws Mango / Paisley / Kalka motifs."""
    step = 85
    for y in range(45, h - 30, step):
        for x in range(45, w - 30, step):
            # Curved teardrop base
            draw.ellipse([x - 16, y - 10, x + 16, y + 26], fill=zari_col)
            # Curled tail tip
            draw.chord([x - 12, y - 28, x + 24, y + 6], start=180, end=360, fill=zari_col)
            # Inner decorative motif
            draw.ellipse([x - 8, y, x + 8, y + 16], fill=contrast_col)
            draw.ellipse([x - 4, y + 4, x + 4, y + 12], fill=zari_col)

def draw_geometric(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws interlocking diamonds, chevrons, and stepped fret weaves."""
    diamond_w = 40
    diamond_h = 40
    for y in range(0, h + diamond_h, diamond_h // 2):
        for x in range(0, w + diamond_w, diamond_w):
            offset = (diamond_w // 2) if (y // (diamond_h // 2)) % 2 == 1 else 0
            cx = x + offset
            cy = y
            pts = [(cx, cy - 16), (cx + 16, cy), (cx, cy + 16), (cx - 16, cy)]
            draw.polygon(pts, outline=zari_col, width=3)
            # Inner mini diamond
            inner_pts = [(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)]
            draw.polygon(inner_pts, fill=contrast_col)

def draw_checks_stripes(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws classic Palum-Pazham checks and zari pinstripes."""
    grid_size = 36
    # Vertical zari lines
    for x in range(0, w, grid_size):
        draw.line([(x, 0), (x, h)], fill=zari_col, width=3)
        draw.line([(x + 6, 0), (x + 6, h)], fill=contrast_col, width=1)
    # Horizontal zari lines
    for y in range(0, h, grid_size):
        draw.line([(0, y), (w, y)], fill=zari_col, width=3)
        draw.line([(0, y + 6), (w, y + 6)], fill=contrast_col, width=1)

def draw_butta_dots(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws scattered circular floral coin motifs (Kasu Buttas / Thilagam)."""
    step = 60
    for y in range(30, h, step):
        row_offset = (step // 2) if (y // step) % 2 == 1 else 0
        for x in range(30, w, step):
            cx = x + row_offset
            if cx < w:
                # Golden sun coin
                draw.ellipse([cx - 12, y - 12, cx + 12, y + 12], fill=zari_col)
                # Intricate central ruby/contrast dot
                draw.ellipse([cx - 5, y - 5, cx + 5, y + 5], fill=contrast_col)
                # Outer radiant spokes
                for deg in range(0, 360, 45):
                    rad = math.radians(deg)
                    sx = cx + int(math.cos(rad) * 16)
                    sy = y + int(math.sin(rad) * 16)
                    draw.line([(cx, y), (sx, sy)], fill=zari_col, width=2)

def draw_traditional_zari(draw: ImageDraw.ImageDraw, w: int, h: int, zari_col, contrast_col):
    """Draws heavy brocade zari pallu with rudraksha and kalash motifs."""
    # Diagonal lattice / crisscross zari lines
    spacing = 30
    for d in range(-h, w + h, spacing):
        draw.line([(d, 0), (d + h, h)], fill=zari_col, width=2)
        draw.line([(d, h), (d + h, 0)], fill=zari_col, width=2)
    # Kalash pot & rudraksha beads at intersections
    for y in range(0, h, spacing):
        for x in range(0, w, spacing):
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=contrast_col, outline=zari_col, width=2)


DESIGN_DISPATCH = {
    "Temple Border": draw_temple_border,
    "Peacock Motif": draw_peacock_motif,
    "Floral Jaal": draw_floral_jaal,
    "Paisley (Kalka)": draw_paisley,
    "Geometric Weave": draw_geometric,
    "Checks & Stripes": draw_checks_stripes,
    "Butta Dots": draw_butta_dots,
    "Traditional Zari": draw_traditional_zari,
}

def generate_all():
    print(f"Generating preset saree images across classes and colors in {OUTPUT_DIR}...")
    size = (320, 320)
    generated_count = 0

    for design_name, draw_fn in DESIGN_DISPATCH.items():
        clean_design = design_name.replace(" ", "_").replace("(", "").replace(")", "").replace("&", "and")
        for theme in COLOR_THEMES:
            # Create base saree fabric
            img = Image.new("RGB", size, color=theme["rgb"])
            draw = ImageDraw.Draw(img)

            # Draw the distinct design motif
            draw_fn(draw, size[0], size[1], theme["zari"], theme["contrast"])

            # Add realistic fabric texture & folds
            textured_img = add_fabric_texture(img)

            # Filename format: {Design}__{ColorTheme}.jpg
            filename = f"{clean_design}__{theme['name']}.jpg"
            save_path = OUTPUT_DIR / filename
            textured_img.save(save_path, format="JPEG", quality=95)
            generated_count += 1

    print(f"Successfully generated {generated_count} preset sarees.")

if __name__ == "__main__":
    generate_all()
