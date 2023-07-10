from utils.chat_utils import send_chat
from utils.mc_utils import get_all_block_ids
from utils.context_utils import Distance, BlockSide, RelativeLocation
import utils.skill_utils as behavior
from skills.item import ItemSkills
from skills.navigate import NavigateSkills
from skills.construct import ConstructSkills


def build_system_message(bot) -> str:
    
    code_context = ""
    with open("utils/context_utils.py", "r") as f:
        text = f.read()
        code_context += text.split("### START CONTEXT ###")[1].strip()
    code_context += "\n\n"

    code_context += "NEARBY_BLOCKS = [\n"
    positions = bot.findBlocks(dict(matching=get_all_block_ids(), maxDistance=16, count=4096))
    found = set()
    for vec in positions:
        block = bot.blockAt(vec)
        if block.name not in found:
            code_context += "    '{}',\n".format(block.name)
            found.add(block.name)
    code_context += "]\n\n"

    # Blocked, see: https://github.com/PrismarineJS/mineflayer/issues/3103
    # code_context += "NEARBY_ENTITIES = [\n"
    # for entity_name in get_all_entity_types():
    #     print(entity_name)
    #     nearest = bot.nearestEntity(lambda x: x.name == entity_name)
    #     print(nearest)
    #     if nearest is not None:
    #         code_context += "    {},\n".format(entity_name)
    # code_context += "]\n\n"

    code_context += "INVENTORY = {\n"
    for item in bot.inventory.items():
        code_context += "    '{}': {},\n".format(item.name, item.count)
    code_context += "}\n\n"
    
    def get_docstrings(cls):
        res = ""
        for attr in dir(cls):
            if not attr.startswith('__'):
                res += attr + ": "
                res += getattr(cls, attr).__doc__.strip() + "\n\n"
        return res
    
    code_context += get_docstrings(ItemSkills)
    code_context += get_docstrings(NavigateSkills)
    code_context += get_docstrings(ConstructSkills)

    return "Use the below code to translate user commands to code:\n\n" + code_context.strip()


def build_examples() -> str:
    return [
        "collect 10 stone",
        "CollectQuantity('stone', 10)",
        "come here please",
        "ComeHere()"
    ]


def execute_skill(bot, sender, message: str) -> None:
    
    response = send_chat(build_examples() + [message], system_message=build_system_message(bot))
    print("Translated \"{}\" to `{}`".format(message, response))

    skill_end = response.find("(")
    skill_name = response[:skill_end]
    skill_args = []
    skill_kwargs = {}

    def get_arg(arg):
        if arg.isnumeric():
            return int(arg)
        elif arg.startswith("Distance."):
            return Distance[arg.split(".")[1]]
        elif arg.startswith("BlockSide."):
            return BlockSide[arg.split(".")[1]]
        elif arg.startswith("RelativeLocation."):
            return RelativeLocation[arg.split(".")[1]]
        elif arg == "None":
            return None
        else:
            return arg.strip("'").strip("\"")

    for arg in response[skill_end + 1:-1].split(", "):
        if arg == "":
            continue
        elif "=" in arg:
            key, value = arg.split("=")
            skill_kwargs[key] = get_arg(value)
        else:
            skill_args.append(get_arg(arg))

    if hasattr(ItemSkills, skill_name):
        behavior.CURRENT_BEHAVIOR = getattr(ItemSkills, skill_name)(*skill_args, bot=bot, child=None, **skill_kwargs)
        behavior.CURRENT_BEHAVIOR.start()
    elif hasattr(NavigateSkills, skill_name):
        behavior.CURRENT_BEHAVIOR = getattr(NavigateSkills, skill_name)(sender, *skill_args, bot=bot, child=None, **skill_kwargs)
        behavior.CURRENT_BEHAVIOR.start()
    elif hasattr(ConstructSkills, skill_name):
        behavior.CURRENT_BEHAVIOR = getattr(ConstructSkills, skill_name)(sender, *skill_args, bot=bot, child=None, **skill_kwargs)
        behavior.CURRENT_BEHAVIOR.start()
    else:
        bot.chat("I don't know how to " + message)
        print("Failed to call", response)
