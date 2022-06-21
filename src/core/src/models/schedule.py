from .schedule_breaking_time_slots import ScheduleBreakingTimeSlots
class Schedule:
    def __init__(self, id, start_time, end_time, lateness, breaking_time_slots : ScheduleBreakingTimeSlots, working_time_slots = []):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.lateness = lateness
        self.breaking_time_slots = breaking_time_slots
        self.working_time_slots = working_time_slots