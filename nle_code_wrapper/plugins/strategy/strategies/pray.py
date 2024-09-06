from nle_code_wrapper.bot.bot import Bot


def pray(bot: "Bot"):
    last_pray = -1
    pray_timeout = 1200

    while True:
        if last_pray == -1:
            last_pray = bot.blstats.time
            bot.pray()
        elif bot.blstats.time - last_pray > pray_timeout:
            last_pray = bot.blstats.time
            bot.pray()

        yield
