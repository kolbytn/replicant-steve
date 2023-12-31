from javascript import require, On
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
collectblock = require('mineflayer-collectblock')

from chat.parse import parse_chat


BOT_USERNAME = 'python'


if __name__ == "__main__":
    bot = mineflayer.createBot({
        'host': '127.0.0.1',
        'port': 55916,
        'username': BOT_USERNAME
    })

    bot.loadPlugin(pathfinder.pathfinder)
    bot.loadPlugin(collectblock.plugin)
    print("Started mineflayer")

    @On(bot, 'spawn')
    def handle_spawn(*args):
        print("I spawned 👋")

        @On(bot, 'whisper')
        def handle_chat(this, sender, message, *args):
            print("Got message", sender, message)

            if sender and (sender != BOT_USERNAME):
                parse_chat(bot, sender, message)

    @On(bot, "end")
    def handle_end(*args):
        print("Bot ended!", args)
