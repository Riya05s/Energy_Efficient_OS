# simulator/cpu_simulator.py
import collections
import copy  # IMPORTANT: Import the copy module
import pandas as pd
import json
import sqlite3

class CPUSimulator:
    """Manages the simulation environment, time, and processes."""
    def __init__(self, processes, num_cores=2):
        # Store the original, untouched list of processes
        self.initial_processes = sorted(processes, key=lambda p: p.arrival_time)
        
        # --- These variables will be RESET for each simulation run ---
        self.ready_queue = collections.deque()
        self.finished_processes = []
        self.gantt_chart = [] 
        self.current_time = 0
        self.current_process_on_cpu = None
        self.time_quantum_slice = 0 
        self.total_energy_consumed = 0
        # --- End of reset variables ---

        # Energy Model
        self.POWER_BUSY = 10 
        self.POWER_IDLE = 1 
        self.POWER_SLEEP = 0.2  # New: Deep sleep state
        self.POWER_TURBO = 15      # New: Turbo mode (high performance, high energy)
        self.POWER_THROTTLE = 5    # New: Throttling mode (low performance, low energy)
        self.sleep_threshold = 3  # New: If idle for >=3 ticks, enter sleep

        self.idle_ticks = 0  # Track consecutive idle ticks
        self.per_process_energy = {}  # Track energy per process

        # New variables for advanced metrics
        self.context_switches = 0
        self.deadline_misses = 0
        self.deadline = 20  # Example: global deadline for all processes

        self.num_cores = num_cores
        self.cores = [None] * num_cores  # Each core can run a process

    def run(self, scheduler):
        """Runs the entire simulation with a given scheduling algorithm."""
        
        # --- FIX: Reset the simulator's state for a clean run ---
        process_pool = [copy.deepcopy(p) for p in self.initial_processes]
        self.finished_processes = []
        self.gantt_chart = []
        self.current_time = 0
        self.current_process_on_cpu = None
        self.ready_queue.clear()
        self.total_energy_consumed = 0
        scheduler.sim = self # Link the scheduler to this specific run's simulator instance
        # --- End of FIX ---

        prev_pid = None
        while process_pool or self.ready_queue or any(self.cores):
            # 1. Add newly arrived processes to the ready queue
            while process_pool and process_pool[0].arrival_time <= self.current_time:
                self.ready_queue.append(process_pool.pop(0))

            # Scheduler assigns processes to each core
            scheduler.schedule_multi_core(self.cores, self.ready_queue)

            # Update each core's process, energy, etc.
            for i, process in enumerate(self.cores):
                if process:
                    pid = process.pid
                    # Example: Turbo mode for high-priority processes
                    if process.priority <= 2:
                        self.gantt_chart.append(f"{pid}-Turbo")
                        self.total_energy_consumed += self.POWER_TURBO
                        self.per_process_energy[pid] = self.per_process_energy.get(pid, 0) + self.POWER_TURBO
                    elif process.priority >= 8:
                        self.gantt_chart.append(f"{pid}-Throttle")
                        self.total_energy_consumed += self.POWER_THROTTLE
                        self.per_process_energy[pid] = self.per_process_energy.get(pid, 0) + self.POWER_THROTTLE
                    else:
                        self.gantt_chart.append(pid)
                        self.total_energy_consumed += self.POWER_BUSY
                        self.per_process_energy[pid] = self.per_process_energy.get(pid, 0) + self.POWER_BUSY

                    if process.start_time == -1:
                        process.start_time = self.current_time

                    process.remaining_time -= 1
                    self.idle_ticks = 0
                else:
                    # Idle or sleep logic for the core
                    if not self.ready_queue and not process_pool:
                        self.gantt_chart.append("Sleep")
                        self.total_energy_consumed += self.POWER_SLEEP
                    else:
                        self.gantt_chart.append("Idle")
                        self.total_energy_consumed += self.POWER_IDLE
                    self.idle_ticks += 1

            # 4. Handle process completion
            for i in range(self.num_cores):
                if self.cores[i] and self.cores[i].remaining_time == 0:
                    self.cores[i].finish_time = self.current_time + 1
                    self.finished_processes.append(self.cores[i])
                    self.cores[i] = None

            # 5. Update wait times for all processes in the ready queue
            for proc in self.ready_queue:
                proc.wait_time += 1

            # Track context switches
            curr_pid = self.current_process_on_cpu.pid if self.current_process_on_cpu else None
            if prev_pid is not None and curr_pid != prev_pid:
                self.context_switches += 1
            prev_pid = curr_pid

            self.current_time += 1

        # Final metrics calculation
        self._calculate_final_metrics()
        
        # The run method now returns its results instead of printing
        return self.finished_processes, self.gantt_chart, self.total_energy_consumed

    def _calculate_final_metrics(self):
        for proc in self.finished_processes:
            proc.turnaround_time = proc.finish_time - proc.arrival_time

        # New metrics
        self.cpu_utilization = (
            sum(1 for pid in self.gantt_chart if pid != "Idle" and pid != "Sleep") / len(self.gantt_chart)
        ) * 100 if self.gantt_chart else 0

        self.idle_time = sum(1 for pid in self.gantt_chart if pid == "Idle")
        self.sleep_time = sum(1 for pid in self.gantt_chart if pid == "Sleep")

    def export_results(self, filename_prefix="results"):
        # Export finished processes metrics
        df = pd.DataFrame([{
            "PID": p.pid,
            "Arrival": p.arrival_time,
            "Burst": p.burst_time,
            "Priority": p.priority,
            "Start": p.start_time,
            "Finish": p.finish_time,
            "Wait": p.wait_time,
            "Turnaround": p.turnaround_time
        } for p in self.finished_processes])
        df.to_excel(f"{filename_prefix}_processes.xlsx", index=False)

        # Export Gantt chart and energy
        gantt_dict = {
            "gantt_chart": self.gantt_chart,
            "total_energy": self.total_energy_consumed,
            "cpu_utilization": self.cpu_utilization,
            "idle_time": self.idle_time,
            "sleep_time": self.sleep_time
        }
        with open(f"{filename_prefix}_summary.json", "w") as f:
            json.dump(gantt_dict, f, indent=2)

    def export_to_db(self, db_path="results.db"):
        conn = sqlite3.connect(db_path)
        df = pd.DataFrame([{
            "PID": p.pid,
            "Arrival": p.arrival_time,
            "Burst": p.burst_time,
            "Priority": p.priority,
            "Start": p.start_time,
            "Finish": p.finish_time,
            "Wait": p.wait_time,
            "Turnaround": p.turnaround_time
        } for p in self.finished_processes])
        df.to_sql("process_results", conn, if_exists="replace", index=False)
        conn.close()


