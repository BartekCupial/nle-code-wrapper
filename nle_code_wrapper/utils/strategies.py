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


def label_dungeon_features(bot: "Bot"):
    level = bot.current_level
    position = bot.entity.position
    structure = ndimage.generate_binary_structure(2, 2)

    # rooms
    room_floor = frozenset({SS.S_room, SS.S_darkroom})
    rooms = utils.isin(level.objects, room_floor, G.STAIR_DOWN, G.STAIR_UP)
    labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)

    # corridors
    corridor_floor = frozenset({SS.S_corr, SS.S_litcorr})
    corridors = utils.isin(level.objects, corridor_floor)
    labeled_corridors, num_corridors = ndimage.label(corridors, structure=structure)

    # doors
    doors = utils.isin(level.objects, frozenset({SS.S_ndoor}), G.DOOR_OPENED)

    # combine rooms and corridors
    labeled_features = np.zeros_like(level.objects)
    labeled_features[rooms] = labeled_rooms[rooms]
    labeled_features[corridors] = labeled_corridors[corridors] + num_rooms

    # include our position
    # if all neighbors which are dungeon features have the same label
    neighbors = []
    for x, y in itertools.product([-1, 0, 1], repeat=2):
        if x == 0 and y == 0:
            continue

        neighbor = labeled_features[position[0] + y, position[1] + x]
        if neighbor != 0:
            neighbors.append(neighbor)
    neighbors = np.array(neighbors)

    if len(neighbors) > 0:
        # if all neighbors are rooms or corridors
        if np.all(neighbors <= num_rooms):
            rooms[position] = True
        else:
            corridors[position] = True

    # we include doors only at the end to be able to detect if we are standing on the door, overall we treat doors as part of the corridor
    corridors[doors] = True
    rooms[doors] = False  # we have to exclude doors from rooms as well, because we could stand on the door

    labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)
    labeled_corridors, num_corridors = ndimage.label(corridors, structure=structure)
    labeled_features = np.zeros_like(level.objects)
    labeled_features[rooms] = labeled_rooms[rooms]
    labeled_features[corridors] = labeled_corridors[corridors] + num_rooms

    return labeled_features, num_rooms, num_corridors


def room_detection(bot: "Bot") -> Tuple[np.ndarray, int]:
    labeled_features, num_rooms, num_corridors = label_dungeon_features(bot)
    labeled_features[labeled_features > num_rooms] = 0

    return labeled_features, num_rooms


def corridor_detection(bot: "Bot") -> Tuple[np.ndarray, int]:
    labeled_features, num_rooms, num_corridors = label_dungeon_features(bot)
    labeled_features[labeled_features <= num_rooms] = 0
    labeled_features -= num_rooms
    labeled_features[labeled_features < 0] = 0

    return labeled_features, num_corridors
