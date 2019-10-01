import itertools
import math

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Vec2, Vec3, AmbientLight, PointLight, Material, CollisionNode, CollisionRay, \
    CollisionHandlerFloor, CollisionTraverser, CollisionHandlerQueue, CollideMask, CollisionPlane, Plane, Point3, \
    CollisionSphere, CollisionHandlerPusher, CollisionBox

import commandmgr
import util

initial_actor_pos = Point3(0, 0, 10)
initial_actor_hpr = Point3(0, 0, 0)
cube_color = (1, 1, 1, 1)
cam_dist = 20
DEATH_DEPTH = -25
GRID_SIZE = 1
ground_cube_size = Vec3(10, 10, .4)


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

        # environment
        self.setBackgroundColor(.0, .0, .0, 1)

        # # ground
        self.ground_cube = self.loader.loadModel("cuby.gltf")
        self.ground_cube.setColor(1, 1, 1, 1)
        self.ground_cube.setScale(ground_cube_size)

        self.ground = self.render.attachNewNode("ground")

        grid_max = GRID_SIZE - 1
        dist = 8
        grid_coordinates = itertools.product(range(GRID_SIZE), range(GRID_SIZE))

        def normalize(x_y):
            x, y = x_y
            return (x - grid_max / 2) * dist, (y - grid_max / 2) * dist

        for x, y in map(normalize, grid_coordinates):
            placeholder = self.ground.attachNewNode("placeholder")
            placeholder.setPos(x, y, -ground_cube_size.z)
            self.ground_cube.instanceTo(placeholder)

            # collision ground
            coll_node = CollisionNode(f"ground_{x}_{y}")
            coll_node.setFromCollideMask(CollideMask.allOff())
            coll_node.setIntoCollideMask(CollideMask.bit(0))
            nodepath = placeholder.attachNewNode(coll_node)
            nodepath.node().addSolid(
                CollisionBox(Point3(0, 0, 0), ground_cube_size.x, ground_cube_size.y, ground_cube_size.z))

        # lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((.2, .2, .2, 1))
        alight = self.render.attachNewNode(ambient_light)
        self.render.setLight(alight)

        # actor
        self.actor_obj = Actor(self, self.render, "cuby.gltf")
        self.actor = self.actor_obj.node
        self.actor.setColor(cube_color)

        # # collision actor
        self.cTrav = CollisionTraverser('traverser')
        # self.cTrav.showCollisions(self.actor)

        self.actor_coll = CollisionNode('actor')
        self.actor_coll.addSolid(CollisionBox(Point3(0, 0, 0), 1, 1, 1))
        self.actor_coll.setFromCollideMask(CollideMask.bit(0))
        self.actor_coll.setIntoCollideMask(CollideMask.allOff())
        self.actor_coll_np = self.actor.attachNewNode(self.actor_coll)

        # self.pusher = CollisionHandlerPusher()
        #
        # self.pusher.addCollider(self.actor_coll_np, self.actor)
        # self.cTrav.addCollider(self.actor_coll_np, self.pusher)

        self.queue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.actor_coll_np, self.queue)

        # lighting
        self.centerlight_np = self.render.attachNewNode("basiclightcenter")
        self.centerlight_np.hprInterval(8, (360, 0, 0)).loop()

        d, h = 10, 1
        self.basic_point_light((-d, 0, h), (.0, .0, .7, 1), "left_light")
        self.basic_point_light((d, 0, h), (.0, .7, 0, 1), "right_light")
        self.basic_point_light((0, d, h), (.7, .0, .0, 1), "front_light")
        self.basic_point_light((0, -d, h), (1, 1, 1, 1), "back_light")

        self.actor_stater = Stater(self.actor)
        self.cmd_mgr.set_actor_stater(self.actor_stater)
        self.actor_mover = Mover(self, self.actor_obj, self.actor_stater)

        self.camera.wrtReparentTo(self.actor)
        self.camera.setPos(Vec3(0, 4, 1).normalized() * cam_dist)
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
            "front": Vec3(0, -1, 0),
            "back": Vec3(0, 1, 0),
            "right": Vec3(-1, 0, 0),
            "left": Vec3(1, 0, 0),
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
    def __init__(self, world, actor_obj, stater):
        self.world = world
        self.actor_obj = actor_obj
        self.actor = self.actor_obj.node
        self.stater = stater
        self.cf_front = 20
        self.cf_turn = 1000

    def straight_walk(self, dt):
        v_dir = sum(self.stater.states["walk"], util.VEC3_NULL)
        if v_dir.xy:
            self.actor_obj.v = Vec3(bound_velocity(self.actor_obj.v.xy + v_dir.xy, Actor.WALK_VELOCITY_MAX),
                                    self.actor_obj.v.z)

    def turn(self, dt):
        if self.world.mouseWatcherNode.hasMouse():
            if self.world.params["mouse_x"]:
                self.actor.setH(self.actor, - self.cf_turn * dt * self.world.params["mouse_x"])
            if self.world.params["mouse_y"]:
                new_z = self.world.camera.getZ() - self.cf_turn * dt * self.world.params["mouse_y"]
                bound = 20
                new_z = bound if new_z > bound else new_z
                new_z = -bound if new_z < -bound else new_z
                self.world.camera.setZ(new_z)
                self.world.camera.lookAt(0, 0, 0)

    def jump(self, dt):
        self.actor_obj.apply_force(self.actor_obj.VEC_JUMP_FORCE)
        self.stater.end_jump()

    def fly(self, dt):
        dir = sum(self.stater.states["fly"])
        if dir:
            self.actor.setZ(self.actor.getZ() + dir * 5 * dt)

    def die(self):
        self.actor.setPos(initial_actor_pos)
        self.actor_obj.v = util.VEC3_NULL
        self.actor_obj.forces = []
        self.actor_obj.a = util.VEC3_NULL
        self.actor_obj.last_known_pos = initial_actor_pos

    def execute(self, task):
        dt = globalClock.getDt()
        if self.actor.getZ() < DEATH_DEPTH:
            self.die()
        else:
            grounded = False
            for entry in self.world.queue.getEntries():
                if entry.getSurfaceNormal(self.world.ground).z > 0:
                    grounded = True
                    self.actor.setZ(1)
                    self.actor_obj.v.z = 0
                    break

            if self.stater.states["walk"]:
                self.straight_walk(dt)
            if self.stater.states["jump"]:
                self.jump(dt)
            if self.stater.states["fly"]:
                self.fly(dt)
            self.turn(dt)
            if grounded:
                ground_friction = 0 if self.stater.states["walk"] else 10
                self.actor_obj.apply_force(-Vec3(self.actor_obj.v.xy, 0) * ground_friction)
            else:
                self.actor_obj.apply_gravity()

            self.actor_obj.move(dt)
        return Task.cont


