"""
IS 597-PR Final Project


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
    """Examine whether a bid is valid or not.

    :param bid: The bid to check.
    :param all_dice: List of dice to check.
    :return: True if bid is valid, False if not."""
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
    """Update the global all_dice structure when a player is removed."""
    all_dice = []
    for active_player in players_dice.keys():
        all_dice.extend(players_dice[active_player])
    return all_dice

def simulate_game(num_players,num_dice, strategies, special_rule = False, first_caller = -1):
    """Simulate the game between multiple players.

    Players alternately make bids or call "liar" to challenge the previous bid.

    Players are eliminated if they lose a challenge. The game continues until
    only one player remains.

    :param num_players: Number of players.
    :param num_dice: Number of dice.
    """
    if num_players < 2 or num_dice <=0:
        raise ValueError("Number of players must be at least 2 and dice must be greater than 0.")

    # I think these are a little bit duplicate
    # number_of_players = num_players
    # number_of_dice = num_dice
    # player_1_dice = roll_dice(number_of_dice)
    # player_2_dice = roll_dice(number_of_dice)
    # all_dice = player_1_dice.extend(player_2_dice)

    #I change the way to get all_dice
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

    # all_dice = []
    # for dice in players_dice.values():
    #     all_dice.extend(dice)

    while len(active_players) >1:
        # all_dice = []
        # for player,dice in players_dice.items():
        #     if player in active_players:
        #         all_dice.extend(dice)
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
                liar_record.append([bid_times,current_player,challenge_bid,'valid',active_players])
                if not special_rule :
                #under normal rule,the previous player loses the game and others restart bidding
                    active_players.remove(previous_player)
                    players_dice.pop(previous_player)
                    current_bid = None
                else:
                #under special rule, the previous player loses  one of dice randomly and everyone restart_bidding
                    players_dice[previous_player].pop(random.randint(0,len(players_dice[previous_player])-1))
                    current_bid = None
                    if len(players_dice[previous_player]) == 0:
                        active_players.remove(previous_player)
                        players_dice.pop(previous_player)
            else:
                liar_record.append([bid_times,current_player, challenge_bid, 'invalid',active_players])
                if not special_rule:
                # under normal rule,the current player loses the game and others restart bidding
                    active_players.remove(current_player)
                    players_dice.pop(current_player)
                    current_bid = None
                else:
                # under special rule, the current player loses  one of dice randomly and everyone restart_bidding
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
#     for _ in range(10000):
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


    # Simulate for n times game
    for _ in range(1000):
        winner, first_player, bid_record, liar_record, bid_times, original_dices = simulate_game(num_players, num_dice,-1,special_rule = True)
        results[f"player{winner} wins"] += 1
        first_players[f"game starts with player {first_player}"] += 1
        print(original_dices)
        print(bid_record)



    # print the results
    print("\nGame Results:")
    for player, wins in results.items():
        print(f"{player} wins: {wins}")
    for player, starts in first_players.items():
        print(f"{player}: {starts}")






















