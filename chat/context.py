from utils.mc_utils import get_all_block_ids

def perception_context(bot) -> str:
    return (nearby_blocks(bot) + inventory(bot) + personal_info(bot)).strip()

def personal_info(bot) -> str:
    e = bot.entity
    context = "## This is your personal information and no one else's ##"
    context += "YOUR_NAME = '{}'\n".format(bot.username)
    context += "YOUR_HEALTH = {}\n".format(bot.health)
    context += "YOUR_FOOD = {}\n".format(bot.food)
    context += "YOUR_LOCATION = {}\n".format(e.position)
    context += "YOUR_PITCH = {}\n".format(e.pitch)
    context += "YOUR_YAW = {}\n".format(e.yaw)
    context += "ON_GROUND = {}\n".format(e.onGround)
    return context

def code_context() -> str:
    context = ""
    with open("utils/context_utils.py", "r") as f:
        text = f.read()
        context += text.split("### START CONTEXT ###")[1].strip()
    return context + "\n\n"

def inventory(bot) -> str:
    context = "INVENTORY = {\n"
    for item in bot.inventory.items():
        context += "    '{}': {},\n".format(item.name, item.count)
    return context + "}\n\n"

def nearby_blocks(bot) -> str:
    context = "NEARBY_BLOCKS = [\n"
    positions = bot.findBlocks(dict(matching=get_all_block_ids(), maxDistance=16, count=4096))
    found = set()
    for vec in positions:
        block = bot.blockAt(vec)
        if block.name not in found:
            context += "    '{}',\n".format(block.name)
            found.add(block.name)
    return context + "]\n\n"

# def nearby_entities(bot):
#     Blocked, see: https://github.com/PrismarineJS/mineflayer/issues/3103
#     code_context = "NEARBY_ENTITIES = [\n"
#     for entity_name in get_all_entity_types():
#         print(entity_name)
#         nearest = bot.nearestEntity(lambda x: x.name == entity_name)
#         print(nearest)
#         if nearest is not None:
#             code_context += "    {},\n".format(entity_name)
#     return code_context + "]\n\n"