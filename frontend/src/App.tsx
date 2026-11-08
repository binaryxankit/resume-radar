import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './components/AuthProvider'
import { ThemeProvider } from './components/ThemeProvider'
import { AnalysisPage } from './pages/AnalysisPage'
import { AuthPage } from './pages/AuthPage'
import { Landing } from './pages/Landing'
import { WorkspacePage } from './pages/WorkspacePage'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<AuthPage />} />
            <Route path="/app" element={<WorkspacePage />} />
            <Route path="/app/analyses/:id" element={<AnalysisPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
