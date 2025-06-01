from PIL import Image

def embed_message_lsb_red(image_path, secret_message, output_path):
    """
    Embeds a secret message into the LSB of the Red channel of a PNG image.
    The message is terminated with a special delimiter string.
    """
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure it's in RGB format
        pixels = img.load()
        width, height = img.size

        # Add a delimiter to know where the message ends
        # Using a less common sequence to avoid accidental matches
        delimiter = "<-END->"
        binary_secret_message = ''.join(format(ord(char), '08b') for char in secret_message)
        binary_secret_message += ''.join(format(ord(char), '08b') for char in delimiter)

        message_len = len(binary_secret_message)
        max_len = width * height  # Max bits we can store in one channel

        if message_len > max_len:
            print(f"Error: Message too long to embed in this image's red channel.")
            print(f"Message requires {message_len} bits, image has space for {max_len} bits.")
            return False

        data_idx = 0
        for y in range(height):
            for x in range(width):
                if data_idx < message_len:
                    r, g, b = pixels[x, y]
                    # Modify LSB of Red channel
                    new_r = (r & 0b11111110) | int(binary_secret_message[data_idx])
                    pixels[x, y] = (new_r, g, b)
                    data_idx += 1
                else:
                    break  # Message embedded
            if data_idx >= message_len:
                break

        img.save(output_path, "PNG")
        print(f"Message embedded successfully into {output_path}")
        return True

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def extract_message_lsb_red(image_path):
    """
    Extracts a secret message from the LSB of the Red channel of a PNG image.
    Stops when it finds the delimiter "<-END->".
    """
    try:
        img = Image.open(image_path)
        img = img.convert("RGB") # Ensure it's in RGB format
        pixels = img.load()
        width, height = img.size

        binary_extracted_message = ""
        delimiter = "<-END->"
        binary_delimiter = ''.join(format(ord(char), '08b') for char in delimiter)
        delimiter_found = False

        for y in range(height):
            for x in range(width):
                r, _, _ = pixels[x, y]
                binary_extracted_message += str(r & 1) # Extract LSB of Red

                # Check if the delimiter is found
                if binary_extracted_message.endswith(binary_delimiter):
                    binary_extracted_message = binary_extracted_message[:-len(binary_delimiter)]
                    delimiter_found = True
                    break
            if delimiter_found:
                break
        
        if not delimiter_found:
            print("Warning: Delimiter not found. Extracted data might be incomplete or incorrect.")

        # Convert binary string back to characters
        extracted_message = ""
        for i in range(0, len(binary_extracted_message), 8):
            byte = binary_extracted_message[i:i+8]
            if len(byte) == 8: # Ensure it's a full byte
                extracted_message += chr(int(byte, 2))
            else:
                # print(f"Warning: Partial byte found at end of message: {byte}")
                pass # Silently ignore partial byte for cleaner output

        print(f"Extracted message: {extracted_message}")
        return extracted_message

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# --- Interactive Usage Example ---
if __name__ == "__main__":
    # --- STEP 1: Normalize your base image through Signal ---
    # Manually:
    # 1. Take 'original_image.png'.
    # 2. Send it to "Note to Self" in Signal.
    # 3. Save the image Signal sends back as 'normalized_image.png'.
    # This 'normalized_image.png' is what you'll use for steganography.

    normalized_image_file = "normalized_image.png" # Replace with your Signal-normalized image
    stego_image_file = "stego_image.png"
    received_image_file = "received_stego_image.png" # The image after you set stego_image.png as profile and download it

    # Ensure 'normalized_image.png' exists before running this.
    # You might need to create a dummy 'normalized_image.png' for the first run
    # or download your current profile pic if it's already "normalized".

    while True:
        print("\nSteganography Test Options:")
        print("1. Embed message into normalized image (creates stego_image.png)")
        print("2. Extract message from stego_image.png (local check)")
        print("3. Extract message from received_stego_image.png (after Signal processing)")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            message = input("Enter secret message to embed: ")
            if not normalized_image_file:
                print("Please define 'normalized_image_file' first.")
                continue
            embed_message_lsb_red(normalized_image_file, message, stego_image_file)
            print(f"Now, manually set '{stego_image_file}' as your Signal profile picture.")
            print(f"Then, from another device or account, download that profile picture and save it as '{received_image_file}'.")
        elif choice == '2':
            print(f"\n--- Extracting from local '{stego_image_file}' ---")
            extract_message_lsb_red(stego_image_file)
        elif choice == '3':
            print(f"\n--- Extracting from '{received_image_file}' (after Signal) ---")
            extract_message_lsb_red(received_image_file)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")
