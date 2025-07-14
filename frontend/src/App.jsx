import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Predict from './pages/Predict'
import Train from './pages/Train'
import TrainStatus from './pages/TrainStatus'
import Models from './pages/Models'
import NotFound from './pages/NotFound'
import TopBar from './components/TopBar'

export default function App() {
  return (
    <BrowserRouter>
      <TopBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="/train" element={<Train />} />
        <Route path="/models" element={<Models />} />
        <Route path="/train/status" element={<TrainStatus />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
