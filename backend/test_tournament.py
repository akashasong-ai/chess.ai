import pytest
from tournament import Tournament, Match

def test_tournament_creation():
    players = ['gpt4', 'claude', 'gemini', 'perplexity']
    tournament = Tournament('chess', players)
    
    # Verify tournament initialization
    assert tournament.game_type == 'chess'
    assert tournament.players == players
    assert not tournament.completed
    assert tournament.current_round == 0
    
    # Start tournament and verify matches
    tournament.start()
    
    # Verify matches are created between all players
    assert len(tournament.matches) == len(players) * (len(players) - 1) // 2
    
    # Verify each player is matched against every other player
    player_pairs = set()
    for match in tournament.matches:
        pair = tuple(sorted([match.player1, match.player2]))
        player_pairs.add(pair)
    
    expected_pairs = set()
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            expected_pairs.add(tuple(sorted([players[i], players[j]])))
    
    assert player_pairs == expected_pairs

def test_tournament_status_updates():
    players = ['gpt4', 'claude']
    tournament = Tournament('chess', players)
    tournament.start()
    
    status = tournament.get_status()
    assert not status['completed']
    assert len(status['matches']) == 1  # One match between two players
    assert len(status['rankings']) == 2  # Two players in rankings
    
    # Simulate match completion
    match = tournament.matches[0]
    match.winner = match.player1
    tournament.update_rankings(match, 'win')
    
    # Check rankings directly from tournament object
    assert tournament.rankings[match.player1]['wins'] == 1  # Winner has one win
    assert tournament.rankings[match.player1]['score'] == 2  # Winner gets 2 points
    assert tournament.rankings[match.player2]['wins'] == 0  # Loser has no wins
    assert tournament.rankings[match.player2]['score'] == 0  # Loser gets 0 points
