#!/usr/bin/env python3

from .util import Struct, Reader


class Symbol(Struct):
    def __init__(self):
        self.hash = None
        self.n_frames = None
        self.frames = None

    @staticmethod
    def read(reader):
        s = Symbol()
        s.hash = reader.read_uint32()
        s.n_frames  = reader.read_uint32()
        s.frames = []
        for _ in range(s.n_frames):
            s.frames.append(Frame.read(reader))

        return s


class Bbox(Struct):
    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None

    @staticmethod
    def read(reader):
        b = Bbox()
        b.x = reader.read_float()
        b.y = reader.read_float()
        b.w = reader.read_float()
        b.h = reader.read_float()
        return b


class Frame(Struct):
    def __init__(self):
        self.num = None
        self.duration = None
        self.bbox = None
        self.alpha_index = None
        self.n_alpha = None

    @staticmethod
    def read(reader):
        f = Frame()
        f.num = reader.read_uint32()
        f.duration = reader.read_uint32()
        f.bbox = Bbox.read(reader)
        f.alpha_index = reader.read_uint32()
        f.n_alpha = reader.read_uint32()
        return f


class Vertex(Struct):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.u = None
        self.v = None
        self.w = None

    @staticmethod
    def read(reader):
        v = Vertex()
        v.x = reader.read_float()
        v.y = reader.read_float()
        v.z = reader.read_float()
        v.u = reader.read_float()
        v.v = reader.read_float()
        v.w = reader.read_float()
        return v


class HashedString(Struct):
    def __init__(self):
        self.hash = None
        self.str = None

    @staticmethod
    def read(reader):
        h = HashedString()
        h.hash = reader.read_uint32()
        h.str = reader.read_string()
        return h


class BILD(Struct):
    def __init__(self):
        self.magic = None
        self.version = None
        self.n_symbols = None
        self.n_frames = None
        self.build_name = None
        self.n_materials = None
        self.materials = None
        self.symbols = None
        self.n_vertices = None
        self.vertices = None
        self.n_strings = None
        self.strings = None

    @staticmethod
    def read(reader):
        b = BILD()
        b.magic = reader.read_bytes(4)
        assert b.magic == b'BILD'
        b.version = reader.read_uint32()
        assert b.version == 6

        b.n_symbols = reader.read_uint32()
        b.n_frames = reader.read_uint32()
        b.build_name = reader.read_string()
        b.n_materials = reader.read_uint32()

        b.materials = []
        for _ in range(b.n_materials):
            b.materials.append(reader.read_string())

        b.symbols = []
        for _ in range(b.n_symbols):
            b.symbols.append(Symbol.read(reader))

        b.n_vertices = reader.read_uint32()
        b.vertices = []
        for _ in range(b.n_vertices):
            b.vertices.append(Vertex.read(reader))

        b.n_strings = reader.read_uint32()
        b.strings = []
        for _ in range(b.n_strings):
            b.strings.append(HashedString.read(reader))

        return b


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fp:
        data = memoryview(fp.read())
    print(BILD.read(Reader(data)).to_json(indent=4))
