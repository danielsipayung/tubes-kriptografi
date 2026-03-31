import os

class BinaryConverter:

    @staticmethod
    def text_to_binary(text):
        data_bytes = text.encode('utf-8')
        return ''.join(format(byte, '08b') for byte in data_bytes)

    @staticmethod
    def binary_to_text(binary_data):
        byte_list = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
        return bytes(byte_list).decode('utf-8')

    @staticmethod
    def file_to_binary(file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        return ''.join(format(byte, '08b') for byte in file_bytes)

    @staticmethod
    def binary_to_file(binary_data, output_file_path):
        byte_list = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
        with open(output_file_path, 'wb') as f:
            f.write(bytes(byte_list))


# Convenience wrapper functions for script compatibility
converter = BinaryConverter()

def text_to_binary(text):
    return converter.text_to_binary(text)


def binary_to_text(binary_data):
    return converter.binary_to_text(binary_data)


def file_to_binary(file_path):
    return converter.file_to_binary(file_path)


def binary_to_file(binary_data, output_file_path):
    return converter.binary_to_file(binary_data, output_file_path)
