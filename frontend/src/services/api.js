import io from 'socket.io-client'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'
const socket = io(API_URL)

export const api = {
  // Game management
  startGame: async (whiteAI = null, blackAI = null) => {
    const response = await fetch(`${API_URL}/api/game/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ whiteAI, blackAI })
    })
    return response.json()
  },

  getGameState: async () => {
    const response = await fetch(`${API_URL}/api/game/state`)
    return response.json()
  },

  makeMove: async (move) => {
    const response = await fetch(`${API_URL}/api/game/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ move })
    })
    return response.json()
  },

  requestAIMove: async () => {
    const response = await fetch(`${API_URL}/api/game/ai-move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    return response.json()
  },

  stopGame: async () => {
    const response = await fetch(`${API_URL}/api/game/stop`, {
      method: 'POST'
    })
    return response.json()
  },

  // Tournament management
  startTournament: async (participants = ['GPT-4', 'CLAUDE', 'GEMINI'], matches = 3) => {
    const response = await fetch(`${API_URL}/api/tournament/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ participants, matches })
    })
    return response.json()
  },

  getTournamentStatus: async () => {
    const response = await fetch(`${API_URL}/api/tournament/status`)
    return response.json()
  },

  stopTournament: async () => {
    const response = await fetch(`${API_URL}/api/tournament/stop`, {
      method: 'POST'
    })
    return response.json()
  },

  // WebSocket events
  onConnect: (callback) => {
    socket.on('connect', callback)
  },

  onDisconnect: (callback) => {
    socket.on('disconnect', callback)
  },

  onGameUpdate: (callback) => {
    socket.on('game_update', callback)
  },

  // Cleanup
  cleanup: () => {
    socket.off('connect')
    socket.off('disconnect')
    socket.off('game_update')
  }
}
