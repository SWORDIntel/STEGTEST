from PIL import Image
import os
import hashlib
# PIL.ExifTags might be used later if more detailed EXIF is needed.
# For now, img.info should provide some basics.
# from PIL import ExifTags

def get_image_properties(image_path):
    """
    Extracts and returns a dictionary containing image properties.
    """
    try:
        img = Image.open(image_path)
        properties = {
            "format": img.format,
            "size_bytes": os.path.getsize(image_path),
            "dimensions": img.size,  # (width, height)
            "mode": img.mode,        # (e.g., 'RGB', 'RGBA', 'P' for palettized)
            "info": img.info,        # Dictionary of metadata
            # "exif": img.getexif() # More complex, skip for now
        }
        if img.format == "JPEG":
            if hasattr(img, 'quantization'):
                properties["quantization_tables"] = img.quantization
            # Attempt to get EXIF more directly if needed, though img.info often has it parsed for JPEGs
            # exif_data = img.getexif()
            # if exif_data:
            #     properties["exif_data"] = {ExifTags.TAGS.get(k,k): v for k,v in exif_data.items()}

        img.close()
        return properties
    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred while getting image properties: {e}")
        return None

def calculate_file_hash(file_path, hash_algorithm="sha256"):
    """
    Calculates the hash of a file using the specified algorithm.
    """
    try:
        hasher = hashlib.new(hash_algorithm)
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192): # Read in chunks
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path} for hashing.")
        return None
    except Exception as e:
        print(f"An error occurred during hash calculation: {e}")
        return None

def print_image_analysis(image_path, header_message="Image Analysis"):
    """
    Prints a comprehensive analysis of an image, including properties and file hash.
    """
    print(f"\n--- {header_message} for: {image_path} ---")

    properties = get_image_properties(image_path)
    if properties:
        print("Image Properties:")
        for key, value in properties.items():
            if key == "info" and isinstance(value, dict):
                print(f"  Info:")
                for k, v in value.items():
                    # EXIF data can be very verbose, shorten it if it's raw bytes
                    if isinstance(v, bytes) and len(v) > 100:
                        print(f"    {k}: {v[:50]}... (truncated)")
                    else:
                        print(f"    {k}: {v}")
            elif key == "quantization_tables":
                print(f"  Quantization Tables:")
                if value: # Check if it's not None or empty
                    for i, table in value.items(): # Iterating through dict: {table_index: table_data}
                        print(f"    Table {i}: {table[:16]}... (first 16 values)") # Print first 16 values as tables can be long
                else:
                    print("    Not available or empty.")
            else:
                print(f"  {key.replace('_', ' ').capitalize()}: {value}")
    else:
        print("Could not retrieve image properties.")

    file_hash = calculate_file_hash(image_path)
    if file_hash:
        print(f"File Hash (SHA-256): {file_hash}")
    else:
        print("Could not calculate file hash.")
    print("--- End of Analysis ---")

def generate_test_payload(byte_length):
    """
    Generates a test payload of a specific byte length.
    Example: "TestLSB_XXbytes_AAAA..." where XX is byte_length.
    """
    if byte_length < 20: # Minimum to fit the prefix
        return "A" * byte_length
    prefix = f"TestLSB_{byte_length}bytes_"
    remaining_length = byte_length - len(prefix)
    if remaining_length < 0: # Should not happen if byte_length check is done
        return "A" * byte_length # Fallback
    payload = prefix + "A" * remaining_length
    return payload[:byte_length] # Ensure exact length

# --- ECC (Error Correction Code) Placeholder Utilities ---
def encode_payload_with_ecc(payload_string, ecc_method="basic_parity"):
    """
    Encodes a string payload with a specified ECC method (placeholder).
    Returns a bit string.
    """
    payload_bytes = payload_string.encode('utf-8')
    encoded_bit_string = ""

    if ecc_method == "basic_parity":
        print("Applying basic_parity ECC (placeholder) during encoding...")
        for byte_val in payload_bytes:
            byte_bits = format(byte_val, '08b')
            parity_bit = '1' if byte_bits.count('1') % 2 != 0 else '0'
            encoded_bit_string += byte_bits + parity_bit
        # print(f"  Original payload (len {len(payload_string)} chars, {len(payload_bytes)} bytes) became bit string of len {len(encoded_bit_string)}")
        return encoded_bit_string
    elif ecc_method is None: # No ECC
        for byte_val in payload_bytes:
            encoded_bit_string += format(byte_val, '08b')
        return encoded_bit_string
    else:
        print(f"Warning: ECC method '{ecc_method}' not implemented. Returning original payload as bits.")
        for byte_val in payload_bytes:
            encoded_bit_string += format(byte_val, '08b')
        return encoded_bit_string

