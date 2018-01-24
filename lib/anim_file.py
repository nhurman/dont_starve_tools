#!/usr/bin/env python3

from .util import Struct, Reader


class Facing(Struct):
    RIGHT = 1<<0
    UP = 1<<1
    LEFT = 1<<2
    DOWN = 1<<3
    UPRIGHT = 1<<4
    UPLEFT = 1<<5
    DOWNRIGHT = 1<<6
    DOWNLEFT = 1<<7

    def __init__(self):
        self.value = None

    @staticmethod
    def read(reader):
        f = Facing()
        f.value = int(reader.read_bytes(1)[0])
        return f

    def json_value(self):
        return str(self)

    def __str__(self):
        out = []
        if self.value == 0xff:
            return f'{self.value} (ALL)'
        if self.value & self.RIGHT:
            out.append('RIGHT')
        if self.value & self.UP:
            out.append('UP')
        if self.value & self.LEFT:
            out.append('LEFT')
        if self.value & self.DOWN:
            out.append('DOWN')
        if self.value & self.UPRIGHT:
            out.append('UPRIGHT')
        if self.value & self.UPLEFT:
            out.append('UPLEFT')
        if self.value & self.DOWNRIGHT:
            out.append('DOWNRIGHT')
        if self.value & self.DOWNLEFT:
            out.append('DOWNLEFT')
        return f'{self.value} ({"|".join(out)})'


class Animation(Struct):
    def __init__(self):
        self.name = None
        self.valid_facings = None
        self.root_symbol = None
        self.frame_rate = None
        self.n_frames = None
        self.frames = None

    @staticmethod
    def read(reader):
        a = Animation()
        a.name = reader.read_string()
        a.valid_facings = Facing.read(reader)
        a.root_symbol = reader.read_uint32()
        a.frame_rate = reader.read_float()
        a.n_frames  = reader.read_uint32()
        a.frames = []
        for _ in range(a.n_frames):
            a.frames.append(Frame.read(reader))

        return a


class Frame(Struct):
    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.n_events = None
        self.events = None
        self.n_elements = None
        self.elements = None

    @staticmethod
    def read(reader):
        f = Frame()
        f.x = reader.read_float()
        f.y = reader.read_float()
        f.w = reader.read_float()
        f.h = reader.read_float()
        f.n_events = reader.read_uint32()
        f.events = []
        for _ in range(f.n_events):
            f.events.append(reader.read_uint32())

        f.n_elements = reader.read_uint32()
        f.elements = []
        for _ in range(f.n_elements):
            f.elements.append(Element.read(reader))

        return f


class Element(Struct):
    def __init__(self):
        self.symbol_hash = None
        self.symbol_frame = None
        self.folder_hash = None
        self.mat = None

    @staticmethod
    def read(reader):
        e = Element()
        e.symbol_hash = reader.read_float()
        e.symbol_frame = reader.read_float()
        e.folder_hash = reader.read_float()
        e.mat = Mat.read(reader)
        return e


class Mat(Struct):
    def __init__(self):
        self.a = None
        self.b = None
        self.c = None
        self.d = None
        self.tx = None
        self.ty = None
        self.z = None

    @staticmethod
    def read(reader):
        m = Mat()
        m.a = reader.read_float()
        m.b = reader.read_float()
        m.c = reader.read_float()
        m.d = reader.read_float()
        m.tx = reader.read_float()
        m.ty = reader.read_float()
        m.z = reader.read_float()
        return m


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


class ANIM(Struct):
    def __init__(self):
        self.magic = None
        self.version = None
        self.n_total_elements = None
        self.n_frames = None
        self.n_total_events = None
        self.n_animations = None
        self.animations = []

    @staticmethod
    def read(reader):
        a = ANIM()
        a.magic = reader.read_bytes(4)
        assert a.magic == b'ANIM'
        a.version = reader.read_uint32()
        assert a.version == 4

        a.n_total_elements = reader.read_uint32()
        a.n_frames = reader.read_uint32()
        a.n_total_events = reader.read_uint32()
        a.n_animations = reader.read_uint32()
        a.animations = []
        for _ in range(a.n_animations):
            a.animations.append(Animation.read(reader))

        a.n_strings = reader.read_uint32()
        a.strings = []
        for _ in range(a.n_strings):
            a.strings.append(HashedString.read(reader))

        return a


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fp:
        data = memoryview(fp.read())
    print(ANIM.read(Reader(data)).to_json(indent=4))
