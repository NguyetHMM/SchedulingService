import json

from src.core.src.input_data_validation import validate_input_data
from src.core.src.models import *
from src.core.src.common import *
from src.core.src.genetic import *
from typing import List
import pandas as pd
# from bson.json_util import dumps



def schedule_generate(start_time, end_time):
    schedule = Schedule(start_time=start_time, end_time=end_time)
    return schedule


def add_breaking_time_slots(schedule: Schedule, time_slots: List[BreakingTimeSlot]):
    """_summary_

    Args:
        schedule (Schedule): _description_
        time_slots (List[BreakingTimeSlot]): _description_

    Returns:
        _type_: _description_
    """
    # print('add_breaking_time_slots')
    start_time_slot = TimeSlot(id=generate_uuid(), start_time=schedule.start_time, end_time=schedule.start_time)
    end_time_slot = TimeSlot(id=generate_uuid(), start_time=schedule.end_time, end_time=schedule.end_time)
    schedule.time_slots.append(start_time_slot)
    schedule.time_slots.append(end_time_slot)
    schedule.time_slots += time_slots
    return schedule


def add_fixed_time_working_time_slots(schedule: Schedule, jobs: List[Job]):
    # print('add_fixed_time_working_time_slots')
    for job in jobs:
        if job.flextime == 0:
            w = WorkingTimeSlot(id= generate_uuid(), start_time=job.early_start_time,
                                end_time=job.late_finish_time, job=job, remaining_time=0)
            schedule.time_slots.append(w)
    return schedule


def filter_list_time_slots(time_slots: List[TimeSlot], min_distance=MIN_DISTANCE):
    for x in time_slots:
        print(type(x), x)
    time_slots.sort(key=lambda x: x.start_time)
    filter_time_slots = [time_slots[0]]
    for i in range(1, len(time_slots)):
        if(int((time_slots[i].start_time - filter_time_slots[-1].end_time).total_seconds() / 60) <= min_distance):
            filter_time_slots[-1].end_time = time_slots[i].end_time
        else:
            filter_time_slots.append(time_slots[i])
    return filter_time_slots


def add_reused_working_time_slots(schedule: Schedule, reused_working_time_slots: List[WorkingTimeSlot], jobs: List[Job]):
    # print('add_reused_working_time_slots')
    timeline = schedule.time_slots.copy()
    start_time_reused_job = []
    timeline = filter_list_time_slots(timeline)
    flextime_jobs = [job for job in jobs if job.flextime == 1]
    weekdays = weekday_count(schedule.start_time, schedule.end_time)
    for job in flextime_jobs:
        for t in reused_working_time_slots:
            job_name = text_to_vector(job.name.lower())
            recent_job_name = text_to_vector(t.job.name.lower())
            cosine_similar = get_cosine(job_name, recent_job_name)
            if cosine_similar >= MIN_COSINE_SIMILARITY:
                # print(job.__dict__)
                # print('______')
                reuse_start_time = t.start_time.strftime('%H:%M:%S')
                reuse_weekday = weekdays[f"{t.start_time.strftime('%A')}"]
                reuse_datetime = []
                for w in reuse_weekday:
                    reuse_date = w.strftime('%Y-%m-%d')
                    x = reuse_date + ' ' + reuse_start_time
                    reuse_datetime.append(string_to_datetime(x))
                # print(reuse_datetime, "reuse_datetime")
                for i in range(len(reuse_datetime)):
                    valid_reuse_datetime, timeline_index = check_valid_reuse_datetime(
                        reuse_datetime[i], timeline)
                    # print(valid_reuse_datetime, timeline_index,
                    #       "valid_reuse_datetime, timeline_index")
                    if not valid_reuse_datetime:
                        i += 1
                    else:
                        # print(reuse_datetime[i], "reuse_datetime")
                        timeline, start_time_reused_job = add_job_to_timeline(
                            timeline, start_time_reused_job, timeline_index, job, reuse_datetime[i])
    return timeline, start_time_reused_job


def check_valid_reuse_datetime(checked_datetime: datetime, timeline: List[TimeSlot]):
    for i in range(len(timeline)-1):
        if (timeline[i].end_time <= checked_datetime and checked_datetime < timeline[i+1].start_time):
            return True, i
    return False, i


