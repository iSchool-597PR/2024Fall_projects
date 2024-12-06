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

def count_dice(all_dice):
    """Using Counter to count each dice face value
    :param all_dice: List of dice to count.
    :return: Counter with face value as keys and their counts as values.
    """
    return Counter(all_dice)

def valid_challenge(bid, all_dice):
    """Examine whether a bid is valid or not.

    :param bid: The bid to check.
    :param all_dice: List of dice to check.
    :return: True if bid is valid, False if not."""
    quantity, face_value = bid
    if not isinstance(quantity, int) or not isinstance(face_value, int):
        raise ValueError("Bid values must be integers.")
    dice_result = count_dice(all_dice)
    if face_value == 1:
        actual_quantity = dice_result[1]
    else:
        actual_quantity = dice_result[1] + dice_result[face_value]
    return quantity > actual_quantity

def random_bid_choice(current_bid,total_dice):
    """Random bid choice depends on current bid and number of dice."""
    # total_dice = num_dice * num_players
    if current_bid is None:
        #First random bid
        quantity = random.randint(2,total_dice)
        face_value = random.randint(1,6)
        return [quantity,face_value]
    else:
        current_bid = [int(value) for value in current_bid]
        quantity, face_value = current_bid

        #If already reach max quantity and max face value 6, the player can only challenge for that
        if quantity == total_dice and face_value == 6:
            return "liar"

        bid_choice = random.choice(["bid", "liar"])

        # new_quantity = random.randint(min(quantity + 1,total_dice), total_dice)
        # new_face_value = random.randint(min(face_value + 1,6), 6)
        available_strategies = ["same_quantity", "same_face_value", "both_increase", "higher_quantity_smaller_face","liar"]

        #If the face value is already 6, then we cannot bid for same_quantity and both_increase
        if face_value == 6:
            available_strategies.remove("same_quantity")
            available_strategies.remove("both_increase")

        #If the face value is 1, then we cannot bid for higher_quantity_smaller_face
        if face_value == 1:
            available_strategies.remove("higher_quantity_smaller_face")

        #If the quantity is max, then we can only use same_quantity strategy
        if quantity == total_dice:
            available_strategies = ["same_quantity"] if face_value < 6 else []

        if not available_strategies:
            return "liar"

        bid_type = random.choice(available_strategies)

        if bid_type == "same_quantity":
            #Increase the face value but same quantity
            new_face_value = random.randint(face_value+1,6)
            return [quantity,new_face_value]

        elif bid_type == "same_face_value":
            #Increase the quantity but same face value
            new_quantity = random.randint(quantity+1,total_dice)
            return [new_quantity,face_value]

        elif bid_type == "both_increase":
            #Increase both quantity and face value
            new_quantity = random.randint(quantity+1,total_dice)
            new_face_value = random.randint(face_value+1,6)
            return [new_quantity,new_face_value]
        elif bid_type == "higher_quantity_smaller_face":
            #Increase the quantity but use smaller face value
            new_quantity = random.randint(quantity+1,total_dice)
            new_face_value = random.randint(1,face_value-1) if face_value > 1 else 1
            return [new_quantity,new_face_value]
        elif bid_type == "liar":
            return "liar"


def update_all_dice(players_dice):
    """Update the global all_dice structure when a player is removed."""
    all_dice = []
    for active_player in players_dice.keys():
        all_dice.extend(players_dice[active_player])
    return all_dice

def simulate_game(num_players,num_dice, starter = -1):
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
    if starter == -1:
        current_player = random.choice(list(active_players))
    else:
        current_player = starter

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

        action = random_bid_choice(current_bid,total_dice)
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
                active_players.remove(previous_player)
                players_dice.pop(previous_player)
                current_bid = None
            else:
                #If the challenge is wrong, then the current player lose
                liar_record.append([bid_times,current_player, challenge_bid, 'not valid',active_players])
                active_players.remove(current_player)
                players_dice.pop(current_player)
                current_bid = None
                #Update the current player to next one
                while current_player not in active_players:
                    current_player = (current_player + 1) % num_players



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
        winner, first_player, bid_record, liar_record, bid_times, original_dices = simulate_game(num_players, num_dice,0)
        results[f"player{winner} wins"] += 1
        first_players[f"game starts with player {first_player}"] += 1



    # print the results
    print("\nGame Results:")
    for player, wins in results.items():
        print(f"{player} wins: {wins}")
    for player, starts in first_players.items():
        print(f"{player}: {starts}")






