def bound_velocity(v, max):
    return v.normalized() * max if v.lengthSquared() > max * max else v


class Actor:
    VEC_GRAVITY_FORCE = Vec3(0, 0, -10)
    VEC_JUMP_FORCE = Vec3(0, 0, 400)
    WALK_VELOCITY_MAX = 10
    VELOCITY_MAX = 50
    VELOCITY_MAX_SQUARED = VELOCITY_MAX * VELOCITY_MAX

    def __init__(self, world, parent, model_path=None, init_pos=initial_actor_pos, init_hpr=initial_actor_hpr, mass=1):
        self.world = world
        self.node = (self.world.loader.loadModel(model_path) if model_path
                     else self.world.render.AttachNewNode(model_path))
        self.node.reparentTo(parent)

        self.node.setPos(init_pos)
        self.node.setHpr(init_hpr)

        self.v = util.VEC3_NULL
        self.a = util.VEC3_NULL
        self.m = mass

        self.last_known_pos = init_pos

        self.forces = []

    def apply_force(self, vec_force):
        self.forces.append(vec_force)

    def apply_gravity(self):
        self.apply_force(self.VEC_GRAVITY_FORCE)

    def compute_accel(self):
        self.a = sum(self.forces, util.VEC3_NULL) / self.m
        self.forces = []

    def compute_speed(self, dt):
        self.v = bound_velocity(self.v + self.a * dt, self.VELOCITY_MAX)
        if self.v.lengthSquared() < 0.01:
            self.v = util.VEC3_NULL

    def compute_position(self, dt):
        current_pos = self.node.getPos()
        self.last_known_pos = current_pos
        self.node.setPos(self.node, self.v * dt)

    def move(self, dt):
        self.compute_accel()
        self.compute_speed(dt)
        self.compute_position(dt)
        print({"accel": self.a, "velocity": self.v})


app = TheWorld()
app.run()
