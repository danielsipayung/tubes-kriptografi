import cv2
import struct
import random
import sys
import os

HEADER_FMT = "<4sIBBBBBH"
MAGIC = b'STEG'
HEADER_SIZE = struct.calcsize(HEADER_FMT)

def extract_bits_from_pixel(pixel_bgr, r_bits, g_bits, b_bits):
    b, g, r = pixel_bgr
    bits = []
    
    for i in range(r_bits - 1, -1, -1):
        bits.append((r >> i) & 1)
    for i in range(g_bits - 1, -1, -1):
        bits.append((g >> i) & 1)
    for i in range(b_bits - 1, -1, -1):
        bits.append((b >> i) & 1)
        
    return bits

def bits_to_bytes(bits: list):
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte << 1) | bit
        byte_array.append(byte)
    return bytes(byte_array)

def extract_video(stego_path, stego_key: str):
    cap = cv2.VideoCapture(stego_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_pixels = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) * w * h

    ret, frame = cap.read()
    if not ret: raise ValueError("Failed to read video.")
    frame_flat = frame.reshape(-1, 3)

    header_bits = []
    for i in range(HEADER_SIZE):
        header_bits.extend(extract_bits_from_pixel(frame_flat[i], 3, 3, 2))
        
    header_bytes = bits_to_bytes(header_bits)
    magic, payload_size, mode_val, type_val, r_bits, g_bits, b_bits, filename_len = struct.unpack(HEADER_FMT, header_bytes)

    if magic != MAGIC:
        raise ValueError("No valid Stego data found in this video.")

    filename_bits = []
    for i in range(HEADER_SIZE, HEADER_SIZE + filename_len):
        filename_bits.extend(extract_bits_from_pixel(frame_flat[i], 3, 3, 2))
        
    filename_bytes = bits_to_bytes(filename_bits)
    original_filename = filename_bytes.decode('utf-8')
    
    mode = 'random' if mode_val == 1 else 'sequential'
    is_file = type_val == 1

    header_pixels_used = HEADER_SIZE + filename_len
    bits_per_payload_pixel = r_bits + g_bits + b_bits
    payload_bits_needed = payload_size * 8
    payload_pixels_needed = (payload_bits_needed + bits_per_payload_pixel - 1) // bits_per_payload_pixel

    available_payload_space = list(range(header_pixels_used, total_pixels))
    if mode == 'random':
        if not stego_key: raise ValueError("Stego key required to extract random payload. Please run again and provide the key.")
        rng = random.Random(stego_key)
        rng.shuffle(available_payload_space)
        
    payload_indices = available_payload_space[:payload_pixels_needed]

    frames_map = {}
    for list_idx, global_idx in enumerate(payload_indices):
        frame_idx = global_idx // (w * h)
        pix_in_frame = global_idx % (w * h)
        if frame_idx not in frames_map: frames_map[frame_idx] = []
        frames_map[frame_idx].append((pix_in_frame, list_idx))

    extracted_bits_array = [0] * (payload_pixels_needed * bits_per_payload_pixel)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 
    
    frame_idx = 0
    max_frame_needed = max(frames_map.keys()) if frames_map else 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        if frame_idx in frames_map:
            frame_flat = frame.reshape(-1, 3)
            for pix_in_frame, list_idx in frames_map[frame_idx]:
                extracted_bits = extract_bits_from_pixel(frame_flat[pix_in_frame], r_bits, g_bits, b_bits)
                start_bit = list_idx * bits_per_payload_pixel
                for b_idx, bit in enumerate(extracted_bits):
                    extracted_bits_array[start_bit + b_idx] = bit

        if frame_idx >= max_frame_needed: break 
        frame_idx += 1

    cap.release()
    
    final_payload_bytes = bits_to_bytes(extracted_bits_array)[:payload_size]
    
    # ---------------------------------------------------------
    # a5/1 encryption
    # ---------------------------------------------------------

    return final_payload_bytes, is_file, original_filename

if __name__ == "__main__":
    print("\n=== LSB EXTRACTOR (DYNAMIC LSB) ===")
    stego_video = input("Enter the stego AVI file name: ").strip()
    
    if not os.path.exists(stego_video):
        print(f"\n [!] ERROR: '{stego_video}' not found.")
        sys.exit(1)

    stego_key = input("Enter Stego-key (press Enter to leave blank if sequential): ").strip()

    print(f" [*] Extracting data from '{stego_video}'...")
    try:
        extracted_bytes, is_file, original_filename = extract_video(stego_video, stego_key=stego_key)
        
        if is_file:
            print(f" [✓] Extracted file. Original name: '{original_filename}'")
            save_name = input(f" Save as [{original_filename}]: ").strip() or original_filename
            with open(save_name, "wb") as f:
                f.write(extracted_bytes)
            print(f" [✓] Saved to {save_name}")
        else:
            extracted_text = extracted_bytes.decode('utf-8')
            print("-" * 50)
            print(" [✓] EXTRACTION SUCCESSFUL!")
            print(f"     Extracted Message: {extracted_text}")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n [!] ERROR during extraction: {e}")