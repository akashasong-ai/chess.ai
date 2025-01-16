// This file is deprecated. Please use GameBoard/ChessBoard.tsx instead.
// Keeping this file for reference until the new implementation is fully tested.
/*
import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { gameApi } from '../services/api';
import './ChessBoard.css';

// Define piece mappings to ensure consistent characters
// Commented out until needed for future feature implementation
// const PIECES = {
//   // Black pieces (solid black)
//   'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
//   // White pieces (solid white)
//   'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟'
// };

// Update the initial board state with solid white pieces
const initialBoard = [
  ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],  // Black pieces
  ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],  // Black pawns
  [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
  [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
  [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
  [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
  ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],  // White pawns
  ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']   // White pieces (solid)
];

import { AI_PLAYERS } from '../config/ai';

// Helper function to get random AI player
const getRandomAI = (excludeAI = null) => {
  let availablePlayers = AI_PLAYERS;
  if (excludeAI) {
    availablePlayers = AI_PLAYERS.filter(ai => ai !== excludeAI);
  }
  const randomIndex = Math.floor(Math.random() * availablePlayers.length);
  return availablePlayers[randomIndex];
};

// Update piece mapping with color styles
const PIECE_MAPPING = {
  // Black pieces (lowercase) - explicitly colored black
  'p': <span style={{color: 'black'}}>♟</span>,
  'r': <span style={{color: 'black'}}>♜</span>,
  'n': <span style={{color: 'black'}}>♞</span>,
  'b': <span style={{color: 'black'}}>♝</span>,
  'q': <span style={{color: 'black'}}>♛</span>,
  'k': <span style={{color: 'black'}}>♚</span>,
  // White pieces (uppercase) - explicitly colored white
  'P': <span style={{color: 'white'}}>♙</span>,
  'R': <span style={{color: 'white'}}>♖</span>,
  'N': <span style={{color: 'white'}}>♘</span>,
  'B': <span style={{color: 'white'}}>♗</span>,
  'Q': <span style={{color: 'white'}}>♕</span>,
  'K': <span style={{color: 'white'}}>♔</span>
};

// Add constants for polling intervals
const REGULAR_POLL_INTERVAL = 300; // 0.3 seconds for moves
// const STATUS_UPDATE_INTERVAL = 150; // 0.15 seconds for status messages - will be used for future status updates
const TOURNAMENT_POLL_INTERVAL = 1;

// Add helper function to check if game should end - commented out until game end validation is implemented
// const isGameOver = (board, gameState) => {
//   // Only check for game over if explicitly stated in gameState
//   if (gameState && gameState.checkmate) return true;
//   if (gameState && gameState.stalemate) return true;
//   
//   // Count kings as backup validation
//   let whiteKing = false;
//   let blackKing = false;
//   
//   board.forEach(row => {
//     row.forEach(piece => {
//       if (piece === '♔') whiteKing = true;
//       if (piece === '♚') blackKing = true;
//     });
//   });
//
//   // Only return true if a king is actually missing
//   return (!whiteKing || !blackKing);
// };

// Add piece validation constants
const VALID_PIECES = {
  white: ['♔', '♕', '♖', '♗', '♘', '♙'],
  black: ['♚', '♛', '♜', '♝', '♞', '♟']
};

// Add board validation function - commented out until board validation is implemented
// const isValidBoard = (board) => {
//   // Check board dimensions
//   if (!board || board.length !== 8 || !board.every(row => row.length === 8)) {
//     return false;
//   }
//
//   let whiteKingCount = 0;
//   let blackKingCount = 0;
//   let whitePawnCount = 0;
//   let blackPawnCount = 0;
//
//   // Check each piece
//   for (let row = 0; row < 8; row++) {
//     for (let col = 0; col < 8; col++) {
//       const piece = board[row][col];
//       
//       // Skip empty squares
//       if (piece === ' ') continue;
//
//       // Validate piece type
//       if (!VALID_PIECES.white.includes(piece) && !VALID_PIECES.black.includes(piece)) {
//         console.error('Invalid piece detected:', piece);
//         return false;
//       }
//
//       // Count kings and pawns
//       if (piece === '♔') whiteKingCount++;
//       if (piece === '♚') blackKingCount++;
//       if (piece === '♙') whitePawnCount++;
//       if (piece === '♟') blackPawnCount++;
//     }
//   }
//
//   // Validate piece counts
//   if (whiteKingCount !== 1 || blackKingCount !== 1) {
//     console.error('Invalid number of kings');
//     return false;
//   }
//   if (whitePawnCount > 8 || blackPawnCount > 8) {
//     console.error('Too many pawns');
//     return false;
//   }
//
//   return true;
// };

// Expanded set of thinking messages with more variety and personality
const THINKING_MESSAGES = [
  "Analyzing tournament openings... 🎯",
  "Calculating 17 moves ahead... 🧮",
  "Consulting grandmaster databases... 📚",
  "Evaluating pawn structure... 👥",
  "Simulating opponent responses... 🤔",
  "Reviewing similar positions... 🔄",
  "Checking endgame theory... 🎬",
  "Planning tactical combinations... ⚡",
  "Studying opponent's patterns... 🔍",
  "Computing material balance... ⚖️",
  "Analyzing center control... 🎯",
  "Considering piece coordination... 🤝",
  "Evaluating king safety... 👑",
  "Searching for forced sequences... 🔎",
  "Reviewing historical matches... 📜",
  "Calculating positional advantages... 📊",
  "Analyzing piece mobility... 🔄",
  "Consulting opening theory... 📖",
  "Evaluating attacking chances... ⚔️",
  "Checking defensive resources... 🛡️",
  "Processing strategic plans... 🧩",
  "Analyzing space advantage... 🌟",
  "Calculating piece exchanges... 💫",
  "Evaluating tempo gains... ⏱️",
  "Considering prophylactic moves... 🎪"
];

// Add the status message helper function - commented out until status message formatting is implemented
// const getStatusMessage = (gameState, lastMove, includeThinking = true) => {
//   if (!gameState) return 'Game not started';
//   
//   const currentAI = gameState.currentPlayer === 'white' ? gameState.whiteAI : gameState.blackAI;
//   
//   if (gameState.status === 'finished') {
//     if (gameState.winner) {
//       return `🎉 Game Over - ${gameState.winner} wins in spectacular fashion! 🏆`;
//     }
//     return '🤝 Game Over - A hard-fought draw! ⭐';
//   }
//
//   // Base status without thinking message
//   let baseStatus = `${currentAI}'s turn (${gameState.currentPlayer})`;
//   
//   // Add last move if available
//   if (lastMove) {
//     const previousAI = gameState.currentPlayer === 'white' ? 
//       gameState.blackAI : gameState.whiteAI;
//     baseStatus += ` | Last move by ${previousAI}: ${lastMove}`;
//   }
//
//   // Add check status if in check
//   if (gameState.isCheck) {
//     baseStatus += ' | ⚠️ CHECK! ⚠️';
//   }
//
//   // Add thinking message if requested
//   if (includeThinking) {
//     const randomMsg = THINKING_MESSAGES[Math.floor(Math.random() * THINKING_MESSAGES.length)];
//     baseStatus += ` | ${randomMsg}`;
//   }
//
//   return baseStatus;
// };

const ChessBoard = () => {
  // State declarations
  const [board, setBoard] = useState(initialBoard);
  const [selectedWhiteAI, setSelectedWhiteAI] = useState(() => {
    const randomAI = getRandomAI();
    return randomAI;
  });
  const [selectedBlackAI, setSelectedBlackAI] = useState(() => {
    // Get a random AI that's different from white's AI
    const randomAI = getRandomAI(selectedWhiteAI);
    return randomAI;
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [isTournament, setIsTournament] = useState(false);
  const [error, setError] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  // Tournament and status tracking state - commented out until these features are implemented
  // const [shouldPollLeaderboard, setShouldPollLeaderboard] = useState(false);
  const [gameStatus, setGameStatus] = useState('Select AI players and click Start Game to start');
  // const [lastValidBoard, setLastValidBoard] = useState(initialBoard);
  // const [statusIndex, setStatusIndex] = useState(0);
  // const [currentPlayer, setCurrentPlayer] = useState('white');
  // const [isTournamentActive, setIsTournamentActive] = useState(false);
  // const [tournamentRound, setTournamentRound] = useState(0);
  // const [tournamentMatches, setTournamentMatches] = useState([]);
  const [thinkingMessage, setThinkingMessage] = useState('');
  const [tournamentLeaderboard, setTournamentLeaderboard] = useState([]);

  // Game control functions
  const startGame = async () => {
    if (selectedWhiteAI === selectedBlackAI) {
      const errorMsg = 'An AI cannot play against itself';
      setError(errorMsg);
      setGameStatus(`Error: ${errorMsg}`);
      return;
    }
    
    try {
      setError(null);
      setCurrentPlayer('white');
      setGameStatus('Starting new game...');
      console.log('Starting new game...');
      const response = await gameApi.startGame(selectedWhiteAI, selectedBlackAI);
      if (response.success) {
        setIsPlaying(true);
        setBoard(initialBoard);
        setLastValidBoard(initialBoard);
        setGameStatus(`Game started: ${selectedWhiteAI} vs ${selectedBlackAI}`);
        console.log('Game started successfully');
      } else {
        const errorMsg = response.error || 'Failed to start game';
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Failed to start game:', error);
      setError(error.message);
      setGameStatus(`Error: ${error.message}`);
    }
  };

  const stopGame = async () => {
    try {
      await gameApi.stopGame();
      setIsPlaying(false);
      setBoard(Array(8).fill(Array(8).fill(' ')));
    } catch (error) {
      console.error('Failed to stop game:', error);
      setError('Failed to stop game');
    }
  };

  const startTournament = async () => {
    try {
      setIsTournament(true);
      setIsPlaying(true);
      await gameApi.startTournament();
      pollTournament();
    } catch (error) {
      console.error('Tournament start error:', error);
      setGameStatus('Tournament failed to start');
    }
  };

  const pollTournament = async () => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await gameApi.getTournamentStatus();
        const tournamentBoard = await gameApi.getTournamentLeaderboard();
        setTournamentLeaderboard(tournamentBoard);

        if (status.completed) {
          clearInterval(pollInterval);
          setIsTournament(false);
          setIsPlaying(false);
          // Update main leaderboard with final tournament results
          const finalLeaderboard = await gameApi.getLeaderboard();
          setLeaderboard(finalLeaderboard);
          setGameStatus('Tournament completed!');
        } else {
          setGameStatus(`Tournament in progress: Game ${status.currentGame} of ${status.totalGames}`);
        }
      } catch (error) {
        console.error('Tournament polling error:', error);
      }
    }, 1000);
  };

  const handleTournamentGameComplete = async (winner) => {
    try {
      // Update current match as completed
      const currentMatchIndex = tournamentMatches.findIndex(match => !match.completed);
      const updatedMatches = [...tournamentMatches];
      updatedMatches[currentMatchIndex] = {
        ...updatedMatches[currentMatchIndex],
        completed: true,
        winner: winner
      };
      setTournamentMatches(updatedMatches);

      // Check if there are more matches
      const nextMatchIndex = currentMatchIndex + 1;
      if (nextMatchIndex < tournamentMatches.length) {
        // Start next match
        const nextMatch = tournamentMatches[nextMatchIndex];
        setSelectedWhiteAI(nextMatch.white);
        setSelectedBlackAI(nextMatch.black);
        setTournamentRound(tournamentRound + 1);
        
        const response = await gameApi.startGame(nextMatch.white, nextMatch.black);
        if (response.success) {
          setIsPlaying(true);
          setBoard(initialBoard);
          setGameStatus(`Tournament Round ${tournamentRound + 1}: ${nextMatch.white} vs ${nextMatch.black}`);
        }
      } else {
        // Tournament complete
        setIsTournamentActive(false);
        setIsTournament(false);
        setGameStatus('Tournament Complete! Check the leaderboard for results 🏆');
        
        // Update final leaderboard
        const leaderboardResponse = await gameApi.getLeaderboard();
        if (leaderboardResponse && leaderboardResponse.leaderboard) {
          setLeaderboard(leaderboardResponse.leaderboard);
        }
      }
    } catch (error) {
      console.error('Failed to handle tournament game completion:', error);
      setError(error.message);
    }
  };

  // Polling effect
  useEffect(() => {
    let pollInterval;
    let isUpdating = false;

    const resetGame = async () => {
      if (pollInterval) clearInterval(pollInterval);
      
      const initialBoard = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
      ];
      setBoard(initialBoard.map(row => row.map(piece => renderPiece(piece))));
      
      try {
        console.log('Game ended, updating leaderboards...');
        
        // Stop the current game
        await gameApi.stopGame();
        
        // Force a fresh leaderboard fetch
        const newLeaderboard = await gameApi.getLeaderboard();
        console.log('New leaderboard data:', newLeaderboard);
        
        if (Array.isArray(newLeaderboard)) {
          console.log('Updating leaderboard state...');
          setLeaderboard(newLeaderboard);
        } else {
          console.error('Invalid leaderboard format:', newLeaderboard);
        }
        
        setIsPlaying(false);
      } catch (error) {
        console.error('Error in resetGame:', error);
      }
    };

    const pollGame = async () => {
      if (isUpdating) return;
      isUpdating = true;
      
      try {
        const response = await gameApi.getGameState();
        
        if (response?.gameState) {
          if (response.gameState.status === 'finished') {
            const finalMessage = response.gameState.winner ? 
              `🎉 Game Over - ${response.gameState.winner} wins! 🏆` :
              '🤝 Game Over - Draw! ⭐';
            setGameStatus(finalMessage);
            await resetGame();
            return;
          }

          const currentAI = response.gameState.currentPlayer === 'white' ? 
            response.gameState.whiteAI : response.gameState.blackAI;
          
          let baseStatus = `${currentAI}'s turn (${response.gameState.currentPlayer})`;
          if (response.lastMove) {
            const previousAI = response.gameState.currentPlayer === 'white' ? 
              response.gameState.blackAI : response.gameState.whiteAI;
            baseStatus += ` | Last move by ${previousAI}: ${response.lastMove}`;
          }

          const randomMsg = THINKING_MESSAGES[Math.floor(Math.random() * THINKING_MESSAGES.length)];
          setGameStatus(`${baseStatus} | ${randomMsg}`);

          // Immediately request next move
          const moveResponse = await gameApi.waitForAIMove();
          if (moveResponse?.board && Array.isArray(moveResponse.board) && moveResponse.board.length === 8) {
            setBoard(moveResponse.board.map(row => row.map(piece => renderPiece(piece))));
          }
        }
      } catch (error) {
        console.error('Poll error:', error);
        setGameStatus(`⚠️ Error: ${error.message}`);
      } finally {
        isUpdating = false;
      }
    };

    if (isPlaying) {
      pollGame();
      pollInterval = setInterval(pollGame, 50); // Reduced to 50ms for faster updates
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
        console.log('Polling stopped');
      }
    };
  }, [isPlaying, selectedWhiteAI, selectedBlackAI]);

  // Add effect to update status when thinking message changes
  useEffect(() => {
    if (thinkingMessage && gameStatus) {
      const baseStatus = gameStatus.split('|')[0].trim();
      setGameStatus(`${baseStatus} | ${thinkingMessage}`);
    }
  }, [thinkingMessage]);

  // Add this effect for leaderboard polling
  useEffect(() => {
    let leaderboardInterval;
    
    const fetchLeaderboard = async () => {
      try {
        const data = await gameApi.getLeaderboard();
        setLeaderboard(data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      }
    };
    
    if (shouldPollLeaderboard) {
      fetchLeaderboard();
      leaderboardInterval = setInterval(fetchLeaderboard, 5000);
    }
    
    return () => {
      if (leaderboardInterval) {
        clearInterval(leaderboardInterval);
      }
    };
  }, [shouldPollLeaderboard]);

  // Update the player selection handler
  const handlePlayerSelection = (color, value) => {
    if (color === 'white') {
      if (value === selectedBlackAI) {
        // If selected white AI matches black AI, change black AI
        const newBlackAI = getRandomAI(value);
        setSelectedBlackAI(newBlackAI);
      }
      setSelectedWhiteAI(value);
    } else {
      if (value === selectedWhiteAI) {
        // If selected black AI matches white AI, change white AI
        const newWhiteAI = getRandomAI(value);
        setSelectedWhiteAI(newWhiteAI);
      }
      setSelectedBlackAI(value);
    }
    setError(null);
  };

  // Update the piece style function
  const getPieceStyle = (piece, rowIndex) => {
    if (rowIndex >= 6) {
      return { 
        color: '#FFFFFF',
        fontSize: '55px',
        fontWeight: 'bold'
      };
    }
    return { 
      color: '#000000',
      fontSize: '55px',
      fontWeight: 'bold'
    };
  };

  // Add a stop game handler
  const handleStopGame = () => {
    setIsPlaying(false);
    setGameStatus('Game stopped');
    // Save the current board state
    setLastValidBoard(board);
    
    // Clear any ongoing game state
    try {
      gameApi.stopGame();  // Make sure this endpoint exists in your API
    } catch (error) {
      console.error('Failed to stop game:', error);
    }
  };

  // Helper function to count differences between boards - commented out until board comparison is needed
  // const countBoardDifferences = (oldBoard, newBoard) => {
  //   let differences = 0;
  //   for (let i = 0; i < 8; i++) {
  //     for (let j = 0; j < 8; j++) {
  //       if (oldBoard[i][j] !== newBoard[i][j]) {
  //         differences++;
  //       }
  //     }
  //   }
  //   return differences;
  // };

  // Disable board validation for initial setup
  useEffect(() => {
    if (isPlaying) {
      const pollGame = async () => {
        try {
          const response = await gameApi.getGameState();
          if (response && response.board) {
            // Skip validation for the first board state
            const newBoard = response.board.map(row =>
              row.map(piece => {
                if (piece === ' ' || piece === '') return ' ';
                return PIECE_MAPPING[piece] || piece;
              })
            );
            setBoard(newBoard);
            // setLastValidBoard(newBoard); // Commented out until board state tracking is implemented
          }
          // ... rest of polling logic
        } catch (error) {
          console.error('Failed to poll game state:', error);
        }
      };

      pollGame();
      const interval = isTournament ? TOURNAMENT_POLL_INTERVAL : REGULAR_POLL_INTERVAL;
      const pollInterval = setInterval(pollGame, interval);

      return () => clearInterval(pollInterval);
    }
  }, [isPlaying, isTournament]);

  // Update the board rendering to preserve piece colors
  const renderPiece = (piece) => {
    if (piece === ' ' || piece === '') return ' ';
    return PIECE_MAPPING[piece] || piece;
  };

  // Add this useEffect to fetch leaderboard on component mount
  useEffect(() => {
    const fetchInitialLeaderboard = async () => {
      try {
        const initialLeaderboard = await gameApi.getLeaderboard();
        console.log('Initial leaderboard:', initialLeaderboard);
        if (Array.isArray(initialLeaderboard)) {
          setLeaderboard(initialLeaderboard);
        }
      } catch (error) {
        console.error('Failed to fetch initial leaderboard:', error);
      }
    };

    fetchInitialLeaderboard();
  }, []); // Empty dependency array for mount only

  // Component render
  return (
    <div className="chess-container">
      <div className="leaderboard">
        <table>
          <thead>
            <tr>
              <th>RANK</th>
              <th>AI MODEL</th>
              <th>WINS</th>
              <th>LOSSES</th>
              <th>WIN RATE</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, index) => (
              <tr key={`${entry.model}-${index}`}>
                <td>{index + 1}</td>
                <td>{entry.model}</td>
                <td>{entry.wins}</td>
                <td>{entry.losses}</td>
                <td>{entry.winRate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="player-selection">
        <div className="player-box">
          <h3>White Player:</h3>
          <select 
            value={selectedWhiteAI} 
            onChange={(e) => handlePlayerSelection('white', e.target.value)}
          >
            <option value="GPT-4">GPT-4</option>
            <option value="Claude 2">Claude 2</option>
            <option value="Gemini Pro">Gemini Pro</option>
          </select>
          <div className="player-description">
            {selectedWhiteAI === 'GPT-4' && 'OpenAI GPT-4'}
            {selectedWhiteAI === 'Claude 2' && 'Anthropic Claude 2'}
            {selectedWhiteAI === 'Gemini Pro' && 'Google Gemini Pro'}
          </div>
        </div>

        <div className="player-box">
          <h3>Black Player:</h3>
          <select 
            value={selectedBlackAI} 
            onChange={(e) => handlePlayerSelection('black', e.target.value)}
          >
            <option value="GPT-4">GPT-4</option>
            <option value="Claude 2">Claude 2</option>
            <option value="Gemini Pro">Gemini Pro</option>
          </select>
          <div className="player-description">
            {selectedBlackAI === 'GPT-4' && 'OpenAI GPT-4'}
            {selectedBlackAI === 'Claude 2' && 'Anthropic Claude 2'}
            {selectedBlackAI === 'Gemini Pro' && 'Google Gemini Pro'}
          </div>
        </div>
      </div>

      <div className="button-container">
        <button 
          onClick={startGame}
          className="start-button"
          disabled={isPlaying}
        >
          Start Game
        </button>

        <button 
          onClick={handleStopGame}
          className="stop-button"
          disabled={!isPlaying}
        >
          Stop Game
        </button>

        <button 
          onClick={startTournament}
          className="tournament-button"
          disabled={isPlaying}
        >
          Start Tournament
        </button>
      </div>

      <div className="game-status">
        {gameStatus}
      </div>

      <div className="chess-board">
        {board.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row">
            {row.map((piece, colIndex) => (
              <div 
                key={`${rowIndex}-${colIndex}`} 
                className={`square ${(rowIndex + colIndex) % 2 === 0 ? 'light' : 'dark'}`}
              >
                {piece !== ' ' && (
                  <div 
                    className="piece"
                    style={getPieceStyle(piece, rowIndex)}
                  >
                    {renderPiece(piece)}
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
};

ChessBoard.propTypes = {
  setLeaderboard: PropTypes.func.isRequired
};

// export default ChessBoard;
*/                     