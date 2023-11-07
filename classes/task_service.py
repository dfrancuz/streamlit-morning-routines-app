class TaskService:
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

    def remove_task(self, task, ref):
        task_key = task.key
        task_date = task.date
        ref.child(f'{task_date}/{task_key}').delete()

    def change_status(self, task, new_status, ref):
        task_key = task.key
        task_date = task.date
        ref.child(f'{task_date}/{task_key}').update({'status': new_status})