def decode_payload_with_ecc(received_bit_string, ecc_method="basic_parity"):
    """
    Decodes a bit string with a specified ECC method (placeholder).
    Returns a tuple: (decoded_string, status_message)
    """
    data_bytes = bytearray()
    status = "Decoded with no errors detected (or ECC method not applied/unknown)."

    if ecc_method == "basic_parity":
        print("Attempting basic_parity ECC decoding (placeholder)...")
        errors_detected = 0
        if len(received_bit_string) % 9 != 0:
            status = "Error: Received bit string length is not a multiple of 9 (8 data + 1 parity). Cannot reliably decode with basic_parity."
            print(status)
            # Attempt to decode as much as possible, or return empty
            # For simplicity, we'll try to process full blocks only.
            num_blocks = len(received_bit_string) // 9
            processed_bits = num_blocks * 9
            if num_blocks == 0: return "", status # Not enough bits for even one block
            print(f"  Processing only the first {processed_bits} bits ({num_blocks} blocks).")
            received_bit_string = received_bit_string[:processed_bits]


        for i in range(0, len(received_bit_string), 9):
            block = received_bit_string[i:i+9]
            if len(block) < 9: # Should be handled by the modulo check above, but as safeguard
                # status = "Warning: Partial block encountered at end of bit string."
                # print(status)
                continue

            data_bits = block[:8]
            received_parity_bit = block[8]

            calculated_parity_bit = '1' if data_bits.count('1') % 2 != 0 else '0'

            if calculated_parity_bit != received_parity_bit:
                errors_detected += 1
                # print(f"  Parity error detected in block {i//9}! Data: {data_bits}, Received Parity: {received_parity_bit}, Calc Parity: {calculated_parity_bit}. (Correction not implemented).")

            data_bytes.append(int(data_bits, 2))

        if errors_detected > 0:
            status = f"Decoded with {errors_detected} parity error(s) detected (uncorrected by placeholder ECC)."
            print(f"  {status}")
        else:
            status = "Decoded with basic_parity. No errors detected."
            print(f"  {status}")

        try:
            return data_bytes.decode('utf-8', errors='replace'), status
        except UnicodeDecodeError as e:
            status = f"UnicodeDecodeError after ECC: {e}. Data might be corrupted."
            print(f"  {status}")
            return data_bytes.decode('utf-8', errors='replace'), status # Try to return what we have

    elif ecc_method is None: # No ECC was applied
        # Convert bit string to bytes directly
        if len(received_bit_string) % 8 != 0:
            status = "Warning: Bit string length is not a multiple of 8. Padding may occur or data might be corrupt."
            print(status)
        for i in range(0, len(received_bit_string), 8):
            byte_bits = received_bit_string[i:i+8]
            if len(byte_bits) < 8 : # Pad if needed for the last byte
                 byte_bits = byte_bits.ljust(8, '0')
            data_bytes.append(int(byte_bits, 2))
        try:
            return data_bytes.decode('utf-8', errors='replace'), status
        except UnicodeDecodeError as e:
            status = f"UnicodeDecodeError (no ECC): {e}. Data might be corrupted."
            print(f"  {status}")
            return data_bytes.decode('utf-8', errors='replace'), status

    else: # Unknown ECC method
        status = f"Warning: ECC method '{ecc_method}' for decoding not implemented. Assuming plain data."
        print(status)
        # Fallback to treat as plain bits
        if len(received_bit_string) % 8 != 0:
            print("  Warning: Bit string length is not a multiple of 8. Padding last byte.")
        for i in range(0, len(received_bit_string), 8):
            byte_bits = received_bit_string[i:i+8]
            if len(byte_bits) < 8 : byte_bits = byte_bits.ljust(8,'0')
            data_bytes.append(int(byte_bits, 2))
        try:
            return data_bytes.decode('utf-8', errors='replace'), status
        except UnicodeDecodeError as e:
            status = f"UnicodeDecodeError (unknown ECC fallback): {e}. Data might be corrupted."
            print(f"  {status}")
            return data_bytes.decode('utf-8', errors='replace'), status


# --- Placeholder functions for Signal interaction ---
def send_image_to_signal(image_path):
    """
    Placeholder for sending an image to Signal.
    In a real scenario, this would involve Signal automation (e.g., signal-cli).
    """
    print(f"\nAUTOMATION PLACEHOLDER: Please manually send the image '{image_path}' to 'Note to Self' in Signal.")
    # Here you could add a call to signal-cli send if it were configured
    # For now, we assume manual action and simulate success.
    return True

def download_image_from_signal(original_image_path, suggested_save_path):
    """
    Placeholder for downloading an image from Signal after it has been processed.
    Guides the user to manually save the file and confirms its existence.
    """
    print(f"\nAUTOMATION PLACEHOLDER: Please manually download the image that Signal processed.")
    print(f"(This image was originally sent from: '{original_image_path}')")
    print(f"Then, save it as: '{suggested_save_path}'.")
    print("IMPORTANT: Ensure you are saving the image in the correct format (e.g., if it's a PNG, save as PNG).")

    while True:
        user_input = input("Press Enter to confirm you have saved the image, or type 'skip' to abandon this processed image: ").strip().lower()
        if user_input == 'skip':
            print(f"Skipped saving/finding processed image for '{original_image_path}'.")
            return None
        elif user_input == "": # User pressed Enter
            if os.path.exists(suggested_save_path):
                print(f"Confirmed: Processed image found at '{suggested_save_path}'.")
                return suggested_save_path
            else:
                print(f"ERROR: File not found at '{suggested_save_path}'. Please ensure the path is correct or type 'skip'.")
        else:
            print("Invalid input. Press Enter or type 'skip'.")

def embed_message_lsb(image_path, secret_message, output_path, channel, ecc_method=None):
    """
    Embeds a secret message into the LSB of the specified color channel (R, G, or B) of a PNG image.
    The message is terminated with a special delimiter string.
    Optionally applies ECC to the payload before embedding.
    """
    if channel.upper() not in ['R', 'G', 'B']:
        print(f"Error: Invalid channel '{channel}'. Must be 'R', 'G', or 'B'.")
        return False

    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure it's in RGB format
        pixels = img.load()
        width, height = img.size

        # Apply ECC to the secret message if specified
        if ecc_method:
            print(f"Encoding message with ECC method: {ecc_method}")
            # ECC is applied to the message only; delimiter is appended raw.
            binary_payload_to_embed = encode_payload_with_ecc(secret_message, ecc_method)
        else:
            binary_payload_to_embed = encode_payload_with_ecc(secret_message, None) # Get raw bits

        if binary_payload_to_embed is None: # Should not happen with current encode_payload_with_ecc
             print("Error: Payload encoding returned None.")
             return False

        delimiter = "<-END->"
        binary_delimiter = ''.join(format(ord(char), '08b') for char in delimiter)

        # Full bit stream to embed: ECC'd payload + raw delimiter
        binary_secret_message_to_embed = binary_payload_to_embed + binary_delimiter

        message_len = len(binary_secret_message_to_embed)
        max_len = width * height  # Max bits we can store in one channel

        if message_len > max_len:
            print(f"Error: Message (payload + delimiter, ECC: {ecc_method}) too long to embed in this image's {channel.upper()} channel.")
            print(f"Message requires {message_len} bits, image has space for {max_len} bits.")
            return False

        data_idx = 0
        for y in range(height):
            for x in range(width):
                if data_idx < message_len:
                    r, g, b = pixels[x, y]
                    bit_to_embed = int(binary_secret_message[data_idx])

                    if channel.upper() == 'R':
                        r = (r & 0b11111110) | bit_to_embed
                    elif channel.upper() == 'G':
                        g = (g & 0b11111110) | bit_to_embed
                    elif channel.upper() == 'B':
                        b = (b & 0b11111110) | bit_to_embed

                    pixels[x, y] = (r, g, b)
                    data_idx += 1
                else:
                    break
            if data_idx >= message_len:
                break

        img.save(output_path, "PNG")
        print(f"Message embedded successfully into {output_path} using {channel.upper()} channel (ECC: {ecc_method}).")
        return True

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return False
    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return False

