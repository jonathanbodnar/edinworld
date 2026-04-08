import { Routes, Route } from 'react-router-dom'
import { WorldProvider } from './context/WorldContext'
import ThreePanelLayout from './layouts/ThreePanelLayout'

export default function App() {
  return (
    <WorldProvider>
      <Routes>
        <Route path="/*" element={<ThreePanelLayout />} />
      </Routes>
    </WorldProvider>
  )
}
