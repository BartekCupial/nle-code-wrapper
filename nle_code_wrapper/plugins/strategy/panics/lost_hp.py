from nle_code_wrapper.bot import Bot


def lost_hp(bot: "Bot"):
    # TODO: we need to check if there was a level up or increase in the hp, maybe max_hp?
    prev_hp = -1
    while True:
        if prev_hp == -1:
            prev_hp = bot.blstats.hitpoints

        if prev_hp > bot.blstats.hitpoints:
            prev_hp = bot.blstats.hitpoints
            yield "lost hp"
        else:
            yield False
