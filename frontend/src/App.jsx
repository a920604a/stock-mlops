import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import TopBar from './components/TopBar'
import Datasets from "./pages/Datasets";
import Models from './pages/Models'
import TrainStatus from './pages/TrainStatus'
import Production from './pages/Production'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <TopBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/models" element={<Models />} />
        <Route path="/train/status" element={<TrainStatus />} />
        <Route path="/production" element={<Production />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