def extract_message_lsb(image_path, channel, ecc_method=None):
    """
    Extracts a secret message from the LSB of the specified color channel (R, G, or B) of a PNG image.
    Stops when it finds the delimiter "<-END->".
    Optionally applies ECC decoding to the extracted payload.
    """
    if channel.upper() not in ['R', 'G', 'B']:
        print(f"Error: Invalid channel '{channel}'. Must be 'R', 'G', or 'B'.")
        return None

    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = img.load()
        width, height = img.size

        raw_binary_extracted_payload_with_delimiter = ""
        delimiter = "<-END->"
        binary_delimiter = ''.join(format(ord(char), '08b') for char in delimiter)

        print(f"Attempting to extract message from {channel.upper()} channel of '{image_path}' (ECC: {ecc_method})...")

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                if channel.upper() == 'R':
                    raw_binary_extracted_payload_with_delimiter += str(r & 1)
                elif channel.upper() == 'G':
                    raw_binary_extracted_payload_with_delimiter += str(g & 1)
                elif channel.upper() == 'B':
                    raw_binary_extracted_payload_with_delimiter += str(b & 1)

                # Check for delimiter at reasonable intervals to avoid excessive endswith() calls on large strings
                if len(raw_binary_extracted_payload_with_delimiter) % (len(binary_delimiter) * 2) == 0 or \
                   len(raw_binary_extracted_payload_with_delimiter) > (width * height - len(binary_delimiter) -10): # near end
                    if raw_binary_extracted_payload_with_delimiter.endswith(binary_delimiter):
                        break
            if raw_binary_extracted_payload_with_delimiter.endswith(binary_delimiter):
                break
        
        delimiter_found_at = raw_binary_extracted_payload_with_delimiter.rfind(binary_delimiter)

        if delimiter_found_at != -1:
            binary_payload_before_delimiter = raw_binary_extracted_payload_with_delimiter[:delimiter_found_at]
            print(f"  Delimiter found. Raw payload bit length before delimiter: {len(binary_payload_before_delimiter)}")
        else:
            print("Warning: Delimiter not found. Extracted data might be incomplete or incorrect.")
            # If no delimiter, the whole thing is treated as payload. ECC might struggle or fail.
            binary_payload_before_delimiter = raw_binary_extracted_payload_with_delimiter
            if not binary_payload_before_delimiter:
                print("  No data bits extracted at all.")
                return "" # No data

        if ecc_method:
            print(f"Decoding payload with ECC method: {ecc_method}")
            extracted_message, ecc_status = decode_payload_with_ecc(binary_payload_before_delimiter, ecc_method)
            print(f"  ECC decoding status: {ecc_status}")
        else:
            # No ECC, convert raw bits (before delimiter) to string
            extracted_message, _ = decode_payload_with_ecc(binary_payload_before_delimiter, None) # Use None for direct conversion

        if extracted_message:
            print(f"Extracted message: {extracted_message}")
        else:
            print("No message content extracted/decoded (payload might have been empty or undecodable).")
        return extracted_message

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        return None

# --- JPEG Steganography (JSteg-like - Placeholder) ---
def embed_message_jpeg(image_path, secret_message, output_path):
    """
    (Placeholder) Embeds a secret message into a JPEG image.
    NOTE: True JSteg modifies DCT coefficients. Pillow does not easily expose these.
    This function currently is a placeholder and will just copy the image,
    optionally trying to maintain quality and EXIF.
    A real implementation would require a library like libjpeg or a custom solution.
    """
    print("\nWARNING: JPEG embedding is a placeholder. Message will not be truly embedded using JSteg.")
    print("Direct DCT coefficient manipulation is not supported by Pillow in a straightforward way.")

    try:
        img = Image.open(image_path)
        img.load() # Ensure image data is loaded

        # Try to preserve quality and EXIF if possible
        quality = img.info.get('quality', 90) # Default to 90 if not found
        exif_data = img.info.get('exif')

        # Conceptual: Add delimiter to message
        delimiter = "<-ENDJPEG->"
        # binary_secret_message = ''.join(format(ord(char), '08b') for char in secret_message)
        # binary_secret_message += ''.join(format(ord(char), '08b') for char in delimiter)
        # Actual embedding into DCT LSBs would go here if possible.

        params = {"quality": quality}
        if exif_data:
            params["exif"] = exif_data
        if img.info.get('icc_profile'):
            params["icc_profile"] = img.info.get('icc_profile')
        if img.info.get('progression'): # For progressive JPEGs
             params["progressive"] = True
        if img.info.get('jfif_unit') and img.info.get('jfif_density'):
            params["jfif_unit"] = img.info.get('jfif_unit')
            params["jfif_density"] = img.info.get('jfif_density')


        img.save(output_path, "jpeg", **params)
        print(f"Placeholder: Image copied to {output_path} (original message NOT embedded).")
        print(f"  Saved with quality: {quality}, EXIF preserved: {bool(exif_data)}")
        return True
    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}")
        return False
    except Exception as e:
        print(f"An error occurred during JPEG placeholder embedding: {e}")
        return False

def extract_message_jpeg(image_path):
    """
    (Placeholder) Extracts a secret message from a JPEG image.
    NOTE: See embed_message_jpeg for limitations.
    """
    print("\nWARNING: JPEG extraction is a placeholder. No message will be truly extracted.")
    # Conceptual: delimiter = "<-ENDJPEG->"
    # Actual extraction from DCT LSBs would go here.

    try:
        img = Image.open(image_path) # Open to check if it's a valid image
        img.load()
        print(f"Placeholder: Checked {image_path}. True extraction requires DCT access.")
    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred during JPEG placeholder extraction: {e}")
        return None

    return "[Placeholder - No message extracted]"

# --- JPEG Steganography (F5-like - Placeholder) ---
def embed_message_f5_jpeg(image_path, secret_message, output_path):
    """
    (Placeholder) Embeds a secret message into a JPEG image using F5 concepts.
    NOTE: True F5 algorithm (DCT coefficient selection, matrix encoding, modification) is NOT implemented.
    This function currently just copies the image.
    """
    print("\nWARNING: EXPERIMENTAL F5 Placeholder: True F5 algorithm (DCT coefficient selection, matrix encoding, modification) is NOT implemented.")
    print("This function currently just copies the image.")

    try:
        img = Image.open(image_path)
        img.load()

        quality = img.info.get('quality', 90)
        exif_data = img.info.get('exif')

        # Conceptual F5 Steps:
        # 1. Decompress JPEG to get DCT coefficients. (Requires specialized library like jpegio or modifying Pillow's internals)
        # 2. Convert secret_message to binary stream, add delimiter.
        # 3. Implement matrix encoding (e.g., (1,n,k) code) to determine bits per coefficient change.
        # 4. Iterate through DCT coefficients (typically AC coefficients, skipping DC).
        #    If a coefficient is non-zero and selected by matrix encoding logic:
        #       Decrement its absolute value to embed a bit (or bits).
        #       (e.g., if embedding '1', change +5 to +4; if embedding '0', no change, or use other logic based on matrix code).
        #       This is a simplification; F5's bit embedding is tied to the matrix code.
        # 5. Handle cases where coefficient becomes zero (F5 typically avoids this by not modifying coefficients that would become zero).
        # 6. Recompress JPEG with modified DCT coefficients, trying to match original quality and settings.

        params = {"quality": quality}
        if exif_data:
            params["exif"] = exif_data
        if img.info.get('icc_profile'):
            params["icc_profile"] = img.info.get('icc_profile')
        if img.info.get('progression'):
             params["progressive"] = True
        if img.info.get('jfif_unit') and img.info.get('jfif_density'):
            params["jfif_unit"] = img.info.get('jfif_unit')
            params["jfif_density"] = img.info.get('jfif_density')

        img.save(output_path, "jpeg", **params)
        print(f"Placeholder F5: Image copied to {output_path} (original message NOT embedded).")
        print(f"  Saved with quality: {quality}, EXIF preserved: {bool(exif_data)}")
        return True
    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}")
        return False
    except Exception as e:
        print(f"An error occurred during F5 JPEG placeholder embedding: {e}")
        return False

