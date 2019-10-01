import sys

from input.commandmgr import BaseCommandMgr


class TheWorldCommandMgr(BaseCommandMgr):
    def __init__(self, the_world):
        super().__init__()
        self.the_world = the_world
        self.actor_stater = None

    def set_actor_stater(self, actor_stater):
        self.actor_stater = actor_stater

    def mouse1(self):
        print("mouse1")

    def arrow_left(self):
        self.actor_stater.start_walk("left")

    def arrow_right(self):
        self.actor_stater.start_walk("right")

    def arrow_up(self):
        self.actor_stater.start_walk("front")

    def arrow_down(self):
        self.actor_stater.start_walk("back")

    def arrow_left_released(self):
        self.actor_stater.stop_walk("left")

    def arrow_right_released(self):
        self.actor_stater.stop_walk("right")

    def arrow_up_released(self):
        self.actor_stater.stop_walk("front")

    def arrow_down_released(self):
        self.actor_stater.stop_walk("back")

    def escape(self):
        sys.exit(0)

    def e(self):
        self.actor_stater.start_walk("front")

    def s(self):
        self.actor_stater.start_walk("left")

    def d(self):
        self.actor_stater.start_walk("back")

    def f(self):
        self.actor_stater.start_walk("right")

    def e_released(self):
        self.actor_stater.stop_walk("front")

    def s_released(self):
        self.actor_stater.stop_walk("left")

    def d_released(self):
        self.actor_stater.stop_walk("back")

    def f_released(self):
        self.actor_stater.stop_walk("right")

    def space(self):
        self.actor_stater.start_fly("up")

    def space_released(self):
        self.actor_stater.stop_fly("up")

    def a(self):
        self.actor_stater.start_fly("down")

    def a_released(self):
        self.actor_stater.stop_fly("down")
