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

def embed_message_lsb(image_path, secret_message, output_path, channel):
    """
    Embeds a secret message into the LSB of the specified color channel (R, G, or B) of a PNG image.
    The message is terminated with a special delimiter string.
    """
    if channel.upper() not in ['R', 'G', 'B']:
        print(f"Error: Invalid channel '{channel}'. Must be 'R', 'G', or 'B'.")
        return False

    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure it's in RGB format
        pixels = img.load()
        width, height = img.size

        delimiter = "<-END->"
        binary_secret_message = ''.join(format(ord(char), '08b') for char in secret_message)
        binary_secret_message += ''.join(format(ord(char), '08b') for char in delimiter)

        message_len = len(binary_secret_message)
        # Max bits we can store in one channel of the image
        max_len = width * height

        if message_len > max_len:
            print(f"Error: Message too long to embed in this image's {channel.upper()} channel.")
            print(f"Message requires {message_len} bits, image has space for {max_len} bits in the {channel.upper()} channel.")
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
        print(f"Message embedded successfully into {output_path} using {channel.upper()} channel.")
        return True

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return False
    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return False

def extract_message_lsb(image_path, channel):
    """
    Extracts a secret message from the LSB of the specified color channel (R, G, or B) of a PNG image.
    Stops when it finds the delimiter "<-END->".
    """
    if channel.upper() not in ['R', 'G', 'B']:
        print(f"Error: Invalid channel '{channel}'. Must be 'R', 'G', or 'B'.")
        return None

    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = img.load()
        width, height = img.size

        binary_extracted_message = ""
        delimiter = "<-END->"
        binary_delimiter = ''.join(format(ord(char), '08b') for char in delimiter)
        delimiter_found = False

        print(f"Attempting to extract message from {channel.upper()} channel of '{image_path}'...")

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                if channel.upper() == 'R':
                    binary_extracted_message += str(r & 1)
                elif channel.upper() == 'G':
                    binary_extracted_message += str(g & 1)
                elif channel.upper() == 'B':
                    binary_extracted_message += str(b & 1)

                if binary_extracted_message.endswith(binary_delimiter):
                    binary_extracted_message = binary_extracted_message[:-len(binary_delimiter)]
                    delimiter_found = True
                    break
            if delimiter_found:
                break
        
        if not delimiter_found:
            print("Warning: Delimiter not found. Extracted data might be incomplete or incorrect.")

        extracted_message = ""
        for i in range(0, len(binary_extracted_message), 8):
            byte = binary_extracted_message[i:i+8]
            if len(byte) == 8:
                extracted_message += chr(int(byte, 2))
            else:
                pass

        if extracted_message:
            print(f"Extracted message: {extracted_message}")
        else:
            print("No message found or extracted (delimiter might have been found immediately or message was empty).")
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

