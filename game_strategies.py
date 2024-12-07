"""
IS 597-PR Final Project

Different strategies to play the game Liar's Dice..

"""

import random
from collections import Counter

class Strategy:
    def __init__(self,prefer_bid = False,normal_threshold = False,optimal_threshold = False):
        """
        prefer_bid is True means that when bidding,prefer to choose the face value with max number in own dice
        normal_threshold is True means that when considering bid or challenge,taking the half of the total dice as a threshold
        optimal_threshold is True means that when considering bid or challenge, taking account of own dice to consider the threshold setting

        """
        self.prefer_bid = prefer_bid
        self.optimal_threshold = optimal_threshold
        self.normal_threshold = normal_threshold

    def random_bid(self,current_bid, total_dice):
        """Random bid choice depends on current bid and number of dice.

        :param current_bid: Current bid, [quantity,face_value] or None.
        :param total_dice: Current number of total dice.
        :return: A new bid [quantity,face_value] or "liar".
        """
        if current_bid is None:
            # First random bid: the lower limit is total_dice // 10 + 1 , and the upper limit is total_dice // 2
            quantity_starter = total_dice // 10 + 1
            quantity = random.randint(quantity_starter, max(quantity_starter, total_dice // 2))
            face_value = random.randint(1, 6)
            return [quantity, face_value]
        else:
            available_strategies = ["same_quantity", "same_face_value", "both_increase",
                                    "higher_quantity_smaller_face"]
            quantity, face_value = current_bid

            # If the face value is already 6, then we cannot bid for same_quantity and both_increase
            if face_value == 6:
                available_strategies.remove("same_quantity")
                available_strategies.remove("both_increase")

            # If the face value is 1, then we cannot bid for higher_quantity_smaller_face
            if face_value == 1:
                available_strategies.remove("higher_quantity_smaller_face")

            # If the quantity is max, then we can only use same_quantity strategy
            if quantity == total_dice:
                available_strategies = ["same_quantity"] if face_value < 6 else []

            if not available_strategies:
                return "liar"

            bid_type = random.choice(available_strategies)

            if bid_type == "same_quantity":
                # Increase the face value but same quantity
                new_face_value = random.randint(face_value + 1, 6)
                return [quantity, new_face_value]

            elif bid_type == "same_face_value":
                # Increase the quantity but same face value
                new_quantity = random.randint(quantity + 1, total_dice)
                return [new_quantity, face_value]

            elif bid_type == "both_increase":
                # Increase both quantity and face value
                new_quantity = random.randint(quantity + 1, total_dice)
                new_face_value = random.randint(face_value + 1, 6)
                return [new_quantity, new_face_value]
            elif bid_type == "higher_quantity_smaller_face":
                # Increase the quantity but use smaller face value
                new_quantity = random.randint(quantity + 1, total_dice)
                new_face_value = random.randint(1, face_value - 1) if face_value > 1 else 1
                return [new_quantity, new_face_value]

    def preferred_faces(self, own_dice):
        """
        Order the face values of dice based on their frequency, treating '1's as wildcards.

        :param own_dice: Player's own dice.
        :return: A sorted list of face values based on preference.
        """
        own_counter = Counter(own_dice)
        # Treat '1's as wildcards, adding them to each face's count
        wildcards = own_counter.get(1, 0)
        face_values = list(range(1, 7))
        face_preference = {}
        for face in face_values:
            face_preference[face] = own_counter.get(face, 0) + (wildcards if face != 1 else 0)

        # Sort face values based on their counts in descending order
        sorted_faces = sorted(face_values, key=lambda x: face_preference[x], reverse=True)
        return sorted_faces


    def inform_bid(self, current_bid, total_dice, own_dice):
        #it seems like need to revised to satisfy different current bid situation
        """
        Generate a new bid based on the preferred faces and own dice.

        :param current_bid: Current bid, [quantity, face_value].
        :param total_dice: Total number of dice in play.
        :param own_dice: Player's own dice.
        :return: A new bid [quantity, face_value] or "liar".
        """

        preferred_faces = self.preferred_faces(own_dice)

        #make first bid,using the face value with max frequency as the bidding face_value
        if current_bid is None:
            face_value = preferred_faces[0]
            quantity_starter = total_dice // 10 + 1
            quantity = random.randint(quantity_starter, max(quantity_starter, total_dice // 2))
            return [quantity, face_value]

        # if it is not the first bid, attempt to increase the bid based on preferred faces
        quantity, face_value = current_bid
        for face in preferred_faces:
            if face > face_value:
                # Try to increase the face value with the same or slightly higher quantity
                new_quantity = quantity
                if new_quantity < total_dice:
                    new_quantity = random.choice([new_quantity, new_quantity + 1])
                return [new_quantity, face]

        # If no preferred face is higher, try increasing the quantity with the same face
        #it seems like need to modify to satisfy different current bid situation
        if quantity < total_dice:
            return [quantity + 1, face_value]
        else:
            return "liar"


    def new_bid(self, current_bid, total_dice, own_dice):
        """
        Determine the new bid based on the chosen strategy.

        :param current_bid: The current bid in the game.
        :param total_dice: Total number of dice in the game.
        :param own_dice: List of integers representing the player's own dice.
        :return: The new bid as an list.

        Strategy:
        - If `self.prefer_bid` is True, use the `inform_bid` method, considering own dice.
        - Otherwise, use the `random_bid` method for a random bid.
        """
        if self.prefer_bid:
            return self.inform_bid(current_bid, total_dice, own_dice)
        else:
            return self.random_bid(current_bid, total_dice)

    def liar_decide(self, current_bid, total_dice, own_dice):
        #todo": if normal_threshold is True, use the half of total dice as threshold,
        # if optimal_threshold is True, use the expected dice count as threshold
        # otherwise,choose bid or challenge randomly"
        bid_or_liar = "bid"
        if not self.normal_threshold and not self.optimal_threshold:
            bid_or_liar = random.choice(["bid", "liar"]) #??? the probability of liar should be 50%?
        elif self.normal_threshold:
            quantity, face_value = current_bid
            threshold = total_dice // 2
            if quantity > threshold:
                bid_or_liar = "liar"
            else:
                bid_or_liar = "bid"
        elif self.optimal_threshold:
            quantity, face_value = current_bid
            own_counter = Counter(own_dice)
            own_face_count = own_counter.get(face_value, 0)
            if face_value != 1: #???好像没有考虑=1的情况
                own_face_count += own_counter.get(1, 0)
                # Estimate the probability that the current bid is correct
                estimated_total = own_face_count
                remaining_dice = total_dice - len(own_dice)

                # Average probability of each face (excluding wildcards if necessary)
                # Assuming each die has a 1/6 chance to be the desired face
                ###???这个weights好像应该是4:2
                estimated_total += sum(random.choices([0, 1], weights=[5, 1], k=remaining_dice))

                # Simple heuristic: if estimated_total is likely, continue bidding; else, call 'liar'
                # Here can implement a more sophisticated probability check further
                # For simplicity, we'll use the expected value
                expected_count = (total_dice) * (2 / 6)  # Probability of a face including wildcards (if applicable)
            if quantity > expected_count + own_face_count:
                bid_or_liar = "liar"
            else:
                bid_or_liar = "bid"
        return bid_or_liar

    def make_action(self, current_bid, total_dice, own_dice):
        if current_bid is None:
            return self.new_bid(current_bid, total_dice, own_dice)
        bid_or_liar = self.liar_decide(current_bid, total_dice, own_dice)
        if bid_or_liar == "liar":
            return "liar"
        else:
            return self.new_bid(current_bid, total_dice, own_dice)


if __name__ == "__main__":
    randomstrategy = Strategy(prefer_bid = True)
    action = randomstrategy.make_action([4,5],10,[1,1,1,3,5])
    print(action)


