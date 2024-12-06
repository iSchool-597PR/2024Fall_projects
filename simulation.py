"""
IS 597-PR Final Project

Simulation of the game.

"""
import random
from game_rules import roll_dice,valid_challenge
from collections import Counter

def update_all_dice(players_dice):
    """Update the all_dice structure when a player is removed."""
    all_dice = []
    for active_player in players_dice.keys():
        all_dice.extend(players_dice[active_player])
    return all_dice

def simulate_game(num_players,num_dice,strategies):
    """Simulate the game between multiple players.

    Players alternately make bids or call "liar" to challenge the previous bid.

    Players are eliminated if they lose a challenge. The game continues until
    only one player remains.

    :param num_players: Number of players.
    :param num_dice: Number of dice.
    """
    if num_players < 2 or num_dice <=0:
        raise ValueError("Number of players must be at least 2 and dice must be greater than 0.")

    #I change the way to get all_dice
    players_dice = {}
    for i in range(num_players):
        players_dice[i] = roll_dice(num_dice)

    active_players = set(players_dice.keys())

    current_bid = None
    #Start with a random player
    current_player = random.choice(list(active_players))

    while len(active_players) >1:
        total_dice = 0
        for player in active_players:
            total_dice += len(players_dice[player])


        strategy = strategies[current_player]
        own_dice = players_dice[current_player]
        action = strategy.make_bid(current_bid, total_dice, own_dice)

        #Find the previous player
        previous_player = current_player
        while True:
            previous_player -= 1
            if previous_player < 0:
                previous_player = num_players - 1
            if previous_player in active_players:
                break

        if action == "liar":
            all_dice = update_all_dice(players_dice)
            if valid_challenge(current_bid, all_dice):
                # If the challenge is right, then the previous player lose
                active_players.remove(previous_player)
                players_dice.pop(previous_player)
                current_bid = None
            else:
                # If the challenge is wrong, then the current player lose
                active_players.remove(current_player)
                players_dice.pop(current_player)
                current_bid = None
                # Update the current player to next one
                while current_player not in active_players:
                    current_player = (current_player + 1) % num_players
        else:
            current_bid = action
            current_player += 1
            if current_player >= num_players:
                current_player = 0
            while current_player not in active_players:
                current_player = (current_player + 1) % num_players

    return next(iter(active_players))