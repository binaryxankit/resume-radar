import { ThemeProvider } from './components/ThemeProvider'
import { Landing } from './pages/Landing'

export default function App() {
  return (
    <ThemeProvider>
      <Landing />
    </ThemeProvider>
  )
}
