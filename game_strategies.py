"""
IS 597-PR Final Project

Different strategies to play the game Liar's Dice..

"""

import random
from collections import Counter

class Strategy:
    """
    A class to define a player's strategy for the dice game, including bidding and deciding whether to call "liar".

    Attributes:
    - prefer_bid (bool): When True, prefer to bid using the face value with the highest count in the player's dice.
    - liar_threshold (str): Strategy for deciding when to call "liar".
        - "Random": Randomly choose to bid or call "liar".
        - "Normal": Use half of the total dice as the threshold to call "liar".
        - "Optimal": Use the sum of the player's dice count and half of the remaining dice as the threshold to call "liar".
    - conservative_increase (bool): When True, bid quantity increases by 1; otherwise, quantity increases randomly.
    """
    def __init__(self,prefer_bid = False,liar_threshold ="Random", conservative_increase = False):
        """
        Initialize the strategy.

        :param prefer_bid: Whether to prioritize bids based on own dice.
        :param liar_threshold (str): Strategy for deciding when to call "liar".
                - "Random": Randomly choose to bid or call "liar".
                - "Normal": Use half of the total dice as the threshold to call "liar".
                - "Optimal": Use the sum of the player's dice count and half of the remaining dice as the threshold to call "liar".
        :param conservative_increase: Whether to increase bid quantity conservatively (+1) or randomly.
        >>> s1 = Strategy()
        >>> s1.prefer_bid
        False
        >>> s1.liar_threshold
        'Random'
        >>> s1.conservative_increase
        False
        >>> s2 = Strategy(prefer_bid=True, liar_threshold="Normal", conservative_increase=True)
        >>> s2.prefer_bid
        True
        >>> s2.liar_threshold
        'Normal'
        >>> s2.conservative_increase
        True
        >>> Strategy(liar_threshold="Aggressive")
        Traceback (most recent call last):
        ...
        ValueError: liar_threshold must be one of: 'Random', 'Normal', 'Optimal'.
        """
        if liar_threshold not in {"Random", "Normal", "Optimal"}:
            raise ValueError("liar_threshold must be one of: 'Random', 'Normal', 'Optimal'.")
        self.prefer_bid = prefer_bid
        self.liar_threshold = liar_threshold
        self.conservative_increase = conservative_increase

    def random_bid(self,current_bid, total_dice):
        """
        Generate a random bid based on the current bid and total number of dice.

        :param current_bid: The current bid, [quantity, face_value], or None if it's the first bid.
        :param total_dice: The total number of dice in play.
        :return: A new bid [quantity, face_value] or "liar".

        >>> s = Strategy()
        >>> [q1,f1] = s.random_bid(None, 20)
        >>> 3 <= q1 <= 10 and 1 <= f1 <= 6
        True
        >>> [q2,f2] = s.random_bid([7,3],20)
        >>> (7 < q2 <= 20 and 1 <= f2 <=6) or (q2 ==7 and 4<=f2<=6)
        True
        >>> [q3,f3] = s.random_bid([20,4],20)
        >>> q3 == 20 and  5 <= f3 <= 6
        True
        >>> [q4,f4] = s.random_bid([6,6],20)
        >>> 7<= q4 <= 20 and  1 <=f4 <= 6
        True

        >>> s2 = Strategy(conservative_increase=True)
        >>> [q5,f5] = s2.random_bid([6,6],20)
        >>> q5 == 7 and  1 <=f4 <= 6
        True
        """
        def increase_quantity(current_quantity):
            """Helper function to increase quantity based on strategy."""
            if self.conservative_increase:
                return min(current_quantity + 1, total_dice)
            else:
                return random.randint(current_quantity + 1, total_dice)


        if current_bid is None:
            # First random bid: the lower limit is total_dice // 10 + 1 , and the upper limit is total_dice // 2
            quantity_starter = total_dice // 10 + 1
            quantity = random.randint(quantity_starter, max(quantity_starter, total_dice // 2))
            face_value = random.randint(1, 6)
            return [quantity, face_value]

        quantity, face_value = current_bid

        available_strategies = ["same_quantity", "same_face_value", "both_increase",
                                    "higher_quantity_smaller_face"]


        # If the face value is already 6, then we cannot bid for same_quantity and both_increase
        if face_value == 6:
            available_strategies.remove("same_quantity")
            available_strategies.remove("both_increase")
        # If the face value is 1, then we cannot bid for higher_quantity_smaller_face
        elif face_value == 1:
            available_strategies.remove("higher_quantity_smaller_face")

        # If the quantity is max, then we can only use same_quantity strategy
        if quantity == total_dice:
            available_strategies = ["same_quantity"] if face_value < 6 else []

        if not available_strategies:
            # If no strategies are available, return "liar"
            return "liar"

        bid_type = random.choice(available_strategies)

        if bid_type == "same_quantity":
            # Increase the face value but same quantity
            new_face_value = random.randint(face_value + 1, 6)
            return [quantity, new_face_value]
        elif bid_type == "same_face_value":
            # Increase the quantity but same face value
            new_quantity = increase_quantity(quantity)
            return [new_quantity, face_value]
        elif bid_type == "both_increase":
            # Increase both quantity and face value
            new_quantity = increase_quantity(quantity)
            new_face_value = random.randint(face_value + 1, 6)
            return [new_quantity, new_face_value]
        elif bid_type == "higher_quantity_smaller_face":
            # Increase the quantity but use smaller face value
            new_quantity = increase_quantity(quantity)
            new_face_value = random.randint(1, face_value - 1) if face_value > 1 else 1
            return [new_quantity, new_face_value]

    def preferred_faces(self, own_dice):
        """
        Order the face values of dice based on their frequency, treating '1's as wildcards.

        Each face value is ranked by its count in the player's dice, augmented by the count
        of wildcards ('1's), except for face value '1' itself.

        :param own_dice: A list of integers representing the player's dice (values from 1 to 6).
        :return: A dictionary of face values and their effective counts, sorted by count in descending order.

        >>> s = Strategy()
        >>> s.preferred_faces([1, 1, 2, 3, 3, 6])
        {3: 4, 2: 3, 6: 3, 1: 2, 4: 2, 5: 2}
        >>> s.preferred_faces([2, 4, 4, 5])
        {4: 2, 2: 1, 5: 1, 1: 0, 3: 0, 6: 0}

        """
        own_counter = Counter(own_dice)
        # Treat '1's as wildcards, adding them to each face's count
        wildcards = own_counter.get(1, 0)
        face_values = list(range(1, 7))
        face_preference = {}
        for face in face_values:
            face_preference[face] = own_counter.get(face, 0) + (wildcards if face != 1 else 0)

        # Sort face values based on their counts in descending order
        # sorted_faces = sorted(face_values, key=lambda x: face_preference[x], reverse=True)
        items = face_preference.items()
        sorted_items = sorted(items, key=lambda item: item[1], reverse=True)
        sorted_faces = {k: v for k, v in sorted_items}
        return sorted_faces


    def inform_bid(self, current_bid, total_dice, own_dice):
        """
        Generate a new bid based on the preferred faces and own dice. If one of the most perfered face is bigger than the
        face value of current_bid,use "same quantity but higher face value" stretegy, return[same quantity, perfered face value];
        Otherwise, use "higer quantity but smaller face value" strategy, return [increased quantity, prefered face value]

        :param current_bid: Current bid, [quantity, face_value].
        :param total_dice: Total number of dice in play.
        :param own_dice: Player's own dice.
        :return: A new bid [quantity, face_value] or "liar".

        >>> s1 = Strategy()
        >>> [q1,f1] = s1.inform_bid(None, 20, [1, 1, 2, 4, 4, 6])
        >>> 3<= q1 <= 10 and f1 == 4
        True
        >>> [q2,f2] = s1.inform_bid([5, 3], 20, [1, 1, 2, 3, 3, 6])
        >>> 6 <=q2 <=20 and f2 == 3
        True

        >>> s2 = Strategy(conservative_increase=True)
        >>> s2.inform_bid([5, 2], 20, [1, 2, 4, 4, 5])
        [5, 4]
        >>> s2.inform_bid([5, 3], 20, [1, 1, 2, 3, 3, 6])
        [6, 3]
        >>> s2.inform_bid([5, 2], 20, [1, 4, 4, 3, 3, 5])
        [5, 3]
        """

        def get_top_faces(preferred_faces):
            """
            Identify the top face values based on their counts.
            If multiple face values have the same count, return them sorted in ascending order.
            """
            max_count = max(preferred_faces.values())
            return sorted(face for face, count in preferred_faces.items() if count == max_count)

        # Get preferred faces sorted by quantity
        preferred_faces = self.preferred_faces(own_dice)
        top_faces = get_top_faces(preferred_faces)

        #Make first bid,using the face value with max frequency as the bidding face_value
        if current_bid is None:
            face_value = top_faces[0] # Use the smallest among the top face values
            quantity_starter = total_dice // 10 + 1
            quantity = random.randint(quantity_starter, max(quantity_starter, total_dice // 2))
            return [quantity, face_value]

        # If it is not the first bid, attempt to increase the bid based on preferred faces
        quantity, face_value = current_bid

        # Determine the next top face value to bid (if there are several top face value)
        next_face = None
        for face in top_faces:
            if face > face_value:
                next_face = face
                return [quantity, next_face]

        # All top faces are less than or equal to current face_value
        if quantity == total_dice:
            # No further bids possible, call "liar"
            return "liar"
        else:
            # Use the smallest face value from top_faces with increased quantity
            smallest_face = top_faces[0]
            if self.conservative_increase:
                new_quantity = min(quantity + 1, total_dice)
            else:
                new_quantity = random.randint(quantity + 1, total_dice)
            return [new_quantity, smallest_face]

        # for face in preferred_faces:
        #     if face > face_value:
        #         # Try to increase the face value with the same or slightly higher quantity
        #         new_quantity = quantity
        #         if new_quantity < total_dice:
        #             new_quantity = random.choice([new_quantity, new_quantity + 1])
        #         return [new_quantity, face]
        #
        # # If no preferred face is higher, try increasing the quantity with the same face
        # #it seems like need to modify to satisfy different current bid situation
        # if quantity < total_dice:
        #     return [quantity + 1, face_value]
        # else:
        #     return "liar"


    def new_bid(self, current_bid, total_dice, own_dice):
        """
        Determine the new bid based on the chosen strategy.

        :param current_bid: The current bid in the game.
        :param total_dice: Total number of dice in the game.
        :param own_dice: List of integers representing the player's own dice.
        :return: The new bid as a list.

        Strategy:
        - If `self.prefer_bid` is True, use the `inform_bid` method, considering own dice.
        - Otherwise, use the `random_bid` method for a random bid.
        """
        if self.prefer_bid:
            return self.inform_bid(current_bid, total_dice, own_dice)
        else:
            return self.random_bid(current_bid, total_dice)

    def liar_decide(self, current_bid, total_dice, own_dice):
        """
        When liar_threshold equals to "Random", choose bid or challenge randomly;
        when liar_threshold equals to "Normal", use half of the total dice as the threshold for deciding whether to challenge;
        When liar_threshold equals to "Opotimal",use own dice  + half of the remaining dice as the threshold for deciding whether to challenge.

        :param current_bid: Current bid, [quantity, face_value].
        :param total_dice: Total number of dice in play.
        :param own_dice: Player's own dice.
        :return: "liar" or "bid".


        >>> s1= Strategy(liar_threshold = "Random")
        >>> result = s1.liar_decide([5, 3], 20, [1, 3, 3, 6])
        >>> result in ["bid","liar"]
        True
        >>> s1= Strategy(liar_threshold = "Normal")
        >>> s1.liar_decide([5, 3], 20, [1, 3, 3, 6])
        'bid'
        >>> s1.liar_decide([11, 3], 20, [1, 3, 3, 6])
        'liar'
        >>> s2 = Strategy(liar_threshold = "Optimal")
        >>> s2.liar_decide([5, 3], 20, [1, 3, 3, 6])
        'bid'
        >>> s2.liar_decide([11, 3], 20, [1, 3, 3, 6])
        'bid'
        >>> s2.liar_decide([15, 6], 20, [1, 3, 3, 6])
        'liar'
        """
        bid_or_liar = "bid"
        if self.liar_threshold == "Random":
            bid_or_liar = random.choice(["bid", "liar"])
        elif self.liar_threshold == "Normal":
            quantity, face_value = current_bid
            threshold = total_dice // 2
            if quantity > threshold:
                bid_or_liar = "liar"
            else:
                bid_or_liar = "bid"
        elif self.liar_threshold == "Optimal":
            quantity, face_value = current_bid
            own_counter = Counter(own_dice)
            own_face_count = own_counter.get(face_value, 0)
            #Here is to recalculate the face value besides 1 because 1 is wild
            if face_value != 1:
                own_face_count += own_counter.get(1, 0)

            remaining_dice = total_dice - len(own_dice)
            # Use 50% of remaining dice to count the threshold
            expected_remaining_face_count = remaining_dice * 0.5
            threshold = own_face_count + expected_remaining_face_count
            if quantity > threshold:
                bid_or_liar = "liar"
            else:
                bid_or_liar = "bid"
        return bid_or_liar

    def make_action(self, current_bid, total_dice, own_dice):
        """
        Decide the next action (make a bid or call "liar") based on the current bid, total dice, and own dice.

        :param current_bid: The current bid, [quantity, face_value], or `None` for the first action.
        :param total_dice: Total number of dice in the game.
        :param own_dice: List of integers representing the player's own dice.
        :return: Either a new bid [quantity, face_value] or the string "liar".

        """
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


