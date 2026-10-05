import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Output to both frontend/public for direct frontend serving and dataset
FRONTEND_PUBLIC = Path(__file__).resolve().parent.parent / "frontend" / "public" / "saree_samples"
FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 320, 260

def create_folded_saree_base(color_rgb, highlight_rgb=None):
    """Creates a realistic folded silk saree with fabric folds, sheen and shadows."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=color_rgb)
    arr = np.array(img, dtype=np.float32)
    
    # 3D folded saree structure
    x = np.arange(WIDTH)
    y = np.arange(HEIGHT)
    xx, yy = np.meshgrid(x, y)
    
    # Silk sheen angle
    sheen = np.sin((xx + yy) / 45.0) * 18.0
    
    # Diagonal drape and folds
    fold_shadow_1 = np.exp(-((xx * 0.4 + yy - 180) ** 2) / 600.0) * -35.0
    fold_shadow_2 = np.exp(-((xx * 0.2 + yy - 90) ** 2) / 500.0) * 20.0
    
    # Weave texture
    fine_weave = (np.sin(xx * 1.2) * np.cos(yy * 1.2) * 5.0)
    
    total_mod = sheen + fold_shadow_1 + fold_shadow_2 + fine_weave
    
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + total_mod, 0, 255)
        
    return Image.fromarray(arr.astype(np.uint8))

def draw_temple_border_saree(base_color, zari_color=(255, 215, 0)):
    img = create_folded_saree_base(base_color)
    draw = ImageDraw.Draw(img)
    
    # Zari border band at bottom fold
    border_y = HEIGHT - 75
    draw.rectangle([0, border_y, WIDTH, HEIGHT], fill=zari_color)
    draw.line([(0, border_y), (WIDTH, border_y)], fill=(180, 130, 0), width=2)
    draw.line([(0, border_y + 8), (WIDTH, border_y + 8)], fill=(120, 90, 0), width=2)
    
    # Temple spires (triangles)
    spire_w = 32
    spire_h = 42
    for x in range(0, WIDTH, spire_w):
        p1 = (x, border_y)
        p2 = (x + spire_w // 2, border_y - spire_h)
        p3 = (x + spire_w, border_y)
        draw.polygon([p1, p2, p3], fill=zari_color)
        
        # Inner fine line
        ip1 = (x + 6, border_y)
        ip2 = (x + spire_w // 2, border_y - spire_h + 10)
        ip3 = (x + spire_w - 6, border_y)
        draw.polygon([ip1, ip2, ip3], fill=(255, 245, 180))
        
    # Extra fine horizontal gold threads on the border
    for y in range(border_y + 16, HEIGHT, 10):
        draw.line([(0, y), (WIDTH, y)], fill=(200, 150, 0), width=1)
        
    return img

def draw_floral_motif_saree(base_color, zari_color=(255, 215, 0)):
    img = create_folded_saree_base(base_color)
    draw = ImageDraw.Draw(img)
    
    # Gold border at bottom
    border_y = HEIGHT - 60
    draw.rectangle([0, border_y, WIDTH, HEIGHT], fill=zari_color)
    draw.line([(0, border_y), (WIDTH, border_y)], fill=(180, 130, 0), width=2)
    
    # Circular floral medallion motifs
    motifs_pos = [(70, 90), (160, 130), (250, 85), (110, 175), (210, 175)]
    for cx, cy in motifs_pos:
        # Central rosette
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=zari_color)
        # 8 radiating floral petals
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = cx + int(math.cos(rad) * 18)
            py = cy + int(math.sin(rad) * 18)
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=zari_color, outline=(255, 245, 180), width=1)
            # Outer tip
            tx = cx + int(math.cos(rad) * 26)
            ty = cy + int(math.sin(rad) * 26)
            draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(255, 245, 180))
            
    return img

def draw_peacock_motif_saree(base_color, zari_color=(255, 215, 0)):
    img = create_folded_saree_base(base_color)
    draw = ImageDraw.Draw(img)
    
    # Heavy zari border at bottom
    border_y = HEIGHT - 65
    draw.rectangle([0, border_y, WIDTH, HEIGHT], fill=zari_color)
    draw.line([(0, border_y), (WIDTH, border_y)], fill=(180, 130, 0), width=3)
    for y in range(border_y + 12, HEIGHT, 12):
        draw.line([(0, y), (WIDTH, y)], fill=(190, 140, 0), width=1)
        
    # Large elegant peacock motif
    cx, cy = 160, 115
    # Body
    draw.ellipse([cx - 18, cy - 10, cx + 18, cy + 30], fill=zari_color)
    # Neck and Head
    draw.ellipse([cx + 10, cy - 35, cx + 28, cy - 12], fill=zari_color)
    draw.line([cx + 12, cy - 15, cx + 6, cy - 2], fill=zari_color, width=6)
    # Beak
    draw.polygon([(cx + 28, cy - 24), (cx + 38, cy - 22), (cx + 28, cy - 20)], fill=(255, 245, 180))
    # Crest crown feathers
    draw.line([cx + 22, cy - 35, cx + 26, cy - 44], fill=zari_color, width=2)
    draw.line([cx + 18, cy - 35, cx + 16, cy - 43], fill=zari_color, width=2)
    draw.ellipse([cx + 24, cy - 47, cx + 28, cy - 43], fill=(255, 245, 180))
    draw.ellipse([cx + 14, cy - 46, cx + 18, cy - 42], fill=(255, 245, 180))
    # Majestic Plumage / Fan Tail
    for deg in range(-140, 30, 22):
        rad = math.radians(deg)
        fx = cx - 12 + int(math.cos(rad) * 44)
        fy = cy + int(math.sin(rad) * 44)
        draw.ellipse([fx - 8, fy - 8, fx + 8, fy + 8], fill=zari_color, outline=(255, 245, 180), width=2)
        draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=(200, 150, 0))
        
    return img

def draw_geometric_saree(base_color, zari_color=(255, 215, 0)):
    img = create_folded_saree_base(base_color)
    draw = ImageDraw.Draw(img)
    
    # Diamond ikat / patola geometric weave across entire body
    diamond_w = 44
    diamond_h = 44
    for y in range(0, HEIGHT + diamond_h, diamond_h // 2):
        for x in range(0, WIDTH + diamond_w, diamond_w):
            offset = (diamond_w // 2) if (y // (diamond_h // 2)) % 2 == 1 else 0
            cx = x + offset
            cy = y
            # Outer diamond
            pts = [(cx, cy - 18), (cx + 18, cy), (cx, cy + 18), (cx - 18, cy)]
            draw.polygon(pts, outline=zari_color, width=3)
            # Inner diamond
            inner_pts = [(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)]
            draw.polygon(inner_pts, fill=zari_color)
            
    # Zari border at bottom
    border_y = HEIGHT - 55
    draw.rectangle([0, border_y, WIDTH, HEIGHT], fill=zari_color)
    draw.line([(0, border_y), (WIDTH, border_y)], fill=(180, 130, 0), width=2)
    return img


# Generate all items exactly as shown in the screenshot:
def generate_all_samples():
    print("Generating exact UI sample sarees matching user screenshot...")
    
    # Example 1 : Temple Border (Red, Blue, Green, Yellow)
    tb_palettes = [
        ("temple_red", (190, 24, 24)),
        ("temple_blue", (20, 60, 150)),
        ("temple_green", (15, 105, 55)),
        ("temple_yellow", (230, 165, 10))
    ]
    for name, col in tb_palettes:
        img = draw_temple_border_saree(col)
        img.save(FRONTEND_PUBLIC / f"{name}.jpg", quality=95)
        
    # Crop motif patch for Temple Border Output
    tb_patch = draw_temple_border_saree((160, 20, 20)).crop((70, HEIGHT - 100, 250, HEIGHT - 10))
    tb_patch.save(FRONTEND_PUBLIC / "output_temple_border.jpg", quality=95)

    # Example 2 : Floral Motif (Pink, Purple, Teal, Beige)
    floral_palettes = [
        ("floral_pink", (220, 30, 110)),
        ("floral_purple", (95, 25, 125)),
        ("floral_teal", (15, 125, 140)),
        ("floral_beige", (225, 215, 185))
    ]
    for name, col in floral_palettes:
        img = draw_floral_motif_saree(col)
        img.save(FRONTEND_PUBLIC / f"{name}.jpg", quality=95)
        
    # Crop motif patch for Floral Output
    floral_patch = draw_floral_motif_saree((180, 25, 45)).crop((35, 50, 205, 220))
    floral_patch.save(FRONTEND_PUBLIC / "output_floral_motif.jpg", quality=95)

    # Example 3 : Peacock Motif (Red, Blue, Green, White)
    peacock_palettes = [
        ("peacock_red", (195, 25, 30)),
        ("peacock_blue", (22, 58, 145)),
        ("peacock_green", (18, 98, 52)),
        ("peacock_white", (235, 230, 215))
    ]
    for name, col in peacock_palettes:
        img = draw_peacock_motif_saree(col)
        img.save(FRONTEND_PUBLIC / f"{name}.jpg", quality=95)
        
    # Crop motif patch for Peacock Output
    peacock_patch = draw_peacock_motif_saree((165, 20, 25)).crop((70, 45, 250, 225))
    peacock_patch.save(FRONTEND_PUBLIC / "output_peacock_motif.jpg", quality=95)

    # Example 4 : Geometric Pattern (Orange, Black, Purple, Maroon)
    geo_palettes = [
        ("geo_orange", (225, 105, 20)),
        ("geo_black", (45, 50, 55)),
        ("geo_purple", (110, 35, 120)),
        ("geo_maroon", (115, 20, 30))
    ]
    for name, col in geo_palettes:
        img = draw_geometric_saree(col, zari_color=(235, 220, 160) if name == "geo_black" else (255, 215, 0))
        img.save(FRONTEND_PUBLIC / f"{name}.jpg", quality=95)
        
    # Crop motif patch for Geometric Output
    geo_patch = draw_geometric_saree((35, 35, 35), zari_color=(230, 210, 150)).crop((40, 40, 220, 220))
    geo_patch.save(FRONTEND_PUBLIC / "output_geometric_pattern.jpg", quality=95)

    # Also generate the similar designs sarees for the right panel:
    sim_palettes = [
        ("similar_red", (190, 24, 24), "96% Similar"),
        ("similar_blue", (20, 60, 150), "94% Similar"),
        ("similar_green", (15, 105, 55), "92% Similar"),
        ("similar_purple", (140, 25, 95), "90% Similar")
    ]
    for name, col, _ in sim_palettes:
        img = draw_temple_border_saree(col)
        img.save(FRONTEND_PUBLIC / f"{name}.jpg", quality=95)

    print("All UI saree sample images successfully created in", FRONTEND_PUBLIC)

if __name__ == "__main__":
    generate_all_samples()
