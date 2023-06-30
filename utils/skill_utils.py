from typing import List, Tuple, Union


class Task:
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @property
    def task_id(self):
        """Unique id for task."""
        raise NotImplementedError()

    def init_task(self):
        """Main logic for the task."""
        raise NotImplementedError()
    
    def get_listeners(self) -> List[Tuple[str, callable]]:
        """Listeners contianing ongoing logic for the task. Also responsible for calling finish()."""
        raise NotImplementedError()

    def start(self):
        print("Starting task", self.task_id)
        self.running = True
        self.init_task()
        listeners = self.get_listeners()
        if len(listeners) == 0:
            TaskQueue().finish_task(self.task_id)
        else:
            for name, fun in listeners:
                self.bot.on(name, fun)

    def finish_task(self):
        print("Finishing task", self.task_id)
        listeners = self.get_listeners()
        for name, fun in listeners:
            self.bot.removeListener(name, fun)
        self.running = False
        TaskQueue().finish_task(self.task_id)


class TaskSequence:
    
    def get_tasks(self) -> List[Task]:
        raise NotImplementedError()


class TaskQueue:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TaskQueue, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.task_queue = []

    @property
    def busy(self) -> bool:
        return len(self.task_queue) > 0

    def queue_task(self, task: Union[Task, TaskSequence]) -> None:
        print("Queuing task", task.task_id)
        if isinstance(task, TaskSequence):
            for subtask in task.get_tasks():
                self.queue_task(subtask)
        else:
            self.task_queue.append(task)
            if len(self.task_queue) == 1:
                self.task_queue[0].start()

    def finish_task(self, task_id: str) -> None:
        if len(self.task_queue) > 0 and self.task_queue[0].task_id == task_id:
            self.task_queue[0].finish()
            self.task_queue = self.task_queue[1:]
            if len(self.task_queue) > 0:
                self.task_queue[0].start()
    
    def cancel_tasks(self) -> None:
        for task in self.task_queue:
            task.finish()
        self.task_queue = []
