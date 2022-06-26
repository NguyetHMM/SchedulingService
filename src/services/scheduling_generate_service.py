from typing import List

from flask import jsonify
from src.core.src.main2 import *
from src.core.src.common import generate_uuid
from src.core.src.models import WorkingTimeSlot


class SchedulingGenerateService:
    def scheduling_generate(self, schedule_start_time, schedule_end_time, jobs, scheduled_working_time_slots,
                            breaking_time_slots):
        run_time_start = time.time()
        start_time = string_to_datetime(schedule_start_time)
        end_time = string_to_datetime(schedule_end_time)
        schedule_breaking_time_slots = []
        schedule_jobs = []
        recent_working_time_slots: List[WorkingTimeSlot] = []
        print(breaking_time_slots)
        for bt in breaking_time_slots:
            b = BreakingTimeSlot(id=bt['id'], start_time=string_to_datetime(bt['start_time']),
                                 end_time=string_to_datetime(bt['end_time']))
            schedule_breaking_time_slots.append(b)
        temp = copy.deepcopy(schedule_breaking_time_slots)
        print(temp)
        for i in range(len(temp)):
            print(temp[i].__dict__)
        for job in jobs:
            j = Job(id=job['id'], name=job['name'], early_start_time=string_to_datetime(job['early_start_time']),
                    late_finish_time=string_to_datetime(job['late_finish_time']),
                    start_time=None, finish_time=None, estimated_time=job['estimated_time'], flextime=job['flextime'])
            schedule_jobs.append(j)

        for t in scheduled_working_time_slots:
            t = WorkingTimeSlot(id=t['id'], start_time=string_to_datetime(t['start_time']),
                                end_time=string_to_datetime(t['end_time']),
                                job=Job(id=t['job']['id'], name=t['job']['name'],
                                        early_start_time=string_to_datetime(t['job']['early_start_time']),
                                        late_finish_time=string_to_datetime(t['job']['late_finish_time']),
                                        start_time=None, finish_time=None, estimated_time=t['job']['estimated_time'],
                                        flextime=t['job']['flextime']), remaining_time=t['remaining_time'])
            recent_working_time_slots.append(t)

        schedule = schedule_generate(start_time=start_time, end_time=end_time)
        schedule = add_breaking_time_slots(schedule, schedule_breaking_time_slots)
        schedule = add_fixed_time_working_time_slots(schedule, schedule_jobs)
        timeline = []
        timeline, start_time_reused_jobs = add_reused_working_time_slots(
            schedule=schedule, reused_working_time_slots=recent_working_time_slots, jobs=schedule_jobs)
        acceptable_individual = {}
        generation = 0
        population = []
        validated = validate_input_data(schedule=schedule, jobs=schedule_jobs, schedule_breaking_time_slots=temp)
        if validated['status']:
            p = on_generation(schedule=schedule, timeline=timeline, start_time_reused_jobs=start_time_reused_jobs,
                              jobs=schedule_jobs)
            population.append(p)
            done = False
            for individual in population[generation]:
                individual.lateness = fitness_func(individual=individual)
                print(individual.lateness, len(individual.schedule.time_slots), "lateness")

                if individual.lateness == 0 and len(individual.schedule.time_slots) != 0:
                    acceptable_individual = individual
                    done = True

            while not done:
                print(generation, "generation")
                new_generation = on_selection(population=population[generation])
                print(new_generation, "new_generation")
                flextime_jobs_1 = []
                flextime_jobs_2 = []
                child_job_ids_on_crossover_1, child_job_ids_on_crossover_2 = on_crossover(new_generation[0],
                                                                                          new_generation[1])
                for id in child_job_ids_on_crossover_1:
                    flextime_jobs_1 += [job for job in new_generation[0].flextime_jobs if job.id == id]
                for id in child_job_ids_on_crossover_2:
                    flextime_jobs_2 += [job for job in new_generation[1].flextime_jobs if job.id == id]

                child_on_crossover_1 = Individual(flextime_jobs=flextime_jobs_1,
                                                  schedule=Schedule(start_time=new_generation[0].schedule.start_time,
                                                                    end_time=new_generation[0].schedule.end_time))
                child_on_crossover_2 = Individual(flextime_jobs=flextime_jobs_2,
                                                  schedule=Schedule(start_time=new_generation[0].schedule.start_time,
                                                                    end_time=new_generation[0].schedule.end_time))
                print(child_job_ids_on_crossover_1, 'child_job_ids_on_crossover_1')
                       # print(child_on_crossover_1.schedule.lateness)
                print(child_job_ids_on_crossover_2, 'child_job_ids_on_crossover_2')
                # print(child_on_crossover_2.schedule.lateness)
                # child_on_crossover_1.schedule.time_slots += set_individual_schedule(flextime_jobs=flextime_jobs_1, timeline=copy.deepcopy(timeline))

                # child_on_crossover_2.schedule.time_slots += set_individual_schedule(flextime_jobs=flextime_jobs_2, timeline=copy.deepcopy(timeline))

                _, added_working_time_slots_on_crossover_1 = set_individual_schedule(flextime_jobs=flextime_jobs_1,
                                                                                     timeline=copy.deepcopy(timeline))
                child_on_crossover_1.schedule.time_slots += added_working_time_slots_on_crossover_1

                _, added_working_time_slots_on_crossover_2 = set_individual_schedule(flextime_jobs=flextime_jobs_2,
                                                                                     timeline=copy.deepcopy(timeline))
                child_on_crossover_1.schedule.time_slots += added_working_time_slots_on_crossover_2

                new_generation.append(child_on_crossover_1)

                new_generation.append(child_on_crossover_2)

                flextime_jobs_mutation = on_mutation(new_generation[0])

                child_on_mutation = Individual(flextime_jobs=flextime_jobs_mutation,
                                               schedule=Schedule(start_time=new_generation[0].schedule.start_time,
                                                                 end_time=new_generation[0].schedule.end_time))
                # child_on_mutation.schedule.time_slots += set_individual_schedule(flextime_jobs=flextime_jobs_mutation, timeline=copy.deepcopy(timeline))
                _, added_working_time_slots_on_mutation = set_individual_schedule(flextime_jobs=flextime_jobs_mutation,
                                                                                  timeline=copy.deepcopy(timeline))
                child_on_mutation.schedule.time_slots += added_working_time_slots_on_mutation
                new_generation.append(child_on_mutation)
                # population.append(new_generation)

                for individual in new_generation:
                    individual.lateness = fitness_func(individual=individual)
                    print(individual.lateness,len(individual.schedule.time_slots),"lateness")
                    if individual.lateness == 0 and len(individual.schedule.time_slots) != 0:
                        acceptable_individual = individual
                        done = True
                population.append(new_generation)
                generation += 1
        total_len = 0
        for p in population:
            total_len += len(p)
        else:
            res = jsonify({
                'message': validated['message']
            })
            # res.status_code = 422

        if (acceptable_individual):
            acceptable_individual.schedule.time_slots.sort(key=lambda x: x.start_time)
            res = {
                'result': acceptable_individual.schedule.serialize()['time_slots']
            }
            # res.status_code = 200
        run_time_end = time.time()
        result_to_file = {
            'Jobs': len(jobs),
            'Flextime': len(acceptable_individual.flextime_jobs),
            'Scheduled Days': (end_time - start_time).days,
            'Individual On Generate': total_len,
            'Total Individual': total_len,
            'Run Time': run_time_end - run_time_start
        }

        import json
        with open(f'data/output/output.json', 'a') as f:
            f.write(f'\n{json.dumps(result_to_file)},')

        # from openpyxl import load_workbook
        # myFileName=r'data/output/output.xlsx'
        # load the workbook, and put the sheet into a variable
        # wb = load_workbook(filename='data/output/output.xlsx')
        # ws = wb['Sheet1']
        # ws.append(result_to_file)

        run_time_end = time.time()
        return res
# 
# , orient='index',
#    columns=['Ngày', 'Tổng số công việc', 'Thời gian lập lịch', 'Số lượng cá thể khởi tạo', 'Số lượng cá thể trong quần thể', 'Thời gian chạy'])
