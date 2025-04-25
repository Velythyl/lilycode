from PIL import Image, ImageDraw, ImageFont
import os
import unicodedata


def get_safe_filename(char):
    # Handle specific characters with more readable names
    replacements = {
        '/': 'slash',
        '\\': 'backslash',
        ':': 'colon',
        '*': 'asterisk',
        '?': 'questionmark',
        '"': 'quote',
        '<': 'lessthan',
        '>': 'greaterthan',
        '|': 'pipe',
        ' ': 'space',
        '\t': 'tab',
        '\n': 'newline',
        '\r': 'return',
        '\x0b': 'vtab',
        '\x0c': 'formfeed'
    }

    if char in replacements:
        return replacements[char]

    # For other characters, use their Unicode name if available
    try:
        name = unicodedata.name(char).lower().replace(' ', '_')
        return f"unicode_{name}"
    except ValueError:
        # Fallback to hex code if no Unicode name exists
        return f"char_0x{ord(char):04x}"


def create_ascii_images(output_dir="ascii_images", font_size=32):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Use a default font (you may need to specify a different path depending on your system)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font if Arial isn't available
        font = ImageFont.load_default()

    # Generate images for all printable ASCII characters (32-126)
    for code in range(32, 127):
        char = chr(code)

        # Calculate text size using getbbox
        left, top, right, bottom = font.getbbox(char)
        text_width = right - left
        text_height = bottom - top

        # Create image with some padding
        img_width = text_width + 20
        img_height = text_height + 20
        image = Image.new("RGB", (img_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Draw the character centered
        draw.text((10, 10), char, font=font, fill=(0, 0, 0))

        # Get safe filename
        safe_name = get_safe_filename(char)
        filename = f"{safe_name}.png"
        print(f"saving {filename}")
        image.save(os.path.join(output_dir, filename))
        print(f"Saved: {filename}")


if __name__ == "__main__":
    create_ascii_images()