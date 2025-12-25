from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pendulum

local_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_etl_train_dag",
    default_args=default_args,
    description="Daily ETL + Train model pipeline",
    # 1. THAY ĐỔI SCHEDULE_INTERVAL: Trigger mỗi 1 giờ
    schedule_interval="0 * * * *", 
    # 2. THAY ĐỔI START_DATE: Đặt thời điểm đầu tiên chạy (Execution Date) vào 8h sáng ngày 2025/1/1.
    # Airflow sẽ chạy lần đầu tiên vào 9h sáng, sau khi kết thúc chu kỳ 8h-9h.
    start_date=datetime(2025, 1, 1, 0, 0, 0, tzinfo=local_tz), # 8h 00 phút 00 giây
    catchup=False,
    tags=["etl", "mlops"],
) as dag:

    # === Task 1: ETL Pipeline ===
    etl_task = BashOperator(
        task_id="run_etl_pipeline",
        bash_command=(
            "cd /opt/airflow/mlops_project/data_pipeline && "
            "python pipeline.py "
            "--start-date '{{ (execution_date.in_timezone('Asia/Ho_Chi_Minh') - macros.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S') }}' "
            "--end-date '{{ execution_date.in_timezone('Asia/Ho_Chi_Minh').strftime('%Y-%m-%d %H:%M:%S') }}'"
        ),
    )

    # === Task 2: Train Model ===
    train_task = BashOperator(
        task_id="run_train_model",
        bash_command=(
            "cd /opt/airflow/mlops_project/btc_prediction && "
            "python train_and_predict.py "
            "--end-date '{{ execution_date.in_timezone('Asia/Ho_Chi_Minh').strftime('%Y-%m-%d %H:%M:%S') }}'"
        ),
    )

    # Luồng chạy: ETL xong mới train
    etl_task >> train_task
