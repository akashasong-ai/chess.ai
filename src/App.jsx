import { useState } from 'react';
import ChessBoard from './components/ChessBoard';
import Leaderboard from './components/Leaderboard';
import './App.css';

function App() {
  const [leaderboard, setLeaderboard] = useState([]);
  // Tournament mode state - will be used for tournament functionality
  // const [isTournament, setIsTournament] = useState(false);

  return (
    <div className="App">
      <div className="main-content">
        <ChessBoard 
          setLeaderboard={setLeaderboard}
          // Tournament functionality temporarily disabled
          // setIsTournament={setIsTournament}
        />
        <div className="leaderboard-section">
          <h2>All-Time Rankings</h2>
          <Leaderboard leaderboard={leaderboard} />
        </div>
      </div>
    </div>
  );
}

export default App;
