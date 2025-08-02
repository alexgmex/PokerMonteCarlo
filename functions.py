import random


# Shuffle new deck
def reset_deck():
    suits = ["H", "D", "C", "S"]
    ranks = range(2, 15)
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck


# Evaluate Hand
def evaluate_hand(cards, ranks, suits):
    """
    Evaluates a poker hand and returns its ranking and high cards/kickers.
    
    Args:
        cards: List of tuples [(rank, suit), ...] where rank is 2-14 (Ace=14) and suit is 'C', 'D', 'H', 'S'
        ranks: Dict mapping rank to list of suits {rank: [suit, ...]}
        suits: Dict mapping suit to list of ranks {suit: [rank, ...]}
    
    Returns:
        Tuple (rank_value, high_cards) where:
        - rank_value: Integer from 1-10 representing hand rank (10=Royal Flush, 1=High Card)
        - high_cards: List of ranks [high_card, kicker1, kicker2, ...] for tiebreakers
    """
    # Check for flush (5+ cards of same suit)
    is_flush = any(len(suit_ranks) >= 5 for suit_ranks in suits.values())
    
    # Get sorted ranks for straight checking
    sorted_ranks = sorted(ranks.keys(), reverse=True)
    
    # Check for straight
    straight_high = 0
    for i in range(len(sorted_ranks) - 4):
        if sorted_ranks[i] - sorted_ranks[i + 4] == 4:
            straight_high = sorted_ranks[i]
            break
    # Check for Ace-low straight (A,2,3,4,5)
    if 14 in ranks and 2 in ranks and 3 in ranks and 4 in ranks and 5 in ranks:
        straight_high = 5
        
    # Check for flush and straight combinations
    if is_flush:
        for suit, suit_ranks in suits.items():
            if len(suit_ranks) >= 5:
                suit_ranks = sorted(suit_ranks, reverse=True)
                for i in range(len(suit_ranks) - 4):
                    if suit_ranks[i] - suit_ranks[i + 4] == 4:
                        return (9, [suit_ranks[i]])  # Straight Flush
                # Check Ace-low straight flush
                if 14 in suit_ranks and 2 in suit_ranks and 3 in suit_ranks and 4 in suit_ranks and 5 in suit_ranks:
                    return (9, [5])
                # Check Royal Flush
                if all(r in suit_ranks for r in [10, 11, 12, 13, 14]):
                    return (10, [14])
    
    # Check for quads
    for rank, rank_suits in ranks.items():
        if len(rank_suits) == 4:
            kicker = max(r for r in sorted_ranks if r != rank)
            return (8, [rank, kicker])
    
    # Check for full house
    trips = None
    pair = None
    for rank, rank_suits in ranks.items():
        if len(rank_suits) == 3 and (trips is None or rank > trips):
            trips = rank
        elif len(rank_suits) >= 2 and (pair is None or rank > pair):
            pair = rank
    if trips and pair:
        return (7, [trips, pair])
    
    # Check for flush
    if is_flush:
        for suit, suit_ranks in suits.items():
            if len(suit_ranks) >= 5:
                return (6, sorted(suit_ranks, reverse=True)[:5])
    
    # Check for straight
    if straight_high:
        return (5, [straight_high])
    
    # Check for three of a kind
    for rank, rank_suits in ranks.items():
        if len(rank_suits) == 3:
            kickers = sorted([r for r in sorted_ranks if r != rank], reverse=True)[:2]
            return (4, [rank] + kickers)
    
    # Check for two pair
    pairs = [rank for rank, rank_suits in ranks.items() if len(rank_suits) >= 2]
    if len(pairs) >= 2:
        pairs = sorted(pairs, reverse=True)[:2]
        kicker = max(r for r in sorted_ranks if r not in pairs)
        return (3, pairs + [kicker])
    
    # Check for one pair
    for rank, rank_suits in ranks.items():
        if len(rank_suits) == 2:
            kickers = sorted([r for r in sorted_ranks if r != rank], reverse=True)[:3]
            return (2, [rank] + kickers)
    
    # High card
    return (1, sorted_ranks[:5])


# Determine Winner
def determine_winner(table, players):
    # Set default winner as first player
    winners = [0]
    players[0].evaluate(table)

    for i in range(1, len(players)):
        # Update each players hand rank and kickers
        players[i].evaluate(table)

        # If a player has equal rank
        if players[i].show_rank == players[winners[0]].show_rank:
            # If they have equal kickers append them to winners list
            if players[i].strength == players[winners[0]].strength:
                winners.append(i)
            # If their kickers aren't different make the winner the first one to have a better card
            else:
                for j in range(len(players[i].strength)):
                    if players[i].strength[j] > players[winners[0]].strength[j]:
                        winners = [i]
                        break
                    if players[i].strength[j] < players[winners[0]].strength[j]:
                        break
        
        # If a player has a higher rank make them the winner
        if players[i].show_rank > players[winners[0]].show_rank:
            winners = [i]

    return winners


# Print Winner
def print_winner(players, winners):
    # Setup variables
    hand_rank = players[winners[0]].show_rank
    strength = players[winners[0]].strength
    prefix = ""
    main_statement = ""

    # Encode cards into names
    encoding = {2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}

    # Switch for hand rank
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
    
    # Add prefix for single winner or tie
    if len(winners) == 1:
        prefix = f"Player {winners[0]} Wins with "
    else:
        for i in range(len(winners)-2):
            prefix += f"{winners[i]}, "
        prefix = "Players " + prefix + f"{winners[len(winners)-2]} and {winners[len(winners)-1]} Tie with "

    # Print
    print(prefix + main_statement)


# Update Stats
def update_stats(players, winners, us_app, us_win, s_app, s_win):
    for i in range(len(players)):
        # Check suitedness
        suited = (players[i].hand[0][1] == players[i].hand[1][1])
        
        # Get indices
        r, c = max(players[i].hand[0][0], players[i].hand[1][0])-2, min(players[i].hand[0][0], players[i].hand[1][0])-2

        # Fill app matrices
        if suited:
            s_app[r][c] += 1
        else: 
            us_app[r][c] += 1
        
        # Fill win matrices
        if i in winners:
            if suited:
                s_win[r][c] += 1
            else: 
                us_win[r][c] += 1
    
    # Return matrices
    return us_app, us_win, s_app, s_win