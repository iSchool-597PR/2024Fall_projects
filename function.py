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
    dice_result = Counter(all_dice)
    return dice_result

def valid_challenge(bid, all_dice):
    quantity, face_value = bid
    dice_result = count_dice(all_dice)
    if face_value == 1:
        actual_quantity = dice_result[1]
    else:
        actual_quantity = dice_result[1] + dice_result[face_value]
    return quantity > actual_quantity

def random_bid_choice(current_bid,num_dice,num_players):
    total_dice = num_dice * num_players
    if current_bid is None:
        quantity = random.randint(2,total_dice)
        face_value = random.randint(1,6)
        new_bid = [quantity,face_value]
        return new_bid
    else:
        quantity, face_value = current_bid
        bid_choice = random.choice(["bid", "liar"])
        if bid_choice == "bid":
            new_quantity = random.randint(min(quantity + 1,total_dice), total_dice)
            new_face_value = random.randint(min(face_value + 1,6), 6)
            if random.choice(["same_quantity","same_face_value"]) == "same_quantity":
                new_bid = [quantity,new_face_value]
            else:
                new_bid = [new_quantity,face_value]
            return new_bid
        else:
            return "liar"

def simulate_game(num_players,num_dice):
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
    for i in range(num_players):
        players_dice[i] = roll_dice(num_dice)

    active_players = set(players_dice.keys())

    current_bid = None
    #Start with a random player
    current_player = random.choice(list(active_players))

    while len(active_players) >1:
        all_dice = []
        for player,dice in players_dice.items():
            if player in active_players:
                all_dice.extend(dice)
        num_active_players = len(active_players)
        action = random_bid_choice(current_bid,num_dice,num_active_players)

        previous_player = current_player
        while True:
            previous_player -= 1
            if previous_player < 0:
                previous_player = num_players - 1
            if previous_player in active_players:
                break

        if action == "liar":
            if valid_challenge(current_bid, all_dice):
                #If the challenge is right, then the previous player lose
                active_players.remove(previous_player)
            else:
                #If the challenge is wrong, then the current player lose
                active_players.remove(current_player)
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

    return next(iter(active_players))

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
    for i in range(num_players):
        results[f"player{i} wins"] = 0

    # Simulate for n times game
    for _ in range(1000):
        winner = simulate_game(num_players, num_dice)
        results[f"player{winner} wins"] += 1

    # print the results
    print("\nGame Results:")
    for player, wins in results.items():
        print(f"{player} wins: {wins}")






















