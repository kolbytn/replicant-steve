from typing import List, Tuple
from javascript import AsyncTask
import random
import math

from utils.context_utils import BlockSide, RelativeLocation
from utils.skill_utils import Task, TaskSequence
from utils.mc_utils import block_side_to_vec, McVec3


def dig(bot, position: McVec3) -> bool:
    target_block = bot.blockAt(position.to_vec3())
    if target_block.name != "air":
        print("digging")
        bot.dig(target_block)
        return True
    return False


def place(bot, position: McVec3, block_type: str) -> bool:

    if bot.blockAt(position.add_to_x(1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_x(1).to_vec3())
        block_vec = McVec3(-1, 0, 0)
    elif bot.blockAt(position.add_to_x(-1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_x(-1).to_vec3())
        block_vec = McVec3(1, 0, 0)
    elif bot.blockAt(position.add_to_y(1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_y(1).to_vec3())
        block_vec = McVec3(0, -1, 0)
    elif bot.blockAt(position.add_to_y(-1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_y(-1).to_vec3())
        block_vec = McVec3(0, 1, 0)
    elif bot.blockAt(position.add_to_z(1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_z(1).to_vec3())
        block_vec = McVec3(0, 0, -1)
    elif bot.blockAt(position.add_to_z(-1).to_vec3()).name != "air":
        reference_block = bot.blockAt(position.add_to_z(-1).to_vec3())
        block_vec = McVec3(0, 0, 1)
    else:
        bot.chat("I can't place a block there!")
        return False

    block_to_place = None
    for item in bot.inventory.items():
        if item.name == block_type:
            block_to_place = item
    if block_to_place is None:
        bot.chat("I don't have that block!")
        return False
    
    if bot.blockAt(position.to_vec3()).name != "air":
        dig(bot, position)
    
    @AsyncTask(start=True)
    def equip(task):
        bot.equip(block_to_place, "hand")
    
    @AsyncTask(start=True)
    def place(task):
        bot.placeBlock(reference_block, block_vec.to_vec3())

    return True


class BuildCube(Task):
    def __init__(self, bot, sender, block_type: str, center_x: int, center_z: int, center_y: int, size_x: int, 
                 size_z: int, size_y: int):
        self.sender = sender
        self.block_type = block_type
        self.center_x = center_x
        self.center_z = center_z
        self.center_y = center_y
        self.size_x = size_x
        self.size_z = size_z
        self.size_y = size_y
        self.to_place = []
        super().__init__(bot)

    @property
    def task_id(self):
        return "build_{}_{}_{}_{}_cube_at_{}_{}_{}".format(
            self.block_type, self.size_x, self.size_z, self.size_y, self.center_x, self.center_z, self.center_y
        )
    
    def init_task(self) -> None:
        center_pos = McVec3(self.center_x, self.center_y, self.center_z)

        for y in range(self.size_y):
            for x in range(-math.floor(self.size_x / 2), math.ceil(self.size_x / 2)):
                for z in range(-math.floor(self.size_z / 2), math.ceil(self.size_z / 2)):
                    self.to_place.append(center_pos + McVec3(x, y, z))
        
        while len(self.to_place) > 0 and not place(self.bot, self.to_place.pop(0), self.block_type):
            pass

        if len(self.to_place) == 0:
            self.finish_task()

    def get_listeners(self) -> List[Tuple[str, callable]]:
        
        def handle_placed(this, old_block, new_block, *args):
            while len(self.to_place) > 0 and not place(self.bot, self.to_place.pop(0), self.block_type):
                pass
            if len(self.to_place) == 0:
                self.finish_task()

        return [("blockPlaced", handle_placed)]


class ConstructSkills:


    class PlaceBlockLooking(Task):
        """
        Place the specified block type on the block the player is looking at.
        Args:
            block_type (str): The type of block to place.
            block_side (BlockSide, optional): The side of the block to place the block on. Chooses random available side if None.
        """

        def __init__(self, bot, sender, block_type: str, block_side: BlockSide = None):
            self.sender = sender
            self.block_type = block_type
            self.block_side = block_side
            super().__init__(bot)

        @property
        def task_id(self):
            return "place_looking_{}".format(self.block_type) + \
                ("_{}".format(self.block_side.name) if self.block_side is not None else "")

        def init_task(self) -> None:
            player = self.bot.nearestEntity(lambda x: x.username == self.sender)
            block = self.bot.blockAtEntityCursor(player)

            available_sides = []
            for side in BlockSide:
                block_side_vec = block_side_to_vec(side, player.yaw)
                block_side_vec += McVec3.from_vec3(block.position)
                adjacent_block = self.bot.blockAt(block_side_vec.to_vec3())
                if adjacent_block.name == "air":
                    available_sides.append(side)

            if self.block_side is None:
                block_vec = block_side_to_vec(random.choice(available_sides), player.yaw)
            elif self.block_side in available_sides:
                block_vec = block_side_to_vec(self.block_side, player.yaw)
            else:
                self.bot.chat("I can't see that side of the block!")
                return
            
            if not place(self.bot, McVec3.from_vec3(block.position) + block_vec, self.block_type):
                self.finish_task()

        def get_listeners(self) -> List[Tuple[str, callable]]:
            
            def handle_placed(this, old_block, new_block, *args):
                if new_block.name == self.block_type:
                    print("Placed block!")
                    self.finish_task()

            return [("blockPlaced", handle_placed)]
        

    class BuildCube(TaskSequence):
        """
        Build a cube of the specified type and dimensions.
        Args:
            block_type (str): The type of block to build the cube out of.
            size_x (int): The side-to-side size of the cube.
            size_z (int): The front-to-back size of the cube.
            size_y (int): The height of the cube.
            location (RelativeLocation, optional): Where to center the cube. Default is RelativeLocation.BOT_STANDING.
        """

        def __init__(self, bot, sender, block_type: str, size_x: int, size_z: int, size_y: int, 
                     location: RelativeLocation = RelativeLocation.BOT_STANDING):
            self.bot = bot
            self.sender = sender
            self.block_type = block_type
            self.size_x = size_x
            self.size_z = size_z
            self.size_y = size_y
            self.location = location
            self.to_place = []
        
        def get_tasks(self) -> List[Task]:
            if self.location == RelativeLocation.BOT_STANDING:
                center = McVec3.from_vec3(self.bot.entity.position)
            elif self.location == RelativeLocation.BOT_LOOKING:
                center = McVec3.from_vec3(self.bot.blockAtEntityCursor(self.bot.entity).position)
            elif self.location == RelativeLocation.PLAYER_STANDING:
                center = McVec3.from_vec3(
                    self.bot.nearestEntity(lambda x: x.username == self.sender).position
                )
            else:
                center = McVec3.from_vec3(
                    self.bot.blockAtEntityCursor(
                        self.bot.nearestEntity(lambda x: x.username == self.sender)
                    ).position
                )

            return [Task(self.bot, self.sender, self.block_type, center.x, center.z, center.y + 1, self.size_x, 
                         self.size_z, self.size_y)]

    
    class BuildBox(TaskSequence):
        """
        Build a hollow box of the specified type and dimensions.
        Args:
            block_type (str): The type of block to build the box out of.
            size_x (int): The side-to-side size of the box.
            size_z (int): The front-to-back size of the box.
            size_y (int): The height of the box.
            location (RelativeLocation, optional): Where to center the box. Default is RelativeLocation.BOT_STANDING.
        """

        def __init__(self, bot, sender, block_type: str, size_x: int, size_z: int, size_y: int, 
                     location: RelativeLocation = RelativeLocation.BOT_STANDING):
            self.bot = bot
            self.sender = sender
            self.block_type = block_type
            self.size_x = size_x
            self.size_z = size_z
            self.size_y = size_y
            self.location = location
            self.to_place = []

        def get_tasks(self) -> List[Task]:
            if self.location == RelativeLocation.BOT_STANDING:
                center = McVec3.from_vec3(self.bot.entity.position)
            elif self.location == RelativeLocation.BOT_LOOKING:
                center = McVec3.from_vec3(self.bot.blockAtEntityCursor(self.bot.entity).position)
            elif self.location == RelativeLocation.PLAYER_STANDING:
                center = McVec3.from_vec3(
                    self.bot.nearestEntity(lambda x: x.username == self.sender).position
                )
            else:
                center = McVec3.from_vec3(
                    self.bot.blockAtEntityCursor(
                        self.bot.nearestEntity(lambda x: x.username == self.sender)
                    ).position
                )

            return [
                Task(self.bot, self.sender, self.block_type, center.x, center.z, center.y, 
                     self.size_x, self.size_z, 1),
                Task(self.bot, self.sender, self.block_type, center.x - math.floor(self.size_x / 2), 
                     center.z, center.y, 1, self.size_z, self.size_y),
                Task(self.bot, self.sender, self.block_type, center.x + math.ceil(self.size_x / 2), 
                     center.z, center.y, 1, self.size_z, self.size_y),
                Task(self.bot, self.sender, self.block_type, center.x, center.z - math.floor(self.size_x / 2), 
                     center.y, self.size_x, 1, self.size_y),
                Task(self.bot, self.sender, self.block_type, center.x, center.z + math.ceil(self.size_x / 2), 
                     center.y, self.size_x, 1, self.size_y),
                Task(self.bot, self.sender, self.block_type, center.x, center.z, center.y + self.size_y,
                     self.size_x, self.size_z, 1)
            ]
