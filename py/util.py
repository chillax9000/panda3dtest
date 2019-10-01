from panda3d.core import WindowProperties, Vec2, Vec3

VEC2_NULL = Vec2(0, 0)
VEC3_NULL = Vec3(0, 0, 0)


def hidden_relative_mouse(base):
    props = WindowProperties()
    props.setCursorHidden(True)
    props.setMouseMode(WindowProperties.M_relative)
    base.win.requestProperties(props)
