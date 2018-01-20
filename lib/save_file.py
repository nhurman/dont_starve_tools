#!/usr/bin/env python3

import argparse
import base64
from slpp import slpp as lua
import struct
import sys
import zlib

from .util import Reader, Printable, BinData


def read_file(data: BinData) -> BinData:
    file_header = data[:11]
    file_contents = data[11:]

    assert(file_header[:10] == b'KLEI     1')
    file_type = file_header[10]
    assert(file_type in (32, 68))

    final_data: BinData = None

    if file_type == 32: # Plain
        final_data = file_contents
    elif file_type == 68: # Encoded
        b64_data = base64.b64decode(file_contents)
        zlib_header = b64_data[:16]
        zlib_data = b64_data[16:]
        (
            magic1,
            magic2,
            inflated_len,
            deflated_len
        ) = struct.unpack('<IIII', zlib_header)
        assert(magic1 == 1)
        assert(magic2 == 16)
        assert(len(zlib_data) == deflated_len)
        final_data = zlib.decompress(zlib_data)
        assert(len(final_data) == inflated_len)

    return final_data


def parse_lua(data: BinData):
    assert(data.startswith(b'return '))
    d = data[7:].decode('utf-8')
    return lua.decode(d)


def write_file(data: BinData, encoded: bool=False) -> bytes:
    file_header = b'KLEI     1'

    if not encoded:
        file_header += bytes([32])
        file_contents = data
    else:
        file_header += bytes([68])
        zlib_data = zlib.compress(data, 9) # type: ignore

        magic1 = 1
        magic2 = 16
        inflated_len = len(data)
        deflated_len = len(zlib_data)

        zlib_header = struct.pack(
            '<IIII',
            magic1,
            magic2,
            inflated_len,
            deflated_len
        )

        file_contents = base64.b64encode(zlib_header + zlib_data)

    return file_header + file_contents # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Utility to parse `Don\'t Starve` save files.'
    )
    parser.add_argument('mode', choices=['r', 'w', 'wc'],
        help='Read/Write/Write Compressed. Takes input from stdin in write mode.')
    parser.add_argument('filename', help='File path')
    args = parser.parse_args()

    data: BinData = None

    if args.mode == 'r':
        with open(args.filename, 'rb') as fp:
            data = memoryview(fp.read())
            sys.stdout.buffer.write(read_file(data)) # type: ignore
    elif args.mode in ('w', 'wc'):
        data = memoryview(sys.stdin.buffer.read())
        with open(args.filename, 'wb+') as fp:
            compress = (args.mode == 'wc')
            fp.write(write_file(data, compress))


if __name__ == '__main__':
    main()
