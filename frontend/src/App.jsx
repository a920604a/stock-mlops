import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import TopBar from './components/TopBar'
import Datasets from "./pages/Datasets";
import Models from './pages/Models'
import Train from './pages/Train'
import TrainStatus from './pages/TrainStatus'
import Predict from './pages/Predict'
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
        <Route path="/train" element={<Train />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
