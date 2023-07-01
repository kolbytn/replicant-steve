from typing import List, Tuple
from javascript import require
pathfinder = require('mineflayer-pathfinder')

from utils.skill_utils import BehaviorNode


# All names and doc strings for all members of this class will be added to the context.
class NavigateSkills:


    class ComeHere(BehaviorNode):
        """
        Tells the bot to come to the player's location.
        """

        def __init__(self, sender, **kwargs):
            self.sender = sender
            super().__init__(**kwargs)

        def _init_behavior(self) -> None:
            player = self.bot.players[self.sender]
            target = player.entity
            if not target:
                self.bot.chat("I don't see you!")
                return

            pos = target.position
            self.bot.pathfinder.setMovements(pathfinder.Movements(self.bot))
            self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))

        def _get_transitions(self) -> List[Tuple[str, callable]]:

            def handle_goal_reached(this, *args):
                print("Reached goal location")
                self.finish()

            return [("goal_reached", handle_goal_reached)]


    class FollowPlayer(BehaviorNode):
        """
        Tells the bot to follow the player until told to stop.
        """

        def __init__(self, sender, **kwargs):
            self.sender = sender
            self.update_freq = 10
            self.last_update = 0
            super().__init__(**kwargs)

        def _init_behavior(self) -> None:
            pass

        def _get_transitions(self) -> List[Tuple[str, callable]]:

            def follow(this, *args):
                self.last_update += 1
                if self.last_update >= self.update_freq:
                    self.last_update = 0
                    player = self.bot.players[self.sender]
                    target = player.entity
                    if not target:
                        self.bot.chat("I don't see you!")
                        self.finish_task()
                        return

                    pos = target.position
                    self.bot.pathfinder.setMovements(pathfinder.Movements(self.bot))
                    self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 5))

            return [("physicsTick", follow)]


    class MoveLooking(BehaviorNode):
        """
        Tells the bot to move to the position the player is looking at.
        """

        def __init__(self, sender, **kwargs):
            self.sender = sender
            super().__init__(**kwargs)

        def _init_behavior(self) -> None:
            entity = self.bot.nearestEntity(lambda x: x.username == self.sender)

            # x, y, z = entity.position.x, entity.position.y + 1.6, entity.position.z
            # while bot.blockAt(init_vec(x, y, z)).name == "air":
            #     x -= math.cos(entity.pitch) * math.sin(entity.yaw)
            #     y += math.sin(entity.pitch)
            #     z -= math.cos(entity.pitch) * math.cos(entity.yaw)

            block = self.bot.blockAtEntityCursor(entity)

            self.bot.pathfinder.setMovements(pathfinder.Movements(self.bot))
            self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(block.x, block.x, block.x, 1))

        def _get_transitions(self) -> List[Tuple[str, callable]]:

            def handle_goal_reached(this, *args):
                print("Reached goal location")
                self.finish()

            return [("goal_reached", handle_goal_reached)]
