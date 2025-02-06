import React, { useEffect, useState } from 'react';
import styles from './Leaderboard.module.css';
import type { LeaderboardEntry } from '../../types/leaderboard';
import { gameSocket } from '../../services/socket';

export interface LeaderboardProps {
  leaderboard: LeaderboardEntry[];
  gameType: 'chess' | 'go';
}

export const Leaderboard: React.FC<LeaderboardProps> = ({ leaderboard, gameType }) => {
  const [localLeaderboard, setLocalLeaderboard] = useState<LeaderboardEntry[]>(leaderboard);
  const [isLoading, setIsLoading] = useState(leaderboard.length === 0);

  useEffect(() => {
    setLocalLeaderboard(leaderboard);
    setIsLoading(leaderboard.length === 0);
  }, [leaderboard]);

  useEffect(() => {
    const unsubscribe = gameSocket.onLeaderboardUpdate((data) => {
      setLocalLeaderboard(data);
      setIsLoading(false);
    });

    if (leaderboard.length === 0) {
      gameSocket.emit('getLeaderboard');
    }

    return () => {
      unsubscribe();
    };
  }, [gameType]);

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
          {localLeaderboard.map((entry) => (
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