def extract_message_f5_jpeg(image_path):
    """
    (Placeholder) Extracts a message embedded with F5 concepts from a JPEG image.
    NOTE: See embed_message_f5_jpeg for limitations.
    """
    print("\nWARNING: EXPERIMENTAL F5 Placeholder: True F5 extraction logic is NOT implemented.")

    # Conceptual F5 Extraction Steps:
    # 1. Decompress JPEG to get DCT coefficients.
    # 2. Implement matrix decoding.
    # 3. Iterate through DCT coefficients, identify which ones were likely modified
    #    (based on F5 rules, e.g., values that could have been decremented, often non-zero AC coefficients).
    # 4. Reconstruct binary message stream until delimiter.
    # 5. Convert binary stream to text.

    try:
        img = Image.open(image_path)
        img.load()
        print(f"Placeholder F5: Checked {image_path}. True extraction requires DCT access and F5 logic.")
    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred during F5 JPEG placeholder extraction: {e}")
        return None

    return "[Placeholder F5 - No message extracted]"


def test_lsb_on_normalized_png_workflow():
    """
    Implements the J-202 workflow: Test LSB on Signal-normalized PNGs.
    """
    print("\n--- Starting LSB on Normalized PNG Test (J-202) ---")

    # a. Select Base Image
    base_image_path = input("Enter path to your base PNG image (e.g., from 'test_images/'): ").strip()
    if not os.path.exists(base_image_path):
        print(f"Error: Base image '{base_image_path}' not found.")
        return
    if not base_image_path.lower().endswith(".png"):
        print(f"Error: Base image '{base_image_path}' must be a PNG file.")
        return
    try:
        with Image.open(base_image_path) as img:
            if img.format != 'PNG':
                print(f"Error: Base image '{base_image_path}' is not a valid PNG (format: {img.format}).")
                return
    except Exception as e:
        print(f"Error opening or validating base image: {e}")
        return

    print_image_analysis(base_image_path, "Analysis for User-Provided Base Image")

    # b. Normalize Base Image
    base_image_dir = os.path.dirname(base_image_path)
    base_image_filename = os.path.basename(base_image_path)
    base_name, base_ext = os.path.splitext(base_image_filename)

    normalized_base_image_suggested_path = os.path.join(base_image_dir, f"{base_name}_normalized{base_ext}")

    print(f"\nStep 1: Normalizing the base image '{base_image_path}' through Signal...")
    send_image_to_signal(base_image_path)
    actual_normalized_path = download_image_from_signal(base_image_path, normalized_base_image_suggested_path)

    if not actual_normalized_path:
        print("Error: Normalization of base image failed or was skipped. This image is crucial for the test. Aborting workflow.")
        return

    print_image_analysis(actual_normalized_path, "Analysis for SIGNAL-NORMALIZED Base Image")

    # c. Define Test Message
    secret_payload = generate_test_payload(32)
    print(f"\nUsing test payload (32 bytes): '{secret_payload}'")

    # d. Iterate Through Channels (R, G, B)
    for channel_to_test in ['R', 'G', 'B']:
        print(f"\n--- Testing LSB for CHANNEL: {channel_to_test} ---")

        # i. Embed Message
        stego_image_channel_path = os.path.join(base_image_dir, f"{base_name}_normalized_lsb_{channel_to_test}{base_ext}")
        print(f"\nStep 2a: Embedding message into '{actual_normalized_path}' (Channel: {channel_to_test}). Output: '{stego_image_channel_path}'")
        if not embed_message_lsb(actual_normalized_path, secret_payload, stego_image_channel_path, channel_to_test):
            print(f"Error: Embedding failed for channel {channel_to_test}. Skipping this channel.")
            print("------------------------------------")
            continue
        print_image_analysis(stego_image_channel_path, f"Analysis for Stego Image (Channel {channel_to_test}) BEFORE Signal")

        # ii. Simulate Signal Processing for Stego Image
        received_stego_channel_suggested_path = os.path.join(base_image_dir, f"{base_name}_normalized_lsb_{channel_to_test}_signalprocessed{base_ext}")
        print(f"\nStep 2b: Simulating Signal processing for stego image '{stego_image_channel_path}'...")
        send_image_to_signal(stego_image_channel_path)
        actual_received_stego_path = download_image_from_signal(stego_image_channel_path, received_stego_channel_suggested_path)

        if not actual_received_stego_path:
            print(f"Error: Signal processing of stego image for channel {channel_to_test} failed or was skipped. Cannot perform extraction test for this channel.")
            print_image_analysis(stego_image_channel_path, f"Re-showing Analysis for Stego Image (Channel {channel_to_test}) as it was the last successfully saved version")
            print("------------------------------------")
            continue

        print_image_analysis(actual_received_stego_path, f"Analysis for Stego Image (Channel {channel_to_test}) AFTER Signal")

        # iii. Extract Message
        print(f"\nStep 2c: Extracting message from '{actual_received_stego_path}' (Channel: {channel_to_test})")
        extracted_message = extract_message_lsb(actual_received_stego_path, channel_to_test)

        if extracted_message is not None:
            print(f"Extracted: '{extracted_message}' (Length: {len(extracted_message)})")
            print(f"Original:  '{secret_payload}' (Length: {len(secret_payload)})")
            if extracted_message == secret_payload:
                print(f"SUCCESS: Data integrity confirmed for channel {channel_to_test}!")
            else:
                print(f"FAILURE: Data integrity FAILED for channel {channel_to_test}.")
                if len(extracted_message) != len(secret_payload):
                    print("  (Length mismatch)")
                # Further comparison could be added here, e.g., Hamming distance or % match
        else:
            print(f"FAILURE: Message extraction failed for channel {channel_to_test} (returned None).")

        print("------------------------------------")

    print("\nLSB on Normalized PNG test complete (J-202).")


