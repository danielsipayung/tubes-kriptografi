class A51:
    def __init__(self, key_string):
        self.regX_size = 19
        self.regY_size = 22
        self.regZ_size = 23
        self.maj_x = 8
        self.maj_y = 10
        self.maj_z = 10
        self.secret_key = self._process_binary_strict(key_string)
        self.frame_counter = 0
        self.reset()

    def _process_binary_strict(self, bin_string):
        if " " in bin_string:
            raise ValueError("Kunci tidak boleh dispasi!")
        if len(bin_string) != 64:
            raise ValueError(f"Kunci harus 64 bit (Inputmu {len(bin_string)} bit)")
        if not all(bit in '01' for bit in bin_string):
            raise ValueError("Kunci hanya boleh berisi angka 0 dan 1 (binary)")
        return [int(bit) for bit in bin_string]

    def reset(self):
        self.regX = [0] * self.regX_size
        self.regY = [0] * self.regY_size
        self.regZ = [0] * self.regZ_size
        self.frame_counter = 0

    def _frame_counter_bits(self, frame_counter):
        return [int(bit) for bit in format(frame_counter % (1 << 22), '022b')]

    def _standard_init(self, frame_counter):
        self.regX = [0] * self.regX_size
        self.regY = [0] * self.regY_size
        self.regZ = [0] * self.regZ_size

        for i in range(64):
            self._clock(ignore_majority=True)
            key_bit = self.secret_key[i]
            self.regX[0] ^= key_bit
            self.regY[0] ^= key_bit
            self.regZ[0] ^= key_bit

        f_bits = self._frame_counter_bits(frame_counter)
        for i in range(22):
            self._clock(ignore_majority=True)
            frame_bit = f_bits[i]
            self.regX[0] ^= frame_bit
            self.regY[0] ^= frame_bit
            self.regZ[0] ^= frame_bit

        for _ in range(100):
            self._clock()

    def enc_block(self, plain_bits):
        cipher_bits = []
        for offset in range(0, len(plain_bits), 228):
            block = plain_bits[offset:offset + 228]
            self._standard_init(self.frame_counter)
            keystream = self.generate_keystream(len(block))
            cipher_bits.extend([b ^ k for b, k in zip(block, keystream)])
            self.frame_counter += 1
        return cipher_bits

    def _get_majority(self):
        x, y, z = self.regX[self.maj_x], self.regY[self.maj_y], self.regZ[self.maj_z]
        return 1 if (x + y + z) >= 2 else 0

    def _rotate_val_x(self):
        return self.regX[13] ^ self.regX[16] ^ self.regX[17] ^ self.regX[18]

    def _rotate_val_y(self):
        return self.regY[20] ^ self.regY[21]

    def _rotate_val_z(self):
        return self.regZ[7] ^ self.regZ[20] ^ self.regZ[21] ^ self.regZ[22]

    def _clock(self, ignore_majority=False):
        maj = self._get_majority()

        if ignore_majority or self.regX[self.maj_x] == maj:
            new_bit = self._rotate_val_x()
            self.regX = [new_bit] + self.regX[:-1]

        if ignore_majority or self.regY[self.maj_y] == maj:
            new_bit = self._rotate_val_y()
            self.regY = [new_bit] + self.regY[:-1]

        if ignore_majority or self.regZ[self.maj_z] == maj:
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
