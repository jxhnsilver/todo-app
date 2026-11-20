from uuid import UUID


class TaskNotFoundError(Exception):
    def __init__(self, task_id: UUID):
        super().__init__(f"Задача с ID {task_id} не найдена")
