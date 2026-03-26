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
while True:
    print("1. Convert text to binary"
          "\n2. Convert binary to text")
    option = input("Choose an option: ")

    if(option == '1'):
        input_text = input("Enter a message to convert to binary: ")
        binary_output = text_to_binary(input_text)
        print(f"Binary: {binary_output}")
    elif(option == '2'):
        binary_input = input("Enter a binary string to convert back to text: ")
        text_output = binary_to_text(binary_input)
        print(f"Text: {text_output}")
    else:
        print("Invalid.")