# Energy_Efficient_OS

**Overview:**

This project is an interactive CPU Scheduling Simulator built using Streamlit, designed to compare traditional scheduling algorithms with an advanced energy-aware scheduling approach.
It allows users to upload process workloads, configure scheduling parameters, and visualize results such as:
Average Turnaround Time
Average Waiting Time
CPU Utilization
Energy Consumption

The simulator is ideal for understanding the trade-offs between performance and energy efficiency in operating systems.

**Objectives**
1. Simulate different CPU scheduling algorithms.
2. Compare performance metrics across algorithms.
3. Introduce energy-aware scheduling techniques.
4. Provide interactive visualization using Gantt charts.

**Features**
1. Upload custom workload files.
2. Adjustable scheduling parameters.
3. Multiple scheduling algorithms:
    1. Round Robin
    2. Shortest Remaining Time First (SRTF)
    3. Priority Scheduling (Preemptive)
4. Advanced Energy-Aware Scheduling
    1. Energy consumption modeling
    2. Comparative performance analysis
    3. Gantt chart visualization
    4. Export results in CSV and JSON format

**Tech Stack**
Frontend
----Streamlit (interactive UI)
Backend
----Python
Libraries
----streamlit – UI framework
----pandas – data handling
----Custom modules:
    ----simulator
    ----algorithms
    ----utils


**Working**

1. Upload Workload File
Users upload a .txt file containing process details
Format:
PID, Arrival Time, Burst Time, Priority
P1, 0, 5, 2
P2, 1, 3, 1
P3, 2, 8, 3

2. Configure Parameters
   
Round Robin time quantum
Energy-aware weights:
Efficiency (a)
Priority (b)
Urgency (c)
Power consumption values:
Busy
Turbo
Throttle
Sleep

3. Run Simulation

Executes all scheduling algorithms
Collects performance + energy metrics

4. Results Display

📊 Comparison table
⚡ CPU utilization, idle time, sleep time
🔋 Per-process energy usage
📈 Gantt charts for each algorithm
