import os
import cv2

from avi_process import extract_frames, rebuild_video
from text_file_binary import text_to_binary, binary_to_text, file_to_binary, binary_to_file
from steganography import split_byte_332, generate_header, get_frame_order, embed_secret, extract_secret, default_delimiter

# Global variable to hold fps in case the user extracts and then rebuilds immediately
current_fps = 30.0 

while True:
    print("\nSteganography Test")
    print("1. extract frames from AVI")
    print("2. rebuild AVI from frames")
    print("3. get frame insertion order")
    print("4. text binary conversion")
    print("5. file binary conversion")
    print("6. 3-3-2 LSB Splitter ('k' as sample byte)")
    print("7. header generation")
    print("8. embed/extract")
    
    option = input("Choose: ")

    if option == '1':
        video_path = os.path.join("avi_video", input("Enter avi video file name (e.g. test.avi): "))
        folder_name = input("Enter target folder name (will be created in /avi_frames): ")
        
        if os.path.exists(video_path):
            current_fps = extract_frames(video_path, folder_name)
        else:
            print(f"Error: Could not find {video_path}")

    elif option == '2':
        folder_name = input("Enter the frame folder name inside /avi_frames to rebuild from: ")
        output_path = os.path.join("output", input("Enter output video name (will be saved in /output): "))
        rebuild_video(folder_name, output_path, current_fps)

    elif option == '3':
        test_folder_name = input("Enter frame folder name (in avi_frames/): ")
        test_frames_path = os.path.join("avi_frames", test_folder_name)
        
        if os.path.exists(test_frames_path):
            frame_order = get_frame_order(test_frames_path, sensitivity=30.0)
            print(f"frame order: {frame_order}")
        else:
            print(f"Error: folder {test_frames_path} not found.")

    elif option == '4':
        print("1. Text to Binary")
        print("2. Binary to Text")
        option = input("Choose: ")
        if option == '1':
            input_text = input("Message to convert to binary: ")
            binary_output = text_to_binary(input_text)
            print(f"Binary: {binary_output}")
        elif option == '2':
            binary_input = input("Enter a binary string: ")
            text_output = binary_to_text(binary_input)
            print(f"Text: {text_output}")

    elif option == '5':
        print("1. File to Binary")
        print("2. Binary to File")
        option = input("Choose: ")
        if option == '1':
            filepath = os.path.join("input", input("Enter file name with extension (in input/): "))
            binary_output = file_to_binary(filepath)
            
            txt_filepath = os.path.join("binary_output", input("Enter the output file name with .txt: "))
            with open(txt_filepath, 'w') as text_file:
                text_file.write(binary_output)
            print(f"Binary saved to {txt_filepath}")
            
        elif option == '2':
            txt_filepath = os.path.join("binary_output", input("Enter the text file name with .txt: "))
            with open(txt_filepath, 'r') as text_file:
                binary_input = text_file.read()
                
            filepath = os.path.join("output", input("Enter output file name with extension: "))
            binary_to_file(binary_input, filepath)
            print(f"File saved to {filepath}")

    elif option == '6':
        sample_byte = "01101011" # binary 'k'
        r, g, b = split_byte_332(sample_byte)
        
        print(f"\nOriginal Byte: {sample_byte}")
        print(f"Red bits (3)    : {r}")
        print(f"Green bits (3)  : {g}")
        print(f"Blue bits (2)   : {b}")
        
        if r == '011' and g == '010' and b == '11':
            print("Status: Split successful")
        else:    
            print("Status: Split failed")

    elif option == '7':
        test_payload = generate_header("madoka", is_file=False, is_random=False)
        header_preview = binary_to_text(test_payload[:1500])
        print(f"\nheader preview: {header_preview}")
        
        if default_delimiter in header_preview:
            print("header generated")
        else:
            print("header failed to generate")

    elif option == '8':
        test_folder_name = input("\nEnter frame folder name (in avi_frames/): ")
        test_frames_path = os.path.join("avi_frames", test_folder_name)
        
        if not os.path.exists(test_frames_path):
            print("Folder not found.")
            continue
            
        frame_order = get_frame_order(test_frames_path, sensitivity=30.0)

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
                    print(f"\nextracted message: {secret_text}")
                    
                elif header["file_type"] == "file":
                    default_name = header["filename"]
                    print(f"\nextracted filename: {default_name}")
                    save_name = input(f"Save as (Enter to keep it as '{default_name}'): ")
                    
                    if save_name.strip() == "":
                        save_name = default_name
                        
                    output_path = os.path.join("output", save_name)
                    binary_to_file(extracted_bits, output_path)
                    print(f"saved to {output_path}")

    else:
        print("invalid")