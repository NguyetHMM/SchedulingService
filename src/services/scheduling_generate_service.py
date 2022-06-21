from flask import jsonify
from src.core.src.main2 import *
from src.core.src.common import generate_uuid

class SchedulingGenerateService:
    def scheduling_generate(self, schedule_start_time, schedule_end_time, jobs, scheduled_working_time_slots, breaking_time_slots):
        run_time_start = time.time()
        start_time = string_to_datetime(schedule_start_time)
        end_time = string_to_datetime(schedule_end_time)
        schedule_breaking_time_slots = []
        schedule_jobs = []
        recent_working_time_slots = [] 
        print(breaking_time_slots)
        for bt in breaking_time_slots:
            b = BreakingTimeSlot(id=bt['id'], start_time=string_to_datetime(bt['start_time']), end_time=string_to_datetime(bt['end_time']))
            schedule_breaking_time_slots.append(b)
        temp = copy.deepcopy(schedule_breaking_time_slots)
        print(temp)
        for i in range(len(temp)):
            print(temp[i].__dict__)
        for job in jobs:
            j = Job(id=job['id'], name=job['name'], early_start_time=string_to_datetime(job['early_start_time']), late_finish_time=string_to_datetime(job['late_finish_time']),
                    start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
            schedule_jobs.append(j)

        for t in scheduled_working_time_slots:
            t = WorkingTimeSlot(id=t['id'], start_time=string_to_datetime(t['start_time']),
                                end_time=string_to_datetime(t['end_time']), job=Job(id=t['job']['id'], name=t['job']['name'], early_start_time=string_to_datetime(t['job']['early_start_time']), late_finish_time=string_to_datetime(t['job']['late_finish_time']),
                    start_time=None, finish_time=None, estimated_time=t['job']['estimated_time'], flextime=t['job']['flextime']), remaining_time=t['remaining_time'])
            recent_working_time_slots.append(t)

        schedule = schedule_generate(start_time=start_time, end_time=end_time)
        schedule = add_breaking_time_slots(schedule, schedule_breaking_time_slots)
        schedule = add_fixed_time_working_time_slots(schedule, schedule_jobs)
        timeline = []
        timeline, start_time_reused_jobs = add_reused_working_time_slots(
        schedule=schedule, reused_working_time_slots=recent_working_time_slots, jobs=schedule_jobs)
        acceptable_individual ={}
        generation = 0
        population = []
        validated = validate_input_data(schedule=schedule, jobs=schedule_jobs, schedule_breaking_time_slots = temp)
        if validated['status']:
            p = on_generation(schedule= schedule, timeline=timeline, start_time_reused_jobs=start_time_reused_jobs, jobs=schedule_jobs)
            population.append(p)
            done = False
            for individual in population[generation]:
                individual.lateness = fitness_func(individual=individual)
                if individual.lateness == 0: 
                    acceptable_individual = individual
                    done = True

            while not done:
                new_generation = on_selection(population=population[generation])
                child_job_ids_on_crossover_1, child_job_ids_on_crossover_2 = on_crossover(new_generation[0], new_generation[1])
                for id in child_job_ids_on_crossover_1:
                    flextime_jobs_1 = [job for job in new_generation[0].flextime_jobs if job.id == id]
                for id in child_job_ids_on_crossover_2:
                    flextime_jobs_2 = [job for job in  new_generation[1].flextime_jobs if job.id == id]

                child_on_crossover_1 = Individual(flextime_jobs=flextime_jobs_1, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))
                child_on_crossover_2 = Individual(flextime_jobs=flextime_jobs_2, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))

                child_on_crossover_1.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_1, timeline=copy.deepcopy(timeline))
                child_on_crossover_2.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_2, timeline=copy.deepcopy(timeline))

                new_generation.append(child_on_crossover_1)

                new_generation.append(child_on_crossover_2)

                flextime_jobs_mutation = on_mutation(new_generation[0])

                child_on_mutation = Individual(flextime_jobs=flextime_jobs_mutation, schedule=Schedule(start_time=new_generation[0].schedule.start_time, end_time=new_generation[0].schedule.end_time))
                child_on_mutation.schedule.time_slots = set_individual_schedule(flextime_jobs=flextime_jobs_mutation, timeline=copy.deepcopy(timeline))
                new_generation.append(child_on_mutation)
                population.append(new_generation)
                
                for individual in new_generation:   
                    individual.lateness = fitness_func(individual=individual)
                    if individual.lateness == 0: 
                        acceptable_individual = individual
                        done = True
                population.append(new_generation)
                
                generation += 1
        total_len = 0
        for p in population:
            total_len+=len(p)
        else:
            res = jsonify({
                'message': validated['message']
            })
            res.status_code = 422

        if (acceptable_individual):
            res = jsonify({
                'result': acceptable_individual.schedule.serialize()['time_slots'],
                'result2' :  acceptable_individual.schedule.serialize()['flextime_jobs']
            })
            res.status_code = 200
        run_time_end = time.time()
        result_to_file = {
            'so cong viec': len(jobs),
            'so cong viec khong co dinh': len(jobs),
            'so ngay lap lich': (end_time - start_time).days,
            'so ca the khoi tao': total_len,
            'tong so ca the': total_len,
            'running_time': run_time_end-run_time_start
        }

        import json
        with open(f'data/output/{generate_uuid()}.json', 'w') as f:
            json.dump(result_to_file, f)
        run_time_end = time.time()
        return res