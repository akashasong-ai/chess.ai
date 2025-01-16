import { useState } from 'react'
import {
  Box,
  Container,
  Flex,
  Heading,
  VStack,
  Button,
  useColorModeValue,
  Text,
} from '@chakra-ui/react'
import ChessBoard from './components/ChessBoard'
import './App.css'

function App() {
  const [selectedMode, setSelectedMode] = useState('player-vs-ai')
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const buttonBgColor = useColorModeValue('white', 'gray.700')
  const activeButtonBgColor = useColorModeValue('blue.500', 'blue.200')
  const activeButtonColor = useColorModeValue('white', 'gray.800')

  const modes = [
    { id: 'player-vs-ai', label: 'Player vs AI', description: 'Challenge a bot from Easy to Master' },
    { id: 'ai-vs-ai', label: 'AI vs AI', description: 'Watch AIs battle it out' },
    { id: 'tournaments', label: 'Tournaments', description: 'Join an Arena where anyone can win' },
    { id: 'variants', label: 'Chess Variants', description: 'Find fun new ways to play chess' },
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
              onClick={() => setSelectedMode(mode.id)}
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
          <ChessBoard mode={selectedMode} />
        </Box>
      </Flex>
    </Container>
  )
}

export default App