def analyze_images_in_directory_workflow():
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

    # d. Embed Message (Placeholder)
    stego_jpeg_path = os.path.join(base_image_dir, f"{base_name}_normalized_jsteg{base_ext}")
    print(f"\nStep 2a: Embedding message into '{actual_normalized_path}'. Output: '{stego_jpeg_path}'")
    if not embed_message_jpeg(actual_normalized_path, secret_payload, stego_jpeg_path):
        print(f"Error: Placeholder JPEG embedding failed for '{actual_normalized_path}'. Aborting this test.")
        return
    print_image_analysis(stego_jpeg_path, "Analysis for Stego JPEG (Placeholder Embedded) BEFORE Signal")

    # e. Simulate Signal Processing for Stego JPEG
    received_stego_jpeg_suggested_path = os.path.join(base_image_dir, f"{base_name}_normalized_jsteg_signalprocessed{base_ext}")
    print(f"\nStep 2b: Simulating Signal processing for stego JPEG '{stego_jpeg_path}'...")
    send_image_to_signal(stego_jpeg_path)
    actual_received_stego_path = download_image_from_signal(stego_jpeg_path, received_stego_jpeg_suggested_path)

    if not actual_received_stego_path:
        print(f"Error: Signal processing of stego JPEG failed or was skipped. Cannot perform extraction test.")
        print_image_analysis(stego_jpeg_path, "Re-showing Analysis for Stego JPEG (Placeholder Embedded) as it was the last successfully saved version")
        return
    print_image_analysis(actual_received_stego_path, "Analysis for Stego JPEG (Placeholder Embedded) AFTER Signal")

    # f. Extract Message (Placeholder)
    print(f"\nStep 2c: Extracting message from '{actual_received_stego_path}'")
    extracted_message = extract_message_jpeg(actual_received_stego_path)

    print(f"Extracted (placeholder): '{extracted_message}'")
    print(f"Original payload:      '{secret_payload}'")
    if extracted_message == secret_payload:
        # This will currently always fail with placeholder, which is expected.
        print("SUCCESS: Data integrity confirmed! (Note: This is unexpected with current placeholders).")
    else:
        print("FAILURE: Data integrity NOT confirmed. (This is expected with current placeholders).")
        print("           The placeholder JPEG steganography does not actually embed/extract data.")

    # g. Completion Message
    print("\nJPEG Stego on Normalized JPEG test complete (J-303).")


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
        print("4. Analyze Images from Directory") # Renamed
        print("5. Test LSB on Normalized PNG (J-202)")
        print("6. JPEG Idempotency Check (J-105)")
        print("7. Embed/Extract message in JPEG (Experimental)")
        print("8. Test JPEG Stego on Normalized JPEG (J-303)")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            message = input("Enter secret message to embed: ")
            if not normalized_image_file:
                print("Please define 'normalized_image_file' first.")
                continue

            chosen_channel_embed = ""
            while chosen_channel_embed.upper() not in ['R', 'G', 'B']:
                chosen_channel_embed = input("Enter channel to embed into (R, G, or B): ").strip().upper()
                if chosen_channel_embed.upper() not in ['R', 'G', 'B']:
                    print("Invalid channel. Please enter R, G, or B.")

            if embed_message_lsb(normalized_image_file, message, stego_image_file, chosen_channel_embed):
                print(f"\n--- Next steps for '{stego_image_file}' (used {chosen_channel_embed} channel) ---")
                send_image_to_signal(stego_image_file)
                print(f"\nNow, prepare to receive the image back from Signal.")
                actual_received_path = download_image_from_signal(stego_image_file, received_image_file)
                if actual_received_path:
                    print(f"The processed image should now be at '{actual_received_path}'. You can use option 3 to extract the message from it (remember to use channel {chosen_channel_embed}).")
                else:
                    print(f"Skipped saving '{received_image_file}'. You will need to manually ensure it exists to use option 3.")
            else:
                print(f"Failed to embed message into '{normalized_image_file}' using channel {chosen_channel_embed}.")

        elif choice == '2':
            print(f"\n--- Extracting from local '{stego_image_file}' ---")
            chosen_channel_extract_local = ""
            while chosen_channel_extract_local.upper() not in ['R', 'G', 'B']:
                chosen_channel_extract_local = input("Enter channel to extract from (R, G, or B): ").strip().upper()
                if chosen_channel_extract_local.upper() not in ['R', 'G', 'B']:
                    print("Invalid channel. Please enter R, G, or B.")
            extract_message_lsb(stego_image_file, chosen_channel_extract_local)
        elif choice == '3':
            print(f"\n--- Extracting from '{received_image_file}' (after Signal) ---")
            chosen_channel_extract_signal = ""
            while chosen_channel_extract_signal.upper() not in ['R', 'G', 'B']:
                chosen_channel_extract_signal = input("Enter channel to extract from (R, G, or B): ").strip().upper()
                if chosen_channel_extract_signal.upper() not in ['R', 'G', 'B']:
                    print("Invalid channel. Please enter R, G, or B.")
            extract_message_lsb(received_image_file, chosen_channel_extract_signal)
        elif choice == '4': # Analyze PNGs
            test_image_dir = "test_images"
            processed_image_suffix = "_signalprocessed.png"

            if not os.path.isdir(test_image_dir):
                print(f"Error: Test image directory '{test_image_dir}' not found.")
                continue

            print(f"\n--- Analyzing PNGs in '{test_image_dir}' ---")
            image_files = sorted([f for f in os.listdir(test_image_dir) if f.lower().endswith(".png") and not f.lower().endswith(processed_image_suffix)])

            if not image_files:
                print(f"No suitable PNG files (not ending with '{processed_image_suffix}') found in '{test_image_dir}'.")
                continue

            for filename in image_files:
                original_image_path = os.path.join(test_image_dir, filename)

                # Check if it's a file and can be opened as an image (basic PNG check)
                if not os.path.isfile(original_image_path):
                    print(f"Skipping '{filename}', not a file.")
                    continue
                try:
                    with Image.open(original_image_path) as img_check:
                        if img_check.format != "PNG":
                            print(f"Skipping '{filename}', not a PNG file (format: {img_check.format}).")
                            continue
                except Exception as e:
                    print(f"Skipping '{filename}', cannot open as image or not a PNG: {e}")
                    continue

                print_image_analysis(original_image_path, header_message=f"Analysis for ORIGINAL: {filename}")

                base_name, ext = os.path.splitext(filename)
                processed_filename = base_name + processed_image_suffix
                processed_image_path = os.path.join(test_image_dir, processed_filename)

                print("\nMANUAL STEP REQUIRED:")
                print(f"1. Send the image '{original_image_path}' to 'Note to Self' in Signal.")
                print(f"2. Download the image Signal sends back (it might be auto-converted to JPG or other format by Signal).")
                print(f"3. If it's not a PNG, convert it back to PNG format.")
                print(f"4. Save this processed PNG image as '{processed_image_path}'.")
                input("Press Enter to continue AFTER you have saved the processed image...")

                if os.path.exists(processed_image_path):
                    try:
                        with Image.open(processed_image_path) as img_check_processed:
                            if img_check_processed.format != "PNG":
                                print(f"Warning: '{processed_image_path}' is not a PNG file (format: {img_check_processed.format}). Analysis might be inaccurate.")
                                # Still proceed with analysis as it might be an image file just misnamed.
                            print_image_analysis(processed_image_path, header_message=f"Analysis for PROCESSED: {os.path.basename(processed_image_path)}")
                    except Exception as e:
                         print(f"Error opening or analyzing processed image '{processed_image_path}': {e}")
                else:
                    print(f"Processed image '{processed_image_path}' not found. Skipping its analysis.")
                print("\n------------------------------------")

            print("PNG analysis complete.")

        elif choice == '5': # Test LSB on Normalized PNG (J-202)
            test_lsb_on_normalized_png_workflow()
        elif choice == '6': # Exit
            break
        else:
            print("Invalid choice. Please try again.")
