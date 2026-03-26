import os

def get_file_binary(file_path)->list[str,str]:

    paths = os.path.splitext(file_path)
    extension = paths[1]

    try:
        with open(file_path, 'rb') as file:
            file_bytes = file.read()
        binary_string = ""
        for bytes in file_bytes:
            binary_string += bytes_to_binary(bytes)
        return binary_string, extension # binary is returned in [0], extention is returned in [1] both str
    
    except FileNotFoundError:
        return None, "File not found"
    

def bytes_to_binary(bytes:bytes)->str:
    divider = [128, 64, 32, 16, 8, 4, 2, 1]
    bits_in_this_byte = ""
    for d in divider:
        if bytes >= d:
            bits_in_this_byte += "1"
            bytes = bytes - d # why does this works
        else:
            bits_in_this_byte += "0"
    return bits_in_this_byte


def binary_to_file(binaries:str,extension:str,output_location:str,filename:str):
    byte_data = []
    for i in range(0, len(binaries), 8):
        chunk = binaries[i:i+8]
        num = binary_to_bytes(chunk)
        byte_data.append(num)

    converted_byte_data = bytes(byte_data)
    if not extension.startswith('.'):
        extension = "." + extension

    full_path = os.path.join(output_location, filename + extension)

    with open(full_path, "wb") as f:
        f.write(converted_byte_data)
        

def binary_to_bytes(eightbits:str)->int: # it returns int for some reason
    divider = [128, 64, 32, 16, 8, 4, 2, 1]
    decimal= 0
    for i in range(8):
        decimal += divider[i] if eightbits[i] != "0" else 0

    return decimal