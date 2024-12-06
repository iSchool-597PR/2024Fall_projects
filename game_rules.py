"""
IS 597-PR Final Project

This module is about game rules and basic functions.

"""
import random
from collections import Counter


def roll_dice(num_dice):
    """Generate a random number between 1 and 6 for each dice.
    :param num_dice: Number of dice to roll.
    :return: A list of dice.
    >>> roll_dice(1) in [[1],[2],[3],[4],[5],[6]]
    True
    """
    return [random.randint(1,6) for _ in range(num_dice)]


def valid_challenge(bid, all_dice):
    """Determine if a challenge against the previous bid is correct.

    :param bid: The previous bid as [quantity, face_value].
    :param all_dice: List of all dice from active players.
    :return: True if challenge is valid, False if not."""
    quantity, face_value = bid
    if not isinstance(quantity, int) or not isinstance(face_value, int):
        raise ValueError("Bid values must be integers.")
    dice_result = Counter(all_dice)
    if face_value == 1:
        actual_quantity = dice_result[1]
    else:
        actual_quantity = dice_result[1] + dice_result[face_value]
    # A challenge is correct if the actual quantity is less than the bid
    return quantity > actual_quantity
