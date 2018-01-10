#!/usr/bin/env python3

import argparse
import base64
from enum import Enum
import PIL.Image
from pprint import pprint
import squish
import struct
import sys
from typing import List
import zlib

from util import Reader, Timed
# Timed.ENABLED = True


class PixelFormat(Enum):
    DXT1 = 0
    DXT3 = 1
    DXT5 = 2
    RGBA = 4
    UNK = 7


class Platform(Enum):
    ANY = 0
    PS3 = 10
    XBOX360 = 11
    PC = 12


class TextureType(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    CUBE = 4


class MipMap:
    def __init__(self) -> None:
        self.width: int = None
        self.height: int = None
        self.pitch: int = None
        self.size: int = None
        self.data: memoryview = None


class TexFile:
    def __init__(self) -> None:
        self.platform: Platform = None
        self.pixel_format: PixelFormat = None
        self.texture_type: TextureType = None
        self.mips: int = None
        self.flags: int = None
        self.unk1: int = None
        self.mipmaps: List[MipMap] = None


def read_compressed(tex: TexFile, mipmap_index: int) -> PIL.Image:
    assert(tex.pixel_format in (
        PixelFormat.DXT1,
        PixelFormat.DXT3,
        PixelFormat.DXT5,
        PixelFormat.RGBA)
    )
    pf_to_squish = {
        PixelFormat.DXT1: squish.DXT1,
        PixelFormat.DXT3: squish.DXT3,
        PixelFormat.DXT5: squish.DXT5
    }

    mipmap = tex.mipmaps[mipmap_index]
    if tex.pixel_format in pf_to_squish:
        with Timed('squish.decompressImage'):
            decompressed_data = memoryview(squish.decompressImage(
                mipmap.data.tobytes(),
                mipmap.width,
                mipmap.height,
                pf_to_squish[tex.pixel_format]
            ))
    elif tex.pixel_format == PixelFormat.RGBA:
        decompressed_data = mipmap.data


    with Timed('PIL.Image.frombuffer'):
        image = PIL.Image.frombuffer(
            'RGBA',
            (mipmap.width, mipmap.height),
            decompressed_data,
            'raw',
            'RGBA',
            0,
            -1 # Vertical flip (along x)
        )

    return image


def read_file(data: memoryview) -> TexFile:
    data = data
    reader = Reader(data)
    assert(reader.read_bytes(4) == b'KTEX')

    b = reader.read_uint32()
    tex = TexFile()
    tex.platform = Platform(b & 15)
    tex.pixel_format = PixelFormat((b >> 4) & 31)
    tex.texture_type = TextureType((b >> 9) & 15)
    tex.mips = (b >> 13) & 31
    tex.flags = (b >> 18) & 3
    tex.unk1 = (b >> 20) & 4095

    mipmaps = []
    for i in range(tex.mips):
        m = MipMap()
        m.width = reader.read_uint16()
        m.height = reader.read_uint16()
        m.pitch = reader.read_uint16()
        m.size = reader.read_uint32()
        mipmaps.append(m)

    for i in range(tex.mips):
        mipmaps[i].data = reader.read_bytes(mipmaps[i].size)

    tex.mipmaps = mipmaps
    return tex


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Utility to parse `Don\'t Starve` texture (.tex) files.',
        epilog='If a mipmap index is not provided, it will list the mipmaps.'
    )
    parser.add_argument('mode', choices=['r', 'w'],
        help='Read/Write')
    parser.add_argument('filename', help='File path')
    parser.add_argument('mipmap', nargs='?', type=int, default=None, help='Mipmap index (starts at 0)')
    parser.add_argument('--image', required=False,
        help='Extracted image file path. Open the image in a new window if unspecified.')
    args = parser.parse_args()

    if args.mode == 'r':
        with open(args.filename, 'rb') as fp:
            data = memoryview(fp.read())
            tex = read_file(data)
            if args.mipmap != None:
                image = read_compressed(tex, args.mipmap)
                if args.image != None:
                    with Timed('PIL.Image.save'):
                        image.save(args.image)
                else:
                    image.show()
            else:
                pprint(dict({k: v for k, v in tex.__dict__.items() if k != 'mipmaps'}))
                pprint(list(dict({k: v for k, v in mipmap.__dict__.items() if k != 'data'}) for mipmap in tex.mipmaps))
    elif args.mode in ('w', 'wc'):
        raise NotImplementedError


if __name__ == '__main__':
    main()
