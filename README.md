# RLE String Compression

Compresses and decompresses strings using a character-based run-length encoding scheme that escapes literal digit runs.

```python
from rle_string_compression import compress, decompress

assert compress("aaaa") == "a4a"
assert decompress("a4a") == "aaaa"
assert decompress(compress("aaabcccccd123\\\\")) == "aaabcccccd123\\\\"
```

## Why this exists

Plain run-length encoding is unambiguous only when the alphabet excludes the characters used to express counts. Real text contains digits, so a naive `a4a` scheme collides with literal input like `a4a`. This library escapes literal digit runs with a `\\` sentinel so that encode and decode are exact inverses for arbitrary input. The trade-off is that the format is no longer a drop-in replacement for classic RLE: the compressed form is slightly larger for digit-heavy input, and a literal backslash in the input is doubled.

## Encoding scheme

- A run of the same character of length >= 4 is written as `char` + `count` + `char`. For example, `aaaa` becomes `a4a`.
- Runs of length 1-3 are left literal, since encoding would not shrink them.
- Any run of one or more decimal digits in the input is wrapped in `\\` sentinels. For example, `123` becomes `\\123\\`.
- A literal `\\` in the input is doubled to `\\\\` so it cannot be mistaken for a sentinel.

## Awkward edge

Decompression is strict: a bare digit that is not part of an escaped run or a valid `char` + `count` + `char` triple raises `CompressionError`. Input produced by `compress` always round-trips; hand-written compressed strings that do not follow the scheme exactly will be rejected rather than silently misdecoded.

## Exported names

`compress(text: str) -> str` — compress a string.

`decompress(text: str) -> str` — decompress a string; raises `CompressionError` on malformed input.

`CompressionError` — subclass of `ValueError`, raised by `decompress`.
