import { useState } from 'react';
import styles from './Tournament.module.css';

interface Match {
  id: string;
  player1: string;
  player2: string;
  status: 'pending' | 'active' | 'completed';
  winner?: string;
}

const AI_PLAYERS = [
  { id: 'gpt4', name: 'GPT-4' },
  { id: 'claude', name: 'CLAUDE' },
  { id: 'gemini', name: 'GEMINI' },
  { id: 'perplexity', name: 'PERPLEXITY' }
];

export const Tournament = ({ gameType }: { gameType: 'chess' | 'go' }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [matches, setMatches] = useState<Match[]>([]);

  const startTournament = async () => {
    try {
      setIsRunning(true);
      const response = await fetch('/api/tournament/start', {
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
      setMatches(data.matches);
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
      
      {isRunning && (
        <div className={styles.matches}>
          {matches.map(match => (
            <div key={match.id} className={styles.matchCard}>
              <div className={styles.players}>
                <span>{getPlayerName(match.player1)}</span>
                <span>vs</span>
                <span>{getPlayerName(match.player2)}</span>
              </div>
              <div className={styles.status}>
                {match.status === 'completed' ? (
                  <span className={styles.winner}>
                    Winner: {match.winner ? getPlayerName(match.winner) : 'Draw'}
                  </span>
                ) : (
                  <span className={styles.status}>
                    {match.status === 'active' ? 'In Progress' : 'Pending'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Tournament;
