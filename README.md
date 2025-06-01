# STEGTEST
Stegadnographicalicicalhelical test suite for a variety of functions

## JPEG Image Processing Analysis Log (Manual)

This section is for manually recording your findings from the JPEG analysis and steganography tests available in `stego_test.py`. Please run the relevant menu options in the script and fill in your observations in the tables/templates below.

### J-103: JPEG Processing Analysis (Menu Option 4)

Run option "4. Analyze Images from Directory" in `stego_test.py`, providing a directory containing your test JPEGs (e.g., `test_images_jpeg`).

| Original Filename | Original Properties (Size, Dimensions, Mode, Quality_if_known, EXIF_summary) | Original Hash (SHA256) | Processed Filename (after Signal) | Processed Properties (Format, Size, Dimensions, Mode, Quantization_Tables_summary, EXIF_summary) | Processed Hash (SHA256) | Key Changes Observed | Are quantization tables significantly different? (Y/N/Partial) |
|-------------------|------------------------------------------------------------------------------|------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------|-------------------------|----------------------|--------------------------------------------------------------|
| `your_image1.jpg` | e.g., 1.2MB, 800x600, RGB, Q95, EXIF: Yes | `hash_value_1`         | `your_image1_signalprocessed.jpg` | e.g., JPEG, 150KB, 800x600, RGB, QTables: Yes, EXIF: No | `hash_value_2`          | Recompressed, EXIF stripped | Y                                                            |
| `your_image2.jpg` |                                                                              |                        |                                   |                                                                                                    |                         |                      |                                                              |
| `...`             |                                                                              |                        |                                   |                                                                                                    |                         |                      |                                                              |

**EXIF_summary**: Note if EXIF was present/stripped, or if specific tags changed.
**Quantization_Tables_summary**: Note if tables are present, seem to be standard or custom, or changed.

### J-105: JPEG Idempotency Check (Menu Option 6)

Run option "6. JPEG Idempotency Check (J-105)" in `stego_test.py`.

*   **Base JPEG Filename**: `your_base_image.jpg`
*   **Hash of 1st Normalized Image (Norm1)**: `hash_value_norm1`
*   **Hash of 2nd Normalized Image (Norm2)**: `hash_value_norm2`
*   **Idempotency Confirmed? (Y/N)**: `Y/N`
*   **If not, what changed between 1st and 2nd normalization?**: `(e.g., size, hash, specific properties like quantization tables, EXIF metadata if any was re-introduced/altered)`

*(Repeat for different base JPEGs if desired)*

### J-303: JPEG Steganography Test on Normalized JPEGs (Menu Option 8)

Run option "8. Test JPEG Stego on Normalized JPEG (J-303)" in `stego_test.py`. This test uses **placeholder** steganography functions, so the primary goal is to observe the file processing workflow.

*   **Base Normalized JPEG Filename (input to `embed_message_jpeg`)**: `your_normalized_image.jpg`
*   **Test Payload**: `(e.g., "TestLSB_32bytes_AAAAAAAAAAAAAAAA")`
*   **Stego Tool Used**: `"Placeholder JSteg-like in stego_test.py"`
*   **Did stego image (`..._normalized_jsteg.jpg`) survive Signal processing (i.e., was `..._jsteg_signalprocessed.jpg` downloadable and viewable)?**: `Y/N`
*   **Extracted Payload (from placeholder function)**: `"[Placeholder - No message extracted]"`
*   **Payload Match? (Y/N)**: `N (Expected with current placeholders)`
*   **Observations on image appearance after stego embedding (if any visual change on `..._normalized_jsteg.jpg` before Signal)**: `(e.g., No change expected as it's a copy)`
*   **Observations on image appearance after Signal processing of stego image (`..._jsteg_signalprocessed.jpg`)**: `(e.g., Recompressed, EXIF stripped, etc.)`

*(Repeat for different base JPEGs if desired)*
