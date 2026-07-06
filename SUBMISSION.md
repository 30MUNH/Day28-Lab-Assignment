# Hướng Dẫn Nộp Bài - Lab #28: Full Platform Integration Sprint

## Yêu Cầu Nộp Bài

**Full AI infrastructure platform demo** - từ data ingestion đến model serving với full observability.

## Các Artifacts Cần Nộp

### 1. Source Code
- Folder `lab28/` hoàn chỉnh với tất cả files
- Tất cả integration scripts hoạt động
- Prefect flows đã deploy và schedule

### 2. Screenshots Demo
Chụp màn hình các bước:
- Prefect UI: http://localhost:4200 (flow đang chạy)
- API Gateway call: `curl http://localhost:8000/health`
- Grafana dashboard: http://localhost:3000

### 3. Kết Quả Smoke Tests
Chạy và chụp màn hình kết quả:
```bash
cd lab28
pytest smoke-tests/ -v
```
Kỳ vọng: 5/5 tests passing

### 4. Production Readiness Score
```bash
python scripts/production_readiness_check.py
```
Kỳ vọng: Score >80%

### 5. Documentation
- `README.md` giải thích cách:
  - Start platform: `docker compose up -d`
  - Deploy Prefect flows
  - Run smoke tests
  - Access dashboards (Grafana:3000, Prometheus:9090, Prefect:4200)

## Định Dạng Nộp Bài

Tạo Repo GitHub chứa:
```
lab28_submission_[student_id]
├── lab28/                    # Source code hoàn chỉnh
│   ├── docker-compose.yml
│   ├── prefect/flows/
│   ├── scripts/
│   ├── api-gateway/
│   └── monitoring/
├── screenshots/              # Screenshots demo
│   ├── prefect_ui.png
│   ├── api_gateway.png
│   └── grafana_dashboard.png
├── smoke_tests_results.png   # Screenshot kết quả pytest
├── production_readiness.png  # Screenshot readiness score
└── README.md                # Hướng dẫn setup
```

## Địa Điểm Nộp
Nộp link repo GitHub qua LMS

## Tiêu Chí Chấm Điểm

| Tiêu Chí | Trọng Số | Mô Tả |
|----------|----------|-------|
| Integration Completeness | 40% | Tất cả 10 integration points hoạt động, data flow end-to-end |
| Observability | 25% | Logs, metrics, traces hiển thị; alerts configured |
| Performance | 20% | Latency trong SLO; load tested; không có memory leaks |
| Architecture Quality | 15% | Clean separation, GitOps config, documented decisions |

## Các Vấn Đề Cần Tránh

- Config drift giữa các environments
- Thiếu error handling tại integration points
- Monitoring coverage không hoàn chỉnh
- Không có rollback strategy
- Demo không test trước khi nộp

## 5 Câu Hỏi Cần Trả Lời Khi Nộp

1. **Phân tích các trade-offs trong thiết kế kiến trúc AI platform của bạn. Bạn đã cân bằng giữa performance, reliability, và maintainability như thế nào?**
   - **Performance vs. Reliability**: Để tối ưu hiệu năng và độ trễ truy vấn vector, dữ liệu được xử lý không đồng bộ (Kafka → Prefect → Delta Lake → Feast → Qdrant). Để đảm bảo reliability, Kafka làm message queue trung gian giúp lưu giữ dữ liệu và tự động retry khi các dịch vụ hạ nguồn gặp sự cố. Trình lưu trữ trực tuyến Feast (Redis) cung cấp độ trễ siêu thấp (<10ms) cho các truy vấn trực tuyến.
   - **Maintainability vs. Performance**: Sử dụng Docker Compose để đóng gói toàn bộ hệ thống giúp triển khai và bảo trì dễ dàng (maintainability), tuy nhiên sẽ tăng một chút độ trễ mạng giữa các container so với chạy native trên host. Sử dụng Prefect giúp trực quan hoá việc giám sát pipeline nhưng cần vận hành thêm Prefect Server và Worker.

