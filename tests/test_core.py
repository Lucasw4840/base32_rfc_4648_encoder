import unittest

from base32_rfc_4648_encoder import encode, decode


class EncodeTests(unittest.TestCase):
    # RFC 4648 Section 10 test vectors.
    RFC_VECTORS = [
        (b"", ""),
        (b"f", "MY======"),
        (b"fo", "MZXQ===="),
        (b"foo", "MZXW6==="),
        (b"foob", "MZXW6YQ="),
        (b"fooba", "MZXW6YTB"),
        (b"foobar", "MZXW6YTBOI======"),
    ]

    def test_rfc_vectors(self):
        for data, expected in self.RFC_VECTORS:
            with self.subTest(data=data):
                self.assertEqual(encode(data), expected)

    def test_returns_str(self):
        self.assertIsInstance(encode(b"x"), str)

    def test_output_always_uppercase(self):
        # Even though b32encode already returns upper-case, pin the contract so
        # a future stdlib regression cannot silently change the case.
        result = encode(b"lower")
        self.assertEqual(result, result.upper())

    def test_output_length_is_multiple_of_eight(self):
        for data, _ in self.RFC_VECTORS:
            with self.subTest(data=data):
                self.assertEqual(len(encode(data)) % 8, 0)

    def test_bytearray_accepted(self):
        self.assertEqual(encode(bytearray(b"foo")), "MZXW6===")

    def test_str_input_rejected(self):
        with self.assertRaises(TypeError):
            encode("foo")  # type: ignore[arg-type]

    def test_none_input_rejected(self):
        with self.assertRaises(TypeError):
            encode(None)  # type: ignore[arg-type]


class DecodeTests(unittest.TestCase):
    def test_rfc_vectors_round_trip(self):
        for data, encoded in EncodeTests.RFC_VECTORS:
            with self.subTest(encoded=encoded):
                self.assertEqual(decode(encoded), data)

    def test_lowercase_accepted(self):
        # RFC 4648 Section 3.2: decoders MUST treat upper and lower as
        # equivalent.
        self.assertEqual(decode("my======"), b"f")
        self.assertEqual(decode("mzxw6ytboi======"), b"foobar")

    def test_mixed_case_accepted(self):
        self.assertEqual(decode("MzXw6YtBoI======"), b"foobar")

    def test_returns_bytes(self):
        self.assertIsInstance(decode("MY======"), bytes)

    def test_bytes_input_rejected(self):
        with self.assertRaises(TypeError):
            decode(b"MY======")  # type: ignore[arg-type]

    def test_non_alphabet_character_rejected(self):
        with self.assertRaises(ValueError):
            decode("MY=====\n")  # trailing newline is not stripped

    def test_dash_rejected(self):
        # '-' belongs to base32hex / other variants, not RFC 4648 base32.
        with self.assertRaises(ValueError):
            decode("MZXW6YTB-OI======")

    def test_underscore_rejected(self):
        with self.assertRaises(ValueError):
            decode("MZXW6YTB_OI======")

    def test_space_rejected(self):
        with self.assertRaises(ValueError):
            decode("MZXW6YTB OI======")

    def test_incorrect_padding_length_rejected(self):
        # Valid would be "MY======" (six '='). One '=' too few should fail.
        with self.assertRaises(ValueError):
            decode("MY=====")

    def test_missing_padding_rejected(self):
        # 5 bytes of input is exactly 8 base32 chars with no padding needed,
        # so this case must succeed. A truncated value that would otherwise
        # require padding (e.g. 1-byte input needs six '=') is tested above.
        self.assertEqual(decode("MZXW6YTB"), b"fooba")

    def test_empty_string(self):
        self.assertEqual(decode(""), b"")


class RoundTripTests(unittest.TestCase):
    def test_random_lengths_round_trip(self):
        # Deterministic pseudo-random bytes so the test is reproducible.
        import hashlib
        seed = b"base32-rfc-4648-roundtrip"
        for length in range(0, 64):
            data = hashlib.sha256(seed + bytes([length])).digest()[:length]
            with self.subTest(length=length):
                self.assertEqual(decode(encode(data)), data)


if __name__ == "__main__":
    unittest.main()
