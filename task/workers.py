import time
from celery.result import AsyncResult

from app_celery import celery
from src.services.scheduling_generate_service import SchedulingGenerateService

def get_status(task_id):
    return AsyncResult(task_id, app=celery)

@celery.task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5}, track_started=True)
def add_schedule():
    try:
        time.sleep(30)
        # Call core Speech recognition
        # Lay ket qua luu DB, export file .json
        # raise ValueError()

        return {
            'message': 'result.json'
        }
    except Exception as e:
        raise e

@celery.task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5}, track_started=True)
def scheduling_worker(args):
    scheduling_generate_service = SchedulingGenerateService()
    return scheduling_generate_service.scheduling_generate(schedule_start_time=args['schedule_start_time'],
                                                    schedule_end_time=args['schedule_end_time'],
                                                    breaking_time_slots=args['breaking_time_slots'],
                                                    jobs=args['jobs'],
                                                    scheduled_working_time_slots=args['scheduled_working_time_slots'])
    return 'Success'