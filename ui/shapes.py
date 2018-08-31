from ctypes import *
import glm
from OpenGL.GL import *
import struct

from . import gl_utils as utils


def colored_object(vertices, colors, draw_type):
    asset = utils.Asset()
    shaders = []
    shaders.append(utils.Shader.load_file(
        'ui/colors.vs',
        GL_VERTEX_SHADER
    ))
    shaders.append(utils.Shader.load_file(
        'ui/colors.ps',
        GL_FRAGMENT_SHADER
    ))
    asset.shaders = utils.Program(shaders)
    data = struct.pack(
        '{}f'.format(len(vertices) + len(colors)),
        *vertices,
        *colors
    )

    with asset:
        glBufferData(
            GL_ARRAY_BUFFER,
            len(data),
            data,
            GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(asset.shaders.attrib('vertPos'))
        glEnableVertexAttribArray(asset.shaders.attrib('vertColor'))
        glVertexAttribPointer(
            index=asset.shaders.attrib('vertPos'),
            size=3,
            type=GL_FLOAT,
            normalized=GL_FALSE,
            stride=0,
            pointer=None
        )
        glVertexAttribPointer(
            index=asset.shaders.attrib('vertColor'),
            size=4,
            type=GL_FLOAT,
            normalized=GL_FALSE,
            stride=0,
            pointer=c_void_p(sizeof(c_float)*len(vertices))
        )

    asset.draw_start = 0
    asset.draw_count = int(len(vertices) / 3)
    asset.draw_type = draw_type
    return utils.Instance(asset)


def axes():
    bounds = [0, 1]

    # Axes
    vertices, colors = [], []
    vertices.extend([
        # X
        bounds[0], 0, 0,
        bounds[1], 0, 0,
        # Y
        0, bounds[0], 0,
        0, bounds[1], 0,
        # Z
        0, 0, bounds[0],
        0, 0, bounds[1],
    ])
    colors.extend([
        # X
        1, 0, 0, 1,
        1, 0, 0, 1,
        # Y
        0, 1, 0, 1,
        0, 1, 0, 1,
        # Z
        0, 0.3, 1, 1,
        0, 0.3, 1, 1,
    ])

    return colored_object(vertices, colors, GL_LINES)


def grid(bounds=[-1, 1], precision=0.1):
    steps = [
        i * precision
        for i in range(int(bounds[0] / precision), int(bounds[1] / precision), 1)
    ]
    steps.append(steps[-1] + steps[-1] - steps[-2])

    vertices, colors = [], []
    for i in steps:
        vertices.extend([
            # X
            0, bounds[0], i,
            0, bounds[1], i,
            0, i, bounds[0],
            0, i, bounds[1],
            # Y
            bounds[0], 0, i,
            bounds[1], 0, i,
            i, 0, bounds[0],
            i, 0, bounds[1],
            # Z
            bounds[0], i, 0,
            bounds[1], i, 0,
            i, bounds[0], 0,
            i, bounds[1], 0,
        ])
        alpha = 0.2
        colors.extend([
            *((1, 0, 0, alpha) * 4), # X
            *((0, 1, 0, alpha) * 4), # X
            *((0, 0.3, 1, alpha) * 4), # Z
        ])

    return colored_object(vertices, colors, GL_LINES)


def quad_to_tris(vertices):
    return [
        *vertices[0],
        *vertices[1],
        *vertices[2],
        *vertices[2],
        *vertices[3],
        *vertices[0],
    ]


def planes(bounds=[-1, 1]):
    vertices, colors = [], []
    vertices.extend([
        # X
        *quad_to_tris((
            (0, bounds[0], bounds[0]),
            (0, bounds[0], bounds[1]),
            (0, bounds[1], bounds[1]),
            (0, bounds[1], bounds[0]),
        )),
        # Y
        *quad_to_tris((
            (bounds[0], 0, bounds[0]),
            (bounds[0], 0, bounds[1]),
            (bounds[1], 0, bounds[1]),
            (bounds[1], 0, bounds[0]),
        )),
        # Z
        *quad_to_tris((
            (bounds[0], bounds[0], 0),
            (bounds[0], bounds[1], 0),
            (bounds[1], bounds[1], 0),
            (bounds[1], bounds[0], 0),
        )),
    ])
    alpha = 1
    colors.extend([
        # X
        *([1, 0, 0, alpha] * 6),
        # Y
        *([0, 1, 0, alpha] * 6),
        # Z
        *([0, 0, 1, alpha] * 6),
    ])

    instance = colored_object(vertices, colors, GL_TRIANGLES)
    instance.transform = glm.scale(glm.mat4(1), glm.vec3(0.2, 0.2, 0.2))
    return instance


def triangle():
    vertices = [
        0, 0, 0,
        1, 0, 0,
        0, 1, 0,
    ]
    colors = [
        1, 0, 0, 1,
        0, 1, 0, 1,
        0, 0, 1, 1,
    ]

    return colored_object(vertices, colors, GL_TRIANGLES)


class empty_context():
    def __enter__(self):
        return self
    def __exit__(self, a, b, c):
        return


def reset_depth():
    asset = utils.Asset()
    asset.draw_type = None
    asset.before = lambda: glClear(GL_DEPTH_BUFFER_BIT)
    asset.shaders = empty_context()
    return utils.Instance(asset)