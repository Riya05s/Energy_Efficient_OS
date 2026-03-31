# algorithms/srtf.py
class SRTF:
    def __init__(self):
        self.sim = None

    def schedule(self):
        best_process = self.sim.current_process_on_cpu

        for proc in self.sim.ready_queue:
            if best_process is None or proc.remaining_time < best_process.remaining_time:
                best_process = proc
        
        if best_process is not self.sim.current_process_on_cpu:
            if self.sim.current_process_on_cpu is not None:
                self.sim.ready_queue.append(self.sim.current_process_on_cpu)
            
            self.sim.current_process_on_cpu = best_process
            if best_process in self.sim.ready_queue:
                self.sim.ready_queue.remove(best_process)

    def schedule_multi_core(self, cores, ready_queue):
        for i in range(len(cores)):
            if cores[i] is None and ready_queue:
                # Pick process with shortest remaining time
                best_proc = min(ready_queue, key=lambda p: p.remaining_time)
                cores[i] = best_proc
                ready_queue.remove(best_proc)