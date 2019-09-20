from math import pi, cos, sin

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Vec2

import commandmgr


class TheWorld(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.cmd_mgr = commandmgr.TheWorldCommandMgr(self)
        for cmd_str, cmd_fn in self.cmd_mgr.mapping.items():
            self.accept(cmd_str, cmd_fn)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        self.cube = self.loader.loadModel("cuby.gltf")
        self.cube.reparentTo(self.render)

        # Load and transform the panda actor.
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)

        self.panda_stater = Stater(self.pandaActor)
        self.panda_mover = Mover(self.pandaActor, self.panda_stater)

        self.taskMgr.add(self.panda_mover.execute, "moveTask")
        # Loop its animation.
        # self.pandaActor.loop("walk")

        # Create the four lerp intervals needed for the panda to
        # walk back and forth.
        # interval_duration = 2
        # pandaPosInterval1 = self.pandaActor.posInterval(interval_duration,
        #                                                 Point3(0, -10, 5),
        #                                                 startPos=Point3(0, 10, 0))
        # pandaPosInterval2 = self.pandaActor.posInterval(interval_duration,
        #                                                 Point3(0, 10, 0),
        #                                                 startPos=Point3(0, -10, 5))
        # pandaHprInterval1 = self.pandaActor.hprInterval(1,
        #                                                 Point3(90, 0, 0),
        #                                                 startHpr=Point3(0, 0, 0))
        # pandaHprInterval2 = self.pandaActor.hprInterval(1,
        #                                                 Point3(0, 0, 0),
        #                                                 startHpr=Point3(90, 0, 0))
        #
        # # Create and play the sequence that coordinates the intervals.
        # self.pandaPace = Sequence(pandaPosInterval1,
        #                           pandaHprInterval1,
        #                           pandaPosInterval2,
        #                           pandaHprInterval2,
        #                           name="pandaPace")
        # self.pandaPace.loop()

    def spinCameraTask(self, task):
        angle_degrees = task.time * 6.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angle_radians), -20.0 * cos(angle_radians), 3)
        self.camera.setHpr(angle_degrees, 0, 0)
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
        if not self.states["walk"]:
            self.obj.loop("walk")

        self.states["walk"].add(self.walk_map[dir])

    def stop_walk(self, dir=None):
        if not dir:
            self.states["walk"].clear()
        elif self.walk_map[dir] in self.states["walk"]:
            self.states["walk"].remove(self.walk_map[dir])

        if not self.states["walk"]:
            self.obj.stop()


VEC2_NULL = Vec2(0, 0)


class Mover:
    def __init__(self, obj, stater):
        self.obj = obj
        self.stater = stater
        self.cf_front = 500

    def straight_walk(self, dt):
        v_dir = sum(self.stater.states["walk"], VEC2_NULL)
        if v_dir.x:  # front/back
            self.obj.setY(self.obj, - v_dir.x * self.cf_front * dt)
        if v_dir.y:  # right/left
            self.obj.setX(self.obj, - v_dir.y * self.cf_front * dt)

    def execute(self, task):
        dt = globalClock.getDt()
        if self.stater.states["walk"]:
            self.straight_walk(dt)
        return Task.cont

app = TheWorld()
app.run()
