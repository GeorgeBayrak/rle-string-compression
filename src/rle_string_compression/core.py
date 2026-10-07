"""Core run-length encoding logic.

The encoding scheme
-------------------
A run of the *same* character of length >= 4 is written as the character,
followed by a digit giving the run length, followed by the character again.
For example, ``aaaa`` becomes ``a4a``.

Runs of length 1, 2, or 3 are left as literal characters, because encoding
them (``a1a``, ``a2a``, ``a3a``) is the same length or longer than the
original and would only add decode overhead.

Why digits are escaped
----------------------
The encoded form mixes characters and run-length digits. To keep the format
unambiguous on decompression, any literal run of decimal digits in the
*input* must be escaped, otherwise a decoder could mistake a literal digit
for a run-length count. We escape a run of one or more digits by prefixing it
with ``'\\\\'`` and suffixing it with ``'\\\\'``. For example, the input
``'123'`` becomes ``'\\\\123\\\\'``. Because ``'\\\\'`` is not a decimal
digit, the decoder can always tell an escaped digit run apart from a
run-length count.

Why the ``\\`` sentinel
-----------------------
A backslash is a poor choice in many formats because it is overloaded as a
generic escape. It is used here deliberately because the input domain is
arbitrary text that may contain *any* printable character, including digits
and punctuation. We need a sentinel that is (a) not a digit, so the decoder
never confuses it with a count, and (b) cheap to produce and inspect. The
backslash satisfies both. The trade-off is that a literal ``'\\\\'`` in the
input is itself escaped (doubled) so it cannot masquerade as a sentinel.
"""

from __future__ import annotations

from typing import List


class CompressionError(ValueError):
    """Raised when a string cannot be decoded as valid RLE output."""


_ESCAPE = "\\"
_DIGITS = "0123456789"


def _is_digit(ch: str) -> bool:
    # str.isdigit() returns True for unicode superscripts and other oddities;
    # we only care about ASCII decimal digits for run-length counts.
 return ch in _DIGITS


def compress(text: str) -> str:
    """Compress ``text`` using character-based RLE with digit escaping.

    The output is always decodable by :func:`decompress`. Empty input yields
    empty output.

    Args:
        text: The string to compress.

    Returns:
        The compressed string.
    """
    if not isinstance(text, str):
        raise TypeError("compress() expects str, got %r" % type(text).__name__)

    out: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if ch == _ESCAPE:
            # A literal backslash would be indistinguishable from our
            # sentinel, so we double it. The decoder treats a doubled
            # backslash as a single literal backslash.
            out.append(_ESCAPE)
            out.append(_ESCAPE)
            i += 1
            continue

        if _is_digit(ch):
            # Find the full run of consecutive digits so we escape the whole
            # run with a single pair of sentinels rather than each digit.
            j = i
            while j < n and _is_digit(text[j]):
                j += 1
            out.append(_ESCAPE)
            out.append(text[i:j])
            out.append(_ESCAPE)
            i = j
            continue

        # Ordinary character: find the run length and decide whether encoding
        # pays off. We encode only runs of length >= 4, since shorter runs
        # would not get smaller.
        j = i
        while j < n and text[j] == ch:
            j += 1
        run = j - i
        if run >= 4:
            out.append(ch)
            out.append(str(run))
            out.append(ch)
        else:
            out.append(ch * run)
        i = j

    return "".join(out)


def decompress(text: str) -> str:
    """Decompress a string produced by :func:`compress`.

    Args:
        text: The compressed string.

    Returns:
        The original uncompressed string.

    Raises:
        CompressionError: If ``text`` is not a valid compressed string.
    """
    if not isinstance(text, str):
        raise TypeError("decompress() expects str, got %r" % type(text).__name__)

    out: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if ch == _ESCAPE:
            if i + 1 >= n:
                raise CompressionError("dangling escape at end of input")
            nxt = text[i + 1]
            if nxt == _ESCAPE:
                # Doubled backslash: a single literal backslash in the
                # original input.
                out.append(_ESCAPE)
                i += 2
                continue
            if _is_digit(nxt):
                # Escaped digit run: copy digits verbatim until the closing
                # sentinel.
                j = i + 1
                while j < n and _is_digit(text[j]):
                    j += 1
                if j >= n or text[j] != _ESCAPE:
                    raise CompressionError(
                        "unterminated escaped digit run at position %d" % i
                    )
                out.append(text[i + 1 : j])
                i = j + 1
                continue
            raise CompressionError(
                "invalid escape sequence at position %d" % i
            )

        if _is_digit(ch):
            # A bare digit (not part of an escape and not a run-length count,
            # because those are consumed by the run-length branch below) is
            # never valid in compressed output.
            raise CompressionError(
                "unexpected bare digit %r at position %d" % (ch, i)
            )

        # Ordinary character. If the next character is a digit and the
        # character after that is the same as the current one, this is an
        # encoded run. Otherwise it is a single literal character.
        if (
            i + 2 < n
            and _is_digit(text[i + 1])
            and text[i + 2] == ch
        ):
            count = int(text[i + 1])
            out.append(ch * count)
            i += 3
            continue

        out.append(ch)
        i += 1

    return "".join(out)
