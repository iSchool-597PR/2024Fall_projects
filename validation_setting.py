import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict


class Validation_varaibales:
    """
    A class to manage and validate game statistics, such as player results, dice distributions, liar call outcomes, and bid records.

    """

    def __init__(self, num_players, num_dice, times):
        """
        Initialize the validation variables.

        :param num_players: Number of players in the game.
        :param num_dice: Number of dice each player has.
        :param times: Number of game iterations to simulate.

        >>> v = Validation_varaibales(3, 5, 100)
        >>> v.num_players
        3
        >>> v.num_dice
        5
        >>> v.times
        100
        >>> len(v.results)  # Number of players
        3
        >>> len(v.original)  # Dice face values from 1 to 6
        6
        """
        self.num_players = num_players
        self.num_dice = num_dice
        self.times = times
        self.results = {}
        self.first_players = {}
        self.personal_liar_record = {}
        quantity = [round(x * 0.1, 1) for x in range(11)]
        face_value = list(range(1, 7))
        data = [(q, f, 0, 0, 0) for q in quantity for f in face_value]
        liar_occur_bid = pd.DataFrame(data,
                                           columns=['quantity', 'face_value', 'times', 'valid_times', 'invalid_times'])
        self.liar_result = {}
        self.max_quantity =  {key: 0 for key in range( num_players * num_dice + 1)}
        for i in range(num_players):
            self.results[f"player{i}"] = 0
            self.first_players[f'player{i}'] = 0
            self.personal_liar_record[f'player{i}'] = liar_occur_bid.copy()
            self.liar_result[f'player{i}'] = {"valid": 0, "invalid": 0}
        self.original = {key: 0 for key in range(1, 7)}


    def valid_bid(self,bids):
        """
        Check if the bid sequence is valid: at least one of quantity or face_value
        increases in every step.

        :param bids: List of bids, where each bid is [quantity, face_value].
        :return: True if all bids are valid, False otherwise.
        >>> v = Validation_varaibales(5,5,1)
        >>> v.valid_bid([[1, 3], [2, 3], [3, 3]])  # Increasing quantity
        True
        >>> v.valid_bid([[1, 3], [1, 4], [1, 5]])  # Increasing face value
        True
        >>> v.valid_bid([[1, 3], [2, 4], [3, 5]])  # Both increasing
        True
        >>> v.valid_bid([[1, 3], [1, 3], [2, 3]])  # InValid: No decrease
        False
        >>> v.valid_bid([[1, 3], [1, 2], [2, 3]])  # Invalid: Decrease in face value
        False
        """
        is_increasing = True
        for i in range(1, len(bids)):
            prev_quantity, prev_face_value = bids[i - 1]
            curr_quantity, curr_face_value = bids[i]
            if not (curr_quantity > prev_quantity or curr_face_value > prev_face_value):
                is_increasing = False
                break
        return is_increasing

    def update(self, winner, first_player, bid_record, liar_record, bid_times, original_dices):
        """
        Update the validation variables after each game iteration.
        Check if the bid is valid

        :param winner: The index of the player who won the game.
        :param first_player: The index of the player who started the game.
        :param bid_record: A record of all bids made during the game.
        :param liar_record: A record of all liar calls made during the game.
        :param bid_times: The total number of bids in the game.
        :param original_dices: A dictionary of dice face value distributions for the game.
        """
        for bid in bid_record:
            bids = []
            for player, action in bid.items():
                if action == 'liar':
                    if self.valid_bid(bids):
                        pass
                    else:
                        print("There are invalid bid exists")
                        break
                else:
                    bids.append(action)

        # record the winner and the first player distribution
        self.results[f"player{winner}"] += 1
        self.first_players[f"player{first_player}"] += 1

        # record the original dice distribution
        for key, values in original_dices.items():
            self.original[key] += values
            if key == 1:
                self.max_quantity[values] += 1

        # record the liar call results
        for i in range(len(liar_record)):
            bid_times, current_player, challenge_bid, result, active_players = liar_record[i]
            if result == "valid":
                self.liar_result[f"player{current_player}"]['valid'] += 1
            else:
                self.liar_result[f"player{current_player}"]['invalid'] += 1
            quantity, face_value = challenge_bid
            total_dice = active_players * self.num_dice
            quantity_percentage = quantity / total_dice
            row_condition = (
                    (self.personal_liar_record[f"player{current_player}"]['quantity'] >= quantity_percentage) &
                    (self.personal_liar_record[f"player{current_player}"]['face_value'] == face_value)
            )

            # Update the times column for the matching row
            if row_condition.any():
                matching_index = self.personal_liar_record[f"player{current_player}"].loc[row_condition].index[0]
                self.personal_liar_record[f"player{current_player}"].loc[matching_index,'times'] += 1
                if result == "valid":
                   self.personal_liar_record[f"player{current_player}"].loc[matching_index,'valid_times'] += 1
                else:
                    self.personal_liar_record[f"player{current_player}"].loc[matching_index,'invalid_times'] += 1

    def check_original_dices(self):
        """
        Analyze and display the dice face value distribution across all games.
        :return: DataFrame showing face value occurrences and occurrence rates.
        >>> v = Validation_varaibales(3, 5, 4)
        >>> v.original = {1: 12, 2: 8, 3: 14, 4: 6, 5: 11, 6: 9}
        >>> df = v.check_original_dices()
        >>> bool(df[df["Face_value"] == 1]["Occurrence"].iloc[0] == 12)
        True
        >>> df[df["Face_value"] == 1]["Occurrence rate"].iloc[0]
        '20.00%'
        """
        original_df = pd.DataFrame(list(self.original.items()), columns=["Face_value", "Occurrence"])
        original_df['Occurrence rate'] = original_df['Occurrence'] / (self.times * self.num_players * self.num_dice)
        original_df["Occurrence rate"] = original_df["Occurrence rate"].apply(lambda x: f"{x:.2%}")
        return original_df

    def check_win_rate(self):
        """
        Analyze and display the win rate for each player.

        :return: DataFrame showing player wins and win rates.

        >>> v = Validation_varaibales(3, 5, 60)
        >>> v.results = {"player0": 10, "player1": 20, "player2": 30}
        >>> df = v.check_win_rate()
        >>> bool(df[df["Player"] == "player0"]["Wins"].iloc[0] == 10)
        True
        >>> df[df["Player"] == "player2"]["Win Rate"].iloc[0]
        '50.00%'

        """
        win_rate_df = pd.DataFrame(list(self.results.items()), columns=["Player", "Wins"])
        win_rate_df['Win Rate'] = win_rate_df['Wins'] / self.times
        #win_rate_df["Win Rate"] = win_rate_df["Win Rate"].apply(lambda x: f"{x:.2%}")
        return win_rate_df

    def check_first_player(self):
        """
        Analyze and display the distribution of first players across games.
        Check if the first player is random.

        :return: DataFrame showing players, the number of times they started, and their start rates.

        >>> v = Validation_varaibales(3, 5, 100)
        >>> v.first_players = {"player0": 30, "player1": 40, "player2": 30}
        >>> df = v.check_first_player()
        >>> bool(df[df["Player"] == "player0"]["Start times"].iloc[0] == 30)
        True
        >>> df[df["Player"] == "player0"]["Start rate"].iloc[0]
        '30.00%'
        """
        start_rate_df = pd.DataFrame(list(self.first_players.items()), columns=["Player", "Start times"])
        start_rate_df['Start rate'] = start_rate_df['Start times'] / self.times
        #start_rate_df["Start rate"] = start_rate_df["Start rate"].apply(lambda x: f"{x:.2%}")
        return start_rate_df

    def check_liar_call(self,player):
        """
        Analyze and visualize the distribution of liar calls.
        Check if the liar call are random

        Generates a heatmap of challenge bids based on the proportion of quantity(quantity / total_dice) and face value.
        """
        # Add a new column for quantity proportion
        liar_occur_bid =self.personal_liar_record[f"player{player}"] .sort_values(by='times', ascending=False)
        print(liar_occur_bid)
        # draw the heatmap of challenge_bid
        pivot_table =liar_occur_bid.pivot(index='face_value', columns='quantity', values='times')
        sns.heatmap(pivot_table, annot=True, fmt="d", cmap="coolwarm", cbar=True)
        plt.title("Heatmap of Quantity percentage vs Face Value")
        plt.xlabel("Quantity percentage")
        plt.ylabel("Face Value")
        plt.show()

    def check_liar_valid_rate(self,player):
        """
        Analyze the relationship between bid quantity and liar call validity rate.

        """
        # check if with the quantity rasies, the valid rate increases,
        # need to exclude the maxmum quantity matching the max_dices
        liar_occur_bid = self.personal_liar_record[f"player{player}"]
        grouped_liar = liar_occur_bid.groupby('quantity').agg(
            {'times': 'sum', 'valid_times': 'sum', 'invalid_times': 'sum'})
        grouped_liar['valid_rate'] = grouped_liar['valid_times'] / grouped_liar['times']
        print(grouped_liar)
        plt.figure(figsize=(8, 6))
        plt.plot(grouped_liar.index, grouped_liar['valid_rate'], marker='o', label='Valid Rate')
        plt.title("Valid Rate across Quantity percentage")
        plt.xlabel("Quantity percentage")
        plt.ylabel("Valid Rate")
        plt.ylim(0, 1)  # Valid rate is a ratio (0 to 1)
        plt.grid(True)
        plt.legend()
        plt.show()

    def check_liar_win_rate(self):
        """
         Calculate the valid call rate for each player in a liar game.

         The function processes a dictionary (`self.liar_result`) with player names as keys and
         their respective call statistics (`valid_calls` and `invalid_calls`) as values.
         It computes the total calls and the percentage of valid calls, returning a formatted
         DataFrame with the results.

         Returns:
             pd.DataFrame: A DataFrame with columns:
                 - 'player': Player names.
                 - 'valid_calls': Number of valid calls made by the player.
                 - 'invalid_calls': Number of invalid calls made by the player.
                 - 'total_calls': Total number of calls made by the player.
                 - 'valid_call_rate': Percentage of valid calls (formatted as a percentage string).
        """
        liar_result_df = pd.DataFrame.from_dict(self.liar_result, orient='index').reset_index()
        liar_result_df.columns = ['player', 'valid_calls', 'invalid_calls']
        liar_result_df['total_calls'] = liar_result_df['valid_calls'] + liar_result_df['invalid_calls']
        liar_result_df['valid_call_rate'] = liar_result_df['valid_calls'] / liar_result_df['total_calls']
        liar_result_df["valid_call_rate"] = liar_result_df["valid_call_rate"].apply(lambda x: f"{x:.2%}")
        return liar_result_df


if __name__ == "__main__":
    pass
