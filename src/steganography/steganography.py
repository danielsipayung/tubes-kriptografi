import os
import json
import cv2
import numpy as np
import random

from text_file_binary import binary_to_file, binary_to_text, file_to_binary, text_to_binary

default_delimiter = "[##MADOKA##]"

def split_byte_332(byte_string):
    r_bits = byte_string[0:3]
    g_bits = byte_string[3:6]
    b_bits = byte_string[6:8]
    
    return r_bits, g_bits, b_bits

# 3-3-2 split test
# sample_byte = "01101011" # binary 'k'
# r, g, b = split_byte_332(sample_byte)

# print(f"Original Byte: {sample_byte}")
# print(f"Red bits (3)    : {r}")
# print(f"Green bits (3)  : {g}")
# print(f"Blue bits (2)   : {b}")

# if r == '011' and g == '010' and b == '11':
#     print("split successful")
# else:    
#     print("split failed")

def generate_header(input_data, is_file, is_random, delimiter=default_delimiter):
    if is_random:
        embed_process = "random"
    else:
        embed_process = "sequential"

    if is_file:
        file_type = "file"
        filename = os.path.basename(input_data)
        if "." in filename:
            extension = "." + filename.split('.')[-1]
        else:
            extension = ""
            
        binary_data = file_to_binary(input_data)
    else:
        file_type = "text"
        filename = ""
        extension = ""
        binary_data = text_to_binary(input_data)

    header_dict = {
        "file_type": file_type,
        "extension": extension,
        "file_size": len(binary_data),
        "filename": filename,
        "encrypted": False,
        "embed_process": embed_process
    }
    
    header_json_string = json.dumps(header_dict)
    full_header_string = header_json_string + delimiter
    binary_header = ''.join(format(ord(char), '08b') for char in full_header_string)
    final_binary_string = binary_header + binary_data
    
    return final_binary_string

# generate header test
# test = generate_header("Secret message", is_file=False, is_random=False)
# header_preview = binary_to_text(test[:1500])
# print(f"Header Preview: {header_preview}")

# if default_delimiter in header_preview:
#     print("header generated")
# else:
#     print("header failed")

def get_frame_order(frames_folder, sensitivity): # normally 30 sensitivity
    all_frames = [img for img in os.listdir(frames_folder) if img.endswith(".bmp")]
    all_frames.sort()
    
    if len(all_frames) < 2:
        return all_frames 
        
    primary_frames = []
    secondary_frames = []
    
    prev_frame_path = os.path.join(frames_folder, all_frames[0])
    prev_gray = cv2.cvtColor(cv2.imread(prev_frame_path), cv2.COLOR_BGR2GRAY)
    
    secondary_frames.append(all_frames[0])
    
    for i in range(1, len(all_frames)):
        curr_frame_name = all_frames[i]
        curr_frame_path = os.path.join(frames_folder, curr_frame_name)
        curr_gray = cv2.cvtColor(cv2.imread(curr_frame_path), cv2.COLOR_BGR2GRAY)
        
        difference = cv2.absdiff(prev_gray, curr_gray)
        avg_diff = np.mean(difference)
        
        if avg_diff > sensitivity:
            primary_frames.append(curr_frame_name)
        else:
            secondary_frames.append(curr_frame_name)
            
        prev_gray = curr_gray

    frame_order = primary_frames + secondary_frames
    
    return frame_order

def embed_secret(final_binary_string, frames_folder, frame_order, mode="sequential", stego_key=None):
    binary_length = len(final_binary_string)
    binary_index = 0

    for frame_name in frame_order:
        if binary_index >= binary_length:
            break

        frame_path = os.path.join(frames_folder, frame_name)
        frame = cv2.imread(frame_path)
        height, width, layers = frame.shape
        
        pixel_coords = [(y, x) for y in range(height) for x in range(width)]
        
        if mode == "random":
            if not stego_key:
                raise ValueError("no stego-key")
            random.seed(stego_key)
            random.shuffle(pixel_coords)
            
        for y, x in pixel_coords:
            if binary_index >= binary_length:
                break 
                
            byte_chunk = final_binary_string    [binary_index : binary_index + 8]
            r_bits, g_bits, b_bits = split_byte_332(byte_chunk)
            
            b_ori, g_ori, r_ori = frame[y, x]
            
            r_new = (r_ori & 248) | int(r_bits, 2)
            g_new = (g_ori & 248) | int(g_bits, 2)
            b_new = (b_ori & 252) | int(b_bits, 2)
            
            frame[y, x] = [b_new, g_new, r_new]
            
            binary_index += 8
        
        # overwrite 
        cv2.imwrite(frame_path, frame)

    if binary_index < binary_length:
        print("not enough frames to embed message")
    else:
        print("embed done")

