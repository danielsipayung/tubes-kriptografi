import os

from avi_process import AviProcess, BASE_DIR
from text_file_binary import BinaryConverter
from steganography import Steganography

avi   = AviProcess()
conv  = BinaryConverter()
stega = Steganography()

current_fps = 30.0


def resolve_file(raw_input):
    if os.path.isfile(raw_input):
        return os.path.abspath(raw_input)
    candidate = os.path.join(BASE_DIR, "input", raw_input)
    if os.path.isfile(candidate):
        return candidate
    return None


def looks_like_filename(text):
    return '.' in text and ' ' not in text.strip()


while True:
    print("\n=== Steganography Test ===")
    print("1. Extract frames from AVI")
    print("2. Rebuild AVI from frames")
    print("3. Get frame order")
    print("4. Text <-> binary conversion")
    print("5. File <-> binary conversion")
    print("6. Test 3-3-2 LSB splitter")
    print("7. Test header generation")
    print("8. Embed / Extract message")
    print("0. Exit")

    option = input("\nChoose: ").strip()

    if option == '0':
        break

    elif option == '1':
        video_name  = input("AVI filename (e.g. test.avi): ").strip()
        video_path  = os.path.join(BASE_DIR, "avi_video", video_name)
        folder_name = input("Target folder name (inside avi_frames/): ").strip()

        if os.path.exists(video_path):
            current_fps = avi.extract_frames(video_path, folder_name)
        else:
            print(f"Error: file not found -> {video_path}")

    elif option == '2':
        folder_name = input("Frames folder name (inside avi_frames/): ").strip()
        output_name = input("Output filename (saved in output/, e.g. result.avi): ").strip()
        output_path = os.path.join(BASE_DIR, "output", output_name)
        os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
        avi.rebuild_video(folder_name, output_path, current_fps)

    elif option == '3':
        folder_name = input("Frames folder name (inside avi_frames/): ").strip()
        frames_path = os.path.join(BASE_DIR, "avi_frames", folder_name)

        if os.path.exists(frames_path):
            frame_order  = stega.get_frame_order(frames_path, sensitivity=30.0)
            sorted_order = stega.get_sorted_frame_order(frames_path)
            print(f"Frame order (scene-change): {frame_order}")
            print(f"Frame order (sorted)      : {sorted_order}")
        else:
            print(f"Error: folder not found -> {frames_path}")

    elif option == '4':
        print("1. Text -> Binary")
        print("2. Binary -> Text")
        sub = input("Choose: ").strip()
        if sub == '1':
            text = input("Enter text: ")
            print(f"Binary: {conv.text_to_binary(text)}")
        elif sub == '2':
            binary = input("Enter binary string: ")
            try:
                print(f"Text: {conv.binary_to_text(binary)}")
            except Exception as e:
                print(f"Error: {e}")

    elif option == '5':
        print("1. File -> Binary (save to binary_output/)")
        print("2. Binary -> File (read from binary_output/)")
        sub = input("Choose: ").strip()
        if sub == '1':
            filename = input("Filename (inside input/): ").strip()
            filepath = os.path.join(BASE_DIR, "input", filename)
            out_name = input("Output .txt filename (in binary_output/): ").strip()
            out_path = os.path.join(BASE_DIR, "binary_output", out_name)
            os.makedirs(os.path.join(BASE_DIR, "binary_output"), exist_ok=True)
            binary = conv.file_to_binary(filepath)
            with open(out_path, 'w') as f:
                f.write(binary)
            print(f"Binary saved to {out_path}")
        elif sub == '2':
            txt_name = input("Binary .txt filename (in binary_output/): ").strip()
            txt_path = os.path.join(BASE_DIR, "binary_output", txt_name)
            with open(txt_path, 'r') as f:
                binary = f.read()
            out_name = input("Output filename (in output/): ").strip()
            out_path = os.path.join(BASE_DIR, "output", out_name)
            os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
            conv.binary_to_file(binary, out_path)
            print(f"File saved to {out_path}")

    elif option == '6':
        sample_byte = "01101011"  # 'k'
        r, g, b = stega._split_byte_332(sample_byte)
        print(f"\nOriginal byte : {sample_byte}")
        print(f"R (3 bits)    : {r}")
        print(f"G (3 bits)    : {g}")
        print(f"B (2 bits)    : {b}")
        status = "OK" if r == '011' and g == '010' and b == '11' else "FAILED"
        print(f"Status        : {status}")

    elif option == '7':
        pass

    elif option == '8':
        folder_name = input("\nFrames folder name (inside avi_frames/): ").strip()
        frames_path = os.path.join(BASE_DIR, "avi_frames", folder_name)

        if not os.path.exists(frames_path):
            print(f"Error: folder not found -> {frames_path}")
            continue

        frame_order = stega.get_sorted_frame_order(frames_path)
        action      = input("embed / extract? (e/x): ").strip().lower()

        if action == 'e':
            raw      = input("File path or text message: ").strip()
            resolved = resolve_file(raw)

            if resolved:
                data_to_embed = resolved
                is_file = True
                print(f"[file] {data_to_embed}")
            elif looks_like_filename(raw):
                print(f"[!] '{raw}' looks like a filename but was not found.")
                print(f"    Place the file in input/ or enter the full path.")
                continue
            else:
                data_to_embed = raw
                is_file = False
                print(f"[text] '{data_to_embed}'")

            embed_mode = input("Mode (seq/ran): ").strip().lower()
            mode_map   = {"seq": "sequential", "ran": "random"}
            mode       = mode_map.get(embed_mode, "sequential")
            stego_key  = input("Stego-key: ").strip() if mode == "random" else None
            is_random  = mode == "random"

            try:
                payload = stega.generate_header(data_to_embed, is_file, is_random)
                stega.embed_secret(payload, frames_path, frame_order, mode=mode, stego_key=stego_key)

                v_header = stega.peek_header(frames_path, frame_order, mode=mode, stego_key=stego_key)
                if v_header:
                    size_str = f"{v_header['file_size'] // 8} bytes"
                    name_str = f", file: {v_header['filename']}" if v_header['file_type'] == 'file' else ""
                    print(f"[OK] Verified: type={v_header['file_type']}, size={size_str}{name_str}")
                else:
                    print("[!] Verification failed - header unreadable after embed")
            except ValueError as e:
                print(f"Error: {e}")

        elif action == 'x':
            extract_mode = input("Mode (seq/ran): ").strip().lower()
            mode_map     = {"seq": "sequential", "ran": "random"}
            mode         = mode_map.get(extract_mode, "sequential")
            stego_key    = input("Stego-key: ").strip() if mode == "random" else None

            try:
                header, extracted_bits = stega.extract_secret(
                    frames_path, frame_order, mode=mode, stego_key=stego_key
                )
            except ValueError as e:
                print(f"Error: {e}")
                continue

            if not header:
                continue

            print(f"\n--- Header Info ---")
            print(f"  Type : {header['file_type']}")
            print(f"  Size : {header['file_size'] // 8} bytes")
            if header['file_type'] == 'file':
                print(f"  Name : {header['filename']}")
            print(f"-------------------")

            if header["file_type"] == "text":
                text_result = conv.binary_to_text(extracted_bits)
                print(f"Message: {text_result}")
                if looks_like_filename(text_result):
                    print(f"\n[!] Extracted text looks like a filename.")
                    print(f"    The file was likely embedded as text, not as a file.")
                    print(f"    Re-embed: place the file in input/ then run option 8 -> e")

            elif header["file_type"] == "file":
                default_name = header["filename"]
                save_name    = input(f"Save as (Enter = '{default_name}'): ").strip()
                if not save_name:
                    save_name = default_name

                output_dir  = os.path.join(BASE_DIR, "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, save_name)

                conv.binary_to_file(extracted_bits, output_path)

                saved_size    = os.path.getsize(output_path)
                expected_size = header['file_size'] // 8
                if saved_size == expected_size:
                    print(f"[OK] File saved: {output_path} ({saved_size} bytes)")
                else:
                    print(f"[!] Size mismatch: saved {saved_size} bytes, expected {expected_size} bytes")

    else:
        print("Invalid option.")
