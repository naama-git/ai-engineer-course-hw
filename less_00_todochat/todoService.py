class TodoService:
    def __init__(self):
        self.tasks = []
        self.counter = 1

    def get_tasks(self):
        """Returns all tasks"""
        return self.tasks

    def add_task(self, description):
        """Adding new task to the tasks array"""
        new_task = {
            "id": self.counter,
            "description": description,
            "completed": False
        }
        self.tasks.append(new_task)
        self.counter += 1
        return new_task

    def update_task(self, task_id, description=None, completed=None):
        """Updating existing task by ID"""
        for task in self.tasks:
            if task["id"] == task_id:
                if description is not None:
                    task["description"] = description
                if completed is not None:
                    task["completed"] = completed
                return task
        return {"error": "Task not found"}

    def delete_task(self, task_id):
        """Deleting task from tasks array"""
        for index, task in enumerate(self.tasks):
            if task["id"] == task_id:
                deleted_task = self.tasks.pop(index)
                return deleted_task
        return {"error": "Task not found"}