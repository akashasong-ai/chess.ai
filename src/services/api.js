// Your backend server URL (should be different from your frontend/Vite server)
const API_BASE_URL = 'http://127.0.0.1:5001/api';

class GameAPI {
  async startGame(whitePlayer, blackPlayer) {
    try {
      const response = await fetch(`${API_BASE_URL}/game/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ whitePlayer, blackPlayer })
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to start game:', error);
      throw error;
    }
  }

  async stopGame() {
    try {
      const response = await fetch(`${API_BASE_URL}/game/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to stop game:', error);
      throw error;
    }
  }

  async getGameState() {
    try {
      const response = await fetch(`${API_BASE_URL}/game/state`);
      return await response.json();
    } catch (error) {
      console.error('Failed to get game state:', error);
      throw error;
    }
  }

  async waitForAIMove() {
    try {
      const response = await fetch(`${API_BASE_URL}/game/move/wait`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to wait for AI move:', error);
      throw error;
    }
  }

  async getLeaderboard() {
    try {
      console.log('Fetching leaderboard from API...');
      const response = await fetch(`${API_BASE_URL}/leaderboard`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        cache: 'no-store'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Raw leaderboard data:', data);
      
      // Transform the data
      const transformedData = (Array.isArray(data) ? data : data.leaderboard || [])
        .map(entry => ({
          name: entry.name || entry.model || 'Unknown',
          wins: entry.wins || 0,
          draws: entry.draws || 0,
          losses: entry.losses || 0,
          winRate: this.getWinRate(entry.wins || 0, entry.losses || 0, entry.draws || 0)
        }));

      console.log('Transformed leaderboard data:', transformedData);
      return transformedData;
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      return [];
    }
  }

  getWinRate(wins, losses, draws) {
    const totalGames = wins + losses + draws;
    if (totalGames === 0) return 0;
    return Math.round((wins / totalGames) * 100);
  }
}

export const gameApi = new GameAPI(); 