def add_job_to_timeline(timeline: List[TimeSlot], start_time_reused_job: List[Job], timeline_index: int, job: Job, reuse_datetime: datetime):
    temp_timeline = timeline.copy()
    updated_start_time_reused_job = start_time_reused_job
    if reuse_datetime < job.early_start_time:
        return temp_timeline
    else:
        temp_timeline_index = 0
        if temp_timeline[timeline_index].end_time < reuse_datetime:
            added_time_slot = TimeSlot(
                id=generate_uuid(),
                start_time=reuse_datetime,
                end_time=reuse_datetime
            )
            temp_timeline.append(added_time_slot)
            temp_timeline.sort(key=lambda x: x.start_time)
            temp_timeline = filter_list_time_slots(
                time_slots=temp_timeline, min_distance=MIN_DISTANCE)
            temp_timeline_index = timeline_index + 1
        elif temp_timeline[timeline_index].end_time == reuse_datetime:
            temp_timeline_index = timeline_index

        job_remaining_time = job.estimated_time
        temp_timeline = temp_timeline.copy()
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

        if job_finish_time > job.late_finish_time:
            updated_timeline = timeline
        else:
            temp_timeline.sort(key=lambda x: x.start_time)
            updated_timeline = filter_list_time_slots(
                time_slots=temp_timeline, min_distance=MIN_DISTANCE)
            updated_start_time_reused_job.append(job)

        return updated_timeline, updated_start_time_reused_job

