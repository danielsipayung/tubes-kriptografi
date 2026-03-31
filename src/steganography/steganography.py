import os
import json
import cv2
import numpy as np
import random


class Steganography:
    DELIMITER = "[##MADOKA##]"

    def _split_byte_332(self, byte_string):
        r_bits = byte_string[0:3]
        g_bits = byte_string[3:6]
        b_bits = byte_string[6:8]
        return r_bits, g_bits, b_bits

    def _read_byte_332(self, b, g, r):
        r_bits = format(r & 7, '03b')
        g_bits = format(g & 7, '03b')
        b_bits = format(b & 3, '02b')
        return r_bits + g_bits + b_bits

    def get_frame_order(self, frames_folder, sensitivity=30.0):
        all_frames = [img for img in os.listdir(frames_folder) if img.endswith(".bmp")]
        all_frames.sort()

        if len(all_frames) < 2:
            return all_frames

        primary_frames = []
        secondary_frames = []

        prev_gray = cv2.cvtColor(cv2.imread(os.path.join(frames_folder, all_frames[0])), cv2.COLOR_BGR2GRAY)
        secondary_frames.append(all_frames[0])

        for i in range(1, len(all_frames)):
            curr_frame_name = all_frames[i]
            curr_gray = cv2.cvtColor(cv2.imread(os.path.join(frames_folder, curr_frame_name)), cv2.COLOR_BGR2GRAY)
            avg_diff = np.mean(cv2.absdiff(prev_gray, curr_gray))

            if avg_diff > sensitivity:
                primary_frames.append(curr_frame_name)
            else:
                secondary_frames.append(curr_frame_name)

            prev_gray = curr_gray

        return primary_frames + secondary_frames

    def get_sorted_frame_order(self, frames_folder):
        all_frames = [img for img in os.listdir(frames_folder) if img.endswith(".bmp")]
        all_frames.sort()
        return all_frames

    def calculate_capacity(self, frames_folder, frame_order):
        total_bits = 0
        for frame_name in frame_order:
            frame = cv2.imread(os.path.join(frames_folder, frame_name))
            if frame is None:
                continue
            height, width, _ = frame.shape
            total_bits += height * width * 8
        return total_bits

    def peek_header(self, frames_folder, frame_order, mode="sequential", stego_key=None):
        header_string = ""
        current_bits = ""

        for frame_name in frame_order:
            frame = cv2.imread(os.path.join(frames_folder, frame_name))
            if frame is None:
                return None
            height, width, _ = frame.shape

            pixel_coords = [(y, x) for y in range(height) for x in range(width)]

            if mode == "random":
                if not stego_key:
                    return None
                random.seed(stego_key)
                random.shuffle(pixel_coords)

            for y, x in pixel_coords:
                b, g, r = frame[y, x]
                current_bits += self._read_byte_332(b, g, r)

                if len(current_bits) >= 8:
                    char_bits = current_bits[:8]
                    current_bits = current_bits[8:]
                    header_string += chr(int(char_bits, 2))

                    if self.DELIMITER in header_string:
                        json_str = header_string.split(self.DELIMITER)[0]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            return None
        return None

    def generate_header(self, input_data, is_file, is_random):
        embed_process = "random" if is_random else "sequential"

        if is_file:
            filename = os.path.basename(input_data)
            extension = ("." + filename.split('.')[-1]) if "." in filename else ""
            with open(input_data, 'rb') as f:
                data_bytes = f.read()
        else:
            filename = ""
            extension = ""
            data_bytes = input_data.encode('utf-8')

        binary_data = ''.join(format(byte, '08b') for byte in data_bytes)

        header_dict = {
            "file_type": "file" if is_file else "text",
            "extension": extension,
            "file_size": len(binary_data),
            "filename": filename,
            "encrypted": False,
            "embed_process": embed_process
        }

        header_json_string = json.dumps(header_dict)
        full_header_string = header_json_string + self.DELIMITER
        binary_header = ''.join(format(ord(char), '08b') for char in full_header_string)
        return binary_header + binary_data

    def embed_secret(self, final_binary_string, frames_folder, frame_order, mode="sequential", stego_key=None):
        binary_length = len(final_binary_string)
        binary_index = 0

        capacity = self.calculate_capacity(frames_folder, frame_order)
        print(f"Ukuran pesan  : {binary_length} bit ({binary_length // 8} byte)")
        print(f"Kapasitas video: {capacity} bit ({capacity // 8} byte)")

        if binary_length > capacity:
            raise ValueError(
                f"Pesan terlalu besar: butuh {binary_length} bit, "
                f"kapasitas video hanya {capacity} bit. "
                f"Selisih: {binary_length - capacity} bit ({(binary_length - capacity) // 8} byte)."
            )

        for frame_name in frame_order:
            if binary_index >= binary_length:
                break

            frame_path = os.path.join(frames_folder, frame_name)
            frame = cv2.imread(frame_path)
            if frame is None:
                raise ValueError(f"Gagal membaca frame: {frame_path}")
            height, width, _ = frame.shape

            pixel_coords = [(y, x) for y in range(height) for x in range(width)]

            if mode == "random":
                if not stego_key:
                    raise ValueError("no stego-key")
                random.seed(stego_key)
                random.shuffle(pixel_coords)

            for y, x in pixel_coords:
                if binary_index >= binary_length:
                    break

                byte_chunk = final_binary_string[binary_index:binary_index + 8]
                r_bits, g_bits, b_bits = self._split_byte_332(byte_chunk)

                b_ori, g_ori, r_ori = frame[y, x]
                r_new = (r_ori & 248) | int(r_bits, 2)
                g_new = (g_ori & 248) | int(g_bits, 2)
                b_new = (b_ori & 252) | int(b_bits, 2)
                frame[y, x] = [b_new, g_new, r_new]

                binary_index += 8

            if not cv2.imwrite(frame_path, frame):
                raise ValueError(f"Gagal menyimpan frame: {frame_path}")

        if binary_index < binary_length:
            print("not enough frames to embed message")
        else:
            print("embed done")

    def extract_secret(self, frames_folder, frame_order, mode="sequential", stego_key=None):
        header_string = ""
        header_found = False
        header_dict = {}

        binary_bits = ""
        binary_length_target = 0
        current_bits = ""

        for frame_name in frame_order:
            if header_found and len(binary_bits) >= binary_length_target:
                break

            frame = cv2.imread(os.path.join(frames_folder, frame_name))
            if frame is None:
                raise ValueError(f"Gagal membaca frame: {frame_name}")
            height, width, _ = frame.shape

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
                pixel_bits = self._read_byte_332(b, g, r)

                if not header_found:
                    current_bits += pixel_bits

                    if len(current_bits) >= 8:
                        char_bits = current_bits[:8]
                        current_bits = current_bits[8:]
                        header_string += chr(int(char_bits, 2))

                        if self.DELIMITER in header_string:
                            header_found = True
                            json_str = header_string.split(self.DELIMITER)[0]
                            header_dict = json.loads(json_str)
                            binary_length_target = header_dict["file_size"]
                            binary_bits += current_bits
                            current_bits = ""
                            print("header found:", header_dict)
                            print(f"target bits: {binary_length_target}")
                else:
                    binary_bits += pixel_bits

        if not header_found:
            print("header not found")
            return None, None

        if len(binary_bits) < binary_length_target:
            print(f"warning: extracted bits ({len(binary_bits)}) < target ({binary_length_target})")

        return header_dict, binary_bits[:binary_length_target]


stego = Steganography()

def split_byte_332(byte_string):
    return stego._split_byte_332(byte_string)

def generate_header(input_data, is_file, is_random):
    return stego.generate_header(input_data, is_file, is_random)

def get_frame_order(frames_folder, sensitivity=30.0):
    return stego.get_frame_order(frames_folder, sensitivity)

def get_sorted_frame_order(frames_folder):
    return stego.get_sorted_frame_order(frames_folder)

def calculate_capacity(frames_folder, frame_order):
    return stego.calculate_capacity(frames_folder, frame_order)

def embed_secret(final_binary_string, frames_folder, frame_order, mode="sequential", stego_key=None):
    return stego.embed_secret(final_binary_string, frames_folder, frame_order, mode, stego_key)

def extract_secret(frames_folder, frame_order, mode="sequential", stego_key=None):
    return stego.extract_secret(frames_folder, frame_order, mode, stego_key)

default_delimiter = Steganography.DELIMITER
