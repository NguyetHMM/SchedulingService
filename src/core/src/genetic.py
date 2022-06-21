from math import inf
from src.core.src.models import *
from src.core.src.common import *
from typing import List
import random
import copy
import time
from datetime import datetime, date, timedelta

LATENESS_MAX = math.inf

def on_generation(schedule: Schedule, timeline: List[TimeSlot],start_time_reused_jobs: List[Job], jobs: List[Job]):
    # print("ongeneration")
    flextime_jobs = [job for job in jobs if (job.flextime == 1 and job not in start_time_reused_jobs)]
    population = []
    num_individual = 5
    for i in range(num_individual):
        # print("______________________________")
        # print("individual", i)
      
        random.shuffle(flextime_jobs)
        individual = Individual(flextime_jobs=flextime_jobs[:], schedule=Schedule(start_time=schedule.start_time, end_time=schedule.end_time))
        individual.schedule.time_slots = set_individual_schedule(flextime_jobs=individual.flextime_jobs, timeline=copy.deepcopy(timeline))
        population.append(individual)
        
        # print(end-start, "individual", i)
        # print("______________________________")
    return population

def set_individual_schedule(flextime_jobs: List[Job], timeline: List[TimeSlot]):
    temp_timeline = timeline.copy()
    temp_timeline_index = 0
    for job in flextime_jobs:
        # print(job, "job in set timeline")
        job_remaining_time = job.estimated_time
        while job_remaining_time > 0:
            x = minutes_between_two_date(
                later_date=temp_timeline[temp_timeline_index + 1].start_time, first_date=temp_timeline[temp_timeline_index].end_time)
            if job_remaining_time < x:
                added_working_time_slot = WorkingTimeSlot(
                    id=generate_uuid(),
                    start_time=temp_timeline[temp_timeline_index].end_time,
                    end_time=temp_timeline[temp_timeline_index].end_time +
                    timedelta(minutes=(job_remaining_time)),
                    job=job,
                    remaining_time=0
                )
                temp_timeline.append(added_working_time_slot)
                job_finish_time = temp_timeline[temp_timeline_index].end_time + timedelta(
                    minutes=(job_remaining_time))
                temp_timeline[temp_timeline_index].end_time = job_finish_time
                job_remaining_time = 0
            elif job_remaining_time == x:
                added_working_time_slot = WorkingTimeSlot(
                    id=generate_uuid(),
                    start_time=temp_timeline[temp_timeline_index].end_time,
                    end_time=temp_timeline[temp_timeline_index].end_time +
                    timedelta(minutes=(job_remaining_time)),
                    job=job,
                    remaining_time=0
                )
                temp_timeline.append(added_working_time_slot)
                job_finish_time = temp_timeline[temp_timeline_index].end_time + timedelta(
                    minutes=(job_remaining_time))
                job_remaining_time = 0
                temp_timeline_index = temp_timeline_index + 1
            else:
                added_working_time_slot = WorkingTimeSlot(
                    id=generate_uuid(),
                    start_time=temp_timeline[temp_timeline_index].end_time,
                    end_time=temp_timeline[temp_timeline_index].end_time +
                    timedelta(minutes=(x)),
                    job=job,
                    remaining_time=job_remaining_time - x
                )
                temp_timeline.append(added_working_time_slot)
                job_remaining_time = job_remaining_time - x
                temp_timeline_index = temp_timeline_index + 1
    return temp_timeline

def fitness_func(individual: Individual):
    flextime_jobs = individual.flextime_jobs
    schedule_lateness = 0
    working_time_slots = [w for w in individual.schedule.time_slots if isinstance(w, WorkingTimeSlot)]
    for time_slot in working_time_slots:
        for job in flextime_jobs:
            if job.id == time_slot.job.id :
                if time_slot.start_time < job.early_start_time:
                    return LATENESS_MAX
                if time_slot.remaining_time == 0:
                    if time_slot.end_time > job.late_finish_time:
                        job_lateness = minutes_between_two_date(time_slot.end_time, job.late_finish_time)
                    else:
                        job_lateness = 0
                    schedule_lateness += job_lateness
    return schedule_lateness

def on_selection(population: List[Individual]):
    population.sort(key=lambda x: x.lateness)
    temp = {}
    for p in population:
        temp[p.lateness] = p
    population = list(temp.values())
    return population[:2]

def on_crossover(individual1: Individual, individual2: Individual):
    flextime_job_ids = [ i.id for i in individual1.flextime_jobs]
    parents_1 = [ i.id for i in individual1.flextime_jobs]
    parents_2 = [ i.id for i in individual2.flextime_jobs]
    temp_child_1_flextime_job_ids = []
    temp_child_2_flextime_job_ids = []
    child_1_flextime_job_ids = []
    child_2_flextime_job_ids = []
    while ( temp_child_1_flextime_job_ids == temp_child_2_flextime_job_ids):
        temp_child_1_flextime_job_ids = []
        temp_child_2_flextime_job_ids = []
        x = random.randint(2,(len(flextime_job_ids)-1))  
        crossover_gens = random.sample(parents_1,x)
        for id in parents_1:
            if id in crossover_gens:
                temp_child_1_flextime_job_ids.append(id)
        for id in parents_2:
            if id in crossover_gens:
                temp_child_2_flextime_job_ids.append(id)
    i = 0
    for p in parents_1:
        if p in temp_child_1_flextime_job_ids:
            child_1_flextime_job_ids.append(temp_child_2_flextime_job_ids[i])
            i+=1
        else:
            child_1_flextime_job_ids.append(p)
    j = 0
    for p in parents_2:
        if p in temp_child_2_flextime_job_ids:
            child_2_flextime_job_ids.append(temp_child_1_flextime_job_ids[j])
            j+=1
        else:
            child_2_flextime_job_ids.append(p)

    return child_1_flextime_job_ids, child_2_flextime_job_ids

def on_mutation(individual: Individual):
    new_flextime_jobs = individual.flextime_jobs
    mutation_gens = random.sample(new_flextime_jobs,2)
    a, b = new_flextime_jobs.index(mutation_gens[0]), new_flextime_jobs.index(mutation_gens[1])
    new_flextime_jobs[b], new_flextime_jobs[a] = new_flextime_jobs[a], new_flextime_jobs[b]
    return new_flextime_jobs

