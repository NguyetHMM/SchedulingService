
import pandas as pd
import random
import copy
import time
from datetime import datetime, date, timedelta
import calendar
import math
import re
from collections import Counter

WORD = re.compile(r"\w+")
MIN_DISTANCE = 15


class Job:
    def __init__(self, id, name, early_start_time, late_finish_time, start_time, finish_time, estimated_time, flextime = 1):
        self.id = id
        self.name = name
        self.early_start_time = early_start_time
        self.late_finish_time = late_finish_time
        self.job_start_time = job_start_time
        self.job_finish_time = job_finish_time
        self.estimated_time = estimated_time
        self.flextime = flextime

class TimeSlot:
    def __init__(self, id, start_time, end_time):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time

class Schedule:
    def __init__(self, id, start_time, end_time, lateness, breaking_time_slots, working_time_slots = []):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.lateness = lateness
        self.breaking_time_slots = breaking_time_slots
        self.working_time_slots = working_time_slots

# total_fixed_time = 0
# for fft in filter_fixed_time :
#     total_fixed_time += minutes_between_two_date(later_date = (fft['to_time']),first_date=(fft['from_time']))
# print(minutes_between_two_date(later_date = toDate(recommended_schedule_to),first_date=toDate(recommended_schedule_from)) - total_fixed_time)

def get_fixed_time(break_time, jobs, recommended_schedule_from, recommended_schedule_to):
    fixed_time = break_time
    fixed_time.append({'from_time': toDate(recommended_schedule_from), 'to_time': toDate(recommended_schedule_from)})
    fixed_time.append({'from_time': toDate(recommended_schedule_to), 'to_time': toDate(recommended_schedule_to)})
    for job in jobs:
        if job['flextime'] == 0:
            fixed_time.append(
                {'from_time': job['early_start_time'], 'to_time': job['late_finish_time']})
    fixed_time.sort(key=lambda x: x['from_time'])
    return fixed_time

def get_filter_fixed_time(fixed_time, min_distance):
    filter_fixed_time = [fixed_time[0]]
    for i in range(1, len(fixed_time)):
        if(int((fixed_time[i]['from_time'] - filter_fixed_time[-1]['to_time']).total_seconds() / 60) <= min_distance):
            filter_fixed_time[-1]['to_time'] = fixed_time[i]['to_time']
        else:
            filter_fixed_time.append(fixed_time[i])
    return filter_fixed_time

def get_recent_working_time_slots(schedule_working_time_slots, recommended_schedule_from):

    return

def check_history_schedule(schedule_breaking_time_slots, flextime_jobs):
    for job in flextime_jobs:
        for time_slot in schedule_breaking_time_slots:
            get_cosine_similarity(job['name'], schedule_breaking_time_slots[job_])
    return

# Sinh cá thể trong quần thể

def on_generation(break_time, jobs, recommended_schedule_from, recommended_schedule_to):
    fixed_time = get_fixed_time(break_time, jobs, recommended_schedule_from, recommended_schedule_to)
    min_distance = MIN_DISTANCE
    filter_fixed_time = get_filter_fixed_time(fixed_time, min_distance)
    flextime_job_ids = []
    for job in jobs:
        if job['flextime'] == 1:
            flextime_job_ids.append(job['id'])

    population = []
    num_individual = 5
    for i in range(num_individual):
        random.shuffle(flextime_job_ids)
        population.append({'individual_id': i, 'flextime_job_ids': flextime_job_ids[:]})
        individual_schedule = set_individual_schedule(flextime_job_ids=population[i]['flextime_job_ids'], filter_fixed_time=copy.deepcopy(filter_fixed_time), jobs=jobs)
        population[i]['individual_schedule'] = individual_schedule
        
    return population

