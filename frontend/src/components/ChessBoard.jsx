import { Box, Grid, GridItem, Text, VStack, HStack, Button } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { Chess } from 'chess.js'

function ChessBoard({ mode }) {
  const [game, setGame] = useState(new Chess())
  const [selectedSquare, setSelectedSquare] = useState(null)
  
  const renderSquare = (i, j) => {
    const isLight = (i + j) % 2 === 0
    const square = String.fromCharCode(97 + j) + (8 - i)
    const piece = game.get(square)
    
    return (
      <GridItem
        key={square}
        w="60px"
        h="60px"
        bg={isLight ? 'gray.200' : 'gray.600'}
        display="flex"
        alignItems="center"
        justifyContent="center"
        cursor="pointer"
        onClick={() => handleSquareClick(square)}
        position="relative"
        _hover={{ bg: selectedSquare === square ? 'blue.400' : (isLight ? 'blue.100' : 'blue.500') }}
        backgroundColor={selectedSquare === square ? 'blue.400' : (isLight ? 'gray.200' : 'gray.600')}
      >
        {piece && (
          <Text fontSize="2xl">
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

  const handleSquareClick = (square) => {
    if (selectedSquare === null) {
      // First click - select the piece
      const piece = game.get(square)
      if (piece && piece.color === (game.turn() === 'w')) {
        setSelectedSquare(square)
      }
    } else {
      // Second click - attempt to move
      try {
        game.move({
          from: selectedSquare,
          to: square,
          promotion: 'q' // Always promote to queen for simplicity
        })
        setGame(new Chess(game.fen()))
        setSelectedSquare(null)
      } catch (e) {
        // Invalid move
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
        <HStack justify="space-between">
          <Text fontSize="xl" fontWeight="bold">
            {mode === 'player-vs-ai' ? 'Player vs AI' : 'AI vs AI'}
          </Text>
          <Button colorScheme="blue" size="sm">
            New Game
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

export default ChessBoard
