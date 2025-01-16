import { useState } from 'react';
import { ChessBoard } from './components/GameBoard/ChessBoard';
import GoBoard from './components/GameBoard/GoBoard.tsx';
import GameTypeSelect from './components/GameControls/GameTypeSelect';
import Leaderboard from './components/Leaderboard';
import './App.css';

function App() {
  const [gameType, setGameType] = useState('chess');
  const [leaderboard, setLeaderboard] = useState([]);

  return (
    <div className="App">
      <div className="main-content">
        <GameTypeSelect onSelect={setGameType} />
        {gameType === 'chess' ? (
          <ChessBoard setLeaderboard={setLeaderboard} />
        ) : (
          <GoBoard setLeaderboard={setLeaderboard} />
        )}
        <div className="leaderboard-section">
          <h2>All-Time Rankings</h2>
          <Leaderboard leaderboard={leaderboard} />
        </div>
      </div>
    </div>
  );
}

export default App;
