from pkg_resources import require
from flask_restful import Resource
from flask import jsonify
from flask_restful import reqparse
import json
# from bson.json_util import dumps
from src.services.scheduling_generate_service import SchedulingGenerateService
from src.core.src.main2 import *
# from task.workers import add_schedule, scheduling_worker

class SchedulingGenerate(Resource):
    def get(self):
        return 1

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('schedule_start_time')
        parser.add_argument('schedule_end_time')
        parser.add_argument('jobs', type=dict, action="append")
        parser.add_argument('scheduled_working_time_slots', type=dict, action="append")
        parser.add_argument('breaking_time_slots', type=dict, action="append")
        args = parser.parse_args()

        if not args.scheduled_working_time_slots:
            args.scheduled_working_time_slots = []

        # task = scheduling_worker.apply_async((args,))

        scheduling_generate_service = SchedulingGenerateService()

        return scheduling_generate_service.scheduling_generate(schedule_start_time=args.schedule_start_time,
                                                               schedule_end_time=args.schedule_end_time,
                                                               breaking_time_slots=args.breaking_time_slots,
                                                               jobs=args.jobs,
                                                               scheduled_working_time_slots=args.scheduled_working_time_slots)
# args.scheduled_working_time_slots

