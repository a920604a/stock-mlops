import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Predict from './pages/Predict'
import Train from './pages/Train'
import Models from './pages/Models'
import NotFound from './pages/NotFound'
import TopBar from './components/TopBar'

function App() {
  return (
    <Router>
      <TopBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="/train" element={<Train />} />
        <Route path="/models" element={<Models />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App
