// frontend/src/pages/Datasets.jsx
import { useEffect, useState } from "react";
import { fetchDatasets } from "../api/datasets";

function Datasets() {
    const [datasets, setDatasets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [ticker, setTicker] = useState("");

    const loadDatasets = async () => {
        setLoading(true);
        try {
            const data = await fetchDatasets(ticker);
            setDatasets(data);
        } catch (err) {
            console.error("❌ 載入資料集失敗", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDatasets();
    }, []);

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">📊 資料集管理</h2>

            <div className="mb-4">
                <input
                    type="text"
                    placeholder="輸入 ticker 搜尋 (如 AAPL)"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    className="border p-2 rounded mr-2"
                />
                <button
                    onClick={loadDatasets}
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                >
                    搜尋
                </button>
            </div>

            {loading ? (
                <p>載入中...</p>
            ) : datasets.length === 0 ? (
                <p>無資料</p>
            ) : (
                <table className="w-full border table-auto">
                    <thead>
                        <tr className="bg-gray-100">
                            <th className="border p-2">Ticker</th>
                            <th className="border p-2">Exchange</th>
                            <th className="border p-2">資料起迄</th>
                            <th className="border p-2">筆數</th>
                        </tr>
                    </thead>
                    <tbody>
                        {datasets.map((ds) => (
                            <tr key={`${ds.ticker}-${ds.exchange}`}>
                                <td className="border p-2">{ds.ticker}</td>
                                <td className="border p-2">{ds.exchange}</td>
                                <td className="border p-2">
                                    {ds.start_date} ~ {ds.end_date}
                                </td>
                                <td className="border p-2">{ds.count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default Datasets;
