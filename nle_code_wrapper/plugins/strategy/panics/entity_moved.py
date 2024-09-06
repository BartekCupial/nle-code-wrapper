from nle_code_wrapper.bot import Bot


def lists_match(list1, list2):
    if len(list1) != len(list2):
        return False
    return all(x == y for x, y in zip(list1, list2))


def entity_moved(bot: "Bot"):
    prev_entities = bot.entities
    while True:
        if prev_entities != bot.entities:
            prev_entities = bot.entities
            yield "entities moved"
        else:
            yield False
