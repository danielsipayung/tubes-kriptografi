import sys

class A51:
    def __init__(self, key_string):

        self.regX_size = 19
        self.regY_size = 22
        self.regZ_size = 23
        
        self.maj_x = 8
        self.maj_y = 10
        self.maj_z = 10
        
        self.secret_key = self._process_binary_strict(key_string)
        self.reset()

    def _process_binary_strict(self, bin_string):
        if " " in bin_string:
            raise ValueError("Kunci tidak boleh mengandung spasi!")
        if len(bin_string) != 64:
            raise ValueError(f"Kunci harus 64 bit (Anda memasukkan {len(bin_string)} bit)")
        if not all(bit in '01' for bit in bin_string):
            raise ValueError("Kunci hanya boleh berisi angka 0 dan 1")
        return [int(bit) for bit in bin_string]

    def reset(self):
        self.regX = self.secret_key[0:19]
        self.regY = self.secret_key[19:41]
        self.regZ = self.secret_key[41:64]

    def _get_majority(self):
        x, y, z = self.regX[self.maj_x], self.regY[self.maj_y], self.regZ[self.maj_z]
        return 1 if (x + y + z) >= 2 else 0

    def _rotate_val_x(self):
        return self.regX[12] ^ self.regX[15] ^ self.regX[16] ^ self.regX[18]

    def _rotate_val_y(self):
        return self.regY[11] ^ self.regY[14] ^ self.regY[16]

    def _rotate_val_z(self):
        return self.regZ[7] ^ self.regZ[13] ^ self.regZ[15] ^ \
               self.regZ[20] ^ self.regZ[21] ^ self.regZ[22]

    def _clock(self):
        maj = self._get_majority()

        if self.regX[self.maj_x] == maj:
            new_bit = self._rotate_val_x()
            self.regX = [new_bit] + self.regX[:-1]

        if self.regY[self.maj_y] == maj:
            new_bit = self._rotate_val_y()
            self.regY = [new_bit] + self.regY[:-1]

        if self.regZ[self.maj_z] == maj:
            new_bit = self._rotate_val_z()
            self.regZ = [new_bit] + self.regZ[:-1]

    def generate_keystream(self, length):
        keystream = []
        for _ in range(length):
            out_bit = self.regX[-1] ^ self.regY[-1] ^ self.regZ[-1]
            keystream.append(out_bit)
            self._clock()
        return keystream

    @staticmethod
    def text_to_bits(text):
        bits = []
        for char in text:
            bin_val = format(ord(char), '08b')
            bits.extend([int(b) for b in bin_val])
        return bits

    @staticmethod
    def bits_to_text(bits):
        chars = []
        bit_str = "".join(map(str, bits))
        for i in range(0, len(bit_str), 8):
            byte = bit_str[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars)

def run_test():
    key_input = "1111111111111111111111111111111111111111111111111111111111111111"
    
    plain_text = "Ayam"
    
    try:
        cipher = A51(key_input)
        
        # pesan ke bit
        message_bits = cipher.text_to_bits(plain_text)
        num_bits = len(message_bits)
        
        # keystream
        keystream = cipher.generate_keystream(num_bits)
        
        print("\n" + "="*60)
        print(f"DEBUG KEYSTREAM (Total: {num_bits} bits)")
        print("="*60)
        ks_str = "".join(map(str, keystream))
        print(" ".join([ks_str[i:i+8] for i in range(0, len(ks_str), 8)]))
        print("="*60)
        
        encrypted_bits = [message_bits[i] ^ keystream[i] for i in range(num_bits)]
        encrypted_str = "".join(map(str, encrypted_bits))
        
        print(f"\nPlaintext      : {plain_text}")
        print(f"Message Bits   : {''.join(map(str, message_bits))}")
        print(f"Encrypted Bits : {encrypted_str}")
        
        cipher.reset()
        new_keystream = cipher.generate_keystream(num_bits)
        decrypted_bits = [encrypted_bits[i] ^ new_keystream[i] for i in range(num_bits)]
        decrypted_text = cipher.bits_to_text(decrypted_bits)
        
        print(f"Decrypted Text : {decrypted_text}")
        print("="*60)

        print("Keystream:", "".join(map(str, keystream)))
        
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test()