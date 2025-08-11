import numpy as np
import matplotlib.pyplot as plt


# Shuffle new deck
suits = ["H", "D", "C", "S"]
ranks = list(range(2, 15))
deck_template = np.array([(rank, suit) for suit in suits for rank in ranks], dtype=[('rank', int), ('suit', 'U1')])

def reset_deck():
    deck = deck_template.copy()  # Copy the template
    np.random.shuffle(deck)     # NumPy shuffle
    return deck.tolist()


# Evaluate Hand
def evaluate_hand(cards, ranks, suits):
    # Convert ranks and suits to NumPy arrays for faster operations
    rank_counts = np.zeros(15, dtype=int)  # Index 2-14 for ranks
    suit_counts = {s: [] for s in 'HDCS'}
    
    for rank, suit in cards:
        rank_counts[rank] += 1
        suit_counts[suit].append(rank)
    
    # Check for flush
    flush_suit = next((s for s, r in suit_counts.items() if len(r) >= 5), None)
    is_flush = flush_suit is not None
    
    # Get sorted unique ranks
    sorted_ranks = np.sort(np.where(rank_counts > 0)[0])[::-1]
    
    # Check for straight
    straight_high = 0
    for i in range(len(sorted_ranks) - 4):
        if sorted_ranks[i] - sorted_ranks[i + 4] == 4:
            straight_high = sorted_ranks[i]
            break
    if 14 in sorted_ranks and 2 in sorted_ranks and 3 in sorted_ranks and 4 in sorted_ranks and 5 in sorted_ranks:
        straight_high = 5
    
    # Straight Flush and Royal Flush
    if is_flush and straight_high:
        suit_ranks = np.sort(suit_counts[flush_suit])[::-1]
        for i in range(len(suit_ranks) - 4):
            if suit_ranks[i] - suit_ranks[i + 4] == 4:
                return (9, [suit_ranks[i]])
        if straight_high == 5 and 14 in suit_ranks and 2 in suit_ranks and 3 in suit_ranks and 4 in suit_ranks and 5 in suit_ranks:
            return (9, [5])
        if all(r in suit_ranks for r in [10, 11, 12, 13, 14]):
            return (10, [14])
    
    # Quads
    quads = np.where(rank_counts == 4)[0]
    if quads.size > 0:
        rank = quads[0]
        kicker = max(r for r in sorted_ranks if r != rank)
        return (8, [rank, kicker])
    
    # Full House
    trips = np.where(rank_counts == 3)[0]
    pairs = np.where(rank_counts >= 2)[0]
    if trips.size > 0 and pairs.size > 1:
        trips_rank = max(trips)
        pair_rank = max(r for r in pairs if r != trips_rank)
        return (7, [trips_rank, pair_rank])
    
    # Flush
    if is_flush:
        return (6, np.sort(suit_counts[flush_suit])[::-1][:5].tolist())
    
    # Straight
    if straight_high:
        return (5, [straight_high])
    
    # Three of a Kind
    if trips.size > 0:
        rank = max(trips)
        kickers = [r for r in sorted_ranks if r != rank][:2]
        return (4, [rank] + kickers)
    
    # Two Pair
    if pairs.size >= 2:
        top_pairs = np.sort(pairs)[-2:][::-1]
        kicker = max(r for r in sorted_ranks if r not in top_pairs)
        return (3, top_pairs.tolist() + [kicker])
    
    # One Pair
    if pairs.size > 0:
        rank = max(pairs)
        kickers = [r for r in sorted_ranks if r != rank][:3]
        return (2, [rank] + kickers)
    
    # High Card
    return (1, sorted_ranks[:5].tolist())


# Determine Winner
def determine_winner(table, players):
    # Evaluate all hands first
    for player in players:
        player.evaluate(table)
    
    # Sort players by rank and strength
    ranked_players = sorted(enumerate(players), key=lambda x: (x[1].show_rank, x[1].strength), reverse=True)
    
    # Find winners (those with the same rank and strength as the top player)
    top_rank, top_strength = ranked_players[0][1].show_rank, ranked_players[0][1].strength
    winners = [i for i, p in ranked_players if p.show_rank == top_rank and p.strength == top_strength]
    
    return winners


