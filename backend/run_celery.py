import multiprocessing
import subprocess
import time

""" 
//run celery Windows
celery -A backend worker --loglevel=info --pool=solo
//or 
run_celery.py
////
//run task
python manage.py shell
from app.tasks import cleanup_sessions
cleanup_sessions.delay()
"""

def run_celery_worker():
    """Функция для запуска в отдельном процессе"""
    try:
        subprocess.call([
            'celery', '-A', 'backend', 'worker',
            '--loglevel=info',
            '--pool=solo',
            '--concurrency=4'
        ])
    except KeyboardInterrupt:
        print("Worker остановлен")


def start_worker_in_process():
    """Запуск worker в отдельном процессе"""
    process = multiprocessing.Process(target=run_celery_worker)
    process.start()
    print(f"Worker запущен в процессе с PID: {process.pid}")
    return process



if __name__ == "__main__":
    worker_process = start_worker_in_process()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Останавливаем worker...")
        worker_process.terminate()
        worker_process.join()