if __name__ == '__main__':
    start = time.time()
    ssf = string_to_datetime('2021-11-15 08:00:00')
    sst = string_to_datetime('2021-11-19 17:00:00')
    schedule = schedule_generate(start_time=ssf, end_time=sst)

    breaking = []
    jobs = []
    working_time_slots = [] #query
    all_jobs= [] #query
    recent_working_time_slots = []

    temp_breaking = pd.read_excel(r'./data/breakTime.xlsx').to_dict('records')
    temp_jobs = pd.read_excel(r'./data/jobs.xlsx').to_dict('records')
    temp_working_time_slots = pd.read_excel(r'./data/scheduled.xlsx').to_dict('records')
    temp_all_jobs = pd.read_excel(r'./data/all_jobs.xlsx').to_dict('records')

    for btime in temp_breaking:
        b = BreakingTimeSlot(
            id=btime['id'], start_time=btime['start_time'], end_time=btime['end_time'])
        breaking.append(b)
        print(b.__dict__)
    # print(dumps(breaking))

    for job in temp_jobs:
        j = Job(id=job['id'], name=job['name'], early_start_time=job['early_start_time'], late_finish_time=job['late_finish_time'],
                start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
        jobs.append(j)

    for job in temp_all_jobs:
        j = Job(id=job['id'], name=job['name'], early_start_time=job['early_start_time'], late_finish_time=job['late_finish_time'],
                start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
        all_jobs.append(j)

    temp_recent_working_time_slots = [time_slot for time_slot in temp_working_time_slots if time_slot['start_time'] > (
        schedule.start_time - timedelta(days=21))]

    # import json
    for t in temp_recent_working_time_slots:
        j = [e for e in all_jobs if e.id == t['job_id']]
        ts = WorkingTimeSlot(id=t['id'], start_time=t['start_time'],
                             end_time=t['end_time'], job=j[0], remaining_time=t['remaining_time'])
        recent_working_time_slots.append(ts)
        print(ts.__dict__)


    # with open('myfile.json', 'w', encoding ='utf8') as json_file:
    #     json.dump({'mix': recent_working_time_slots}, json_file)
    # print(dumps(recent_working_time_slots))


    schedule = add_breaking_time_slots(schedule, breaking)
    schedule = add_fixed_time_working_time_slots(schedule, jobs)

    timeline = []
    timeline, start_time_reused_jobs = add_reused_working_time_slots(
        schedule=schedule, reused_working_time_slots=recent_working_time_slots, jobs=jobs)

    if validate_input_data(schedule=schedule, jobs=jobs, timeline=timeline):
        generation = 0
        population = []
        p = on_generation(schedule= schedule, timeline=timeline, start_time_reused_jobs=start_time_reused_jobs, jobs=jobs)
        population.append(p)
        done = False
        for individual in population[generation]:
            individual.lateness = fitness_func(individual=individual)
            if individual.lateness == 0:
                print ('acceptable individual', individual.__dict__)
                done = True

        while not done:
            # print(population[generation],"(population[generation]", generation)
            new_generation = on_selection(population=population[generation])
            child_job_ids_on_crossover_1, child_job_ids_on_crossover_2 = on_crossover(new_generation[0], new_generation[1])
            for id in child_job_ids_on_crossover_1:
                flextime_jobs_1 = [job for job in new_generation[0].flextime_jobs if job.id == id]
            for id in child_job_ids_on_crossover_2:
                flextime_jobs_2 = [job for job in  new_generation[1].flextime_jobs if job.id == id]

            child_on_crossover_1 = Individual(flextime_jobs=flextime_jobs_1, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))
            child_on_crossover_2 = Individual(flextime_jobs=flextime_jobs_2, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))

            _, added_working_time_slots_on_crossover_1 = set_individual_schedule(flextime_jobs=flextime_jobs_1, timeline=copy.deepcopy(timeline))
            child_on_crossover_1.schedule.time_slots += added_working_time_slots_on_crossover_1

            _, added_working_time_slots_on_crossover_2 = set_individual_schedule(flextime_jobs=flextime_jobs_2, timeline=copy.deepcopy(timeline))
            child_on_crossover_1.schedule.time_slots += added_working_time_slots_on_crossover_2

            # child_on_crossover_1.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_1, timeline=copy.deepcopy(timeline))
            # child_on_crossover_2.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_2, timeline=copy.deepcopy(timeline))

            new_generation.append(child_on_crossover_1)

            new_generation.append(child_on_crossover_2)

            flextime_jobs_mutation = on_mutation(new_generation[0])
            # print(flextime_jobs_mutation, "flextime_jobs_mutation")

            child_on_mutation = Individual(flextime_jobs=flextime_jobs_mutation, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))
            _, added_working_time_slots_on_mutation = set_individual_schedule(flextime_jobs=flextime_jobs_mutation, timeline=copy.deepcopy(timeline))
            child_on_mutation.schedule.time_slots += added_working_time_slots_on_mutation
            # child_on_mutation.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_mutation, timeline=copy.deepcopy(timeline))
            new_generation.append(child_on_mutation)
            population.append(new_generation)
            for individual in new_generation:
                individual.lateness = fitness_func(individual=individual)
                if individual.lateness == 0:
                    print ('acceptable individual', individual.__dict__)
                    done = True
            # print(new_generation, "new_generation")
            population.append(new_generation)

            generation += 1

        total_len = 0
        for p in population:
            total_len+=len(p)
        print(total_len)




    end = time.time()
    print(end-start, "run time")


    # for x in timeline:
    #     print(x.__dict__)
    # print(x.__repr__())

    # reuse
    #________________________________

    # test_reuse_break_time = []
    # test_reuse_jobs = []
    # test_reuse_working = []
    # recent_test_reuse_working = []
    # test_all_jobs = []

    # temp_test_reuse_break_time = pd.read_excel(
    #     r'./data/test_reuse_scheduled_breakTime.xlsx').to_dict('records')
    # temp_test_reuse_jobs = test_reuse_scheduled_jobs = pd.read_excel(
    #     r'./data/test_reuse_scheduled_jobs.xlsx').to_dict('records')
    # temp_test_reuse_working = pd.read_excel(
    #     r'./data/test_reuse_scheduled.xlsx').to_dict('records')
    # temp_test_all_jobs = pd.read_excel(
    #     r'./data/test_reused_all_jobs.xlsx').to_dict('records')

    # for t in temp_test_reuse_break_time:
    #     b = BreakingTimeSlot(
    #         id=t['id'], start_time=t['start_time'], end_time=t['end_time'])
    #     test_reuse_break_time.append(b)

    # for job in temp_test_reuse_jobs:
    #     j = Job(id=job['id'], name=job['name'], early_start_time=job['early_start_time'], late_finish_time=job['late_finish_time'],
    #             start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
    #     test_reuse_jobs.append(j)

    # for job in temp_test_all_jobs:
    #     j = Job(id=job['id'], name=job['name'], early_start_time=job['early_start_time'], late_finish_time=job['late_finish_time'],
    #             start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
    #     test_all_jobs.append(j)

    # recent_temp_test_reuse_working = [time_slot for time_slot in temp_test_reuse_working if time_slot['start_time'] > (
    #     schedule.start_time - timedelta(days=21))]

    # for t in recent_temp_test_reuse_working:
    #     j = [e for e in test_all_jobs if e.id == t['job_id']]
    #     ts = WorkingTimeSlot(id=t['id'], start_time=t['start_time'],
    #                          end_time=t['end_time'], job=j[0], remaining_time=t['remaining_time'])
    #     recent_test_reuse_working.append(ts)

    # timeline = []
    # timeline, start_time_reused_job = add_reused_working_time_slots(
    #     schedule=schedule, reused_working_time_slots=recent_test_reuse_working, jobs=jobs)

    # # generation algorithm

    # for x in timeline:
    #     print(x.__dict__)

    # for x in start_time_reused_job:
    #     print(x.__dict__)

    #________________________________
    # test reuse

    # population = on_generation(schedule= schedule, timeline=timeline, start_time_reused_jobs=start_time_reused_job, jobs=jobs)
    # done = FALSE
    # while not done:
    #     print(population)