# --- Interactive Usage Example ---

# --- Sub-Menu Handler Functions ---
def handle_image_analysis_submenu():
    while True:
        print("\n--- Image Analysis & Preparation Sub-Menu ---")
        print("1. Analyze Images from Directory")
        print("2. JPEG Idempotency Check (J-105)")
        print("3. Back to Main Menu")
        sub_choice = input("Enter your choice: ")

        if sub_choice == '1':
            analyze_images_in_directory_workflow()
        elif sub_choice == '2':
            jpeg_idempotency_check_workflow()
        elif sub_choice == '3':
            break
        else:
            print("Invalid choice, please try again.")

def handle_png_lsb_steganography_submenu(normalized_image_file, stego_image_file, received_image_file):
    while True:
        print("\n--- PNG LSB Steganography Sub-Menu ---")
        print("1. Embed Message in PNG (LSB)")
        print("2. Extract Message from Local PNG (LSB)")
        print("3. Extract Message from \"Received\" (Signal-Processed) PNG (LSB)")
        print("4. Test LSB on Normalized PNG (J-202 Workflow)")
        print("5. Back to Main Menu")
        sub_choice = input("Enter your choice: ")

        if sub_choice == '1':
            message = input("Enter secret message to embed: ")
            # Use pre-defined normalized_image_file or prompt for it
            if not os.path.exists(normalized_image_file):
                 print(f"Warning: Default normalized image '{normalized_image_file}' not found.")
                 current_normalized_image = input(f"Enter path to normalized PNG image (or press Enter to use default '{normalized_image_file}'): ").strip()
                 if not current_normalized_image: current_normalized_image = normalized_image_file # Fallback to default name even if not found initially
            else:
                current_normalized_image = normalized_image_file

            if not os.path.exists(current_normalized_image):
                 print(f"Error: Normalized image '{current_normalized_image}' not found. Please create or specify a valid file.")
                 continue

            current_stego_image = input(f"Enter path for output stego PNG (default: '{stego_image_file}'): ").strip() or stego_image_file

            chosen_channel_embed = ""
            while chosen_channel_embed.upper() not in ['R', 'G', 'B']:
                chosen_channel_embed = input("Enter channel to embed into (R, G, or B): ").strip().upper()

            ecc_choice_embed = input("Apply basic ECC (placeholder)? (y/n): ").strip().lower()
            ecc_method_to_use_embed = "basic_parity" if ecc_choice_embed == 'y' else None

            if embed_message_lsb(current_normalized_image, message, current_stego_image, chosen_channel_embed, ecc_method=ecc_method_to_use_embed):
                print(f"\n--- Next steps for '{current_stego_image}' (used {chosen_channel_embed} channel, ECC: {ecc_method_to_use_embed}) ---")
                send_image_to_signal(current_stego_image)

                current_received_image = input(f"Enter path to save downloaded 'received' stego image (default: '{received_image_file}'): ").strip() or received_image_file
                actual_received_path = download_image_from_signal(current_stego_image, current_received_image)
                if actual_received_path:
                    print(f"The processed image should now be at '{actual_received_path}'. You can use option 2.3 to extract from it.")
                else:
                    print(f"Skipped saving '{current_received_image}'.")
            else:
                print(f"Failed to embed message into '{current_normalized_image}'.")

        elif sub_choice == '2':
            print(f"\n--- Extracting from Local PNG (e.g., '{stego_image_file}') ---")
            local_stego_path = input(f"Enter path to local stego PNG (default: '{stego_image_file}'): ").strip() or stego_image_file
            if not os.path.exists(local_stego_path):
                print(f"Error: File not found: {local_stego_path}")
                continue

            chosen_channel_extract = ""
            while chosen_channel_extract.upper() not in ['R', 'G', 'B']:
                chosen_channel_extract = input("Enter channel to extract from (R, G, or B): ").strip().upper()

            ecc_choice_extract = input("Was basic ECC (placeholder) used for embedding? (y/n): ").strip().lower()
            ecc_method_to_use_extract = "basic_parity" if ecc_choice_extract == 'y' else None
            extract_message_lsb(local_stego_path, chosen_channel_extract, ecc_method=ecc_method_to_use_extract)

        elif sub_choice == '3':
            print(f"\n--- Extracting from 'Received' PNG (e.g., '{received_image_file}') ---")
            received_stego_path = input(f"Enter path to 'received' stego PNG (default: '{received_image_file}'): ").strip() or received_image_file
            if not os.path.exists(received_stego_path):
                print(f"Error: File not found: {received_stego_path}")
                continue

            chosen_channel_extract_recv = ""
            while chosen_channel_extract_recv.upper() not in ['R', 'G', 'B']:
                chosen_channel_extract_recv = input("Enter channel to extract from (R, G, or B): ").strip().upper()

            ecc_choice_extract_recv = input("Was basic ECC (placeholder) used for embedding? (y/n): ").strip().lower()
            ecc_method_to_use_extract_recv = "basic_parity" if ecc_choice_extract_recv == 'y' else None
            extract_message_lsb(received_stego_path, chosen_channel_extract_recv, ecc_method=ecc_method_to_use_extract_recv)

        elif sub_choice == '4':
            test_lsb_on_normalized_png_workflow()
        elif sub_choice == '5':
            break
        else:
            print("Invalid choice, please try again.")

