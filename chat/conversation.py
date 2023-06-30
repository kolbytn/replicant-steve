from utils.chat_utils import send_chat


def execute_conversation(bot, sender, message: str) -> None:
    
    system_message = "You are a helpful Minecraft bot. Chat with the players and give them information if they ask for it."
    response = send_chat([message], system_message=system_message)
    bot.chat(response)