# Print Winner
def print_winner(players, winners, sim, sims, print_interval=1000):
    # Only print on interval to reduce overhead
    if sim % print_interval != 0:
        return
    
    # Establish key variables
    hand_rank = players[winners[0]].show_rank
    strength = players[winners[0]].strength
    encoding = {2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
    main_statement = ""

    # Set prefix for draw or single win
    prefix = "Player " + str(winners[0]) + " Wins with " if len(winners) == 1 else "Players " + ", ".join(map(str, winners[:-1])) + f" and {winners[-1]} Tie with "

    # Switch statement for different win types
    match hand_rank:
        case 10:
            main_statement = "a Royal Flush!"
        case 9:
            main_statement = f"a Straight Flush, {encoding[strength[0]]} High"
        case 8:
            main_statement = f"Quad {encoding[strength[0]]}s, {encoding[strength[1]]} Kicker"
        case 7:
            main_statement = f"a Full House, {encoding[strength[0]]}s over {encoding[strength[1]]}s"
        case 6:
            main_statement = f"a Flush, {encoding[strength[0]]} High"
        case 5:
            main_statement = f"a Straight, {encoding[strength[0]]} High"
        case 4:
            main_statement = f"Trip {encoding[strength[0]]}s, {encoding[strength[1]]}-{encoding[strength[2]]} Kicker"
        case 3:
            main_statement = f"a Two Pair, {encoding[strength[0]]}s over {encoding[strength[1]]}s with {encoding[strength[2]]} Kicker"
        case 2:
            main_statement = f"a Pair of {encoding[strength[0]]}s, with {encoding[strength[1]]}-{encoding[strength[2]]}-{encoding[strength[3]]} Kicker"
        case 1:
            main_statement = f"a High Card of {encoding[strength[0]]}s, with {encoding[strength[1]]}-{encoding[strength[2]]}-{encoding[strength[3]]}-{encoding[strength[4]]} Kicker"
    
    # Print with percent complete
    print(f"{prefix}{main_statement} ({round(100*(sim/sims), 2)}%)")


# Update Stats
def update_stats(players, winners, us_app, us_win, s_app, s_win, wintype):
    # Update win type
    wintype[players[winners[0]].show_rank - 1] += 1

    # Update matrices
    for i, player in enumerate(players):
        r1, s1 = player.hand[0]
        r2, s2 = player.hand[1]
        r, c = max(r1, r2) - 2, min(r1, r2) - 2
        suited = s1 == s2
        
        if suited:
            s_app[r, c] += 1
            if i in winners:
                s_win[r, c] += 1
        else:
            us_app[r, c] += 1
            if i in winners:
                us_win[r, c] += 1
    
    # Return
    return us_app, us_win, s_app, s_win, wintype


# Plot Wintype
def plot_wintype(wintype, sims):
    # Define hand types for labels
    hand_types = [
        "High Card", "One Pair", "Two Pair", "Three of a Kind", 
        "Straight", "Flush", "Full House", "Four of a Kind", 
        "Straight Flush", "Royal Flush"
    ]
    
    # Calculate percentages
    percentages = (wintype / sims * 100)
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(hand_types, percentages, color='skyblue', edgecolor='black')
    
    # Customize the plot
    plt.title('Poker Hand Win Type Distribution', fontsize=14, pad=15)
    plt.xlabel('Hand Type', fontsize=12)
    plt.ylabel('Percentage of Wins (%)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%', ha='center', va='bottom')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Display the plot
    plt.show()


# Rank Hands
def rank_hands(us_app, us_win, s_app, s_win):
    # Establish variables
    winchance = {}
    encoding = {0:"2", 1:"3", 2:"4", 3:"5", 4:"6", 5:"7", 6:"8", 7:"9", 8:"10", 9:"J", 10:"Q", 11:"K", 12:"A"}

    for row in range(13):
        for col in range(row+1):
            winchance[f"{encoding[row]}-{encoding[col]} o"] = round(100*(us_win[row][col]/us_app[row][col]),2)
    
    for row in range(1,13):
        for col in range(row):
            winchance[f"{encoding[row]}-{encoding[col]} s"] = round(100*(s_win[row][col]/s_app[row][col]),2)
        
    for key, value in sorted(winchance.items(), key=lambda x: x[1], reverse=True):
        print(f"{key}: {value}%")