from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import glm
import numpy
import PIL.Image


class Shader:
    def __init__(self, source_code, shader_type):
        self.source_code = source_code
        self.shader_type = shader_type

        self._res = glCreateShader(shader_type)
        if not self._res:
            raise RuntimeError('glCreateShader()')

        glShaderSource(self._res, source_code)
        glCompileShader(self._res)

        compile_status = glGetShaderiv(self._res, GL_COMPILE_STATUS)
        if not compile_status:
            msg = b'glCompileShader():\n{}'.format(
                glGetShaderInfoLog(self._res)
            )
            self.__del__()
            raise RuntimeError(msg)

    def __del__(self):
        if self._res:
            glDeleteShader(self._res)
            self._res = 0

    def res(self):
        return self._res

    @staticmethod
    def load_file(path, shader_type):
        with open(path, 'rb') as fp:
            data = fp.read()
        return Shader(data, shader_type)


class Program:
    def __init__(self, shaders):
        self.enabled = False
        self._res = 0
        if not shaders:
            raise RuntimeError('No shaders provided')

        self._res = glCreateProgram()
        if not self._res:
            raise RuntimeError('glCreateProgram()')

        for shader in shaders:
            glAttachShader(self._res, shader.res())
        glLinkProgram(self._res)
        for shader in shaders:
            glDetachShader(self._res, shader.res())

        link_status = glGetProgramiv(self._res, GL_LINK_STATUS)
        if not link_status:
            msg = b'glLinkProgram():\n'.format(
                glGetProgramInfoLog(self._res)
            )
            self.__del__()
            raise RuntimeError(msg)

    def __del__(self):
        if self._res:
            if glDeleteProgram:
                glDeleteProgram(self._res)
            self._res = 0

    def res(self):
        return self._res

    def attrib(self, name):
        pos = glGetAttribLocation(self._res, name)
        if pos == -1:
            raise RuntimeError(f'glGetAttribLocation({name})')
        return pos

    def uniform(self, name):
        pos = glGetUniformLocation(self._res, name)
        if pos == -1:
            raise RuntimeError(f'glGetUniformLocation({name})')
        return pos

    def __enter__(self):
        assert(not self.enabled)
        self.enabled = True
        glUseProgram(self.res())

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert(self.enabled)
        self.enabled = False
        glUseProgram(0)


class Asset:
    def __init__(self):
        self.shaders = None
        self.texture = None
        self.vao = None
        self.vbo = None
        self.draw_type = None
        self.draw_start = 0
        self.draw_count = 0
        self.before = None
        self.after = None

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

    def __del__(self):
        if glDeleteVertexArrays:
            glDeleteVertexArrays(1, numpy.array([self.vao]))
        if glDeleteBuffers:
            glDeleteBuffers(1, numpy.array([self.vbo]))

    def __enter__(self):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


class Instance:
    def __init__(self):
        self.asset = None
        self.transform = glm.mat4()


def error_callback(*args, **kwargs):
    print('------ Error! --------')
    print(args, kwargs)
    print('----------------------')


class Scene:
    def __init__(self, title=''):
        self.title = title
        self.shaders = None
        self.window = None
        self.screen_x = 800
        self.screen_y = 600
        self.instances = []

    def main(self):
        glfw.set_error_callback(error_callback)
        if not glfw.init():
            raise RuntimeError('glfw.init()')

        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(
            self.screen_x,
            self.screen_y,
            self.title,
            None,
            None
        )
        if not self.window:
            raise RuntimeError('glfw.CreateWindow())')

        glfw.make_context_current(self.window)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glClearColor(0, 0, 0, 1)

        # print(b'OpenGL version: ' + glGetString(GL_VERSION))
        # print(b'GLSL version: ' + glGetString(GL_SHADING_LANGUAGE_VERSION))
        # print(b'Vendor: ' + glGetString(GL_VENDOR))
        # print(b'Renderer: ' + glGetString(GL_RENDERER))

        self.init()

        old_time = glfw.get_time()
        try:
            while not glfw.window_should_close(self.window):
                glfw.poll_events()
                if glfw.get_key(self.window, glfw.KEY_ESCAPE):
                    glfw.set_window_should_close(self.window, True)

                now = glfw.get_time()
                self.update(float(now - old_time))
                old_time = now

                self.render()
                glfw.swap_buffers(self.window)
        except KeyboardInterrupt:
            pass

        glfw.terminate()

    def init(self):
        raise NotImplementedError

    def update(self, elapsed):
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        projection = numpy.array(self.projection).tobytes()
        camera = numpy.array(self.camera).tobytes()

        for instance in self.instances:
            with instance.asset.shaders:
                if instance.asset.before:
                    instance.asset.before()
                glUniformMatrix4fv(
                    instance.asset.shaders.uniform('projection'),
                    1,
                    False,
                    projection
                )
                glUniformMatrix4fv(
                    instance.asset.shaders.uniform('camera'),
                    1,
                    False,
                    camera
                )

                transform = numpy.array(instance.transform).tobytes()
                glUniformMatrix4fv(
                    instance.asset.shaders.uniform('transform'),
                    1,
                    False,
                    transform
                )

                with instance.asset:
                    glDrawArrays(
                        instance.asset.draw_type,
                        instance.asset.draw_start,
                        instance.asset.draw_count
                    )

                if instance.asset.after:
                    instance.asset.after()


class Texture:
    def __init__(
        self, width, height, image,
        minMagFiler=GL_LINEAR, wrapMode=GL_CLAMP_TO_EDGE
    ):
        self._res = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, _res)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minMagFiler)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, minMagFiler)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrapMode)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrapMode)
        glTexImage2D(GL_TEXTURE_2D,
            0,
            GL_RGB,
            width,
            height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            image)
        glBindTexture(GL_TEXTURE_2D, 0)
        return self._res

    def __del__(self):
        if self._res:
            glDeleteTextures(self._res)
            self._res = 0

    @staticmethod
    def from_file(path):
        tex = PIL.Image.open(filename)
        width, height, image = (
            tex.size[0],
            tex.size[1],
            tex.tobytes('raw', 'RGB', 0, -1)
        )
        # tex.show()
        return Texture(width, height, image)

