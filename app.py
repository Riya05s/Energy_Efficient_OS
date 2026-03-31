# app.py
import streamlit as st
import pandas as pd
from simulator.process import Process
from simulator.cpu_simulator import CPUSimulator
from algorithms.round_robin import RoundRobin
from algorithms.srtf import SRTF
from algorithms.priority_preemptive import PriorityPreemptive
from algorithms.advanced_energy_aware import AdvancedEnergyAware
from utils.plotter import create_gantt_chart

st.set_page_config(layout="wide")
st.title("⚡️ Energy-Efficient CPU Scheduling Simulator")

def load_processes_from_upload(uploaded_file):
    processes = []
    if uploaded_file is not None:
        string_data = uploaded_file.getvalue().decode("utf-8").splitlines()
        for line in string_data:
            if line.startswith('#') or not line.strip():
                continue
            pid, arrival, burst, priority = line.strip().split(',')
            processes.append(Process(pid.strip(), int(arrival), int(burst), int(priority)))
    return processes

def get_metrics_df(results_dict):
    data = []
    for name, result in results_dict.items():
        finished_procs = result[0]
        energy = result[2]
        if finished_procs:
            avg_turnaround = sum(p.turnaround_time for p in finished_procs) / len(finished_procs)
            avg_wait = sum(p.wait_time for p in finished_procs) / len(finished_procs)
        else:
            avg_turnaround, avg_wait = 0, 0
        data.append([name, f"{avg_turnaround:.2f}", f"{avg_wait:.2f}", energy])
    
    df = pd.DataFrame(data, columns=["Algorithm", "Avg Turnaround Time", "Avg Wait Time", "Total Energy (units)"])
    return df

# --- Sidebar Controls ---
st.sidebar.header("Simulation Configuration")
uploaded_file = st.sidebar.file_uploader("Upload Workload File", type=['txt'])

st.sidebar.subheader("Algorithm Parameters")
rr_quantum = st.sidebar.slider("Round Robin Time Quantum", 2, 10, 4)
st.sidebar.markdown("---")
st.sidebar.subheader("Energy-Aware Weights")
w_a = st.sidebar.slider("Efficiency (a)", 0.0, 1.0, 0.6, 0.05)
w_b = st.sidebar.slider("Priority (b)", 0.0, 1.0, 0.3, 0.05)
w_c = st.sidebar.slider("Urgency (c)", 0.0, 1.0, 0.1, 0.05)

st.sidebar.subheader("Advanced Energy Model")
power_busy = st.sidebar.slider("Busy Power", 5, 20, 10)
power_turbo = st.sidebar.slider("Turbo Power", 10, 30, 15)
power_throttle = st.sidebar.slider("Throttle Power", 1, 10, 5)
power_sleep = st.sidebar.slider("Sleep Power", 0.1, 2.0, 0.2)

run_button = st.sidebar.button("Run Simulation", type="primary")

# --- Main App Body ---
if run_button and uploaded_file:
    processes = load_processes_from_upload(uploaded_file)
    if not processes:
        st.error("Uploaded file is empty or invalid. Please check the format.")
    else:
        st.success(f"Loaded {len(processes)} processes. Running simulations...")

        # Initialize Simulator and Schedulers
        sim = CPUSimulator(processes)
        sim.POWER_BUSY = power_busy
        sim.POWER_TURBO = power_turbo
        sim.POWER_THROTTLE = power_throttle
        sim.POWER_SLEEP = power_sleep

        schedulers = {
            "Round Robin": RoundRobin(time_quantum=rr_quantum),
            "SRTF": SRTF(),
            "Priority (Preemptive)": PriorityPreemptive(),
            "Advanced Energy-Aware": AdvancedEnergyAware(a=w_a, b=w_b, c=w_c)
        }
        
        results = {}
        for name, scheduler in schedulers.items():
            results[name] = sim.run(scheduler)
            # Export results for each algorithm
            sim.export_results(filename_prefix=f"{name.replace(' ', '_').lower()}")

        st.header("📊 Comparative Analysis")
        st.dataframe(get_metrics_df(results), use_container_width=True)

        # Show new metrics
        st.subheader("Additional Metrics")
        st.write(f"CPU Utilization: {sim.cpu_utilization:.2f}%")
        st.write(f"Idle Time: {sim.idle_time} ticks")
        st.write(f"Sleep Time: {sim.sleep_time} ticks")

        # Show per-process stats
        st.subheader("Per-Process Energy Usage")
        energy_df = pd.DataFrame([
            {"PID": pid, "Energy": sim.per_process_energy.get(pid, 0)}
            for pid in [p.pid for p in processes]
        ])
        st.dataframe(energy_df)

        st.header("Gantt Charts")
        for name, result in results.items():
            with st.expander(f"**{name}** - Gantt Chart", expanded=True):
                gantt_chart_data = result[1]
                fig = create_gantt_chart(gantt_chart_data)
                st.pyplot(fig)
        st.success("Results exported as CSV and JSON in the project folder.")
else:
    st.info("Please upload a workload file and click 'Run Simulation' to begin.")