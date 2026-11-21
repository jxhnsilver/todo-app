from uuid import UUID


class TaskNotFoundError(Exception):
    def __init__(self, task_id: UUID):
        super().__init__(f"Задача с ID {task_id} не найдена")


class CategoryNotFoundError(Exception):
    def __init__(self, category_id: UUID):
        super().__init__(f"Категория с ID {category_id} не найдена")

class CategoryHasTasksError(Exception):
    def __init__(self, category_id: UUID):
        self.category_id = category_id
        super().__init__(f"Невозможно удалить категорию '{category_id}': существуют связанные задачи")
