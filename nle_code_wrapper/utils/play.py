import os
import readline
import sys
import termios
import tty
from functools import partial


def play_using_strategies(env, action_mode="human"):
    if action_mode == "random":
        action = env.action_space.sample()
    elif action_mode == "human":
        while True:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = os.read(fd, 3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if len(ch) == 1:
                if ord(ch) == 3:
                    raise KeyboardInterrupt
                else:
                    action = int(ch)

            try:
                assert action in env.action_space
                break
            except ValueError:
                print(f"Selected action '{ch}' is not in action list. " "Please try again.")
                continue

    return action


def completer(text, state, commands=[]):
    options = [cmd for cmd in commands if cmd.startswith(text)]
    return options[state] if state < len(options) else None


def setup_autocomplete(completer_fn):
    os.system("stty sane")  # forces the terminal back to “cooked” mode
    readline.parse_and_bind("tab: complete")
    print("Type commands and use TAB to autocomplete.")
    print("To see strategies use command: `help`")
    readline.set_completer(completer_fn)


def play_using_strategies_autocomplete(env, action_mode="human"):
    if action_mode == "random":
        action = env.action_space.sample()
    elif action_mode == "human":
        names = [strategy for strategy in env.bot.strategies]
        setup_autocomplete(partial(completer, commands=names))

        while True:
            command = input("> ")

            if command == "help":
                for name in names:
                    print(name)
                continue
            else:
                try:
                    action = names.index(command)
                    action = command
                    break
                except ValueError:
                    print(f"Selected action '{command}' is not in action list. Please try again.")
                    continue

    return action


def play_from_actions(env, action_mode="human", actions=[]):
    if len(actions) > 0:
        action = actions.pop(0)
        return action
    else:
        return play_using_strategies_autocomplete(env, action_mode)
