from PIL import Image, ImageDraw, ImageFont
import os
import unicodedata
import argparse
import glob


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

    try:
        name = unicodedata.name(char).lower().replace(' ', '_')
        return f"unicode_{name}"
    except ValueError:
        return f"char_0x{ord(char):04x}"


def create_ascii_images(output_dir="ascii_images", font_size=32):
    os.makedirs(output_dir, exist_ok=True)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for code in range(32, 127):
        char = chr(code)

        left, top, right, bottom = font.getbbox(char)
        text_width = right - left
        text_height = bottom - top

        img_width = text_width + 20
        img_height = text_height + 20
        image = Image.new("RGB", (img_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        draw.text((10, 10), char, font=font, fill=(0, 0, 0))

        safe_name = get_safe_filename(char)
        filename = f"{safe_name}.png"
        image.save(os.path.join(output_dir, filename))
        print(f"Saved: {filename}")


def encode_message(message, images_dir="ascii_images", pad=0):
    existing_messages = glob.glob("message*.png")
    max_num = -1
    for filename in existing_messages:
        try:
            num = int(filename[7:-4])
            if num > max_num:
                max_num = num
        except ValueError:
            continue
    output_filename = f"message{max_num + 1}.png"

    if not os.path.exists(images_dir):
        print(f"Error: ASCII images directory '{images_dir}' not found. Please generate images first.")
        return

    char_images = []
    total_width = 0
    max_height = 0

    for i, char in enumerate(message):
        safe_name = get_safe_filename(char)
        char_filename = f"{safe_name}.png"
        char_path = os.path.join(images_dir, char_filename)

        if not os.path.exists(char_path):
            print(f"Warning: No image found for character '{char}' (file: {char_filename})")
            continue

        img = Image.open(char_path)
        char_images.append(img)
        total_width += img.width
        if img.height > max_height:
            max_height = img.height

    if not char_images:
        print("Error: No valid character images found to encode the message.")
        return

    total_width += pad * (len(char_images) - 1)

    output_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))
    x_offset = 0

    for i, img in enumerate(char_images):
        output_image.paste(img, (x_offset, 0))
        x_offset += img.width + pad

    output_image.save(output_filename)
    print(f"Message saved as: {output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII Image Generator and Message Encoder")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gen-ascii-images", action="store_true", help="Generate ASCII character images")
    group.add_argument("--encode-message", type=str, help="Encode a message using ASCII images")

    parser.add_argument("--output-dir", default="ascii_images", help="Directory to store/load ASCII images (default: ascii_images)")
    parser.add_argument("--font-size", type=int, default=32, help="Font size for ASCII images (default: 32)")
    parser.add_argument("--pad", type=int, default=0, help="Padding in pixels between characters when encoding a message (default: 0)")

    args = parser.parse_args()

    print(args)

    if args.gen_ascii_images:
        create_ascii_images(output_dir=args.output_dir, font_size=args.font_size)
    elif args.encode_message:
        encode_message(args.encode_message, images_dir=args.output_dir, pad=args.pad)