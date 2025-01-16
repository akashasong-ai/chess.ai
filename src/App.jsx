import React, { useState } from 'react';
import ChessBoard from './components/ChessBoard';
import Leaderboard from './components/Leaderboard';
import AISelector from './components/AISelector';
import './App.css';

function App() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [isTournament, setIsTournament] = useState(false);
  const [selectedWhiteAI, setSelectedWhiteAI] = useState(null);
  const [selectedBlackAI, setSelectedBlackAI] = useState(null);

  return (
    <div className="App">
      <div className="main-content">
        <div className="game-controls">
          <AISelector 
            position="White" 
            selectedAI={selectedWhiteAI} 
            onSelect={setSelectedWhiteAI}
          />
          <AISelector 
            position="Black" 
            selectedAI={selectedBlackAI} 
            onSelect={setSelectedBlackAI}
          />
        </div>
        <ChessBoard 
          setLeaderboard={setLeaderboard}
          setIsTournament={setIsTournament}
          selectedWhiteAI={selectedWhiteAI}
          selectedBlackAI={selectedBlackAI}
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
