"""
TODO:
 - zipfile?
 - tarfile?
 - lzf?
 - blosc?
 - python-lzo?
 - zfp -> fp8?

Compression choice:
 - lzma if-available minimal-space
 - lz4 if-available read-heavy
 - zstd if-available
 - bz2 read-heavy (but no parallel decompress)
 - gz
"""
