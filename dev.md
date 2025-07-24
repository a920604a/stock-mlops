好的！根據你提供的多服務架構與技術棧，我幫你整理一份常用且方便開發者用來 debug、測試或瀏覽 API 文件的 URL 清單，並簡短說明用途，方便你或團隊快速找到服務入口。

---

## 常用 Debug / Test URL 一覽

| 服務名稱                  | URL / 連線資訊                          | 用途說明                                                     | 備註              |
|-----------------------|----------------------------------|----------------------------------------------------------|-----------------|
| **Frontend**          | [http://localhost:5173](http://localhost:5173)<br>[http://localhost](http://localhost) | React 開發伺服器 / 靜態頁面                                     | 🔵 前端          |
| **Backend1 FastAPI**  | [http://localhost:8001/docs](http://localhost:8001/docs)<br>[http://localhost:8001/redoc](http://localhost:8001/redoc) | Swagger UI、ReDoc 自動生成的 REST API 文件與測試介面               | 🟢 後端 API      |
| **Backend2 FastAPI**  | [http://localhost:8002/docs](http://localhost:8002/docs)<br>[http://localhost:8002/redoc](http://localhost:8002/redoc) | Swagger UI、ReDoc（Kafka Producer 服務）                        | 🟢 後端 API      |
| **Model Experience**  | [http://localhost:5010](http://localhost:5010)         | MLflow Tracking Server，模型實驗、版本管理                            | 🟣 模型管理      |
| **MinIO Storage**     | [http://localhost:9001](http://localhost:9001)         | MinIO 控制台，物件儲存管理（bucket）                               | 🟤 物件儲存      |
| **Celery Flower UI**  | [http://localhost:5555](http://localhost:5555)         | Celery 任務監控與管理 Web UI                                   | 🟠 非同步任務監控  |
| **Celery Worker**     | 無 Web UI (CLI 查看日誌)              | celery_predict / celery_train Worker                            | 🟠 非同步任務執行  |
| **Redis Broker**      | Redis 6379 DB 0                  | Celery 任務隊列 Broker                                        | 🔴 快取/隊列系統  |
| **Redis Backend**     | Redis 6379 DB 1                  | Celery 任務狀態追蹤 Backend                                   | 🔴 快取/隊列系統  |
| **Kafka backend2**    | —                                | Kafka Producer                                              | 🟦 消息串流      |
| **Kafka metrics_publisher** | —                                | Kafka Producer                                              | 🟦 消息串流      |
| **Kafka Broker**      | kafka:9092                     | Kafka Broker                                               | 🟦 消息串流      |
| **Kafka ws_monitor**  | [http://localhost:8010/docs](http://localhost:8010/docs) | Kafka Consumer                                             | 🟦 消息串流      |
| **Kafka UI**          | [http://localhost:8082/](http://localhost:8082/)       | Kafka Web UI                                               | 🟦 消息串流      |
| **PostgreSQL model_meta_db** | postgres:5411                 | 模型元資料庫                                               | 🟢 資料庫        |
| **PostgreSQL raw_db** | postgres:5412                 | OLTP 原始資料庫                                            | 🟢 資料庫        |
| **PostgreSQL mlflow-db** | postgres:5422                 | MLflow 內部資料庫                                           | 🟢 資料庫        |
| **Redis**             | redis:6379                    | 快取層與 Celery Broker                                     | 🔴 快取/隊列系統  |
| **ClickHouse SQL Play** | [http://localhost:8123/play](http://localhost:8123/play)  | ClickHouse SQL 線上查詢介面                                  | 🟢 資料庫        |
| **ClickHouse Dashboard** | [http://localhost:8123/dashboard](http://localhost:8123/dashboard) | ClickHouse 儀表板                                          | 🟢 資料庫        |
| **celery_exporter**   | —                                | Prometheus 監控 Celery 任務指標                                 | ⚪️ 監控          |
| **Prometheus**        | [http://localhost:9090](http://localhost:9090)         | Prometheus 監控界面                                         | ⚪️ 監控          |
| **Grafana**           | [http://localhost:3002/](http://localhost:3002/)       | Grafana 儀表板（預設帳號密碼 admin/admin12345）                  | ⚪️ 監控          |
| **node-exporter**     | [http://localhost:9100/](http://localhost:9100/)       | 監控主機系統狀態指標                                        | ⚪️ 監控          |
| **cAdvisor**          | [http://localhost:8080](http://localhost:8080)         | Docker 容器資源監控                                        | ⚪️ 監控          |
| **blackbox-exporter** | [http://localhost:9115](http://localhost:9115)         | 網路服務可用性監控                                         | ⚪️ 監控          |


---

### 補充說明

* **FastAPI 的 `/docs` 與 `/redoc`** 是官方內建的兩種 Swagger 文件視覺化工具，方便前端與後端開發者測試 API。
* **MLflow UI** 用於監控實驗執行狀況與查看模型版本。
* **Prometheus 與 Grafana** 組合用於即時監控系統狀態與模型表現。
* **ClickHouse** HTTP 介面可以直接用瀏覽器測試 SQL 查詢，也可透過 BI 工具連線。
* **MinIO** 是物件儲存服務，主要給 MLflow 用來存放模型 artifact。


| 特性     | **Celery**       | **Kafka**               |
| ------ | ---------------- | ----------------------- |
| 核心定位   | 任務隊列（Task Queue） | 流處理（Streaming Platform） |
| 吞吐量    | 中等（受 broker 限制）  | 極高                      |
| 任務回傳   | 支援               | 無                       |
| 適合場景   | 短任務、批次、排程        | 高頻事件、實時流                |
| Broker | RabbitMQ、Redis   | Kafka Cluster           |
| 保留訊息   | 不常用（完成即刪除）       | 可長期保留並回放                |

> Client → Broker → Worker → Result Backend
> Producer → Kafka Broker (Topic + Partition) → Consumer Group
