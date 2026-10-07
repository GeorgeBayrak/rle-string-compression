"""RLE String Compression.

A focused library for compressing and decompressing strings using a
character-based run-length encoding scheme that escapes literal digit runs.
"""

from .core import compress, decompress, CompressionError

__all__ = ["compress", "decompress", "CompressionError"]
