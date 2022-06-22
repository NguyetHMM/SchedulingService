from typing import List
import time
from datetime import datetime, date, timedelta
from src.core.src.common import generate_uuid


class Job:
    id: str
    name: str
    early_start_time: datetime
    late_finish_time: datetime
    start_time: datetime
    finish_time: datetime
    estimated_time: int
    flextime: bool

    def __init__(self, id, name, early_start_time, late_finish_time, start_time, finish_time, estimated_time,
                 flextime=1):
        self.id = id
        self.name = name
        self.early_start_time = early_start_time
        self.late_finish_time = late_finish_time
        self.start_time = start_time
        self.finish_time = finish_time
        self.estimated_time = estimated_time
        self.flextime = flextime

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'early_start_time': datetime.strftime(self.early_start_time, '%Y-%m-%d %H:%M:%S'),
            'late_finish_time': datetime.strftime(self.late_finish_time, '%Y-%m-%d %H:%M:%S'),
            'start_time': self.start_time,
            'finish_time': self.finish_time,
            'estimated_time': self.estimated_time,
            'flextime': self.flextime,
        }


class TimeSlot:
    def __init__(self, id, start_time, end_time):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time

    def serialize(self):
        return {
            'id': self.id,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S'),
        }


class WorkingTimeSlot(TimeSlot):
    def __init__(self, id, start_time, end_time, job: Job, remaining_time):
        super().__init__(id, start_time, end_time)
        self.job = job
        self.remaining_time = remaining_time

    def serialize(self):
        return {
            'id': self.id,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S'),
            'job': self.job.serialize(),
            'remaining_time': self.remaining_time
        }


class BreakingTimeSlot(TimeSlot):
    def __init__(self, id, start_time, end_time):
        super().__init__(id, start_time, end_time)

    def serialize(self):
        return {
            'id': self.id,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S'),
        }


class FreeTimeSlot(TimeSlot):
    def __init__(self, id, start_time, end_time):
        super().__init__(id, start_time, end_time)

    def serialize(self):
        return {
            'id': self.id,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S'),
        }


class Schedule:
    id: str
    time_slots: List[TimeSlot]
    lateness: float
    start_time: datetime
    end_time: datetime

    def __init__(self, start_time, end_time):
        self.id = generate_uuid()
        self.start_time = start_time
        self.end_time = end_time
        self.time_slots = []
        # time_slot_id = generate_uuid()
        # free_time_slot = FreeTimeSlot(id = time_slot_id, start_time = start_time, end_time= end_time)
        # self.time_slots.append(free_time_slot)

    def serialize(self):
        # for item in self.time_slots:
        #     print(type(item), item)
        # # print(self.time_slots[10].serialize())
        return {
            'id': self.id,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S'),
            'time_slots': [t.serialize() for t in self.time_slots],
            # 'lateness': self.lateness
        }


class Individual:
    id: str
    flextime_jobs: List[Job]
    schedule: Schedule
    lateness: float

    def __init__(self, flextime_jobs: object, schedule: object) -> object:
        self.id = generate_uuid()
        self.flextime_jobs = flextime_jobs
        self.schedule = schedule