def set_individual_schedule(flextime_job_ids, filter_fixed_time, jobs):
    individual_schedule = []
    filter_fixed_time_index = 0
    flextime_jobs=[]
    for j in flextime_job_ids :
        for job in jobs :
            if (job['id']==j):
                flextime_jobs.append(job)
    for job in flextime_jobs :
        job['remaining_time'] = job['estimated_time']
        while job['remaining_time'] > 0 :
            x = minutes_between_two_date(later_date = filter_fixed_time[filter_fixed_time_index+ 1]['from_time'], first_date = filter_fixed_time[filter_fixed_time_index]['to_time'])
            if job['remaining_time'] < x:
                individual_schedule.append({
                    'id': job['id'],
                    'start_time': filter_fixed_time[filter_fixed_time_index]['to_time'],
                    'duration': job['remaining_time'],
                    'remaining_time': 0
                    })
                filter_fixed_time[filter_fixed_time_index]['to_time'] += timedelta(minutes=(job['remaining_time']))
                job['remaining_time'] = 0

            elif job['remaining_time'] == x:
                individual_schedule.append({
                    'id': job['id'],
                    'start_time': filter_fixed_time[filter_fixed_time_index]['to_time'],
                    'duration': job['remaining_time'],
                    'remaining_time': 0
                    })
                job['remaining_time'] = 0
                filter_fixed_time_index = filter_fixed_time_index + 1
            else:
                individual_schedule.append({
                    'id': job['id'],
                    'start_time': filter_fixed_time[filter_fixed_time_index]['to_time'],
                    'duration': x,
                    'remaining_time': job['remaining_time'] - x
                    })
                job['remaining_time'] = job['remaining_time'] - x
                filter_fixed_time_index = filter_fixed_time_index + 1
    # printListObject(individual_schedule)
    # print('_______')
    return individual_schedule

def minutes_between_two_date(later_date, first_date):
    duration = later_date - first_date
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0]
    return minutes


def fitness_func(individual_schedule, flextime_job_ids, jobs):
    flextime_jobs=[]
    for j in flextime_job_ids :
        for job in jobs :
            if (job['id']==j):
                flextime_jobs.append(job)
    schedule_lateness = 0
    for schedule in individual_schedule:
        if schedule['remaining_time'] == 0:
            for job in flextime_jobs:
                if job['id'] == schedule['id'] :
                    if (schedule['start_time'] + timedelta(minutes=(schedule['duration']))) > job['late_finish_time']:
                        job['lateness'] = minutes_between_two_date((schedule['start_time'] + timedelta(minutes=(schedule['duration']))), job['late_finish_time'])
                    else:
                        job['lateness'] = 0
                    schedule_lateness += job['lateness']
    # print(schedule_lateness)
    # print(flextime_job_ids)
    return schedule_lateness

def on_selection(population):
    selected_population = population
    selected_population.sort(key=lambda x: x['lateness'])
    temp = {}
    for p in selected_population:
        temp[p['lateness']] = p
    selected_population = list(temp.values())
    return selected_population[:2]

def on_crossover(parents):
    flextime_job_ids = parents[0]['flextime_job_ids']
    parents_1 = parents[0]['flextime_job_ids']
    parents_2 = parents[1]['flextime_job_ids']
    temp_child_1 = []
    temp_child_2 = []
    child_1 = []
    child_2 = []
    while ( temp_child_1 == temp_child_2):
        temp_child_1 = []
        temp_child_2 = []
        x = random.randint(2,(len(flextime_job_ids)-1))  
        crossover_gens = random.sample(parents[0]['flextime_job_ids'],x)
        for id in parents_1:
            if id in crossover_gens:
                temp_child_1.append(id)
        for id in parents_2:
            if id in crossover_gens:
                temp_child_2.append(id)
    i = 0
    for p in parents_1:
        if p in temp_child_1:
            child_1.append(temp_child_2[i])
            i+=1
        else:
            child_1.append(p)
    j = 0
    for p in parents_2:
        if p in temp_child_2:
            child_2.append(temp_child_1[j])
            j+=1
        else:
            child_2.append(p)
    return child_1, child_2

def on_mutation(individual):
    mutation_gens = random.sample(individual['flextime_job_ids'],2)
    a, b = individual['flextime_job_ids'].index(mutation_gens[0]), individual['flextime_job_ids'].index(mutation_gens[1])
    individual['flextime_job_ids'][b], individual['flextime_job_ids'][a] = individual['flextime_job_ids'][a], individual['flextime_job_ids'][b]
    return individual

