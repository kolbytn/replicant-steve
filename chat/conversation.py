from utils.chat_utils import send_chat
import chat.context as ctx

# TODO: include skill requests/executions in chat history
chat_history = []

def execute_conversation(bot, sender, message: str) -> None:
    
    system_message = "You are a helpful Minecraft bot that is currently playing in a world that you can see and interact with. \
    Chat with the players and give them information if they ask for it. Avoid saying 'as a minecraft bot...'. \
    Use this context to inform your conversation:\n"
    system_message += ctx.perception_context(bot)
    chat_history.append(message)
    response = send_chat(chat_history, system_message=system_message)
    bot.chat(response)
    chat_history.append(response)
