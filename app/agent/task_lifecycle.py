class TaskLifecycleManager:
    def __init__(self):
        self.task_active = False
        self.awaiting_termination_approval = False
        self.awaiting_user_input = False

    def begin_task(self):
        self.task_active = True
        self.awaiting_termination_approval = False

    def is_task_running(self):
        return self.task_active

    def mark_ready_to_terminate(self):
        self.awaiting_termination_approval = True

    def ready_to_terminate(self) -> bool:
        return self.awaiting_termination_approval  # ✔ correct method now exists

    def confirm_termination(self):
        self.task_active = False
        self.awaiting_termination_approval = False

    def mark_awaiting_user_input(self):
        self.awaiting_user_input = True

    def clear_awaiting_user_input(self):
        self.awaiting_user_input = False

    def is_awaiting_user_input(self) -> bool:
        return self.awaiting_user_input