def handle_jpeg_steganography_submenu():
    while True:
        print("\n--- JPEG Steganography Sub-Menu (Experimental Placeholders) ---")
        print("1. Embed/Extract - JSteg Placeholder")
        print("2. Embed/Extract - F5 Placeholder")
        print("3. Test JPEG Stego on Normalized JPEG (J-303 - JSteg/F5 Placeholders)")
        print("4. Back to Main Menu")
        sub_choice = input("Enter your choice: ")

        if sub_choice == '1': # JSteg Placeholder Embed/Extract
            action = input("Choose action for JSteg JPEG placeholder: (embed/extract): ").strip().lower()
            if action == "embed":
                jpeg_base_path = input("Enter path to base JPEG image: ").strip()
                if not (jpeg_base_path.lower().endswith(".jpg") or jpeg_base_path.lower().endswith(".jpeg")):
                    print("Error: Base image must be a .jpg or .jpeg file.")
                    continue
                if not os.path.exists(jpeg_base_path):
                    print(f"Error: File not found at '{jpeg_base_path}'")
                    continue
                secret_msg = input("Enter secret message to embed: ")
                output_dir = os.path.dirname(jpeg_base_path)
                base_name, ext = os.path.splitext(os.path.basename(jpeg_base_path))
                jpeg_output_stego_path = os.path.join(output_dir, f"{base_name}_jsteg{ext}")
                if embed_message_jpeg(jpeg_base_path, secret_msg, jpeg_output_stego_path):
                    print(f"Placeholder JSteg JPEG saved to '{jpeg_output_stego_path}'.")
                    print("\nNow, guide this image through Signal:")
                    send_image_to_signal(jpeg_output_stego_path)
                    received_jpeg_stego_path_suggested = os.path.join(output_dir, f"{base_name}_jsteg_signalprocessed{ext}")
                    actual_received_jpeg_path = download_image_from_signal(jpeg_output_stego_path, received_jpeg_stego_path_suggested)
                    if actual_received_jpeg_path:
                        print(f"Processed JSteg JPEG (placeholder) saved as '{actual_received_jpeg_path}'. Use extract option on this.")
            elif action == "extract":
                jpeg_stego_path = input("Enter path to JSteg stego JPEG image: ").strip()
                if not (jpeg_stego_path.lower().endswith(".jpg") or jpeg_stego_path.lower().endswith(".jpeg")):
                    print("Error: Stego image must be a .jpg or .jpeg file.")
                    continue
                if not os.path.exists(jpeg_stego_path):
                    print(f"Error: File not found at '{jpeg_stego_path}'")
                    continue
                extracted_msg = extract_message_jpeg(jpeg_stego_path)
                print(f"Message from JSteg JPEG (placeholder): {extracted_msg}")
            else:
                print("Invalid action for JSteg. Choose 'embed' or 'extract'.")

        elif sub_choice == '2': # F5 Placeholder Embed/Extract
            action = input("Choose action for F5 JPEG placeholder: (embed/extract): ").strip().lower()
            if action == "embed":
                jpeg_base_path = input("Enter path to base JPEG image: ").strip()
                if not (jpeg_base_path.lower().endswith(".jpg") or jpeg_base_path.lower().endswith(".jpeg")):
                    print("Error: Base image must be a .jpg or .jpeg file.")
                    continue
                if not os.path.exists(jpeg_base_path):
                    print(f"Error: File not found at '{jpeg_base_path}'")
                    continue
                secret_msg = input("Enter secret message to embed: ")
                output_dir = os.path.dirname(jpeg_base_path)
                base_name, ext = os.path.splitext(os.path.basename(jpeg_base_path))
                jpeg_output_f5_path = os.path.join(output_dir, f"{base_name}_f5{ext}")
                if embed_message_f5_jpeg(jpeg_base_path, secret_msg, jpeg_output_f5_path):
                    print(f"Placeholder F5 stego JPEG saved to '{jpeg_output_f5_path}'.")
                    print("\nNow, guide this image through Signal:")
                    send_image_to_signal(jpeg_output_f5_path)
                    received_jpeg_f5_path_suggested = os.path.join(output_dir, f"{base_name}_f5_signalprocessed{ext}")
                    actual_received_jpeg_f5_path = download_image_from_signal(jpeg_output_f5_path, received_jpeg_f5_path_suggested)
                    if actual_received_jpeg_f5_path:
                        print(f"Processed F5 JPEG (placeholder) saved as '{actual_received_jpeg_f5_path}'. Use extract option on this.")
            elif action == "extract":
                jpeg_f5_stego_path = input("Enter path to F5 stego JPEG image: ").strip()
                if not (jpeg_f5_stego_path.lower().endswith(".jpg") or jpeg_f5_stego_path.lower().endswith(".jpeg")):
                    print("Error: Stego image must be a .jpg or .jpeg file.")
                    continue
                if not os.path.exists(jpeg_f5_stego_path):
                    print(f"Error: File not found at '{jpeg_f5_stego_path}'")
                    continue
                extracted_msg = extract_message_f5_jpeg(jpeg_f5_stego_path)
                print(f"Message from F5 JPEG (placeholder): {extracted_msg}")
            else:
                print("Invalid action for F5. Choose 'embed' or 'extract'.")

        elif sub_choice == '3':
            test_jpeg_stego_on_normalized_jpeg_workflow()
        elif sub_choice == '4':
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    """
    Workflow to analyze images in a specified directory based on extensions.
    This refactors the previous 'Analyze PNGs from test_images' functionality.
    """
    print("\n--- Analyze Images from Directory ---")
    test_image_dir_input = input("Enter directory to analyze (e.g., test_images, test_images_jpeg): ").strip()

    if not test_image_dir_input:
        print("No directory entered. Using 'test_images' as default.")
        test_image_dir_input = "test_images" # Default if empty

    if not os.path.isdir(test_image_dir_input):
        print(f"Error: Directory '{test_image_dir_input}' not found.")
        return

    extensions_input = input("Enter image extensions to analyze (comma-separated, e.g., png, jpg, jpeg) [Default: png,jpg,jpeg]: ").strip().lower()
    if not extensions_input:
        extensions_to_check = ["png", "jpg", "jpeg"]
    else:
        extensions_to_check = [ext.strip().lstrip('.') for ext in extensions_input.split(',')]

    print(f"\n--- Analyzing images in '{test_image_dir_input}' with extensions: {', '.join(extensions_to_check)} ---")

    # Filter out potential processed image files from the main list to avoid analyzing them as originals
    # This simple suffix check might need refinement if filenames are complex
    all_files_in_dir = os.listdir(test_image_dir_input)
    potential_original_files = [
        f for f in all_files_in_dir
        if not (f.lower().endswith("_signalprocessed.png") or \
                f.lower().endswith("_signalprocessed.jpg") or \
                f.lower().endswith("_signalprocessed.jpeg"))
    ]

    image_files = sorted([
        f for f in potential_original_files
        if any(f.lower().endswith("." + ext) for ext in extensions_to_check)
    ])

    if not image_files:
        print(f"No suitable image files found in '{test_image_dir_input}' with specified extensions.")
        return

    for filename in image_files:
        original_image_path = os.path.join(test_image_dir_input, filename)

        if not os.path.isfile(original_image_path):
            print(f"Skipping '{filename}', not a file.")
            continue

        try:
            with Image.open(original_image_path) as img_check:
                # Basic check if Pillow can open it; format specific checks done by print_image_analysis
                pass
            print_image_analysis(original_image_path, header_message=f"Analysis for ORIGINAL: {filename}")
        except Exception as e:
            print(f"Skipping '{filename}', cannot open as image or not a recognized format: {e}")
            continue

        base_name, ext = os.path.splitext(filename)
        # Adapt suffix to the original extension
        processed_image_suffix = f"_signalprocessed{ext}"
        processed_filename = base_name + processed_image_suffix
        suggested_processed_image_path = os.path.join(test_image_dir_input, processed_filename)

        send_image_to_signal(original_image_path)
        actual_processed_image_path = download_image_from_signal(original_image_path, suggested_processed_image_path)

        if actual_processed_image_path:
            try:
                # No need to check format strictly here, as Signal might convert.
                # print_image_analysis will report its actual format.
                print_image_analysis(actual_processed_image_path, header_message=f"Analysis for PROCESSED: {os.path.basename(actual_processed_image_path)}")
            except FileNotFoundError:
                print(f"Error: Processed image file '{actual_processed_image_path}' not found. Skipping analysis.")
            except Exception as e:
                print(f"Error opening or analyzing processed image '{actual_processed_image_path}': {e}")
        else:
            print(f"Analysis for processed version of '{filename}' was skipped or the file was not found at '{suggested_processed_image_path}'.")

        print("\n------------------------------------")

    print("Image analysis for directory complete.")

