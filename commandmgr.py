import sys


class TheWorldCommandMgr:
    def __init__(self, the_world):
        self.mapping = {
            "mouse1": self.mouse1,
            "arrow_up": self.arrow_up,
            "arrow_down": self.arrow_down,
            "arrow_left": self.arrow_left,
            "arrow_right": self.arrow_right,
            "arrow_up-up": self.arrow_up_released,
            "arrow_down-up": self.arrow_down_released,
            "arrow_left-up": self.arrow_left_released,
            "arrow_right-up": self.arrow_right_released,
            "escape": self.escape,
            "e": self.e,
            "s": self.s,
            "d": self.d,
            "f": self.f,
            "e-up": self.e_released,
            "s-up": self.s_released,
            "d-up": self.d_released,
            "f-up": self.f_released,
            "space": self.space,
            "space-up": self.space_released,
            "a": self.a,
            "a-up": self.a_released,
        }
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
