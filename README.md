# game-analytics-portfolio
mobile-game-analytics/
├── data/                            # Dữ liệu thô và dữ liệu đã gen
│   ├── dim_users.csv                #
│   ├── dim_levels.csv               #
│   ├── fact_sessions.csv            #
│   ├── fact_gameplay_events.csv     #
│   ├── fact_monetization.csv        #
│   ├── fact_technical_health.csv    #
│   └── events_nested.json           # File nòng cốt để upload BigQuery
├── scripts/                         # Python kịch bản vận hành hệ thống
│   ├── data_generator.py            # Gen data v2 (10 nước, no-null revenue)
│   └── upload_to_bq.py              # Script đẩy JSON lên Warehouse
├── sql/                             # Tầng biến đổi (Transformation) trên BigQuery
│   ├── 00_create_raw.sql            # Khởi tạo bảng thô (Staging)
│   ├── 01_dim_users.sql             # View người chơi (Country, Device Tier)
│   ├── 02_dim_levels.sql            # View màn chơi (Difficulty Index)
│   ├── 03_fact_sessions.sql         # View phiên chơi (App Version)
│   ├── 04_fact_gameplay_events.sql  # View hành vi (Fail reason)
│   ├── 05_fact_monetization.sql     # View doanh thu (IAP, Ads)
│   ├── 06_fact_technical_health.sql # View kỹ thuật (FPS, Crash)
│   └── ddl_schema.sql               # Master script triển khai toàn bộ View
├── streamlit_app/                   # Ứng dụng Dashboard
│   ├── pages/                       # Các trang báo cáo chi tiết
│   │   ├── 1_Executive_Summary.py   # Chỉ số ARPDAU, Retention, LTV
│   │   ├── 2_Company_Performance.py # Ma trận Cohort
│   │   ├── 3_Product_Issues.py      # Phân tích Crash & FPS theo Tier
│   │   └── 4_Geographic_Trends.py   # Bản đồ nhiệt 10 quốc gia
│   ├── chart_factory.py             # Hàm vẽ biểu đồ Plotly tập trung
│   ├── data_utils.py                # Kết nối BigQuery & xử lý logic data
│   ├── config.py                    # Quản lý hằng số dự án
│   └── home.py                      # Trang chủ giới thiệu dự án
├── .env                             # Quản lý Key và ID (Ẩn khỏi Git)
├── .gitignore                       # Khai báo ẩn .env, venv và service_account.json
├── requirements.txt                 # Thư viện: pandas, faker, streamlit, google-cloud-bigquery
└── service_account.json             # File chứng thực Google Cloud (Ẩn khỏi Git)