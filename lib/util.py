from json import JSONEncoder
import struct
import time
from typing import Generic, TypeVar, Union


BinData = Union[bytes, memoryview]
T = TypeVar('T')

# This not really a generic, it has to be indexable
class Reader(Generic[T]):
    """
    Tokenizer
    """
    def __init__(self, data: T) -> None:
        self.data = data
        self.offset: int = 0

    def read_uint32(self) -> int:
        i = struct.unpack(
            '<I',
            self.data[self.offset:self.offset+4] # type: ignore
        )[0]
        self.offset += 4
        return i

    def read_uint16(self) -> int:
        i = struct.unpack(
            '<H',
            self.data[self.offset:self.offset+2] # type: ignore
        )[0]
        self.offset += 2
        return i

    def read_float(self) -> float:
        i = struct.unpack(
            '<f',
            self.data[self.offset:self.offset+4] # type: ignore
        )[0]
        self.offset += 4
        return i

    def read_string(self) -> T:
        str_len = self.read_uint32()
        str_dat = self.data[self.offset:self.offset+str_len] # type: ignore
        self.offset += str_len
        return str_dat

    def read_bytes(self, size: int) -> T:
        dat = self.data[self.offset:self.offset+size] # type: ignore
        self.offset += size
        return dat


class Printable:
    """
    Helper class to somewhat print an object's value based on its attribs
    """
    __noprint__ = []

    def __repr__(self) -> str:
        out = {}
        for k in dir(self):
            if not k.startswith('_'):
                attr = getattr(self, k)
                if callable(attr):
                    continue
                if isinstance(attr, memoryview):
                    attr = attr.tobytes()
                out[k] = attr
        return repr(out)

    def json_value(self):
        raise NotImplementedError()

    def to_json(self, **kwargs) -> str:
        class Encoder(JSONEncoder):
            def default(self, o):
                if isinstance(o, memoryview):
                    try:
                        return o.tobytes().decode('utf-8')
                    except UnicodeDecodeError:
                        return repr(o.tobytes())
                if isinstance(o, bytes):
                    try:
                        return o.decode('utf-8')
                    except UnicodeDecodeError:
                        return repr(o)

                if isinstance(o, Printable):
                    try:
                        return o.json_value()
                    except NotImplementedError:
                        return {
                            k:v for k,v in o.__dict__.items()
                            if k not in o.__noprint__
                        }
                try:
                    return o.__dict__
                except AttributeError:
                    return super().default(o)
        return Encoder(**kwargs).encode(self)


class Timed:
    """
    Prints the run time of the enclosed block
    """
    ENABLED = False

    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self, *args) -> 'Timed':
        self.start = time.time()
        return self

    def __exit__(self, *args) -> None:
        if not self.ENABLED:
            return
        elapsed = time.time() - self.start
        print(f'Elapsed[{self.name}]: {elapsed}s')


class Struct(Printable):
    @staticmethod
    def read(reader):
        raise NotImplementedError()

    @staticmethod
    def write(writer):
        raise NotImplementedError()