def jpeg_idempotency_check_workflow():
    """
    Implements the J-105 workflow: Check JPEG idempotency after Signal processing.
    """
    print("\n--- Starting JPEG Idempotency Check (J-105) ---")

    # a. Select Base JPEG Image
    base_image_path = input("Enter path to your base JPEG image (e.g., from 'test_images_jpeg/'): ").strip()
    if not os.path.exists(base_image_path):
        print(f"Error: Base image '{base_image_path}' not found.")
        return

    is_jpeg = False
    if base_image_path.lower().endswith(".jpg") or base_image_path.lower().endswith(".jpeg"):
        try:
            with Image.open(base_image_path) as img:
                if img.format == 'JPEG':
                    is_jpeg = True
                else:
                    print(f"Error: Base image '{base_image_path}' is not a valid JPEG (Pillow format: {img.format}).")
                    return
        except Exception as e:
            print(f"Error opening or validating base image as JPEG: {e}")
            return
    else:
        print(f"Error: Base image '{base_image_path}' must be a .jpg or .jpeg file.")
        return

    if not is_jpeg: # Should be caught above, but as a safeguard
        print(f"Error: File '{base_image_path}' is not recognized as JPEG. Aborting.")
        return

    print_image_analysis(base_image_path, "Analysis for User-Provided Base JPEG Image")

    base_image_dir = os.path.dirname(base_image_path)
    base_image_filename = os.path.basename(base_image_path)
    base_name, base_ext = os.path.splitext(base_image_filename) # base_ext will include '.'

    # b. First Pass Normalization
    normalized_1_suggested_path = os.path.join(base_image_dir, f"{base_name}_norm1{base_ext}")
    print(f"\nStep 1: First Signal normalization pass for '{base_image_path}'...")
    send_image_to_signal(base_image_path)
    actual_normalized_1_path = download_image_from_signal(base_image_path, normalized_1_suggested_path)

    if not actual_normalized_1_path:
        print("Error: First normalization pass failed or was skipped. Aborting idempotency check.")
        return

    props_norm1 = get_image_properties(actual_normalized_1_path)
    hash_norm1 = calculate_file_hash(actual_normalized_1_path)
    print_image_analysis(actual_normalized_1_path, "Analysis for FIRST Normalized Image (Norm1)")

    # c. Second Pass Normalization
    normalized_2_suggested_path = os.path.join(base_image_dir, f"{base_name}_norm2{base_ext}")
    print(f"\nStep 2: Second Signal normalization pass, using '{actual_normalized_1_path}' as input...")
    send_image_to_signal(actual_normalized_1_path) # Send the first normalized image
    actual_normalized_2_path = download_image_from_signal(actual_normalized_1_path, normalized_2_suggested_path)

    if not actual_normalized_2_path:
        print("Error: Second normalization pass failed or was skipped. Cannot complete idempotency check.")
        print("Properties of the first normalized image for reference:")
        if props_norm1:
             for key, value in props_norm1.items(): print(f"  {key}: {value}")
        if hash_norm1: print(f"  Hash: {hash_norm1}")
        return

    props_norm2 = get_image_properties(actual_normalized_2_path)
    hash_norm2 = calculate_file_hash(actual_normalized_2_path)
    print_image_analysis(actual_normalized_2_path, "Analysis for SECOND Normalized Image (Norm2)")

    # d. Compare Results
    print("\n--- Idempotency Comparison ---")
    print(f"Hash of Norm1 ('{os.path.basename(actual_normalized_1_path)}'): {hash_norm1}")
    print(f"Hash of Norm2 ('{os.path.basename(actual_normalized_2_path)}'): {hash_norm2}")

    if hash_norm1 == hash_norm2:
        print("\nIDEMPOTENCY LIKELY CONFIRMED: Processing the image a second time resulted in no further changes (hashes match).")
    else:
        print("\nIDEMPOTENCY NOT CONFIRMED: Processing the image a second time resulted in further changes (hashes differ).")
        if props_norm1 and props_norm2:
            print("\nKey Property Comparison (Norm1 vs Norm2):")
            for key in props_norm1.keys():
                val1 = props_norm1.get(key)
                val2 = props_norm2.get(key)
                if isinstance(val1, dict) and 'info' in key: # Don't deep compare full info dicts for this summary
                    print(f"  {key.capitalize()}: ... (see full analysis above)")
                    continue
                if isinstance(val1, list) and 'quantization' in key: # Quantization tables are lists of lists/arrays
                     # Simple direct comparison might be too verbose if they differ slightly
                     # Check if they are identical byte-for-byte effectively
                    if str(val1) == str(val2):
                         print(f"  {key.capitalize()}: Identical")
                    else:
                         print(f"  {key.capitalize()}: Norm1={str(val1)[:60]}... vs Norm2={str(val2)[:60]}... (DIFFER)")
                    continue

                if val1 != val2:
                    print(f"  {key.capitalize()}: Norm1='{val1}' vs Norm2='{val2}' (DIFFER)")
                else:
                    print(f"  {key.capitalize()}: '{val1}' (Identical)")
            # Check if keys are different
            if set(props_norm1.keys()) != set(props_norm2.keys()):
                print("  Property sets are different:")
                print(f"    Keys unique to Norm1: {set(props_norm1.keys()) - set(props_norm2.keys())}")
                print(f"    Keys unique to Norm2: {set(props_norm2.keys()) - set(props_norm1.keys())}")

    print("\nJPEG Idempotency Check complete (J-105).")

