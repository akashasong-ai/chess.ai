import React, { useEffect, useState } from 'react';
import styles from './Leaderboard.module.css';
import type { LeaderboardEntry } from '../../types/leaderboard';
import { gameSocket } from '../../services/socket';

export const Leaderboard: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = gameSocket.onLeaderboardUpdate((data) => {
      setLeaderboard(data);
      setIsLoading(false);
    });

    // Initial fetch
    gameSocket.emit('getLeaderboard');

    return () => {
      unsubscribe();
      gameSocket.emit('leaveGame');
    };
  }, []);

  if (isLoading) {
    return <div className={styles.loading}>Loading leaderboard...</div>;
  }

  return (
    <div className={styles.leaderboard}>
      <h2>Leaderboard</h2>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Player</th>
            <th>Score</th>
            <th>Win Rate</th>
            <th>Wins</th>
            <th>Losses</th>
            <th>Draws</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry) => (
            <tr key={entry.player} className={styles.row}>
              <td>{entry.player}</td>
              <td>{entry.score}</td>
              <td>{entry.winRate ? `${(entry.winRate * 100).toFixed(1)}%` : 'N/A'}</td>
              <td>{entry.wins || 0}</td>
              <td>{entry.losses || 0}</td>
              <td>{entry.draws || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Leaderboard;

