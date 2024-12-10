"""
IS 597-PR Final Project

This module provides functions to simulate the game "Liar's Dice."
It includes rolling dice for players, validating challenges to previous bids, updating dice sets when players are removed,
and simulating an entire game until a single winner remains.

Functions:
- roll_dice(num_dice): Roll a specified number of dice and return the results.
- valid_challenge(bid, all_dice): Check if a challenge (calling "liar") on the previous bid is valid.
- update_all_dice(players_dice): Update the global list of all dice after a challenge action happened.
- simulate_game(num_players, num_dice, strategies, special_rule=False, first_caller=-1): Simulate a full game.

"""
import random
from collections import Counter
import game_strategies as stra


def roll_dice(num_dice):
    """
    Roll a specified number of dice, each returning a random integer from 1 to 6.

    :param num_dice: Number of dice to roll.
    :return: A list of integers representing dice values.

    >>> roll_dice(1) in [[1],[2],[3],[4],[5],[6]]
    True
    """
    return [random.randint(1,6) for _ in range(num_dice)]


def valid_challenge(bid, all_dice):
    """
    Determine if a challenge against the previous bid is correct.

    In this game, the bid is specified as [quantity, face_value]. The face '1' is considered wild:
    - If face_value is 1, only dice showing '1' count towards the quantity.
    - If face_value is not 1, then both dice showing '1' (wild) and dice showing the face_value itself count.

    If the actual total number of dice that match the bid (considering the above rules) is less than the bid quantity,
    the challenge is correct (returns True). Otherwise, the challenge is incorrect (returns False).

    :param bid: The previous bid as [quantity, face_value].
    :param all_dice: A list of integers representing all dice currently in play.
    :return: True if the challenge is correct, False otherwise.

    >>> all_dice_test = [1,4,5,2,4,1,2,4,6,3,5,5,3,1,2,5,1,5,1,1]
    >>> bid_test1 = [10, 5]
    >>> valid_challenge(bid_test1, all_dice_test) # 6 '1' + 5 '5' = 11 total towards '5', so the bid of 10 is met and the challenge is invalid.
    False
    >>> bid_test2 = [8, 6]
    >>> valid_challenge(bid_test2, all_dice_test) # 6 '1' + 1 '6' = 7 total towards '6', so the bid of 8 is not met and the challenge is valid.
    True
    """
    quantity, face_value = bid
    if not isinstance(quantity, int) or not isinstance(face_value, int):
        raise ValueError("Bid values must be integers.")
    dice_result = Counter(all_dice)
    if face_value == 1:
        actual_quantity = dice_result[1]
    else:
        actual_quantity = dice_result[1] + dice_result[face_value]
    return quantity > actual_quantity


def update_all_dice(players_dice):
    """
    Update the list of all dice currently in play after any changes (e.g., player removal).

    :param players_dice: A dictionary mapping players ID to their list of dice.
    :return: A list containing all dice from all remaining active players.
    """
    all_dice = []
    for active_player in players_dice.keys():
        all_dice.extend(players_dice[active_player])
    return all_dice

