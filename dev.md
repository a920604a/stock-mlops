好的！根據你提供的多服務架構與技術棧，我幫你整理一份常用且方便開發者用來 debug、測試或瀏覽 API 文件的 URL 清單，並簡短說明用途，方便你或團隊快速找到服務入口。

---

## 常用 Debug / Test URL 一覽

| 服務名稱                         | URL                             | 用途說明                                            |
| ---------------------------- | ------------------------------- | ----------------------------------------------- |
| **Backend1 FastAPI**         | `http://localhost:8001/docs`    | Swagger UI，自動生成的 REST API 文件與測試介面               |
|                              | `http://localhost:8001/redoc`   | ReDoc 風格的 API 文件瀏覽介面                            |
| **Backend2 FastAPI**         | `http://localhost:8002/docs`    | Swagger UI（同上，另一實例）                             |
|                              | `http://localhost:8002/redoc`   | ReDoc 介面                                        |
| **Celery Worker**            | 無 Web UI（CLI 查看 logs）           | 以 CLI 方式觀察任務執行情況與日誌                             |
| **PostgreSQL OLTP DB**       | 連線端口：`localhost:5412`           | 可用 DBeaver、pgAdmin 連線測試資料庫                      |
| **PostgreSQL Model Meta DB** | 連線端口：`localhost:5411`           | 用於模型元資料存取                                       |
| **Redis**                    | 連線端口：`localhost:6379`           | 用 Redis CLI (`redis-cli`) 或 RedisInsight 檢查快取   |
| **MLflow Tracking Server**   | `http://localhost:5010`         | MLflow UI，實驗追蹤、模型版本管理                           |
| **Prometheus**               | `http://localhost:9090`         | Prometheus 監控界面，查看指標數據                          |
| **Grafana**                  | `http://localhost:3002`         | Grafana Dashboard 監控儀表板，預設帳號密碼 admin/admin12345 |
| **ClickHouse**               | HTTP 介面：`http://localhost:8123` | 可用於直接用瀏覽器或 DBeaver 連線查詢 OLAP                    |
| **MinIO Web Console**        | `http://localhost:9001`         | MinIO 控制台，管理物件儲存（bucket）                        |

---

### 補充說明

* **FastAPI 的 `/docs` 與 `/redoc`** 是官方內建的兩種 Swagger 文件視覺化工具，方便前端與後端開發者測試 API。
* **MLflow UI** 用於監控實驗執行狀況與查看模型版本。
* **Prometheus 與 Grafana** 組合用於即時監控系統狀態與模型表現。
* **ClickHouse** HTTP 介面可以直接用瀏覽器測試 SQL 查詢，也可透過 BI 工具連線。
* **MinIO** 是物件儲存服務，主要給 MLflow 用來存放模型 artifact。
