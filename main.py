"""
IS 597-PR Final Project

Main script to run the Liar's Dice simulation with fixed strategies and compare different strategies.

"""
from strategies import RandomStrategy, ThresholdStrategy, OptimalStrategy
from simulation import simulate_game

def main():
    # Simulation parameters
    num_simulations = 1000  # Number of simulations per strategy
    num_dice = 5             # Number of dice per player at the start
    test_strategies = ["RandomStrategy", "Threshold", "Optimal"]  # Strategies to test for Player 0

    # Define available strategies
    strategy_classes = {
        "RandomStrategy": RandomStrategy,
        "Threshold": ThresholdStrategy,
        "Optimal": OptimalStrategy
    }

    for strategy_name in test_strategies:
        # Assign strategies to players
        # Player 0 uses the specified strategy
        # Players 1, 2, 3 use RandomStrategy
        strategies = {}
        for i in range(4):
            if i == 0:
                strategy_class = strategy_classes.get(strategy_name, RandomStrategy)
            else:
                strategy_class = RandomStrategy
            strategies[i] = strategy_class()

        # Initialize win counts for each player
        win_counts = {i: 0 for i in range(4)}

        print(f"\nStarting simulation for Player 0 Strategy: {strategy_name}")
        print(f"Players 1, 2, 3 Strategy: RandomStrategy")
        print(f"Running {num_simulations} simulations...\n")

        for sim in range(1, num_simulations + 1):
            winner = simulate_game(4, num_dice, strategies)
            if winner is not None:
                win_counts[winner] += 1
            else:
                # In case of a draw, you can choose to handle it as needed
                pass

            # Optionally, print progress every 100 simulations
            if sim % 100 == 0:
                print(f"Completed {sim} simulations...")

        # Calculate and display results
        print("\nSimulation Results:")
        for player_id in range(4):
            wins = win_counts[player_id]
            win_percentage = (wins / num_simulations) * 100
            if player_id == 0:
                print(f"Player {player_id} ({strategy_name}) Wins: {wins} times ({win_percentage:.2f}%)")
            else:
                print(f"Player {player_id} (RandomStrategy) Wins: {wins} times ({win_percentage:.2f}%)")


if __name__ == "__main__":
    main()