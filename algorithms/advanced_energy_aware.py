# algorithms/advanced_energy_aware.py
import math
import openpyxl

class AdvancedEnergyAware:
    def __init__(self, a=0.6, b=0.3, c=0.1):
        self.sim = None
        self.a = a  # Weight for energy efficiency (shorter jobs)
        self.b = b  # Weight for priority
        self.c = c  # Weight for urgency (aging)

    def _calculate_score(self, process):
        if process is None:
            return -1
        # Normalize values to be between 0 and 1
        efficiency_score = 1 / (process.remaining_time + 1)
        priority_score = 1 / (process.priority + 1)
        urgency_score = math.tanh(process.wait_time / 10.0) # tanh scales it nicely

        return (self.a * efficiency_score +
                self.b * priority_score +
                self.c * urgency_score)

    def schedule(self):
        best_process = self.sim.current_process_on_cpu
        current_score = self._calculate_score(best_process)

        for proc in self.sim.ready_queue:
            proc_score = self._calculate_score(proc)
            if proc_score > current_score:
                best_process = proc
                current_score = proc_score

        if best_process is not self.sim.current_process_on_cpu:
            if self.sim.current_process_on_cpu is not None:
                self.sim.ready_queue.append(self.sim.current_process_on_cpu)
            
            self.sim.current_process_on_cpu = best_process
            if best_process in self.sim.ready_queue:
                self.sim.ready_queue.remove(best_process)

    def schedule_multi_core(self, cores, ready_queue):
        for i in range(len(cores)):
            if cores[i] is None and ready_queue:
                # Pick process with highest energy-aware score
                best_proc = max(ready_queue, key=self._calculate_score)
                cores[i] = best_proc
                ready_queue.remove(best_proc)