"""
IS 597-PR Final Project

Different strategies to play the game Liar's Dice..

"""

import random
from collections import Counter

class Strategy:
    """Base class for player strategies."""
    def make_bid(self,current_bid,dice_counts,total_dice, own_dice):
        """

        :param current_bid: Current bid, [quantity,face_value] or None.
        :param dice_counts: A Counter object of all dice.
        :param total_dice: Current number of total dice.
        :param own_dice: Player's own dice.
        :return: A new bid [quantity,face_value] or "liar".
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def new_bid(self,current_bid,total_dice):
        """Random bid choice depends on current bid and number of dice.

        :param current_bid: Current bid, [quantity,face_value] or None.
        :param total_dice: Current number of total dice.
        :return: A new bid [quantity,face_value] or "liar".
        """
        if current_bid is None:
            #First random bid
            quantity = random.randint(2,max(2, total_dice // 2))
            face_value = random.randint(1,6)
            return [quantity,face_value]
        else:
            available_strategies = ["same_quantity", "same_face_value", "both_increase", "higher_quantity_smaller_face"]
            quantity, face_value = current_bid

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

class RandomStrategy(Strategy):
    """Strategy that randomly decides to bid or call 'liar'."""
    def make_bid(self,current_bid,dice_counts,total_dice, own_dice):
        bid_or_liar = random.choice(["bid","liar"])
        if bid_or_liar == "liar":
            return "liar"
        else:
            return self.new_bid(current_bid,total_dice)

class ThresholdStrategy(Strategy):
    def make_bid(self,current_bid,dice_counts,total_dice, own_dice):
        if current_bid is None:
            return self.new_bid(current_bid,total_dice)
        quantity, face_value = current_bid

        threshold = total_dice // 2

        if quantity > threshold:
            return "liar"
        else:
            return self.new_bid(current_bid,total_dice)

class OptimalStrategy(Strategy):
    """Player make bid base their own dice quantity and face value."""
    def make_bid(self,current_bid,dice_counts,total_dice, own_dice):
        if current_bid is None:
            return self.new_bid(current_bid,total_dice)
        quantity, face_value = current_bid

        own_counter = Counter(own_dice)
        own_face_count = own_counter.get(face_value,0)
        if face_value != 1:
            own_face_count += own_counter.get(1,0)

            # Estimate the probability that the current bid is correct
            estimated_total = own_face_count
            remaining_dice = total_dice - len(own_dice)

            # Average probability of each face (excluding wildcards if necessary)
            # Assuming each die has a 1/6 chance to be the desired face
            estimated_total += sum(random.choices([0, 1], weights=[5, 1], k=remaining_dice))

            # Simple heuristic: if estimated_total is likely, continue bidding; else, call 'liar'
            # Here can implement a more sophisticated probability check further
            # For simplicity, we'll use the expected value
            expected_count = (total_dice) * (2 / 6)  # Probability of a face including wildcards (if applicable)

            if quantity > expected_count + own_face_count:
                return "liar"
            else:
                # Make a more informed bid
                return self.inform_bid(current_bid, total_dice, own_dice)

    def inform_bid(self, current_bid, total_dice, own_dice):
        """
        Generate a new bid based on the preferred faces and own dice.

        :param current_bid: Current bid, [quantity, face_value].
        :param total_dice: Total number of dice in play.
        :param own_dice: Player's own dice.
        :return: A new bid [quantity, face_value] or "liar".
        """
        quantity, face_value = current_bid
        preferred_faces = self.preferred_faces(own_dice)

        # Attempt to increase the bid based on preferred faces
        for face in preferred_faces:
            if face > face_value:
                # Try to increase the face value with the same or slightly higher quantity
                new_quantity = quantity
                if new_quantity < total_dice:
                    new_quantity += 1
                return [new_quantity, face]

        # If no preferred face is higher, try increasing the quantity with the same face
        if quantity < total_dice:
            return [quantity + 1, face_value]
        else:
            return "liar"


    def preferred_faces(self, own_dice):
        """
        Base on the face value and quantity of player's own_dice.

        :param own_dice: Player's own dice.
        :return: A sorted list of face values based on preference.
        """
        own_counter = Counter(own_dice)
        # Treat '1's as wildcards, adding them to each face's count
        wildcards = own_counter.get(1, 0)
        face_values = list(range(2, 7))
        face_preference = {}
        for face in face_values:
            face_preference[face] = own_counter.get(face, 0) + wildcards

        # Sort face values based on their counts in descending order
        sorted_faces = sorted(face_values, key=lambda x: face_preference[x], reverse=True)
        return sorted_faces
