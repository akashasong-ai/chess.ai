export interface LeaderboardEntry {
  player: string;
  score: number;
  wins?: number;
  losses?: number;
  draws?: number;
  winRate?: number;
}   