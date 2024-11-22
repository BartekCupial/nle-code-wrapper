import itertools
from typing import Tuple

import numpy as np
from nle_utils.glyph import SS, G
from PIL import Image
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.utils import utils


def print_boolean_array_ascii(arr):
    # Normalize the array to (0, 1)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if min_val == max_val:
        normalized = np.full(arr.shape, 0.5)
    else:
        normalized = (arr - min_val) / (max_val - min_val)
    # Create ASCII visualization
    chars = " ._-=+*#%@"

    for row in normalized:
        line = ""
        for val in row:
            index = int(val * (len(chars) - 1))
            line += chars[index]
        print(line)


def save_boolean_array_pillow(arr):
    # Normalize the array to (0, 1)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if min_val == max_val:
        normalized = np.full(arr.shape, 0.5)
    else:
        normalized = (arr - min_val) / (max_val - min_val)

    normalized = (normalized * 255).astype(np.uint8)
    Image.fromarray(normalized).save("array.png")

    # Create a random colormap (one color for each label)
    unique_values = np.unique(arr)
    num_colors = len(unique_values)  # +1 for background
    colormap = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
    # Set background (label 0) to black
    colormap[0] = [0, 0, 0]

    # Convert labeled array to RGB using the colormap
    height, width = arr.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    for label in unique_values:
        mask = arr == label
        rgb_image[mask] = colormap[label]

    # Create and save PIL Image
    img = Image.fromarray(rgb_image)
    img.save("labeled_rooms.png")


def room_detection(bot: "Bot") -> Tuple[np.ndarray, int]:
    """
    Detect rooms in the dungeon using connected components analysis.

    Args:
        bot: Bot

    Returns:
        Tuple containing:
        - labeled_rooms: numpy array where each room has a unique integer label
        - num_rooms: number of distinct rooms found
    """
    level = bot.current_level
    position = bot.entity.position

    room_floor = frozenset({SS.S_room, SS.S_darkroom})  # TODO: use also SS.S_ndoor?
    rooms = utils.isin(level.objects, room_floor, G.STAIR_DOWN, G.STAIR_UP)

    structure = ndimage.generate_binary_structure(2, 2)
    labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)

    # include our position as part of the room
    # if all neighbors which are room floor have the same label
    neighbors = []
    for x, y in itertools.product([-1, 0, 1], repeat=2):
        if x == 0 and y == 0:
            continue

        neighbor = labeled_rooms[position[0] + y, position[1] + x]
        if neighbor != 0:
            neighbors.append(neighbor)

    # if we are standing inside the room treat my place as part of the room
    # then we need to recompute closest components (if we were stading on the doors)
    if neighbors:
        rooms[position] = neighbors[0]
        labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)

    # save_boolean_array_pillow(labeled_rooms)
    return labeled_rooms, num_rooms


def corridor_detection(bot: "Bot"):
    position = bot.entity.position

    # treat corridors as everything what is floor and not room
    labeled_rooms, num_rooms = room_detection(bot)
    floor = utils.isin(bot.glyphs, G.FLOOR, G.DOOR_OPENED)
    corridors = np.logical_and(floor, labeled_rooms == 0)

    # include our position as part of the room
    # if all neighbors which are corridor have the same label
    neighbors = []
    for x, y in itertools.product([-1, 0, 1], repeat=2):
        if x == 0 and y == 0:
            continue

        neighbor = labeled_rooms[position[0] + y, position[1] + x]
        neighbors.append(neighbor)

    if neighbors and np.all(neighbors == neighbors[0]):
        corridors[position] = True

    return corridors
