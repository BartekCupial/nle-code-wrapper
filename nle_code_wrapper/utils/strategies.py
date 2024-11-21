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

    room_floor = frozenset({SS.S_room, SS.S_darkroom})  # TODO: use also SS.S_ndoor?
    rooms = utils.isin(bot.glyphs, G.WALL, G.DOORS, G.BARS, room_floor)
    structure = ndimage.generate_binary_structure(2, 2)
    rooms = ndimage.binary_closing(rooms, structure=structure)
    slices = ndimage.find_objects(ndimage.label(rooms)[0])
    if slices:
        for bbox in slices:
            rooms[bbox] = 1

    labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)

    return labeled_rooms, num_rooms
