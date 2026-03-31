# utils/plotter.py
import matplotlib.pyplot as plt
import numpy as np

def extract_pid_number(pid):
    # Handles cases like "P1", "p5-Throttle", "P3-Turbo"
    base = pid.split('-')[0]  # Get "P1" or "p5"
    num = ''.join(filter(str.isdigit, base))  # Extract digits
    return int(num) if num else 0

def create_gantt_chart(gantt_data):
    fig, ax = plt.subplots(figsize=(12, 4))
    
    pids = sorted(list(set(p for p in gantt_data if p != "Idle" and p != "Sleep")), key=extract_pid_number)
    pid_map = {pid: i for i, pid in enumerate(pids)}
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(pids)))
    pid_colors = {pid: colors[i] for i, pid in enumerate(pids)}
    
    start_time = 0
    for i in range(1, len(gantt_data)):
        if gantt_data[i] != gantt_data[i-1]:
            pid = gantt_data[i-1]
            if pid != "Idle" and pid != "Sleep":
                ax.barh(pid_map[pid], i - start_time, left=start_time, height=0.6, align='center',
                        color=pid_colors[pid], edgecolor='black')
            start_time = i
    
    # Add the last block
    pid = gantt_data[-1]
    if pid != "Idle" and pid != "Sleep":
        ax.barh(pid_map[pid], len(gantt_data) - start_time, left=start_time, height=0.6, align='center',
                color=pid_colors[pid], edgecolor='black')

    ax.set_yticks(range(len(pids)))
    ax.set_yticklabels(pids)
    ax.set_xlabel("Time (ticks)")
    ax.set_title("CPU Gantt Chart")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    return fig