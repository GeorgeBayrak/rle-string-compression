import unittest

from rle_string_compression import compress, decompress, CompressionError


class TestRoundtrip(unittest.TestCase):
    def assert_roundtrip(self, s):
        self.assertEqual(decompress(compress(s)), s)

    def test_empty(self):
        self.assertEqual(compress(""), "")
        self.assertEqual(decompress(""), "")

    def test_single_char(self):
        self.assert_roundtrip("a")

    def test_short_runs_not_encoded(self):
        # Runs of length 1-3 are left literal.
        self.assertEqual(compress("aa"), "aa")
        self.assertEqual(compress("aaa"), "aaa")
        self.assert_roundtrip("aa")
        self.assert_roundtrip("aaa")

    def test_long_run_encoded(self):
        self.assertEqual(compress("aaaa"), "a4a")
        self.assertEqual(compress("aaaaa"), "a5a")
        self.assert_roundtrip("aaaa")
        self.assert_roundtrip("aaaaa")

    def test_mixed_text(self):
        s = "aaabcccccd"
        self.assert_roundtrip(s)

    def test_digit_run_escaped(self):
        self.assertEqual(compress("123"), "\\123\\")
        self.assert_roundtrip("123")

    def test_single_digit_escaped(self):
        self.assertEqual(compress("5"), "\\5\\")
        self.assert_roundtrip("5")

    def test_backslash_doubled(self):
        self.assertEqual(compress("\\\\"), "\\\\\\\\")
        self.assert_roundtrip("\\\\")

    def test_backslash_and_digit(self):
        self.assert_roundtip = self.assert_roundtrip
        self.assert_roundtip("a\\1b")

    def test_long_run_of_digits_escaped_once(self):
        # A run of digits is escaped as a single block, not per-digit.
        self.assertEqual(compress("1111"), "\\1111\\")
        self.assert_roundtrip("1111")

    def test_repeated_char_is_digit(self):
        # Digits are never run-length encoded even if they repeat.
        self.assertEqual(compress("5555555"), "\\5555555\\")
        self.assert_roundtrip("5555555")


class TestDecompressErrors(unittest.TestCase):
    def test_bare_digit_rejected(self):
        with self.assertRaises(CompressionError):
            decompress("a1b")

    def test_dangling_escape_rejected(self):
        with self.assertRaises(CompressionError):
            decompress("\\")

    def test_unterminated_escaped_run_rejected(self):
        with self.assertRaises(CompressionError):
            decompress("\\123")

    def test_invalid_escape_rejected(self):
        with self.assertRaises(CompressionError):
            decompress("\\a\\")


class TestTypes(unittest.TestCase):
    def test_compress_rejects_non_str(self):
        with self.assertRaises(TypeError):
            compress(123)

    def test_decompress_rejects_non_str(self):
        with self.assertRaises(TypeError):
            decompress(123)


if __name__ == "__main__":
    unittest.main()