def test_jpeg_stego_on_normalized_jpeg_workflow():
    """
    Implements the J-303 workflow: Test (placeholder) JPEG Stego on Signal-normalized JPEGs.
    """
    print("\n--- Starting Test JPEG Stego on Normalized JPEG (J-303) ---")

    # a. Select Base JPEG Image
    base_image_path = input("Enter path to your base JPEG image (e.g., from 'test_images_jpeg/'): ").strip()
    if not os.path.exists(base_image_path):
        print(f"Error: Base image '{base_image_path}' not found.")
        return

    is_jpeg = False
    if base_image_path.lower().endswith(".jpg") or base_image_path.lower().endswith(".jpeg"):
        try:
            with Image.open(base_image_path) as img:
                if img.format == 'JPEG':
                    is_jpeg = True
                else:
                    print(f"Error: Base image '{base_image_path}' is not a valid JPEG (Pillow format: {img.format}).")
                    return
        except Exception as e:
            print(f"Error opening or validating base image as JPEG: {e}")
            return
    else:
        print(f"Error: Base image '{base_image_path}' must be a .jpg or .jpeg file.")
        return
    if not is_jpeg: return # Should be caught above

    print_image_analysis(base_image_path, "Analysis for User-Provided Base JPEG")

    # b. Normalize Base JPEG
    base_image_dir = os.path.dirname(base_image_path)
    base_image_filename = os.path.basename(base_image_path)
    base_name, base_ext = os.path.splitext(base_image_filename)

    normalized_base_jpeg_suggested_path = os.path.join(base_image_dir, f"{base_name}_normalized{base_ext}")
    print(f"\nStep 1: Normalizing the base JPEG '{base_image_path}' through Signal...")
    send_image_to_signal(base_image_path)
    actual_normalized_path = download_image_from_signal(base_image_path, normalized_base_jpeg_suggested_path)

    if not actual_normalized_path:
        print("Error: Normalization of base JPEG failed or was skipped. Aborting J-303 workflow.")
        return
    print_image_analysis(actual_normalized_path, "Analysis for SIGNAL-NORMALIZED Base JPEG")

    # c. Define Test Message
    secret_payload = generate_test_payload(32)
    print(f"\nUsing test payload (32 bytes): '{secret_payload}'")

    # Select Stego Type
    stego_type = ""
    while stego_type not in ["jsteg", "f5"]:
        stego_type = input("Enter JPEG steganography type for this test (jsteg / f5): ").strip().lower()
        if stego_type not in ["jsteg", "f5"]:
            print("Invalid type. Please enter 'jsteg' or 'f5'.")

    stego_func_embed = embed_message_jpeg if stego_type == "jsteg" else embed_message_f5_jpeg
    stego_func_extract = extract_message_jpeg if stego_type == "jsteg" else extract_message_f5_jpeg
    stego_name_suffix = "_jsteg" if stego_type == "jsteg" else "_f5"

    # d. Embed Message (Placeholder)
    stego_jpeg_path = os.path.join(base_image_dir, f"{base_name}_normalized{stego_name_suffix}{base_ext}")
    print(f"\nStep 2a: Embedding message into '{actual_normalized_path}' using '{stego_type}' placeholder. Output: '{stego_jpeg_path}'")
    if not stego_func_embed(actual_normalized_path, secret_payload, stego_jpeg_path):
        print(f"Error: Placeholder JPEG embedding ({stego_type}) failed for '{actual_normalized_path}'. Aborting this test.")
        return
    print_image_analysis(stego_jpeg_path, f"Analysis for Stego JPEG ({stego_type} Placeholder Embedded) BEFORE Signal")

    # e. Simulate Signal Processing for Stego JPEG
    received_stego_jpeg_suggested_path = os.path.join(base_image_dir, f"{base_name}_normalized{stego_name_suffix}_signalprocessed{base_ext}")
    print(f"\nStep 2b: Simulating Signal processing for stego JPEG '{stego_jpeg_path}'...")
    send_image_to_signal(stego_jpeg_path)
    actual_received_stego_path = download_image_from_signal(stego_jpeg_path, received_stego_jpeg_suggested_path)

    if not actual_received_stego_path:
        print(f"Error: Signal processing of stego JPEG failed or was skipped. Cannot perform extraction test.")
        print_image_analysis(stego_jpeg_path, f"Re-showing Analysis for Stego JPEG ({stego_type} Placeholder Embedded) as it was the last successfully saved version")
        return
    print_image_analysis(actual_received_stego_path, f"Analysis for Stego JPEG ({stego_type} Placeholder Embedded) AFTER Signal")

    # f. Extract Message (Placeholder)
    print(f"\nStep 2c: Extracting message from '{actual_received_stego_path}' using '{stego_type}' placeholder")
    extracted_message = stego_func_extract(actual_received_stego_path)

    print(f"Extracted ({stego_type} placeholder): '{extracted_message}'")
    print(f"Original payload:                 '{secret_payload}'")
    if extracted_message == secret_payload:
        # This will currently always fail with placeholder, which is expected.
        print(f"SUCCESS: Data integrity confirmed for {stego_type}! (Note: This is unexpected with current placeholders).")
    else:
        print(f"FAILURE: Data integrity NOT confirmed for {stego_type}. (This is expected with current placeholders).")
        print(f"           The placeholder {stego_type} JPEG steganography does not actually embed/extract data.")

    # g. Completion Message
    print(f"\nJPEG Stego ({stego_type}) on Normalized JPEG test complete (J-303).")


if __name__ == "__main__":
    # --- STEP 1: Normalize your base image through Signal ---
    # --- Global filenames for default LSB operations ---
    # These are used as defaults in the PNG LSB Steganography sub-menu.
    # User will be prompted if these defaults are not found or if they wish to change them.
    default_normalized_image_file = "normalized_image.png"
    default_stego_image_file = "stego_image.png"
    default_received_image_file = "received_stego_image.png"

    # Initial check for the default normalized image (optional, provides early user feedback)
    if not os.path.exists(default_normalized_image_file):
        print(f"FYI: Default normalized image '{default_normalized_image_file}' not found.")
        print("You may need to create it or specify image paths manually in relevant options.")

    while True:
        print("\n--- Steganography Test Suite: Main Menu ---")
        print("1. Image Analysis & Preparation")
        print("2. PNG LSB Steganography")
        print("3. JPEG Steganography (Experimental Placeholders)")
        print("4. Exit")
        main_choice = input("Enter your choice: ")

        if main_choice == '1':
            handle_image_analysis_submenu()
        elif main_choice == '2':
            handle_png_lsb_steganography_submenu(
                default_normalized_image_file,
                default_stego_image_file,
                default_received_image_file
            )
        elif main_choice == '3':
            handle_jpeg_steganography_submenu()
        elif main_choice == '4':
            print("Exiting test suite.")
            break
        else:
            print("Invalid choice, please try again.")
