from utils.chat_utils import send_chat
from utils.skill_utils import CURRENT_BEHAVIOR
from chat.skill import execute_skill
from chat.conversation import execute_conversation


def parse_chat(bot, sender, message: str) -> None:
    
    system_message = "You are a Minecraft bot. Determine whether the player wants to chat or is giving you a command or is telling you to stop."
    turns = [
        "Player message: Hello! How are you today?",
        "chat",
        "Player message: don't do that anymore",
        "stop",
        "Player message: How do you make a stone pickaxe?",
        "chat",
        "Player message: collect 10 stone",
        "command",
        "Player message: stop following me",
        "stop",
        "Player message: I want to find diamond ore",
        "chat",
        "Player message: Hi. Will you follow me please?",
        "command"
    ]

    print("Predicting type of message:", message)
    response = send_chat(turns + ["Player message: {}".format(message)], system_message=system_message)

    print("Predicted type:", response)
    if "command" in response:
        if CURRENT_BEHAVIOR is not None:
            bot.chat("I'm busy right now. You can ask me to stop what I'm doing first if you want me to change tasks.")
        else:
            execute_skill(bot, sender, message)
    elif "chat" in response:
        execute_conversation(bot, sender, message)
    elif "stop" in response:
        bot.chat("Okay, I'll stop.")
        CURRENT_BEHAVIOR.stop()
        CURRENT_BEHAVIOR = None
    else:
        bot.chat("I don't understand what you mean by that.")
    print()
