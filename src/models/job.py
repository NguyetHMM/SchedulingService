class Jobs:
    def __init__(self, id, name, early_start_time, late_finish_time, start_time, finish_time, estimated_time, flextime = 1):
        self.id = id
        self.name = name
        self.early_start_time = early_start_time    #arrival_time
        self.late_finish_time = late_finish_time    #deadline
        self.start_time = start_time
        self.finish_time = finish_time
        self.estimated_time = estimated_time
        self.flextime = flextime        #flexible