def toDate(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

def printListObject(listObject):
    for item in listObject:
        print(item)

def main():
    start = time.time()
    recommended_schedule_from = '2021-12-01 08:00:00'
    recommended_schedule_to = '2021-11-19 17:00:00'
    jobs = pd.read_excel(r'./data/jobs.xlsx').to_dict('records')
    break_time = pd.read_excel(r'./data/breakTime.xlsx').to_dict('records')
    schedule_working_time_slots = pd.read_excel(r'./data/scheduled.xlsx').to_dict('records')
    # for working_time_slot in schedule_working_time_slots:
        # print(schedule_working_time_slot['start_time'])
        # > (toDate(recommended_schedule_from) - timedelta(days=21)))
    schedule_working_time_slots_new = [ schedule_working_time_slot for schedule_working_time_slot in schedule_working_time_slots if schedule_working_time_slot['start_time'] > (toDate(recommended_schedule_from) - timedelta(days=21))]
    print(schedule_working_time_slots_new)

    # population = on_generation(break_time=break_time, jobs=jobs, recommended_schedule_from=recommended_schedule_from,
    #               recommended_schedule_to=recommended_schedule_to)
    # for i in range(len(population)):
    #     population[i]['lateness'] = fitness_func(individual_schedule = population[i]['individual_schedule'], flextime_job_ids = population[i]['flextime_job_ids'], jobs=jobs)
    
    # two_best_individuals = on_selection(population)
    # # print(two_best_individuals)
    # x= on_crossover(parents = two_best_individuals)
    # print(x, "crossover")
    # on_mutation(individual = two_best_individuals[0])
    end = time.time()
    print(end-start)

def reuse_scheduled(break_time, jobs):
    recommended_schedule_from = '2021-11-15 08:00:00'
    recommended_schedule_to = '2021-11-17 06:45:00'
    schedule_working_time_slots = pd.read_excel(r'./data/test_reuse_scheduled.xlsx').to_dict('records')
    jobs = pd.read_excel(r'./data/test_reuse_scheduled_jobs.xlsx').to_dict('records')

    recent_schedule_working_time_slots = [ schedule_working_time_slot for schedule_working_time_slot in schedule_working_time_slots if schedule_working_time_slot['start_time'] > (toDate(recommended_schedule_from) - timedelta(days=21))]
    weekday_count(recommended_schedule_from, recommended_schedule_to)

    fixed_time = get_fixed_time(break_time, jobs, recommended_schedule_from, recommended_schedule_to)
    min_distance = MIN_DISTANCE
    filter_fixed_time = get_filter_fixed_time(fixed_time, min_distance)
    
    flextime_jobs = []
    for job in jobs:
        if job['flextime'] == 1:
            flextime_jobs.append(job)
    
    weekday = weekday_count(start = recommended_schedule_from, end = recommended_schedule_to)
    updated_filter_fixed_time = filter_fixed_time
    updated_flextime_jobs = flextime_jobs

    for job in flextime_jobs:
        for t in recent_schedule_working_time_slots:
            job_name = text_to_vector(job['name'].lower())
            recent_job_name = text_to_vector(t['task_name'].lower())
            cosine_similar = get_cosine(job_name, recent_job_name)
            
            if cosine_similar >= 0.8:
                reuse_start_time = t['start_time'].strftime('%H:%M:%S')
                reuse_weekday = weekday[f"{t['start_time'].strftime('%A')}"]
                reuse_datetime = []
                for w in reuse_weekday :
                    reuse_date = w.strftime('%Y-%m-%d')
                    x = reuse_date + ' ' + reuse_start_time
                    reuse_datetime.append(toDate(x))
                print(reuse_datetime)
                for i in range(len(reuse_datetime)):
                    valid_reuse_datetime, filter_fixed_time_index = check_valid_reuse_datetime(reuse_datetime[i], filter_fixed_time)
                    if not valid_reuse_datetime:
                        i+=1
                    else:
                        updated_filter_fixed_time = add_job_to_fixed_time(updated_filter_fixed_time, filter_fixed_time_index, job, reuse_datetime[i])
                        # updated_flextime_jobs = update_flextime_jobs(job, flextime_jobs)
    
    return updated_filter_fixed_time
    # , updated_flextime_jobs

# def update_flextime_jobs(job, flextime_jobs):

#     return updated_flextime_jobs

def add_job_to_fixed_time(updated_filter_fixed_time, filter_fixed_time_index, job, reuse_datetime):
    print(job, "job")
    if reuse_datetime < job['early_start_time']:
        return updated_filter_fixed_time
    else :
    # print(updated_filter_fixed_time[filter_fixed_time_index]['to_time'], 'abacabcc')
        updated_filter_fixed_time_index = 0
        if updated_filter_fixed_time[filter_fixed_time_index]['to_time'] < reuse_datetime:
            updated_filter_fixed_time.append({
                'from_time': reuse_datetime,
                'to_time': reuse_datetime
            })
            updated_filter_fixed_time.sort(key=lambda x: x['from_time'])
            updated_filter_fixed_time = get_filter_fixed_time(fixed_time = updated_filter_fixed_time, min_distance = MIN_DISTANCE)
            updated_filter_fixed_time_index = filter_fixed_time_index + 1
        elif updated_filter_fixed_time[filter_fixed_time_index]['to_time'] == reuse_datetime:
            updated_filter_fixed_time_index = filter_fixed_time_index
        job['remaining_time'] = job['estimated_time']
        temp_working_time_slots = []
        while job['remaining_time'] > 0 :
            x = minutes_between_two_date(later_date = updated_filter_fixed_time[updated_filter_fixed_time_index+ 1]['from_time'], first_date = updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'])
            if job['remaining_time'] < x:
                temp_working_time_slots.append({
                    'id': job['id'],
                    'start_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'duration': job['remaining_time'],
                    'remaining_time': 0
                    })
                job['finish_time'] = updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'] + timedelta(minutes=(job['remaining_time']))
                updated_filter_fixed_time.append({
                    'from_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'to_time': job['finish_time']
                    })            
                updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'] = job['finish_time']
                job['remaining_time'] = 0
                print(job)
            elif job['remaining_time'] == x:
                temp_working_time_slots.append({
                    'id': job['id'],
                    'start_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'duration': job['remaining_time'],
                    'remaining_time': 0
                    })
                job['finish_time'] = updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'] + timedelta(minutes=(job['remaining_time']))
                updated_filter_fixed_time.append({
                    'from_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'to_time': job['finish_time']
                    })
                job['remaining_time'] = 0
                print(job)
                updated_filter_fixed_time_index = updated_filter_fixed_time_index + 1
            else:
                temp_working_time_slots.append({
                    'id': job['id'],
                    'start_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'duration': x,
                    'remaining_time': job['remaining_time'] - x
                    })
                updated_filter_fixed_time.append({
                    'from_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'],
                    'to_time': updated_filter_fixed_time[updated_filter_fixed_time_index]['to_time'] + timedelta(minutes=(x))
                    })
                job['remaining_time'] = job['remaining_time'] - x
                updated_filter_fixed_time_index = updated_filter_fixed_time_index + 1   
        print(temp_working_time_slots[-1],'job')
        if temp_working_time_slots[-1]['finish_time'] > temp_working_time_slots[-1]['late_finish_time']:
            temp_id = temp_working_time_slots[-1]['id']
            temp_working_time_slots = list(filter(lambda x: x['id']!= temp_id, temp_working_time_slots))
        updated_filter_fixed_time.sort(key=lambda x: x['from_time']) #chưa update
        updated_filter_fixed_time = get_filter_fixed_time(updated_filter_fixed_time, MIN_DISTANCE)

        return updated_filter_fixed_time


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def check_valid_reuse_datetime(checked_datetime, filter_fixed_time):
    # checked_datetime = toDate(checked_datetime)
    for i in range(len(filter_fixed_time)-1):
        # if ( i == 1 and filter_fixed_time[i]['to_time'] == filter_fixed_time[i]['from_time']):
        #     return True
        if (filter_fixed_time[i]['to_time'] <= checked_datetime and checked_datetime < filter_fixed_time[i+1]['from_time']):
            print(filter_fixed_time[i]['to_time'], checked_datetime, filter_fixed_time[i+1]['from_time'])
            return True, i
    return False, i

def weekday_count(start, end):
    start_date  = toDate(start).date()
    end_date    = toDate(end).date()
    week        = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday' :[],
        'Thursday' : [],
        'Friday': [],
        'Saturday': [],
        'Sunday': []
    }
    delta =  end_date - start_date
    for i in range(delta.days + 1):
        day       = calendar.day_name[(start_date + timedelta(days=i)).weekday()]
        week[day].append(start_date + timedelta(days=i))
    return week

if __name__ == '__main__':
    # main()
    # test()
    # weekday_count('2021-11-15 08:00:00', '2021-11-30 17:00:00')
    break_time = pd.read_excel(r'./data/test_reuse_scheduled_breakTime.xlsx').to_dict('records')
    jobs = pd.read_excel(r'./data/test_reuse_scheduled_jobs.xlsx').to_dict('records')
    ssf = '2021-11-15 08:00:00'
    sst = '2021-11-17 06:45:00'
    fixed_time = get_fixed_time(break_time, jobs, ssf, sst)
    min_distance = MIN_DISTANCE
    filter_fixed_time = get_filter_fixed_time(fixed_time, min_distance)
    # printListObject(filter_fixed_time)
    x = check_valid_reuse_datetime(checked_datetime = toDate('2021-11-19 17:00:00'), filter_fixed_time = filter_fixed_time)
    print(x)
    reuse_scheduled(break_time, jobs)