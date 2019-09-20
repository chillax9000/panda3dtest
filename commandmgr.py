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
        }
        self.the_world = the_world

    def mouse1(self):
        print("mouse1")

    def arrow_left(self):
        self.the_world.panda_stater.start_walk("left")

    def arrow_right(self):
        self.the_world.panda_stater.start_walk("right")

    def arrow_up(self):
        self.the_world.panda_stater.start_walk("front")

    def arrow_down(self):
        self.the_world.panda_stater.start_walk("back")

    def arrow_left_released(self):
        self.the_world.panda_stater.stop_walk("left")

    def arrow_right_released(self):
        self.the_world.panda_stater.stop_walk("right")

    def arrow_up_released(self):
        self.the_world.panda_stater.stop_walk("front")

    def arrow_down_released(self):
        self.the_world.panda_stater.stop_walk("back")