2. **Trong kiến trúc hybrid (Local + Kaggle), bạn xử lý ngắt kết nối giữa local và Kaggle như thế nào? Có cơ chế fallback không?**
   - **Xử lý ngắt kết nối**: Khi Kaggle tunnel (qua Ngrok) bị ngắt kết nối, API Gateway sẽ nhận được lỗi kết nối hoặc timeout từ client HTTP.
   - **Cơ chế Fallback**:
     - Trong API Gateway, các yêu cầu suy luận được bọc trong các cơ chế timeout và xử lý ngoại lệ (Exception Handling) của HTTPX để tránh crash gateway.
     - Khi service vLLM/Embedding từ Kaggle bị offline, hệ thống có thể chuyển sang chế độ fallback bằng cách trả về phản hồi mặc định, sử dụng cache cục bộ, hoặc sử dụng mô hình embedding gọn nhẹ chạy trực tiếp trên CPU local.
     - Trong pipeline Ingestion, các task của Prefect được cấu hình cơ chế tự động retry để hoãn xử lý cho tới khi kết nối đến dịch vụ Embedding trên Kaggle được khôi phục.

3. **Giải thích cách event-driven architecture với Kafka giúp decouple các components trong AI platform của bạn.**
   - **Temporal Decoupling**: Hệ thống sản xuất dữ liệu (Data Producer) chỉ cần đẩy tin nhắn vào topic `data.raw` trên Kafka mà không cần quan tâm khi nào hoặc bằng cách nào hệ thống hạ nguồn xử lý. Nếu Delta Lake hoặc Qdrant gặp sự cố tạm thời, dữ liệu vẫn được lưu trữ an toàn trên Kafka.
   - **Interface Decoupling**: Các service giao tiếp với nhau qua schema tin nhắn được chuẩn hoá. Thay đổi công nghệ lưu trữ hạ nguồn (ví dụ chuyển từ Qdrant sang Milvus hoặc từ Delta Lake sang Iceberg) không làm ảnh hưởng đến mã nguồn của Data Producer.
   - **Mở rộng dễ dàng (Scalability)**: Cho phép dễ dàng tăng số lượng partition của Kafka topic và chạy song song nhiều worker/consumer để tăng tốc độ xử lý mà không cần cấu hình lại hệ thống upstream.

4. **Bạn đã implement observability như thế nào? Logs, metrics, và traces được thu thập và visualized ra sao?**
   - **Metrics**: API Gateway tích hợp sẵn thư viện `prometheus-fastapi-instrumentator` để tự động expose metrics tại `/metrics`. Prometheus định kỳ scrape các chỉ số này và lưu trữ. Grafana lấy Prometheus làm datasource để trực quan hoá qua dashboard giám sát (độ trễ, số lượng request, lỗi HTTP).
   - **Traces**: Cấu hình các biến môi trường LangSmith để theo dõi các chuỗi xử lý AI (như quá trình RAG: Vector search → LLM query completions) giúp giám sát từng bước thực thi chi tiết.
   - **Logs**: Ghi log chuẩn ra stdout/stderr ở dạng cấu trúc từ các container để các dịch vụ log collector có thể dễ dàng thu gom và phân tích.

5. **Nếu một service trong stack (ví dụ: Qdrant hoặc Kafka) bị crash, hệ thống của bạn sẽ xử lý như thế nào? Có graceful degradation không?**
   - **Nếu Kafka crash**: Producer tạm thời lưu trữ dữ liệu cục bộ hoặc báo lỗi, nhưng API Gateway vẫn phục vụ các truy vấn RAG bình thường thông qua dữ liệu hiện tại đã có sẵn trong Qdrant và Feast online store (Redis).
   - **Nếu Qdrant crash**: API Gateway không thể lấy context. Thay vì crash toàn bộ hệ thống, nó sẽ kích hoạt cơ chế graceful degradation bằng cách fallback sang tìm kiếm văn bản đơn giản (keyword search) hoặc trực tiếp chuyển câu hỏi của người dùng tới LLM không kèm context (chế độ non-RAG), đồng thời bắn metrics cảnh báo hệ thống giám sát.
   - **Nếu Redis/Feast crash**: Các online features không thể lấy ra. Hệ thống có thể tạm thời đọc các tính năng mặc định hoặc chuyển sang đọc từ offline store (Delta Lake) để tiếp tục phục vụ.

## Câu Hỏi Thêm?
Liên hệ giảng viên qua LMS hoặc office hours.
