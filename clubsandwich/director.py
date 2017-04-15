import weakref
from .blt_loop import BearLibTerminalEventLoop


class Scene():
    def __init__(self):
        super().__init__()
        self.terminal_readers = []

    def add_terminal_reader(self, reader):
        if not getattr(reader, 'terminal_read'):
            raise ValueError("Invalid reader")
        self.terminal_readers.append(reader)

    def remove_terminal_reader(self, reader):
        self.terminal_readers.remove(reader)

    def enter(self):
        pass

    def exit(self):
        pass

    def terminal_update(self):
        return True

    def terminal_read(self, char):
        for reader in self.terminal_readers:
            reader.terminal_read(char)
        return True


class DirectorLoop(BearLibTerminalEventLoop):
    def __init__(self):
        super().__init__()
        self._scene = None

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, new_value):
        if self._scene:
            self._scene.exit()
            self._scene.director = lambda: None
        self._scene = new_value
        self._scene.director = weakref.ref(self)
        self._scene.enter()

    def get_initial_scene(self):
        raise NotImplementedError()

    def terminal_init(self):
        super().terminal_init()
        self.scene = self.get_initial_scene()

    def terminal_update(self):
        return self.scene.terminal_update()

    def terminal_read(self, char):
        return self.scene.terminal_read(char)