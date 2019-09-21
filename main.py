from math import pi, sin, cos

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Vec2

import commandmgr
import util


class TheWorld(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.params = {
            "mouse_x": 0,
            "mouse_y": 0,
        }

        self.disableMouse()
        self.cmd_mgr = commandmgr.TheWorldCommandMgr(self)
        util.hidden_relative_mouse(self)
        for cmd_str, cmd_fn in self.cmd_mgr.mapping.items():
            self.accept(cmd_str, cmd_fn)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        self.setBackgroundColor(0.53, 0.80, 0.92, 1)

        # Reparent the model to render.
        self.scene.reparentTo(self.render)

        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        self.cube = self.loader.loadModel("cuby.gltf")
        self.cube.setColor(.1, .8, .4)
        self.cube.reparentTo(self.render)

        self.actor_stater = Stater(self.cube)
        self.cmd_mgr.set_actor_stater(self.actor_stater)
        self.actor_mover = Mover(self, self.cube, self.actor_stater)

        self.camera.wrtReparentTo(self.cube)
        self.camera.setPos(0, 40, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_params, "paramsTask")
        self.taskMgr.add(self.actor_mover.execute, "moveTask")
        self.taskMgr.add(self.log, "logTask")

    def update_params(self, task):
        if self.mouseWatcherNode.hasMouse():
            self.params["mouse_x"] = self.mouseWatcherNode.getMouseX()
            self.params["mouse_y"] = self.mouseWatcherNode.getMouseY()
            self.win.movePointer(0, self.win.getProperties().getXSize() // 2, self.win.getProperties().getYSize() // 2)
        return Task.cont

    def log(self, task):
        return Task.cont


class Stater:
    def __init__(self, obj):
        self.obj = obj
        self.states = {
            "walk": set(),
        }
        self.walk_map = {
            "front": Vec2(1, 0),
            "back": Vec2(-1, 0),
            "right": Vec2(0, 1),
            "left": Vec2(0, -1),
        }

    def start_walk(self, dir="front"):
        # if not self.states["walk"]:
        #     self.obj.loop("walk")

        self.states["walk"].add(self.walk_map[dir])

    def stop_walk(self, dir=None):
        if not dir:
            self.states["walk"].clear()
        elif self.walk_map[dir] in self.states["walk"]:
            self.states["walk"].remove(self.walk_map[dir])

        # if not self.states["walk"]:
        #     self.obj.stop()


class Mover:
    def __init__(self, world, obj, stater):
        self.world = world
        self.obj = obj
        self.stater = stater
        self.cf_front = 50
        self.cf_turn = 1000

    def straight_walk(self, dt):
        v_dir = sum(self.stater.states["walk"], util.VEC2_NULL)
        if v_dir.x:  # front/back
            self.obj.setY(self.obj, - v_dir.x * self.cf_front * dt)
        if v_dir.y:  # right/left
            self.obj.setX(self.obj, - v_dir.y * self.cf_front * dt)

    def turn(self, dt):
        if self.world.mouseWatcherNode.hasMouse():
            if self.world.params["mouse_x"]:
                self.obj.setH(self.obj.getH() - self.cf_turn * dt * self.world.params["mouse_x"])

    def execute(self, task):
        dt = globalClock.getDt()
        if self.stater.states["walk"]:
            self.straight_walk(dt)
        self.turn(dt)
        return Task.cont


app = TheWorld()
app.run()
