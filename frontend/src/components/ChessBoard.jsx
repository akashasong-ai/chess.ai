import { Box, Grid, GridItem, Text, VStack, HStack, Button } from '@chakra-ui/react'
import { useToast } from '@chakra-ui/toast'
import { useState, useEffect } from 'react'
import { Chess } from 'chess.js'
import { api } from '../services/api'
import PropTypes from 'prop-types'

function ChessBoard({ mode, whiteAI, blackAI }) {
  const [game, setGame] = useState(new Chess())
  const [selectedSquare, setSelectedSquare] = useState(null)
  const [gameState, setGameState] = useState(null)
  const [isPlayerTurn, setIsPlayerTurn] = useState(true)
  const toast = useToast()

  useEffect(() => {
    const initGame = async () => {
      try {
        await api.startGame(whiteAI, blackAI)
        const state = await api.getGameState()
        setGameState(state)
        setGame(new Chess(state.gameState.fen))
        setIsPlayerTurn(state.gameState.currentPlayer === 'white' && !whiteAI)
      } catch (error) {
        toast({
          title: 'Error starting game',
          description: error.message,
          status: 'error',
          duration: 3000,
          isClosable: true,
        })
      }
    }

    initGame()
    setupWebSocket()

    return () => {
      api.cleanup()
    }
  }, [mode, toast])

  useEffect(() => {
    const handleAIMove = async () => {
      if (gameState && !isPlayerTurn && !game.isGameOver()) {
        try {
          const result = await api.requestAIMove()
          if (result.success) {
            setGame(new Chess(result.gameState.fen))
            setGameState(result)
            setIsPlayerTurn(!result.gameState.whiteAI || 
              (result.gameState.currentPlayer === 'white' && !result.gameState.whiteAI) ||
              (result.gameState.currentPlayer === 'black' && !result.gameState.blackAI))
          }
        } catch (error) {
          toast({
            title: 'Error making AI move',
            description: error.message,
            status: 'error',
            duration: 3000,
            isClosable: true,
          })
        }
      }
    }

    handleAIMove()
  }, [gameState, isPlayerTurn, game, toast])

  const setupWebSocket = () => {
    api.onConnect(() => {
      console.log('Connected to game server')
    })

    api.onGameUpdate((update) => {
      setGame(new Chess(update.fen))
      setGameState(update)
      setIsPlayerTurn(update.currentPlayer === 'white' && !update.whiteAI)
    })

    api.onDisconnect(() => {
      console.log('Disconnected from game server')
    })
  }
  
  const renderSquare = (i, j) => {
    const isLight = (i + j) % 2 === 0
    const square = String.fromCharCode(97 + j) + (8 - i)
    const piece = game.get(square)
    
    return (
      <GridItem
        key={square}
        w="60px"
        h="60px"
        bg={isLight ? 'board.light' : 'board.dark'}
        display="flex"
        alignItems="center"
        justifyContent="center"
        cursor="pointer"
        onClick={() => handleSquareClick(square)}
        position="relative"
        _hover={{ bg: selectedSquare === square ? 'blue.400' : (isLight ? 'board.light' : 'board.dark') }}
        backgroundColor={selectedSquare === square ? 'blue.400' : (isLight ? 'board.light' : 'board.dark')}
      >
        {piece && (
          <Text fontSize="4xl">
            {getPieceSymbol(piece)}
          </Text>
        )}
      </GridItem>
    )
  }

  const getPieceSymbol = (piece) => {
    const symbols = {
      'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
      'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔'
    }
    return symbols[piece.type]
  }

  const handleSquareClick = async (square) => {
    if (!isPlayerTurn) return

    if (selectedSquare === null) {
      // First click - select the piece
      const piece = game.get(square)
      if (piece && piece.color === (game.turn() === 'w')) {
        setSelectedSquare(square)
      }
    } else {
      // Second click - attempt to move
      try {
        const move = {
          from: selectedSquare,
          to: square,
          promotion: 'q' // Always promote to queen for simplicity
        }

        // Validate move locally first
        const newGame = new Chess(game.fen())
        newGame.move(move)

        // If local validation passes, send to server
        const result = await api.makeMove(move.from + move.to)
        if (result.success) {
          setGame(new Chess(result.gameState.fen))
          setGameState(result)
          setIsPlayerTurn(false)
        }
        setSelectedSquare(null)
      } catch (e) {
        toast({
          title: 'Invalid move',
          description: e.message,
          status: 'warning',
          duration: 2000,
          isClosable: true,
        })
        setSelectedSquare(null)
      }
    }
  }

  return (
    <Box>
      <Grid
        templateColumns="repeat(8, 60px)"
        gap={0}
        border="2px"
        borderColor="gray.300"
        width="fit-content"
      >
        {Array(8).fill().map((_, i) =>
          Array(8).fill().map((_, j) => renderSquare(i, j))
        )}
      </Grid>
      
      <VStack mt={4} align="stretch" spacing={4}>
        <HStack justify="space-between" spacing={3}>
          <Button
            variant="game"
            isDisabled={!gameState}
            onClick={() => api.startGame(whiteAI, blackAI)}
          >
            Start Game
          </Button>
          <Button
            variant="game"
            isDisabled={!gameState}
            onClick={() => api.stopGame()}
          >
            Stop Game
          </Button>
          <Button
            variant="game"
            colorScheme="blue"
            onClick={async () => {
              try {
                await api.startGame(whiteAI, blackAI)
                const newState = await api.getGameState()
                setGame(new Chess(newState.gameState.fen))
                setGameState(newState)
                setSelectedSquare(null)
                setIsPlayerTurn(newState.gameState.currentPlayer === 'white' && !whiteAI)
              } catch (error) {
                toast({
                  title: 'Error starting new game',
                  description: error.message,
                  status: 'error',
                  duration: 3000,
                  isClosable: true,
                })
              }
            }}
          >
            New Game
          </Button>
          <Button
            variant="game"
            colorScheme="purple"
            onClick={() => api.startTournament()}
          >
            Round Robin Tournament
          </Button>
        </HStack>
        
        <Box>
          <Text>Current Turn: {game.turn() === 'w' ? 'White' : 'Black'}</Text>
          {game.isCheckmate() && <Text color="red.500">Checkmate!</Text>}
          {game.isDraw() && <Text color="gray.500">Draw!</Text>}
        </Box>
      </VStack>
    </Box>
  )
}

ChessBoard.propTypes = {
  mode: PropTypes.string.isRequired,
  whiteAI: PropTypes.string,
  blackAI: PropTypes.string
}

export default ChessBoard
