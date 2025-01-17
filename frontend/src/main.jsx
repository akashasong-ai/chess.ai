import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import './index.css'
import App from './App.jsx'

const theme = extendTheme({
  colors: {
    board: {
      light: "#F0EAD6",  // Cream color
      dark: "#8BA160",   // Sage green
      go: "#E6D5AC"      // Tan/beige for Go board
    }
  },
  styles: {
    global: {
      body: {
        bg: "gray.900",
        color: "white"
      }
    }
  },
  components: {
    Button: {
      variants: {
        game: {
          height: "36px",
          px: "12px",
          py: "6px",
          borderRadius: "6px",
          fontSize: "14px"
        }
      }
    }
  }
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </StrictMode>,
)
