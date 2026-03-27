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

def generate_header(input_data, is_file=True, is_random=False):
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
# test = generate_header("Secret message", is_file=False)
# header_preview = binary_to_text(test[:1000])
# print(f"Header Preview: {header_preview}")

# if "[##MADOKA##]" in header_preview:
#     print("header generated")
# else:
#     print("header failed")