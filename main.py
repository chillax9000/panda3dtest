from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Vec2, Vec3, AmbientLight, DirectionalLight, PointLight, NodePath, PandaNode, Material

import commandmgr
import util

initial_actor_pos = Vec3(0, 0, 0)
cube_color = (1, 1, 1, 1)


class TheWorld(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.params = {
            "mouse_x": 0,
            "mouse_y": 0,
            "actor_pos": initial_actor_pos,
        }

        self.disableMouse()
        self.cmd_mgr = commandmgr.TheWorldCommandMgr(self)
        util.hidden_relative_mouse(self)
        for cmd_str, cmd_fn in self.cmd_mgr.mapping.items():
            self.accept(cmd_str, cmd_fn)

        # environment
        self.setBackgroundColor(.0, .0, .0, 1)
        self.ground = self.loader.loadModel("cuby.gltf")
        self.ground.setColor(1, 1, 1, 1)
        self.ground.reparentTo(self.render)

        self.ground.setScale(16, 16, 1)
        self.ground.setZ(-2)

        # lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((.2, .2, .2, 1))
        alight = self.render.attachNewNode(ambient_light)
        self.render.setLight(alight)

        # actor
        self.actor = self.loader.loadModel("cuby.gltf")
        self.actor.setColor(cube_color)
        self.actor.reparentTo(self.render)
        self.actor.setPos(initial_actor_pos)

        self.centerlight_np = self.actor.attachNewNode("basiclightcenter")
        self.centerlight_np.hprInterval(4, (360, 0, 0)).loop()

        d, h = 2, 0
        self.basic_point_light((-d, 0, h), (.0, .0, .7, 1), "left_light")
        self.basic_point_light((d, 0, h), (.0, .7, 0, 1), "right_light")
        self.basic_point_light((0, d, h), (.7, .0, .0, 1), "front_light")
        self.basic_point_light((0, -d, h), (1, 1, 1, 1), "back_light")

        self.actor_stater = Stater(self.actor)
        self.cmd_mgr.set_actor_stater(self.actor_stater)
        self.actor_mover = Mover(self, self.actor, self.actor_stater)

        self.camera.wrtReparentTo(self.actor)
        self.camera.setPos(0, 40, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_params, "paramsTask")
        self.taskMgr.add(self.actor_mover.execute, "moveTask")
        self.taskMgr.add(self.log, "logTask")

        self.render.setShaderAuto()

    def update_params(self, task):
        if self.mouseWatcherNode.hasMouse():
            self.params["mouse_x"] = self.mouseWatcherNode.getMouseX()
            self.params["mouse_y"] = self.mouseWatcherNode.getMouseY()
            self.win.movePointer(0, self.win.getProperties().getXSize() // 2, self.win.getProperties().getYSize() // 2)
        self.params["actor_pos"] = self.actor.getPos()
        return Task.cont

    def log(self, task):
        return Task.cont

    def basic_point_light(self, position, color, name, attenuation=(1, 0, 0.02)):
        light = PointLight(name)
        light.setColor(color)
        light.setAttenuation(attenuation)
        # light.setShadowCaster(True)
        # light.getLens().setNearFar(5, 20)
        plight = self.centerlight_np.attachNewNode(light)
        plight.setPos(position)
        self.render.setLight(plight)

        light_cube = self.loader.loadModel("cuby.gltf")
        light_cube.reparentTo(plight)
        light_cube.setScale(0.25)
        material = Material()
        material.setEmission(color)
        light_cube.setMaterial(material)


class Stater:
    def __init__(self, obj):
        self.obj = obj
        self.states = {
            "walk": set(),
            "jump": False,
            "fly": set(),
        }
        self.walk_map = {
            "front": Vec2(1, 0),
            "back": Vec2(-1, 0),
            "right": Vec2(0, 1),
            "left": Vec2(0, -1),
        }
        self.fly_map = {
            "up": 1,
            "down": -1
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

    def start_fly(self, dir="up"):
        self.states["fly"].add(self.fly_map[dir])

    def stop_fly(self, dir=None):
        if not dir:
            self.states["fly"].clear()
        elif self.fly_map[dir] in self.states["fly"]:
            self.states["fly"].remove(self.fly_map[dir])

    def do_jump(self):
        self.states["jump"] = True

    def end_jump(self):
        self.states["jump"] = False


class Mover:
    def __init__(self, world, actor, stater):
        self.world = world
        self.actor = actor
        self.stater = stater
        self.cf_front = 20
        self.cf_turn = 1000

    def straight_walk(self, dt):
        v_dir = sum(self.stater.states["walk"], util.VEC2_NULL)
        if v_dir.x:  # front/back
            self.actor.setY(self.actor, - v_dir.x * self.cf_front * dt)
        if v_dir.y:  # right/left
            self.actor.setX(self.actor, - v_dir.y * self.cf_front * dt)

    def turn(self, dt):
        if self.world.mouseWatcherNode.hasMouse():
            if self.world.params["mouse_x"]:
                self.actor.setH(self.actor.getH() - self.cf_turn * dt * self.world.params["mouse_x"])

    def jump(self, dt):
        self.actor.setZ(self.actor.getZ() + 500 * dt)

    def fly(self, dt):
        dir = sum(self.stater.states["fly"])
        if dir:
            self.actor.setZ(self.actor.getZ() + dir * 5 * dt)

    def gravity(self, dt):
        actor_z = self.actor.getZ()
        if actor_z > 0:
            self.actor.setZ(actor_z - 10 * dt)
            if self.actor.getZ() < 0:
                self.actor.setZ(0)

    def execute(self, task):
        dt = globalClock.getDt()
        if self.stater.states["walk"]:
            self.straight_walk(dt)
        if self.stater.states["jump"]:
            self.jump(dt)
            self.stater.end_jump()
        if self.stater.states["fly"]:
            self.fly(dt)
        self.turn(dt)
        # self.gravity(dt)
        return Task.cont


app = TheWorld()
app.run()
