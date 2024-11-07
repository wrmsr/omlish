"""
TODO:
 - clean up interface - not supposed to be full fileobjs! do not subclass DecompressReader
 - http: 'Accept-Encoding: 'gzip, deflate, zstd'

Impls:
 - std
  - lzma
 - ext
  - lz4.frame
  - snappy
  - zstandard
"""
