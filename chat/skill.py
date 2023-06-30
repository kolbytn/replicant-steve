from utils.chat_utils import send_chat
from utils.context_utils import Distance, BlockSide, RelativeLocation
from utils.skill_utils import TaskQueue
from skills.item import ItemSkills
from skills.navigate import NavigateSkills
from skills.construct import ConstructSkills


def build_code_context() -> str:
    code_context = ""
    with open("utils/context_utils.py", "r") as f:
        text = f.read()
        code_context += text.split("### START CONTEXT ###")[1].strip()
    code_context += "\n\n"

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

    return code_context.strip()


def build_examples() -> str:
    return [
        "collect 10 stone",
        "CollectQuantity('stone', 10)",
        "come here please",
        "ComeHere()"
    ]


def build_system_message() -> str:
    return "Use the below code to translate user commands to code:\n\n" + build_code_context()


def execute_skill(bot, sender, message: str) -> None:
    
    response = send_chat(build_examples() + [message], system_message=build_system_message())
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
        TaskQueue().queue_task(getattr(ItemSkills, skill_name)(bot, *skill_args, **skill_kwargs))
    elif hasattr(NavigateSkills, skill_name):
        TaskQueue().queue_task(getattr(NavigateSkills, skill_name)(bot, sender, *skill_args, **skill_kwargs))
    elif hasattr(ConstructSkills, skill_name):
        TaskQueue().queue_task(getattr(ConstructSkills, skill_name)(bot, sender, *skill_args, **skill_kwargs))
    else:
        bot.chat("I don't know how to " + message)
        print("Failed to call", response)
