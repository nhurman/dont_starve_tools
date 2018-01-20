from ctypes import *
import struct
import ui.gl_utils as utils
from OpenGL.GL import *
import glm

def axes():
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
        0, 0.5, 1, 1,
        0, 0.5, 1, 1,
    ])
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
    asset.draw_type = GL_LINES

    def before():
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
    def after():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

    asset.before = before
    asset.after = after

    instance = utils.Instance()
    instance.asset = asset
    return instance


def grid():
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

    bounds = [-1, 1]
    precision = 100
    steps = [
        i / precision
        for i in range(precision * bounds[0], precision * bounds[1], 1)
    ]

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
        alpha = 0.1
        colors.extend([
            # X
            1, 0, 0, alpha,
            1, 0, 0, alpha,
            1, 0, 0, alpha,
            1, 0, 0, alpha,
            # Y
            0, 1, 0, alpha,
            0, 1, 0, alpha,
            0, 1, 0, alpha,
            0, 1, 0, alpha,
            # Z
            0, 0.5, 1, alpha,
            0, 0.5, 1, alpha,
            0, 0.5, 1, alpha,
            0, 0.5, 1, alpha,
        ])
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
    asset.draw_type = GL_LINES

    instance = utils.Instance()
    instance.asset = asset
    return instance


def triangle():
    tr = utils.Asset()
    shaders = []
    shaders.append(utils.Shader.load_file(
        'ui/colors.vs',
        GL_VERTEX_SHADER
    ))
    shaders.append(utils.Shader.load_file(
        'ui/colors.ps',
        GL_FRAGMENT_SHADER
    ))
    tr.shaders = utils.Program(shaders)

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
    data = struct.pack(
        '{}f'.format(len(vertices) + len(colors)),
        *vertices,
        *colors
    )

    with tr:
        glBufferData(
            GL_ARRAY_BUFFER,
            len(data),
            data,
            GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(tr.shaders.attrib('vertPos'))
        glEnableVertexAttribArray(tr.shaders.attrib('vertColor'))
        glVertexAttribPointer(
            index=tr.shaders.attrib('vertPos'),
            size=3,
            type=GL_FLOAT,
            normalized=GL_FALSE,
            stride=0,
            pointer=None
        )
        glVertexAttribPointer(
            index=tr.shaders.attrib('vertColor'),
            size=4,
            type=GL_FLOAT,
            normalized=GL_TRUE,
            stride=0,
            pointer=c_void_p(sizeof(c_float)*len(vertices))
        )

    tr.draw_start = 0
    tr.draw_count = 3
    tr.draw_type = GL_TRIANGLES

    tra = glm.translate(
        glm.mat4(),
        glm.vec3(0, 0, 0)
    )
    sca = glm.scale(
        glm.mat4(),
        glm.vec3(1, 1, 1)
    )

    instance = utils.Instance()
    instance.asset = tr
    instance.transform = tra * glm.mat4()
    return instance
