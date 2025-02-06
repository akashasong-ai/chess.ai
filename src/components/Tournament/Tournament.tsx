import { useState, useEffect } from 'react';
import styles from './Tournament.module.css';
import { gameSocket } from '../../services/socket';

interface TournamentStatus {
  currentMatch: number;
  totalMatches: number;
  matches: Array<{
    white: string;
    black: string;
    result: string | null;
  }>;
  currentGame: {
    white: string;
    black: string;
  };
}

const AI_PLAYERS = [
  { id: 'gpt4', name: 'GPT-4' },
  { id: 'claude', name: 'CLAUDE' },
  { id: 'gemini', name: 'GEMINI' },
  { id: 'perplexity', name: 'PERPLEXITY' }
];

export const Tournament = ({ gameType }: { gameType: 'chess' | 'go' }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState<TournamentStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = gameSocket.onTournamentUpdate((data) => {
      setStatus(data);
    });
    return () => {
      unsubscribe();
    };
  }, []);

  const startTournament = async () => {
    try {
      setIsRunning(true);
      const response = await fetch('http://localhost:5000/api/tournament/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gameType,
          participants: AI_PLAYERS.map(ai => ai.id)
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to start tournament');
      }
      
      const data = await response.json();
      if (data.success) {
        setStatus(data.tournamentStatus);
      } else {
        setError(data.error || 'Failed to start tournament');
      }
    } catch (error) {
      console.error('Tournament error:', error);
      setIsRunning(false);
    }
  };

  const getPlayerName = (id: string) => {
    return AI_PLAYERS.find(ai => ai.id === id)?.name || id;
  };

  return (
    <div className={styles.tournament}>
      <h2 className={styles.title}>AI Tournament</h2>
      <button 
        onClick={startTournament}
        disabled={isRunning}
        className={styles.startButton}
      >
        Start Round Robin Tournament
      </button>
      
      {error && <div className={styles.error}>{error}</div>}
      {isRunning && status && (
        <div className={styles.tournament}>
          <div className={styles.progress}>
            Match {status.currentMatch} of {status.totalMatches}
          </div>
          <div className={styles.currentMatch} data-testid="current-match">
            <h3>Current Match</h3>
            <div className={styles.players}>
              <span>{getPlayerName(status.currentGame.white)}</span>
              <span>vs</span>
              <span>{getPlayerName(status.currentGame.black)}</span>
            </div>
          </div>
          <div className={styles.matches}>
            {status.matches.map((match, index) => (
              <div key={index} className={styles.matchCard} data-testid="match-card">
                <div className={styles.players} data-testid="match-players">
                  <span>{getPlayerName(match.white)}</span>
                  <span>vs</span>
                  <span>{getPlayerName(match.black)}</span>
                </div>
                <div className={styles.status}>
                  {match.result ? (
                    <span className={styles.result}>{match.result}</span>
                  ) : (
                    <span className={styles.pending}>Pending</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Tournament;
