from typing import List, Tuple, Union, Dict, Any


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
        global CURRENT_BEHAVIOR
        CURRENT_BEHAVIOR = None
        if child is not None:
            CURRENT_BEHAVIOR = child
            CURRENT_BEHAVIOR.start()

    def _init_behavior(self):
        self.finish()
    
    def _get_transitions(self) -> List[Tuple[str, callable]]:
        return []
    

def construct_sequence(behaviors: List[Dict[str, Any]], bot=None):
    behavior = None
    for node in reversed(behaviors):
        cls_ = node.pop("clss")
        bot_ = node.pop("bot", bot)
        args = node.pop("args", [])
        behavior = cls_(
            *args,
            bot=bot_,
            child=behavior,
            **node
        )
    return behavior
