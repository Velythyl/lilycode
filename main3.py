from PIL import Image, ImageDraw, ImageFont
import os
import unicodedata
import argparse
import glob
import numpy as np


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
        image.save(os.path.join(output_dir, filename))
        print(f"Saved: {filename}")


def encode_message(message, images_dir="ascii_images"):
    # Find all existing message files to determine the next number
    existing_messages = glob.glob("message*.png")
    max_num = -1
    for filename in existing_messages:
        try:
            num = int(filename[7:-4])  # Extract number from "message123.png"
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    output_filename = f"message{max_num + 1}.png"

    # Check if images directory exists
    if not os.path.exists(images_dir):
        print(f"Error: ASCII images directory '{images_dir}' not found. Please generate images first.")
        return

    # Create a list to hold all character images
    char_images = []
    total_width = 0
    max_height = 0

    # Load each character image
    for char in message:
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

    # Create the output image
    output_image = Image.new("RGB", (total_width, max_height), (255, 255, 255))
    x_offset = 0

    # Paste each character image
    for img in char_images:
        output_image.paste(img, (x_offset, 0))
        x_offset += img.width

    # Save the output image
    output_image.save(output_filename)
    print(f"Message saved as: {output_filename}")


def decode_image(image_path, images_dir="ascii_images"):
    # Define the replacements dictionary here so it's accessible
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

    # Check if images directory exists
    if not os.path.exists(images_dir):
        print(f"Error: ASCII images directory '{images_dir}' not found. Please generate images first.")
        return

    # Load all character images into a dictionary
    char_images = {}
    char_widths = set()

    for filename in os.listdir(images_dir):
        if filename.endswith(".png"):
            char_path = os.path.join(images_dir, filename)
            img = Image.open(char_path)
            char_images[filename] = img
            char_widths.add(img.width)

    if not char_images:
        print("Error: No character images found in the directory.")
        return

    # Load the message image
    try:
        message_img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Message image '{image_path}' not found.")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Create inverse replacements mapping
    replacements_inv = {v: k for k, v in replacements.items()}

    # Split the message image into individual characters
    message_width, message_height = message_img.size
    x = 0
    decoded_chars = []

    while x < message_width:
        # Try all possible widths in descending order
        for width in sorted(char_widths, reverse=True):
            if x + width > message_width:
                continue

            # Extract the candidate character
            char_candidate = message_img.crop((x, 0, x + width, message_height))

            # Compare with all character images
            for filename, char_img in char_images.items():
                if char_img.size != char_candidate.size:
                    continue

                # Convert to numpy arrays for comparison
                arr1 = np.array(char_img)
                arr2 = np.array(char_candidate)

                if np.allclose(arr1, arr2):
                    # Found a match
                    char_name = filename[:-4]  # Remove .png extension

                    # Reverse the get_safe_filename function
                    if char_name.startswith("unicode_"):
                        try:
                            char_name = char_name[8:].replace('_', ' ')
                            char = unicodedata.lookup(char_name)
                        except:
                            continue
                    elif char_name.startswith("char_0x"):
                        try:
                            char_code = int(char_name[7:], 16)
                            char = chr(char_code)
                        except:
                            continue
                    else:
                        # Check replacements
                        if char_name in replacements_inv:
                            char = replacements_inv[char_name]
                        else:
                            # This might be a regular character (like letters)
                            if len(char_name) == 1:
                                char = char_name
                            else:
                                continue

                    decoded_chars.append(char)
                    x += width
                    break
            else:
                continue
            break
        else:
            # No matching character found, move to next pixel
            x += 1

    decoded_message = ''.join(decoded_chars)
    print(f"Decoded message: {decoded_message}")
    return decoded_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII Image Generator and Message Encoder/Decoder")

    # Add mutually exclusive group for the modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gen-ascii-images", action="store_true",
                       help="Generate ASCII character images")
    group.add_argument("--encode-message", type=str,
                       help="Encode a message using ASCII images")
    group.add_argument("--decode-image", type=str,
                       help="Decode a message from a concatenated image (message*.png)")

    # Optional arguments
    parser.add_argument("--output-dir", default="ascii_images",
                        help="Directory to store/load ASCII images (default: ascii_images)")
    parser.add_argument("--font-size", type=int, default=32,
                        help="Font size for ASCII images (default: 32)")

    args = parser.parse_args()

    if args.gen_ascii_images:
        create_ascii_images(output_dir=args.output_dir, font_size=args.font_size)
    elif args.encode_message:
        encode_message(args.encode_message, images_dir=args.output_dir)
    elif args.decode_image:
        decode_image(args.decode_image, images_dir=args.output_dir)