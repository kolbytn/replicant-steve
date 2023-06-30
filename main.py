from javascript import require, On
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
collectblock = require('mineflayer-collectblock')

from chat.handle import handle_chat


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
    def handle(*args):
        print("I spawned 👋")
        movements = pathfinder.Movements(bot)

        @On(bot, 'chat')
        def handleMsg(this, sender, message, *args):
            print("Got message", sender, message)

            if sender and (sender != BOT_USERNAME):
                handle_chat(bot, sender, message)

    @On(bot, "end")
    def handle(*args):
        print("Bot ended!", args)
