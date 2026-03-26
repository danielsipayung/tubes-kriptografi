import os

def text_to_binary(text):
    binary_string = ''.join(format(ord(char), '08b') for char in text)
    return binary_string

def binary_to_text(binary_data):
    text = ""

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        text += chr(int(byte, 2))
    return text

# test text to binary
# while True:
#     print("1. Convert text to binary"
#           "\n2. Convert binary to text")
#     option = input("Choose an option: ")

#     if(option == '1'):
#         input_text = input("message to convert to binary: ")
#         binary_output = text_to_binary(input_text)
#         print(f"Binary: {binary_output}")
#     elif(option == '2'):
#         binary_input = input("Enter a binary string to convert back to text: ")
#         text_output = binary_to_text(binary_input)
#         print(f"Text: {text_output}")
#     else:
#         print("Invalid.")

def file_to_binary(file_path):
    with open(file_path, 'rb') as file:
        file_bytes = file.read()

    binary_string = ''.join(format(byte, '08b') for byte in file_bytes)
    return binary_string

def binary_to_file(binary_data, output_file_path):
    byte_list = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    file_bytes = bytes(byte_list)
    
    with open(output_file_path, 'wb') as file:
        file.write(file_bytes)

# test file to binary
# while True:
#     print("\n1. Convert file to binary")
#     print("2. Convert binary to file")
#     option = input("Choose an option: ")

#     if option == '1':
#         filepath = "input/" + input("Enter file name with extension: ")
#         binary_output = file_to_binary(filepath)
        
#         txt_filepath = "binary_output/" + input("Enter name for the output text file: ") + ".txt"
        
#         with open(txt_filepath, 'w') as text_file:
#             text_file.write(binary_output)
            
#         print(f"Binary saved to {txt_filepath}")

#     elif option == '2':
#         txt_filepath = "binary_output/" + input("Enter the text file name: ") + ".txt"
        
#         with open(txt_filepath, 'r') as text_file:
#             binary_input = text_file.read()
            
#         filepath = "output/" + input("Enter output file name with extension: ")
        
#         binary_to_file(binary_input, filepath)
#         print(f"File saved to {filepath}")

#     else:
#         print("Invalid option.")