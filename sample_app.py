#!/usr/bin/env python3
import glm

import ui.gl_utils as utils
import ui.shapes as shapes


class Scene(utils.Scene):
    def __init__(self, *args):
        super().__init__('dont_starve_tools')

    def init(self):
        self.projection = glm.perspective(
            glm.radians(60),
            float(self.screen_x)/self.screen_y,
            0.1,
            10
        )
        self.camera = glm.lookAt(
            eye=glm.vec3(1.5, 1.5, 1.5),
            center=glm.vec3(0, 0, 0),
            up=glm.vec3(0, 1, 0)
        )

        self.triangle = shapes.triangle()
        self.instances.append(self.triangle)
        self.instances.append(shapes.axes())
        self.instances.append(shapes.planes())
        self.instances.append(shapes.grid())

    def update(self, elapsed):
        self.triangle.transform = glm.rotate(
            self.triangle.transform,
            glm.radians(elapsed * 180),
            glm.vec3(0, 1, 0)
        )


def main():
    scene = Scene()
    scene.main()

    # PyOpenGL functions don't work when called during interpreter shutdown,
    # so make it call the destructors before it dies
    scene = None

if __name__ == '__main__':
    main()