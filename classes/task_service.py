# Class for managing Task operations in a database
class TaskService:

    # Method to add a task to the database 
    def add_task(self, task, date_ref, ref, current_date):
        new_task = {
            'task': task.task,
            'description': task.description,
            'estimated_time': task.duration,
            'status': task.status
        }

        if date_ref.get() is None:
            date_ref.push(new_task)
        else:
            ref.child(current_date).push(new_task)

    # Method to remove a task from the database
    def remove_task(self, task, ref):
        task_key = task.key
        task_date = task.date
        ref.child(f'{task_date}/{task_key}').delete()

    # Method to change the status of a task in the database
    def change_status(self, task, new_status, ref):
        task_key = task.key
        task_date = task.date
        ref.child(f'{task_date}/{task_key}').update({'status': new_status})
