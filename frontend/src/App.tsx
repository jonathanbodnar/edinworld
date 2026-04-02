import { Routes, Route } from 'react-router-dom'
import { ChapterProvider } from './context/ChapterContext'
import ThreePanelLayout from './layouts/ThreePanelLayout'

export default function App() {
  return (
    <ChapterProvider>
      <Routes>
        <Route path="/*" element={<ThreePanelLayout />} />
      </Routes>
    </ChapterProvider>
  )
}
