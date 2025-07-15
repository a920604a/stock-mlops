| 功能                | 說明                                                |
| ----------------- | ------------------------------------------------- |
| React SPA 前端      | `location /` serve `/usr/share/nginx/html` 中的靜態檔案 |
| Fallback routing  | `try_files $uri /index.html;` 確保前端路由可正常運作         |
| 後端 API 負載平衡       | `/api/` 請求會輪詢轉發給 backend1/2                       |
| 一個容器搞定前後端 gateway | 不需額外設立 backend\_nginx container                   |
