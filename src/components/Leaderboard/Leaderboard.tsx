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
            <th>Rank</th>
            <th>Player</th>
            <th>Rating</th>
            <th>W/L/D</th>
            <th>Win Rate</th>
            <th>Streak</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry) => (
            <tr key={entry.id} className={styles.row}>
              <td>{entry.rank}</td>
              <td>{entry.username}</td>
              <td>{entry.rating}</td>
              <td>{`${entry.wins}/${entry.losses}/${entry.draws}`}</td>
              <td>{`${(entry.winRate * 100).toFixed(1)}%`}</td>
              <td>{entry.winStreak > 0 ? `+${entry.winStreak}` : entry.winStreak}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Leaderboard;

