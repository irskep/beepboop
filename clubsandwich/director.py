from .blt_loop import BearLibTerminalEventLoop


class Scene():
    def enter(self):
        pass

    def exit(self):
        pass

    def terminal_update(self):
        return True

    def terminal_read(self, char):
        return True


class DirectorLoop(BearLibTerminalEventLoop):
    def __init__(self):
        super().__init__()
        self.scene = None

    def get_initial_scene(self):
        raise NotImplementedError()

    def terminal_init(self):
        super().terminal_init()
        self.scene = self.get_initial_scene()

    def terminal_update(self):
        return self.scene.terminal_update()

    def terminal_read(self, char):
        return self.scene.terminal_read(char)