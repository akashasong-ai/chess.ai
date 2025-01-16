import { useState } from 'react'
import {
  Box,
  Container,
  Flex,
  Heading,
  VStack,
  Button,
  Text,
  useColorModeValue,
  Select,
  FormControl,
  FormLabel,
} from '@chakra-ui/react'
import ChessBoard from './components/ChessBoard'
import './App.css'

function App() {
  const [selectedMode, setSelectedMode] = useState('player-vs-ai')
  const [whiteAI, setWhiteAI] = useState(null)
  const [blackAI, setBlackAI] = useState('GPT-4')

  const buttonBgColor = useColorModeValue('white', 'gray.700')
  const activeButtonBgColor = useColorModeValue('blue.500', 'blue.200')
  const activeButtonColor = useColorModeValue('white', 'gray.800')

  const modes = [
    { id: 'player-vs-ai', label: 'Player vs AI', description: 'Challenge GPT-4, CLAUDE, GEMINI, or PERPLEXITY' },
    { id: 'ai-vs-ai', label: 'AI vs AI', description: 'Watch GPT-4, CLAUDE, GEMINI, or PERPLEXITY battle it out' },
    { id: 'tournaments', label: 'Tournaments', description: 'Join an Arena where anyone can win' }
  ]

  return (
    <Container maxW="container.xl" p={4}>
      <Flex gap={8} align="start">
        {/* Sidebar */}
        <VStack
          spacing={4}
          align="stretch"
          w="300px"
          bg={buttonBgColor}
          p={4}
          borderRadius="lg"
          boxShadow="base"
        >
          <Heading size="lg" mb={4}>Play Chess</Heading>
          
          {modes.map((mode) => (
            <Button
              key={mode.id}
              onClick={() => {
                setSelectedMode(mode.id)
                // Reset AI selections when changing modes
                if (mode.id === 'player-vs-ai') {
                  setWhiteAI(null)
                  setBlackAI('GPT-4')
                } else if (mode.id === 'ai-vs-ai') {
                  setWhiteAI('GPT-4')
                  setBlackAI('CLAUDE')
                }
              }}
              bg={selectedMode === mode.id ? activeButtonBgColor : buttonBgColor}
              color={selectedMode === mode.id ? activeButtonColor : 'inherit'}
              _hover={{
                bg: selectedMode === mode.id ? activeButtonBgColor : 'gray.100',
              }}
              h="auto"
              p={4}
              display="flex"
              flexDirection="column"
              alignItems="flex-start"
              width="100%"
            >
              <Text fontWeight="bold">{mode.label}</Text>
              <Text fontSize="sm" color="gray.500">{mode.description}</Text>
            </Button>
          ))}

          {/* AI Selection Controls */}
          {(selectedMode === 'player-vs-ai' || selectedMode === 'ai-vs-ai') && (
            <Box mt={4} p={4} bg="white" borderRadius="md" boxShadow="sm">
              <Heading size="sm" mb={4}>AI Players</Heading>
              
              {selectedMode === 'ai-vs-ai' && (
                <FormControl mb={4}>
                  <FormLabel>White Player (AI)</FormLabel>
                  <Select
                    value={whiteAI}
                    onChange={(e) => setWhiteAI(e.target.value)}
                    bg="white"
                  >
                    <option value="GPT-4">GPT-4</option>
                    <option value="CLAUDE">CLAUDE</option>
                    <option value="GEMINI">GEMINI</option>
                    <option value="PERPLEXITY">PERPLEXITY</option>
                  </Select>
                </FormControl>
              )}

              <FormControl>
                <FormLabel>{selectedMode === 'ai-vs-ai' ? 'Black Player (AI)' : 'AI Opponent'}</FormLabel>
                <Select
                  value={blackAI}
                  onChange={(e) => setBlackAI(e.target.value)}
                  bg="white"
                >
                  <option value="GPT-4">GPT-4</option>
                  <option value="CLAUDE">CLAUDE</option>
                  <option value="GEMINI">GEMINI</option>
                  <option value="PERPLEXITY">PERPLEXITY</option>
                </Select>
              </FormControl>
            </Box>
          )}

          {/* Additional sections */}
          <Box mt={8}>
            <Heading size="md" mb={4}>Game History</Heading>
            {/* Game history content will go here */}
          </Box>

          <Box mt={4}>
            <Heading size="md" mb={4}>Leaderboard</Heading>
            {/* AI-only leaderboard will go here */}
          </Box>
        </VStack>

        {/* Main content area */}
        <Box flex={1}>
          <ChessBoard 
            mode={selectedMode}
            whiteAI={whiteAI}
            blackAI={blackAI}
          />
        </Box>
      </Flex>
    </Container>
  )
}

export default App
