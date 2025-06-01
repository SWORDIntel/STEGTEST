# STEGTEST
Steganographical Test Suite for a variety of image processing and steganography functions.

## Usage / Running the Script

This script uses a hierarchical menu system. When you run `python stego_test.py`:
1.  You will be presented with a **Main Menu**.
    *   **1. Image Analysis & Preparation**
    *   **2. PNG LSB Steganography**
    *   **3. JPEG Steganography (Experimental Placeholders)**
    *   **4. Exit**
2.  Choose a category by entering the corresponding number.
3.  This will either lead to a **Sub-Menu** with specific actions or execute a direct test workflow (like Exit).
4.  Each sub-menu has an option to return to the Main Menu.

Please follow the prompts for each selected action. Default filenames are provided for some operations (e.g., for LSB PNG steganography), but you can usually specify your own paths.

Ensure that any required test images (e.g., in `test_images/` or `test_images_jpeg/`) are present, or provide valid paths when prompted.

## Manual Log Sections

This README includes sections for manually recording your findings from the various tests available in `stego_test.py`. After running a test, please fill in your observations in the relevant tables/templates below.

---

## PNG Image Processing and LSB Steganography Log (Manual)

This section is for observations related to PNG images, including LSB steganography and the effects of Error Correction Codes (ECC).

### PNG LSB Steganography Operations (Main Menu: 2, Sub-Menu: 1-3)

Use this section to log results from:
*   Sub-Menu 2, Option 1: Embed Message in PNG (LSB)
*   Sub-Menu 2, Option 2: Extract Message from Local PNG (LSB)
*   Sub-Menu 2, Option 3: Extract Message from "Received" (Signal-Processed) PNG (LSB)

When prompted, you can choose to apply **(7,4) Hamming Code** as an ECC method. This code takes 4 data bits and encodes them into 7 bits, allowing for the correction of a single-bit error within each 7-bit block. This adds overhead, increasing payload size (7 bits stored for every 4 bits of original data, plus a 16-bit header for original message length).

| Action (Embed/Extract Local/Extract Received) | Base Image Filename | Stego Image Filename | Received Image Filename | Secret Message | Channel (R/G/B) | ECC Method Used (None, hamming_7_4) | ECC Encoding Output (e.g., bit length change, header size) | ECC Decoding Status (e.g., errors corrected) | Extracted Message | Payload Match? (Y/N) | Observations |
|-----------------------------------------------|---------------------|----------------------|-------------------------|----------------|-----------------|---------------------------------------|----------------------------------------------------------|----------------------------------------------|-------------------|----------------------|--------------|
| Embed                                         | `normalized.png`    | `stego.png`          | `received_stego.png`    | `Test1`        | `R`             | `None`                                | N/A                                                      | N/A                                          | N/A               | N/A                  |              |
| Extract Local                                 | N/A                 | `stego.png`          | N/A                     | N/A            | `R`             | `None`                                | N/A                                                      | N/A                                          | `Test1`           | Y                    |              |
| Embed                                         | `normalized.png`    | `stego_ecc.png`      | `recv_stego_ecc.png`    | `ECC Test`     | `G`             | `hamming_7_4`                         | `e.g., header:16, payload: X->Y bits`                    | N/A                                          | N/A               | N/A                  | Payload is larger |
| Extract Received                              | N/A                 | N/A                  | `recv_stego_ecc.png`    | N/A            | `G`             | `hamming_7_4`                         | N/A                                                      | `No errors detected` / `X errors corrected`  | `ECC Test`        | Y                    |              |
|                                               |                     |                      |                         |                |                 |                                       |                                                          |                                              |                   |                      |              |


### J-202: Test LSB on Normalized PNG (Main Menu: 2, Sub-Menu: 4)

Run the "Test LSB on Normalized PNG (J-202 Workflow)" option. Note: This specific workflow currently uses LSB embedding *without* an explicit ECC option within its direct flow. To test LSB with ECC, use the general "Embed/Extract Message in PNG (LSB)" options from Sub-Menu 2 (options 1-3).

*   **Base PNG Image Used**: `your_base_image.png`
*   **Normalized PNG Filename (created by workflow)**: `your_base_image_normalized.png`
*   **Test Payload Used**: `(e.g., "TestLSB_32bytes_AAAAAAAAAAAAAAAA")`
*   **ECC Method Used**: `None (by default for this specific J-202 workflow)`

For each channel (R, G, B) tested:
*   **Channel**: `R / G / B`
*   **Stego Image (before Signal, e.g., `..._lsb_R.png`) Analysis Summary**: `(Key properties, hash)`
*   **Received Stego Image (after Signal, e.g., `..._lsb_R_signalprocessed.png`) Analysis Summary**: `(Key properties, hash)`
*   **Extracted Message**: `extracted_payload_for_this_channel`
*   **Payload Match? (Y/N)**: `Y/N`
*   **SUCCESS/FAILURE for data integrity**: `(e.g., SUCCESS for R, FAILURE for G)`
*   **Observations**: `(Any noteworthy changes, errors, or unexpected behavior for this channel)`

