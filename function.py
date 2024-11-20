import random
from collections import Counter


def roll_dice(num_dice):
    return [random.randint(1,6) for _ in range(num_dice)]

def count_dice(all_dice):
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
    number_of_players = num_players
    number_of_dice = num_dice
    player_1_dice = roll_dice(number_of_dice)
    player_2_dice = roll_dice(number_of_dice)
    all_dice = player_1_dice.extend(player_2_dice)

    current_bid = None
    current_player = random.choice([0,1])

    while True:
        action = random_bid_choice(current_bid, number_of_dice,number_of_players)
        if action == "liar":
            if valid_challenge(current_bid, all_dice):
                return current_player
            else:
                return 1-current_player
        else:
            current_bid = action
            current_player = 1 - current_player

if __name__ == "__main__":
    results = {"player0 wins" : 0, "player1 wins": 0}
    for _ in range(10000):
        winner = simulate_game(2,5)
        if winner == 0 :
            results['player0 wins'] += 1
        else:
            results['player1 wins'] += 1
    print(results)
