def simulate_game(num_players,num_dice, strategies, special_rule = False, first_caller = -1):
    """
    Simulate a game of Liar's Dice with a given number of players, dice, and player strategies.

    Game Rules Simplified:
    - Each player rolls 'num_dice' dice at the beginning of the game.
    - Players take turns making bids or challenging the previous bid by calling "liar".
    - A bid consists of a [quantity, face_value], suggesting that there are at least 'quantity' dice
      of 'face_value' (with '1' acting as wild).
    - If a player calls "liar", the correctness of the last bid is checked:
       - If the bid is not met, the previous player (who made the bid) loses (either loses a die or is removed).
       - If the bid is met, the challenger loses (either loses a die or is removed).
    - The game continues until only one player remains, who is the winner.

    :param num_players: Number of players.
    :param num_dice: Number of dice each player starts with.
    :param strategies: A dictionary of player strategies.
    :param special_rule: If True, instead of removing a player after losing a challenge, that player only loses one die.
                         If a player loses all dice, they are then removed.
    :param first_caller: The player ID who starts the game. If -1, a random active player starts.

    :return: A tuple containing:
             - winner (int): The ID of the winning player.
             - first_player (int): The ID of the player who started the game.
             - bid_record (list): A list of bid actions taken during the game.
             - liar_record (list): A list of all 'liar' calls and their outcomes.
             - bid_times (int): The total number of bids made during the game.
             - original_dice (dict): A dictionary summarizing the original dice distribution at the start.
    """
    if num_players < 2 or num_dice <=0:
        raise ValueError("Number of players must be at least 2 and dice must be greater than 0.")


    players_dice = {}
    original_dice = {key :0 for key in range(1,7)}
    for i in range(num_players):
        players_dice[i] = roll_dice(num_dice)
        for j in range(len(players_dice[i])):
            face_value = players_dice[i][j]
            original_dice[face_value] += 1


    active_players = set(players_dice.keys())

    current_bid = None
    #Start with a random player
    if first_caller == -1:
        current_player = random.choice(list(active_players))
    else:
        current_player = first_caller

    # record the first player and the bid records for validation
    first_player = current_player
    bid_record = []
    liar_record = []
    bid_times = 0

    #simulate the game
    while len(active_players) >1:
        total_dice = 0
        for player in active_players:
            total_dice += len(players_dice[player])

        strategy = strategies[current_player]
        own_dice = players_dice[current_player]
        action = strategy.make_action(current_bid, total_dice, own_dice)
        bid_record.append({current_player : action})
        bid_times += 1

        previous_player = current_player
        while True:
            previous_player -= 1
            if previous_player < 0:
                previous_player = num_players - 1
            if previous_player in active_players:
                break

        if action == "liar":
            all_dice = update_all_dice(players_dice)
            challenge_bid = current_bid
            if valid_challenge(current_bid, all_dice):
                #If the challenge is right, then the previous player lose
                liar_record.append([bid_times,current_player,challenge_bid,'valid',len(active_players)])
                if not special_rule :
                    # Under normal rule,the previous player loses the game and others restart bidding
                    active_players.remove(previous_player)
                    players_dice.pop(previous_player)
                    current_bid = None
                else:
                    # Under special rule, the previous player loses  one of dice randomly and everyone restart bidding
                    players_dice[previous_player].pop(random.randint(0, len(players_dice[previous_player]) - 1))
                    current_bid = None
                    if len(players_dice[previous_player]) == 0:
                        active_players.remove(previous_player)
                        players_dice.pop(previous_player)
            else:
                liar_record.append([bid_times,current_player, challenge_bid, 'invalid',len(active_players)])
                if not special_rule:
                    # Under normal rule,the current player loses the game and others restart bidding
                    active_players.remove(current_player)
                    players_dice.pop(current_player)
                    current_bid = None
                else:
                    # Under special rule, the current player loses  one of dice randomly and everyone restart_bidding
                    players_dice[current_player].pop(random.randint(0, len(players_dice[current_player]) - 1))
                    current_bid = None
                    #if the current player loses all of their dice, he loses.
                    if len(players_dice[current_player]) == 0:
                        active_players.remove(current_player)
                        players_dice.pop(current_player)
        else:
            current_bid = action
        current_player += 1
        if current_player >= num_players:
            current_player = 0
        while current_player not in active_players:
            current_player = (current_player + 1) % num_players

    return next(iter(active_players)), first_player, bid_record, liar_record, bid_times,original_dice

# if __name__ == "__main__":
#     results = {"player0 wins" : 0, "player1 wins": 0}
#     for _ in range(1000):
#         winner = simulate_game(2,5)
#         if winner == 0 :
#             results['player0 wins'] += 1
#         else:
#             results['player1 wins'] += 1
#     print(results)

if __name__ == "__main__":
    num_players = 5
    num_dice = 5

    # Initialize the results
    results = {}
    first_players = {}
    for i in range(num_players):
        results[f"player{i} wins"] = 0
        first_players[f'game starts with player {i}'] = 0
    Strategies = {}
    for i in range(num_players):
        Strategies[i] = stra.Strategy()

    # Simulate for n times game
    for _ in range(10):
        winner, first_player, bid_record, liar_record, bid_times, original_dices = simulate_game(num_players, num_dice,Strategies)
        results[f"player{winner} wins"] += 1
        first_players[f"game starts with player {first_player}"] += 1
        print(original_dices)
        print(bid_record)
        print(liar_record)



    # print the results
    print("\nGame Results:")
    for player, wins in results.items():
        print(f"{player} wins: {wins}")
    for player, starts in first_players.items():
        print(f"{player}: {starts}")