---

## JPEG Image Processing Analysis Log (Manual)

This section is for manually recording your findings from the JPEG analysis and steganography tests.

### J-103: JPEG Processing Analysis (Main Menu: 1, Sub-Menu: 1)

Run "Analyze Images from Directory" (select the JPEG test image directory).

| Original Filename | Original Properties (Size, Dimensions, Mode, Quality_if_known, EXIF_summary) | Original Hash (SHA256) | Processed Filename (after Signal) | Processed Properties (Format, Size, Dimensions, Mode, Quantization_Tables_summary, EXIF_summary) | Processed Hash (SHA256) | Key Changes Observed | Are quantization tables significantly different? (Y/N/Partial) |
|-------------------|------------------------------------------------------------------------------|------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------|-------------------------|----------------------|--------------------------------------------------------------|
| `your_image1.jpg` | e.g., 1.2MB, 800x600, RGB, Q95, EXIF: Yes | `hash_value_1`         | `your_image1_signalprocessed.jpg` | e.g., JPEG, 150KB, 800x600, RGB, QTables: Yes, EXIF: No | `hash_value_2`          | Recompressed, EXIF stripped | Y                                                            |
| `your_image2.jpg` |                                                                              |                        |                                   |                                                                                                    |                         |                      |                                                              |
| `...`             |                                                                              |                        |                                   |                                                                                                    |                         |                      |                                                              |

**EXIF_summary**: Note if EXIF was present/stripped, or if specific tags changed.
**Quantization_Tables_summary**: Note if tables are present, seem to be standard or custom, or changed.

### J-105: JPEG Idempotency Check (Main Menu: 1, Sub-Menu: 2)

Run the "JPEG Idempotency Check (J-105)" option.

*   **Base JPEG Filename**: `your_base_image.jpg`
*   **Hash of 1st Normalized Image (Norm1)**: `hash_value_norm1`
*   **Hash of 2nd Normalized Image (Norm2)**: `hash_value_norm2`
*   **Idempotency Confirmed? (Y/N)**: `Y/N`
*   **If not, what changed between 1st and 2nd normalization?**: `(e.g., size, hash, specific properties like quantization tables, EXIF metadata if any was re-introduced/altered)`

*(Repeat for different base JPEGs if desired)*

### J-303: JPEG Steganography Test on Normalized JPEGs (Main Menu: 3, Sub-Menu: 3)

Run the "Test JPEG Stego on Normalized JPEG (J-303 Workflow)" option. This test uses **conceptual/placeholder** steganography functions. Remember to note which placeholder (JSteg_Conceptual or F5_Placeholder) was selected during the test.

*   **Base Normalized JPEG Filename (input to embedding function)**: `your_normalized_image.jpg`
*   **Stego Technique Selected in Test**: `(JSteg_Conceptual / F5_Placeholder)`
*   **Test Payload**: `(e.g., "TestLSB_32bytes_AAAAAAAAAAAAAAAA")`
*   **Stego Image Filename (e.g., `..._normalized_jsteg.jpg` or `..._normalized_f5.jpg`)**: `filename_here`
*   **Did stego image survive Signal processing (i.e., was `..._signalprocessed.jpg` downloadable and viewable)?**: `Y/N`
*   **Received Stego Image Filename**: `filename_here`
*   **Extracted Payload (from placeholder function)**: `"[JSteg Placeholder - ...]"` or `"[Placeholder F5 - ...]"`
*   **Payload Match? (Y/N)**: `N (Expected with current conceptual/placeholder functions)`
*   **Observations on image appearance after placeholder stego embedding (before Signal)**: `(e.g., No change expected as it's a copy)`
*   **Observations on image appearance after Signal processing of placeholder stego image**: `(e.g., Recompressed, EXIF stripped, etc.)`

*(Repeat for different base JPEGs and different placeholder techniques if desired)*

### Direct JPEG Steganography Placeholder Tests (Main Menu: 3, Sub-Menu: 1 & 2)

Use this section if you are testing direct embedding/extraction using the "Embed/Extract - JSteg Conceptual" or "Embed/Extract - F5 Placeholder" options.

*   **Action Performed**: `(Embed JSteg_Conceptual / Extract JSteg_Conceptual / Embed F5_Placeholder / Extract F5_Placeholder)`
*   **Input Image Filename**: `your_image.jpg`
*   **Output Image Filename (if embedding)**: `your_stego_output.jpg`
*   **Secret Message (if embedding)**: `your_secret`
*   **Extracted Message (if extracting)**: `(placeholder message)`
*   **Observations**: `(e.g., File copied, warnings displayed, conceptual logic notes, Signal simulation steps followed)`

---
