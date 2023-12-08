class Task:
    def __init__(self, task, description, duration, status='Not Started', key=None, date=None):
        # Initialize the Task class with the given parameters
        self.task = task
        self.description = description
        self.duration = duration
        self.status = status
        self.key = key
        self.date = date
