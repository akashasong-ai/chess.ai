import { Box, Grid, GridItem, Text, VStack, HStack, Button } from '@chakra-ui/react'
import { useToast } from '@chakra-ui/toast'
import { useState, useEffect } from 'react'
import { api } from '../services/api'
import PropTypes from 'prop-types'

function GoBoard({ mode, whiteAI, blackAI }) {
  const [board, setBoard] = useState(Array(19).fill(Array(19).fill(null)))
  const [gameState, setGameState] = useState(null)
  const [isPlayerTurn, setIsPlayerTurn] = useState(true)
  const toast = useToast()

  useEffect(() => {
    const initGame = async () => {
      try {
        await api.startGame(whiteAI, blackAI)
        const state = await api.getGameState()
        setGameState(state)
        setBoard(state.board)
        setIsPlayerTurn(state.currentPlayer === 'white' && !whiteAI)
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

  const setupWebSocket = () => {
    api.onConnect(() => {
      console.log('Connected to game server')
    })

    api.onGameUpdate((update) => {
      setBoard(update.board)
      setGameState(update)
      setIsPlayerTurn(update.currentPlayer === 'white' && !update.whiteAI)
    })

    api.onDisconnect(() => {
      console.log('Disconnected from game server')
    })
  }

  const renderIntersection = (row, col) => {
    const isStarPoint = [3, 9, 15].includes(row) && [3, 9, 15].includes(col)
    const stone = board[row][col]

    return (
      <GridItem
        key={`${row}-${col}`}
        w="60px"
        h="60px"
        bg="board.go"
        display="flex"
        alignItems="center"
        justifyContent="center"
        cursor="pointer"
        onClick={() => handleIntersectionClick(row, col)}
        position="relative"
        _hover={{ bg: 'board.go' }}
      >
        <Box
          position="absolute"
          width="100%"
          height="1px"
          bg="gray.300"
          top="50%"
        />
        <Box
          position="absolute"
          width="1px"
          height="100%"
          bg="gray.300"
          left="50%"
        />
        {isStarPoint && (
          <Box
            position="absolute"
            width="8px"
            height="8px"
            borderRadius="full"
            bg="gray.500"
          />
        )}
        {stone && (
          <Box
            width="90%"
            height="90%"
            borderRadius="full"
            bg={stone === 'black' ? 'gray.800' : 'white'}
            border="1px solid"
            borderColor={stone === 'black' ? 'gray.900' : 'gray.300'}
            boxShadow="md"
          />
        )}
      </GridItem>
    )
  }

  const handleIntersectionClick = async (row, col) => {
    if (!isPlayerTurn) return

    try {
      const result = await api.makeMove({ row, col })
      if (result.success) {
        setBoard(result.board)
        setGameState(result)
        setIsPlayerTurn(false)
      }
    } catch (error) {
      toast({
        title: 'Invalid move',
        description: error.message,
        status: 'warning',
        duration: 2000,
        isClosable: true,
      })
    }
  }

  return (
    <Box>
      <Grid
        templateColumns="repeat(19, 60px)"
        gap={0}
        border="2px"
        borderColor="gray.300"
        width="fit-content"
      >
        {Array(19).fill().map((_, i) =>
          Array(19).fill().map((_, j) => renderIntersection(i, j))
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
                setBoard(newState.board)
                setGameState(newState)
                setIsPlayerTurn(newState.currentPlayer === 'white' && !whiteAI)
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
          <Text>Current Turn: {gameState?.currentPlayer === 'white' ? 'White' : 'Black'}</Text>
          {gameState?.winner && (
            <Text color="red.500">Winner: {gameState.winner}!</Text>
          )}
        </Box>
      </VStack>
    </Box>
  )
}

GoBoard.propTypes = {
  mode: PropTypes.string.isRequired,
  whiteAI: PropTypes.string,
  blackAI: PropTypes.string
}

export default GoBoard
