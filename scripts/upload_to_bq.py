import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

def upload_nested_json():
    # Khởi tạo client
    client = bigquery.Client()

    # Định nghĩa địa chỉ bảng đích
    table_id = f"{os.getenv('PROJECT_ID')}.{os.getenv('DATASET_ID')}.{os.getenv('TABLE_ID')}"

    # Cấu hình Job Upload cho dữ liệu lồng nhau
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    # Đẩy dữ liệu
    file_path = "data/events_nested.json"
    if os.path.exists(file_path):
        with open(file_path, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        print(f"Đang đẩy dữ liệu lên BigQuery...")
        job.result()
        print(f"Thành công! Dữ liệu đã nằm tại: {table_id}")
    else:
        print(f"Lỗi: Không tìm thấy file {file_path}. Hãy chạy data_generator.py trước.")

if __name__ == "__main__":
    upload_nested_json()