import subprocess

if __name__ == "__main__":
    subprocess.run([
        "prefect", "deployment", "build",
        "etl_script.py:etl_flow_with_schedule",
        "-n", "daily_stock_etl",
        "-q", "default",
        "--cron", "0 6 * * *",
        "--timezone", "Asia/Taipei",
        "-a"
    ])
