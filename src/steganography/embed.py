import cv2
import struct
import random
import os
import sys

HEADER_FMT = "<4sIBBBBBH"
MAGIC = b'STEG'

def bytes_to_bits(data: bytes):
    bits = []
    for b in data:
        bits.extend([(b >> i) & 1 for i in range(7, -1, -1)])
    return bits

def embed_bits_in_pixel(pixel_bgr, bits, r_bits, g_bits, b_bits):
    b = int(pixel_bgr[0])
    g = int(pixel_bgr[1])
    r = int(pixel_bgr[2])
    idx = 0
    
    for i in range(r_bits - 1, -1, -1):
        if idx < len(bits):
            r = (r & ~(1 << i)) | (bits[idx] << i)
            idx += 1
            
    for i in range(g_bits - 1, -1, -1):
        if idx < len(bits):
            g = (g & ~(1 << i)) | (bits[idx] << i)
            idx += 1
            
    for i in range(b_bits - 1, -1, -1):
        if idx < len(bits):
            b = (b & ~(1 << i)) | (bits[idx] << i)
            idx += 1
            
    return [b, g, r]

def embed_video(cover_path, output_path, data: bytes, is_file: bool, original_filename: str, mode: str, stego_key: str, r_bits: int, g_bits: int, b_bits: int):
    # ---------------------------------------------------------
    # TEAMMATE TODO: A5/1 ENCRYPTION GOES HERE
    # if use_encryption:
    #     data = a51_encrypt(data, a51_key)
    # ---------------------------------------------------------

    mode_val = 1 if mode == 'random' else 0
    type_val = 1 if is_file else 0
    filename_bytes = original_filename.encode('utf-8')
    filename_len = len(filename_bytes)

    header_fixed = struct.pack(HEADER_FMT, MAGIC, len(data), mode_val, type_val, r_bits, g_bits, b_bits, filename_len)
    full_header_bytes = header_fixed + filename_bytes
    
    header_bits = bytes_to_bits(full_header_bytes)
    payload_bits = bytes_to_bits(data)

    cap = cv2.VideoCapture(cover_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_pixels = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) * w * h

    header_pixels_needed = len(full_header_bytes) 
    bits_per_payload_pixel = r_bits + g_bits + b_bits
    payload_pixels_needed = (len(payload_bits) + bits_per_payload_pixel - 1) // bits_per_payload_pixel

    if header_pixels_needed + payload_pixels_needed > total_pixels:
        raise ValueError(f"Payload too large! Exceeds video capacity.")

    header_indices = list(range(0, header_pixels_needed))
    
    available_payload_space = list(range(header_pixels_needed, total_pixels))
    if mode == 'random':
        if not stego_key: raise ValueError("Stego key required for random mode")
        rng = random.Random(stego_key)
        rng.shuffle(available_payload_space)
        
    payload_indices = available_payload_space[:payload_pixels_needed]

    frames_map = {}
    def add_to_map(global_idx, bit_chunk, is_header):
        frame_idx = global_idx // (w * h)
        pix_in_frame = global_idx % (w * h)
        if frame_idx not in frames_map: frames_map[frame_idx] = []
        frames_map[frame_idx].append((pix_in_frame, bit_chunk, is_header))

    for i in range(header_pixels_needed):
        chunk = header_bits[i*8 : (i+1)*8]
        add_to_map(header_indices[i], chunk, True)
        
    for i in range(payload_pixels_needed):
        chunk = payload_bits[i*bits_per_payload_pixel : (i+1)*bits_per_payload_pixel]
        add_to_map(payload_indices[i], chunk, False)

    fourcc = cv2.VideoWriter_fourcc(*'FFV1') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break

        if frame_idx in frames_map:
            frame_flat = frame.reshape(-1, 3)
            for pix_in_frame, bit_chunk, is_header in frames_map[frame_idx]:
                if is_header:
                    frame_flat[pix_in_frame] = embed_bits_in_pixel(frame_flat[pix_in_frame], bit_chunk, 3, 3, 2)
                else:
                    frame_flat[pix_in_frame] = embed_bits_in_pixel(frame_flat[pix_in_frame], bit_chunk, r_bits, g_bits, b_bits)
            frame = frame_flat.reshape(h, w, 3)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"\n [✓] Successfully embedded into: {output_path}")

if __name__ == "__main__":
    print("\n=== LSB EMBEDDER (DYNAMIC LSB) ===")
    cover_video = input("Enter the cover AVI file name: ").strip()
    
    if not os.path.exists(cover_video):
        print(f"\n [!] ERROR: '{cover_video}' not found.")
        sys.exit(1)
        
    output_video = input("Enter output file name (e.g., stego_output.avi): ").strip()
    
    r_val = int(input("Enter LSB for Red (1-4): ") or 3)
    g_val = int(input("Enter LSB for Green (1-4): ") or 3)
    b_val = int(input("Enter LSB for Blue (1-4): ") or 2)
    
    mode_val = input("Mode (seq/rand) [rand]: ").strip().lower() or 'rand'
    actual_mode = 'random' if mode_val == 'rand' else 'sequential'
    
    # ONLY ask for a stego key if random is selected
    stego_key = ""
    if actual_mode == 'random':
        stego_key = input("Enter Stego-key for random mode: ").strip()
        if not stego_key:
            print("\n [!] ERROR: Stego-key cannot be empty for random mode.")
            sys.exit(1)
    
    filepath = input("Enter a file to hide (or press Enter to type text): ").strip()
    
    is_file = False
    original_name = "message.txt"
    payload = b""
    
    if filepath and os.path.exists(filepath):
        is_file = True
        original_name = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            payload = f.read()
    else:
        text_msg = input("Enter the secret message to hide:\n> ").strip()
        payload = text_msg.encode('utf-8')
    
    embed_video(
        cover_path=cover_video,
        output_path=output_video,
        data=payload,
        is_file=is_file,
        original_filename=original_name,
        mode=actual_mode,
        stego_key=stego_key,
        r_bits=r_val,
        g_bits=g_val,
        b_bits=b_val
    )