def read_byte_332(b, g, r):
    r_bits = format(r & 7, '03b')
    g_bits = format(g & 7, '03b')
    b_bits = format(b & 3, '02b')

    return r_bits + g_bits + b_bits

def extract_secret(frames_folder, frame_order, mode="sequential", stego_key=None, delimiter=default_delimiter):
    header_string = ""
    header_found = False
    header_dict = {}

    binary_bits = ""
    binary_length_target = 0
    current_bits = ""

    for frame_name in frame_order:
        if header_found and len(binary_bits) >= binary_length_target:
            break 

        frame_path = os.path.join(frames_folder, frame_name)
        frame = cv2.imread(frame_path)
        height, width, layers = frame.shape

        pixel_coords = [(y, x) for y in range(height) for x in range(width)]

        if mode == "random":
            if not stego_key:
                raise ValueError("no stego-key")
            random.seed(stego_key)
            random.shuffle(pixel_coords)

        for y, x in pixel_coords:
            if header_found and len(binary_bits) >= binary_length_target:
                break

            b, g, r = frame[y, x]
            pixel_bits = read_byte_332(b, g, r)
            
            if not header_found:
                current_bits += pixel_bits
                
                if len(current_bits) >= 8:
                    char_bits = current_bits[:8]
                    current_bits = current_bits[8:]
                    
                    char = chr(int(char_bits, 2))
                    header_string += char

                    if delimiter in header_string:
                        header_found = True
                        
                        json_str = header_string.split(delimiter)[0]
                        header_dict = json.loads(json_str)
        
                        binary_length_target = header_dict["file_size"]

                        binary_bits += current_bits
                        current_bits = ""
            else:
                binary_bits += pixel_bits

    if not header_found:
        print("header not found")
        return None, None

    final_binary_bits = binary_bits[:binary_length_target]
    
    return header_dict, final_binary_bits

# full test (embed and extract)
while True:
    test_folder_name = input("\nEnter frame folder name (in avi_frames/): ")
    test_frames_path = os.path.join("avi_frames", test_folder_name)
    frame_order = get_frame_order(test_frames_path, sensitivity=30.0)
    # print(f"frame order: {frame_order}")

    action = input("embed/extract? (e/x): ").lower()

    if action == 'e':
        secret_type = input("Embed text or file? (t/f): ").lower()
        
        if secret_type == 't':
            data_to_embed = input("Enter secret: ")
            is_file = False
        elif secret_type == 'f':
            filename = input("Enter filename (in input/ folder): ")
            data_to_embed = os.path.join("input", filename)
            is_file = True
        else:
            print("Invalid choice.")
            continue

        embed_mode = input("Mode (seq/ran): ").lower()
        if embed_mode == "seq":
            test_seq = generate_header(data_to_embed, is_file, is_random=False)
            embed_secret(test_seq, test_frames_path, frame_order, mode="sequential")
        elif embed_mode == "ran":
            key = input("Enter stego-key: ")
            test_rand = generate_header(data_to_embed, is_file, is_random=True)
            embed_secret(test_rand, test_frames_path, frame_order, mode="random", stego_key=key)

    elif action == 'x':
        extract_mode = input("Mode (seq/ran): ").lower()
        
        if extract_mode == "seq":
            header, extracted_bits = extract_secret(test_frames_path, frame_order, mode="sequential")
        elif extract_mode == "ran":
            key = input("Enter stego-key: ")
            header, extracted_bits = extract_secret(test_frames_path, frame_order, mode="random", stego_key=key)
        else:
            continue

        if header:
            if header["file_type"] == "text":
                secret_text = binary_to_text(extracted_bits)
                print(f"\nsecret message: {secret_text}")
                
            elif header["file_type"] == "file":
                default_name = header["filename"]
                print("\nsecret extracted")
                print(f"file name: {default_name}")
                save_name = input(f"save as (Enter to keep it as '{default_name}'): ")
                
                if save_name.strip() == "":
                    save_name = default_name
                    
                output_path = os.path.join("output", save_name)
                binary_to_file(extracted_bits, output_path)
                print(f"file saved to {output_path}")