import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="flex gap-4">
        <Link to="/" className="hover:underline">首頁</Link>
        <Link to="/predict" className="hover:underline">預測</Link>
        <Link to="/train" className="hover:underline">訓練</Link>
        <Link to="/models" className="hover:underline">模型管理</Link>
        <Link to="/datasets" className="hover:underline">資料集管理</Link>
        <Link to="/production" className="hover:underline">生產監控</Link>
      </div>
    </nav>
  );
}
