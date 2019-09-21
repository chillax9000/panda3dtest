from panda3d.core import WindowProperties


def hidden_relative_mouse(base):
    props = WindowProperties()
    props.setCursorHidden(True)
    props.setMouseMode(WindowProperties.M_relative)
    base.win.requestProperties(props)
