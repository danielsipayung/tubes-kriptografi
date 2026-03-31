import unittest

from a51 import A51


class TestA51(unittest.TestCase):
    def setUp(self):
        self.key = "1010101111001101111001100101010101011110001100111110001100110011"
        self.a51 = A51(self.key)

    def test_basic_flow_228_blocks(self):
        payload = "A" * 60  # 60 chars = 480 bit, 2 blok 228 + sisa 24
        plain_bits = self.a51.text_to_bits(payload)

        cipher_bits = self.a51.enc_block(plain_bits)
        self.assertEqual(len(cipher_bits), len(plain_bits), "Cipher bits hsrus sesuai dengan plaintext")

        a51_dec = A51(self.key)
        decrypted_bits = a51_dec.enc_block(cipher_bits)

        self.assertEqual(plain_bits, decrypted_bits)

        self.assertEqual(self.a51.frame_counter, 3)
        self.assertEqual(a51_dec.frame_counter, 3)

    def test_text_encrypt_decrypt(self):
        input_text = "Hello"
        plain_bits = self.a51.text_to_bits(input_text)

        cipher_bits = self.a51.enc_block(plain_bits)
        decrypted_bits = A51(self.key).enc_block(cipher_bits)
        decrypted_text = self.a51.bits_to_text(decrypted_bits)

        self.assertEqual(input_text, decrypted_text)

    def test_print_full_roundtrip(self):
        input_text = "Secret"
        plain_bits = self.a51.text_to_bits(input_text)

        print("Plaintext:", input_text)
        print("Plaintext bits:", "".join(map(str, plain_bits)))

        self.a51._standard_init(0)
        keystream = self.a51.generate_keystream(len(plain_bits))
        print("Keystream bits:", "".join(map(str, keystream)))

        ciphertext = [plain_bits[i] ^ keystream[i] for i in range(len(plain_bits))]
        print("Ciphertext bits:", "".join(map(str, ciphertext)))

        self.a51._standard_init(0)
        keystream_again = self.a51.generate_keystream(len(ciphertext))
        decrypted_bits = [ciphertext[i] ^ keystream_again[i] for i in range(len(ciphertext))]
        decrypted_text = self.a51.bits_to_text(decrypted_bits)

        print("Decrypted bits:", "".join(map(str, decrypted_bits)))
        print("Decrypted text:", decrypted_text)

        self.assertEqual(plain_bits, decrypted_bits)
        self.assertEqual(input_text, decrypted_text)


if __name__ == '__main__':
    unittest.main()
