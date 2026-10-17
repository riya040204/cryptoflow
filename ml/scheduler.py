
import time
import schedule
from anomaly_detection import detect_anomalies


def run_detection():
    print("\nRunning scheduled anomaly detection...", flush=True)
    try:
        detect_anomalies()
    except Exception as error:
        print(f"Detection failed: {error}", flush=True)


if __name__ == "__main__":
    print("CryptoFlow ML Scheduler Started", flush=True)
    run_detection()
    schedule.every(60).seconds.do(run_detection)

    while True:
        schedule.run_pending()
        time.sleep(1)
