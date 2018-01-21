#!/usr/bin/env python3
import glm

import ui.gl_utils as utils
import ui.shapes as shapes


class Scene(utils.Scene):
    def __init__(self, *args):
        super().__init__('dont_starve_tools')

    def init(self):
        super().init()

        # self.instances.append(shapes.planes())
        self.triangle = shapes.triangle()
        self.instances.append(self.triangle)

        # Transparent at the end (and axes on top of everything)
        self.instances.append(shapes.grid())
        self.instances.append(shapes.reset_depth())
        self.instances.append(shapes.axes())

    def update(self, elapsed):
        super().update(elapsed)
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