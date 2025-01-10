export interface PlayerStats {
  id: string;
  username: string;
  rating: number;
  wins: number;
  losses: number;
  draws: number;
  winStreak: number;
}

export interface LeaderboardEntry extends PlayerStats {
  rank: number;
  gamesPlayed: number;
  winRate: number;
} 