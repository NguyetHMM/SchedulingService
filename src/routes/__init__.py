from src.controllers.scheduling_generate_controller import SchedulingGenerate

def initialize_routes(api):
    api.add_resource(SchedulingGenerate, '/scheduling')