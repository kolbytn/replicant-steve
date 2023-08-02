from utils.mc_utils import get_all_block_ids, get_all_item_ids, get_block_id, get_item_type

def perception_context(bot) -> str:
    return (nearby_blocks(bot) + personal_info(bot) + inventory(bot) + craftable_items(bot)).strip()

def personal_info(bot) -> str:
    e = bot.entity
    context = "## This is your personal information, the minecraft bot. This is NOT the player's information. ##"
    context += "BOT_NAME = '{}'\n".format(bot.username)
    context += "BOT_HEALTH = {}\n".format(bot.health)
    context += "BOT_FOOD = {}\n".format(bot.food)
    context += "BOT_LOCATION = x:{}, y:{}, z:{}\n".format(e.position.x, e.position.y, e.position.z)
    context += "BOT_PITCH = {}\n".format(e.pitch)
    context += "BOT_YAW = {}\n".format(e.yaw)
    context += "BOT_ON_GROUND = {}\n".format(e.onGround)
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
    context += "}\n"
    if bot.inventory.selectedItem is not None:
        context += "EQUIPPED_ITEM = '{}'\n".format(bot.inventory.selectedItem.name)
    else:
        context += "EQUIPPED_ITEM = None\n"
    print(context)
    return context + "\n\n"

def nearby_blocks(bot) -> str:
    context = "NEARBY_BLOCKS = [\n"
    positions = bot.findBlocks(dict(matching=get_all_block_ids(to_ignore='air'), maxDistance=16, count=4096))
    found = set()
    # TODO: Find a faster way to do this. It is extemely slow and bogs down chat speed.
    for vec in positions:
        block = bot.blockAt(vec)
        if block.name not in found:
            context += "    '{}',\n".format(block.name)
            found.add(block.name)
    return context + "]\n\n"

def craftable_items(bot) -> str:
    crafting_table = bot.findBlock({
        "matching": get_block_id("crafting_table"),
        "maxDistance": 100
    })
    context = "CRAFTABLE_ITEMS = [\n"
    for item_id in get_all_item_ids():
        # Need to iterate over Proxy
        for recipe in bot.recipesFor(item_id, None, 1, crafting_table):
            context += "    '{}',\n".format(get_item_type(recipe.result.id))
            break
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