from typing import List
from javascript import require
import math
minecraft_data = require('minecraft-data')
Vec3 = require("vec3").Vec3

from utils.context_utils import BlockSide


MC_VERSION = "1.19.3"
MC_DATA = minecraft_data(MC_VERSION)


class McVec3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_vec3(vec3: Vec3) -> "McVec3":
        return McVec3(vec3.x, vec3.y, vec3.z)

    def to_vec3(self) -> Vec3:
        return Vec3(self.x, self.y, self.z)
    
    def add_to_x(self, x: int) -> "McVec3":
        return McVec3(self.x + x, self.y, self.z)
    
    def add_to_y(self, y: int) -> "McVec3":
        return McVec3(self.x, self.y + y, self.z)
    
    def add_to_z(self, z: int) -> "McVec3":
        return McVec3(self.x, self.y, self.z + z)

    def __eq__(self, other: Vec3) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __add__(self, other: Vec3) -> Vec3:
        return McVec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: Vec3) -> Vec3:
        return McVec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other: float) -> Vec3:
        return McVec3(self.x * other, self.y * other, self.z * other)
    

def get_all_block_names() -> List[str]:
    return [MC_DATA.blocks[x].name for x in MC_DATA.blocks]
    

def get_all_block_ids(to_ignore : List[str] = []) -> List[str]:
    return [int(x) for x in MC_DATA.blocks if MC_DATA.blocks[x].name not in to_ignore]


def get_all_entity_types() -> List[str]:
    return [MC_DATA.entities[x].name for x in MC_DATA.entities]


def set_global_version(version: str) -> None:
    global MC_VERSION
    global MC_DATA
    MC_VERSION = version
    MC_DATA = minecraft_data(MC_VERSION)


def get_block_id(block_type: str) -> int:
    return MC_DATA.blocksByName[block_type]


def get_item_id(item_type: str) -> int:
    return MC_DATA.itemsByName[item_type]


def block_side_to_vec(block_side: BlockSide, yaw: float) -> Vec3:
    if block_side == BlockSide.BOTTOM:
        return McVec3(0, -1, 0)
    if block_side == BlockSide.TOP:
        return McVec3(0, 1, 0)
        
    if yaw >= math.radians(315) or yaw < math.radians(45):
        if block_side == BlockSide.LEFT:
            return McVec3(-1, 0, 0)
        if block_side == BlockSide.RIGHT:
            return McVec3(1, 0, 0)
        if block_side == BlockSide.FRONT:
            return McVec3(0, 0, 1)
        if block_side == BlockSide.BACK:
            return McVec3(0, 0, -1)
    elif yaw >= math.radians(45) and yaw < math.radians(135):
        if block_side == BlockSide.LEFT:
            return McVec3(0, 0, 1)
        if block_side == BlockSide.RIGHT:
            return McVec3(0, 0, -1)
        if block_side == BlockSide.FRONT:
            return McVec3(1, 0, 0)
        if block_side == BlockSide.BACK:
            return McVec3(-1, 0, 0)
    elif yaw >= math.radians(135) and yaw < math.radians(225):
        if block_side == BlockSide.LEFT:
            return McVec3(1, 0, 0)
        if block_side == BlockSide.RIGHT:
            return McVec3(-1, 0, 0)
        if block_side == BlockSide.FRONT:
            return McVec3(0, 0, -1)
        if block_side == BlockSide.BACK:
            return McVec3(0, 0, 1)
    elif yaw >= math.radians(225) and yaw < math.radians(315):
        if block_side == BlockSide.LEFT:
            return McVec3(0, 0, -1)
        if block_side == BlockSide.RIGHT:
            return McVec3(0, 0, 1)
        if block_side == BlockSide.FRONT:
            return McVec3(-1, 0, 0)
        if block_side == BlockSide.BACK:
            return McVec3(1, 0, 0)
