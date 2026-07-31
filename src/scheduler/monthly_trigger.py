import schedule
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline():
    logging.info("Starting automated monthly AI pipeline execution...")
    try:
        # Calls the main orchestrator script
        result = subprocess.run(["python", "src/main.py"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Monthly pipeline completed successfully.")
        else:
            logging.error(f"Pipeline failed with error:\n{result.stderr}")
    except Exception as e:
        logging.error(f"Failed to trigger pipeline: {e}")

# This sets up the local Python scheduler (useful for VPS or always-on servers).
# In production, the GitHub Actions cron workflow (.github/workflows/monthly_pipeline.yml) is preferred.
# schedule.every(30).days.do(run_pipeline)
# For demo/presentation purposes, scheduling to run on the 1st of every month:

def schedule_monthly():
    # A simple loop to check if it is the 1st of the month (crude local implementation)
    logging.info("Local scheduler started. Waiting for the 1st of the month...")
    import datetime
    
    while True:
        now = datetime.datetime.now()
        if now.day == 1 and now.hour == 0 and now.minute == 0:
            run_pipeline()
            # Sleep for a day to avoid triggering multiple times
            time.sleep(86400)
        else:
            # Check every hour
            time.sleep(3600)

if __name__ == "__main__":
    schedule_monthly()
