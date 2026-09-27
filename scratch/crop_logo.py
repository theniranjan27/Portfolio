from PIL import Image, ImageDraw

def process_logo():
    img = Image.open('static/images/logo.png').convert('RGBA')
    width, height = img.size

    # Find tight bounding box of the glowing content (threshold > 15)
    gray = img.convert('L')
    bbox = gray.point(lambda p: 255 if p > 18 else 0).getbbox()
    print("Detected bbox:", bbox)
    
    if bbox:
        # Crop to the glowing emblem
        cropped = img.crop(bbox)
    else:
        cropped = img

    w, h = cropped.size
    
    # Create a rounded rectangle alpha mask matching the inner logo shape
    # We want a smooth rounded mask for the 4 corners outside the glowing frame
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    
    # Radius for rounded corners of the logo container (approx 15% of width)
    corner_radius = int(min(w, h) * 0.16)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=corner_radius, fill=255)
    
    # Apply mask to cropped image
    cropped.putalpha(mask)
    
    # Save as logo.png
    cropped.save('static/images/logo.png', 'PNG')
    cropped.save('static/images/new_logo.png', 'PNG')
    print("Logo successfully processed and saved with transparent rounded corners! Dimensions:", cropped.size)

if __name__ == '__main__':
    process_logo()
