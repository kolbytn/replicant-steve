from typing import List, Tuple, Union


CURRENT_BEHAVIOR = None


# TODO have behavior timeout
class BehaviorNode:

    def __init__(self, bot=None, child: Union["BehaviorNode", callable] = None):
        assert bot is not None
        self.bot = bot
        self._get_child = child if callable(child) else lambda: child

    def start(self):
        for name, fun in self._get_transitions():
            self.bot.on(name, fun)
        self._init_behavior()

    def stop(self):
        for name, fun in self._get_transitions():
            self.bot.removeListener(name, fun)

    def finish(self):
        self.stop()
        child = self._get_child()
        if child is not None:
            child.start()

    def _init_behavior(self):
        raise NotImplementedError()
    
    def _get_transitions(self) -> List[Tuple[str, callable]]:
        raise NotImplementedError()
