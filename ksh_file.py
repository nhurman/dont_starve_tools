#!/usr/bin/env python3

import argparse
import os
import pprint
import struct
import sys
from typing import List, TypeVar

from util import Reader, Printable, BinData


class HWEffect(Printable):
    def __init__(self) -> None:
        self.name: BinData = None
        self.n_parameters: int = None
        self.parameters: List[ShaderParameter] = None
        self.vertex_shader: Shader = None
        self.pixel_shader: Shader = None
        self.shader_program: ShaderProgram = None


class Shader(Printable):
    __noprint__ = ['code']

    def __init__(self) -> None:
        self.name: BinData = None
        self.code: BinData = None


class ShaderParameter(Printable):
    def __init__(self) -> None:
        self.name: BinData = None
        self.unk1: BinData = None
        self.flags: int = None
        self.values_per_item: int = None
        self.n_defaults: int = 0
        self.defaults: List[float] = None


class ShaderProgram(Printable):
    def __init__(self) -> None:
        self.n_vertex_uniforms: int = None
        self.vertex_uniforms: List[int] = None
        self.n_pixel_uniforms: int = None
        self.pixel_uniforms: List[int] = None


def read_file(data: BinData) -> HWEffect:
    reader = Reader(data)
    effect = HWEffect()

    effect.name = reader.read_string()

    ## ParameterPool
    effect.n_parameters = reader.read_uint32()
    effect.parameters = []
    for i in range(effect.n_parameters):
        param = ShaderParameter()
        param.name = reader.read_string()
        param.unk1 = reader.read_string()
        param.flags = reader.read_uint32()
        param.values_per_item = reader.read_uint32()

        if not 42 <= param.flags <= 45:
            param.n_defaults = reader.read_uint32()
            param.defaults = []
            for j in range(param.n_defaults):
                param.defaults.append(reader.read_float())
        effect.parameters.append(param)

    ## VertexShader
    vertex_shader = Shader()
    vertex_shader.name = reader.read_string()
    vertex_shader.code = reader.read_string()
    if vertex_shader.code[-1] == 0:
        vertex_shader.code = vertex_shader.code[:-1]
    effect.vertex_shader = vertex_shader

    ## PixelShader
    pixel_shader = Shader()
    pixel_shader.name = reader.read_string()
    pixel_shader.code = reader.read_string()
    if pixel_shader.code[-1] == 0:
        pixel_shader.code = pixel_shader.code[:-1]
    effect.pixel_shader = pixel_shader

    ## ShaderProgram
    program = ShaderProgram()
    program.n_vertex_uniforms = reader.read_uint32()
    program.vertex_uniforms = []
    for i in range(program.n_vertex_uniforms):
        program.vertex_uniforms.append(reader.read_uint32())

    program.n_pixel_uniforms = reader.read_uint32()
    program.pixel_uniforms = []
    for i in range(program.n_pixel_uniforms):
        program.pixel_uniforms.append(reader.read_uint32())

    effect.shader_program = program

    return effect


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Utility to parse `Don\'t Starve` shader (.ksh) files.'
    )
    parser.add_argument('mode', choices=['r', 'w'], help='Read/Write')
    parser.add_argument('filename', help='File path')
    parser.add_argument('extract', choices=['vertex', 'pixel', 'unpack'],
        nargs='?', help='Extract vertex/pixel shader to stdout. ' + \
        'Unpack extracts both files to their original file names in the ' + \
        '`dest` directory (defaults to current directory)')
    parser.add_argument('--overwrite', action='store_true',
        help='Overwrite existing files in unpack mode')
    parser.add_argument('--dest', default='.',
        help='Output directory in `unpack` mode')
    args = parser.parse_args()

    if args.mode == 'r':
        with open(args.filename, 'rb') as fp:
            data = memoryview(fp.read())
            out = read_file(data)
            if args.extract == 'vertex':
                sys.stdout.buffer.write(out.vertex_shader.code)
            elif args.extract == 'pixel':
                sys.stdout.buffer.write(out.pixel_shader.code)
            elif args.extract == 'unpack':
                mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
                if not args.overwrite:
                    mode |= os.O_EXCL

                n = os.path.join(
                    args.dest,
                    os.path.basename(
                        out.vertex_shader.name.tobytes().decode('utf-8'))
                )
                if not args.overwrite and os.path.exists(n):
                    print('File already exists: ' + n + \
                        ' (add --overwrite if ok)')
                else:
                    os.makedirs(args.dest, exist_ok=True)
                    fd = os.open(n, mode)
                    os.write(fd, out.vertex_shader.code)
                    os.close(fd)
                    print(f'Extracted {n}')

                n = os.path.join(
                    args.dest,
                    os.path.basename(
                        out.pixel_shader.name.tobytes().decode('utf-8'))
                )
                if not args.overwrite and os.path.exists(n):
                    print('File already exists: ' + n + \
                        ' (add --overwrite if ok)')
                else:
                    os.makedirs(args.dest, exist_ok=True)
                    fd = os.open(n, mode)
                    os.write(fd, out.pixel_shader.code)
                    os.close(fd)
                    print(f'Extracted {n}')
            else:
                print(out.to_json(indent=4))
    elif args.mode == 'w':
        raise NotImplementedError


if __name__ == '__main__':
    main()
