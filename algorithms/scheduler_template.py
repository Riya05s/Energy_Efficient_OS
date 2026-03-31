# algorithms/scheduler_template.py

class SchedulerTemplate:
    """
    Template for creating new CPU scheduling algorithms.
    Implement the schedule() method with your logic.
    """
    def __init__(self, **kwargs):
        self.sim = None  # Will be set by CPUSimulator

    def schedule(self):
        """
        Decide which process to run next.
        Access self.sim.ready_queue and self.sim.current_process_on_cpu.
        Set self.sim.current_process_on_cpu to your chosen process.
        """
        # Example: Always pick the first process in the ready queue
        if self.sim.current_process_on_cpu is None and self.sim.ready_queue:
            self.sim.current_process_on_cpu = self.sim.ready_queue.popleft()