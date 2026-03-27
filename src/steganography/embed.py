import os
import json
import cv2
import numpy as np
import random

from text_file_binary import binary_to_text, file_to_binary, text_to_binary

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

def generate_header(input_data, is_file, is_random):
    if is_random:
        embed_process = "random"
    else:
        embed_process = "sequential"

    if is_file:
        file_type = "file"
        filename = input_data.split('/')[-1]
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
    delimiter = "[##MADOKA##]"
    full_header_string = header_json_string + delimiter
    binary_header = ''.join(format(ord(char), '08b') for char in full_header_string)
    final_binary_string = binary_header + binary_data
    
    return final_binary_string

# generate header test
# test = generate_header("Secret message", is_file=False, is_random=False)
# header_preview = binary_to_text(test[:1500])
# print(f"Header Preview: {header_preview}")

# if "[##MADOKA##]" in header_preview:
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

def embed_secret(final_binary_string, frames_folder, frame_order, mode, stego_key=None):
    binary_length = len(final_binary_string)
    binary_index = 0

    for frame_name in frame_order:
        if binary_index >= binary_length:
            break

        frame_path = "avi_frames/" + frames_folder + "/" + frame_name
        frame = cv2.imread(frame_path)
        height, width, _ = frame.shape
        
        pixel_coords = [(y, x) for y in range(height) for x in range(width)]
        
        if mode == "random":
            if not stego_key:
                raise ValueError("A stego-key is required for random embedding!")
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

# test frame order and embedding
# while True:
#     test_folder_name = input("frame folder name: ")
#     test_frames_path = "avi_frames/" + test_folder_name
#     frame_order = get_frame_order(test_frames_path, sensitivity=30)

#     embed_mode = input("(seq/ran): ").lower()

#     if embed_mode == "seq":
#         test_seq = generate_header("This is a secret message injected into the video!", is_file=False, is_random=False)
#         embed_secret(test_seq, test_folder_name, frame_order, mode="sequential")
#     elif embed_mode == "ran":
#         print(f"Using 'homura' as stego-key")
#         test_rand = generate_header("This is a secret message injected into the video!", is_file=False, is_random=True)
#         embed_secret(test_rand, test_folder_name, frame_order, mode="random", stego_key="homura")
#     else:
#         print("Invalid mode. Defaulting to sequential.")