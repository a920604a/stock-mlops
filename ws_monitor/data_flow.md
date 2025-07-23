```
[Kafka stock_predictions] ----> [kafka_predictions_consumer_loop]
       |                     \
       |                      --> [ClickHouse 寫入 (可選)]
       |                      --> [update_data_stream] 更新 current_data
       |                      --> [Evidently] get_monitoring_metrics()
       |                      --> [WebSocket] broadcast_predictions()

[Kafka monitoring_metrics] ----> [kafka_metrics_consumer_loop]
                                --> [WebSocket] broadcast_metrics()

[前端 Client]
   |--- ws://server/ws/predictions --> 即時預測 + 漂移指標
   |--- ws://server/ws/metrics     --> Prometheus 系統指標

```
