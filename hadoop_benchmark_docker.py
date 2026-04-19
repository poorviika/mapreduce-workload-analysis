import time
import psutil
import subprocess
import matplotlib.pyplot as plt
import numpy as np

# Configuration
ITERATIONS = 5
DATA_SIZE = 1000000000  # 1GB
BLOCK_SIZE = 134217728  # 128MB
MAPPERS = 4
REDUCERS = 4
HDFS_PATH = "/user/hadoop"

# Benchmark execution
def run_benchmark(command, cleanup_path=None):
    print(f"\nRunning: {command}")
    start_time = time.time()

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    cpu_usage = []
    mem_usage = []

    while process.poll() is None:
        cpu_usage.append(psutil.cpu_percent(interval=1))
        mem_usage.append(psutil.virtual_memory().percent)

    process.communicate()
    end_time = time.time()

    elapsed_time = round(end_time - start_time, 2)
    avg_cpu = round(sum(cpu_usage) / len(cpu_usage), 2) if cpu_usage else 0
    avg_mem = round(sum(mem_usage) / len(mem_usage), 2) if mem_usage else 0

    if cleanup_path:
        subprocess.run(
            f"docker exec namenode hdfs dfs -rm -r -skipTrash {cleanup_path}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return elapsed_time, avg_cpu, avg_mem

# HDFS cleanup
def clean_hdfs():
    subprocess.run(
        f"docker exec namenode hdfs dfs -rm -r -skipTrash {HDFS_PATH}/*",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# Cluster initialization
print("\nRestarting Hadoop cluster...")
subprocess.run(
    "docker-compose down && docker-compose up -d",
    shell=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(60)

# Benchmark execution
results = []

with open("benchmark_results.txt", "w") as f:
    f.write("Hadoop Benchmark Results (Docker) - 1GB\n\n")

    for i in range(1, ITERATIONS + 1):
        print(f"\nIteration {i}/{ITERATIONS}")

        clean_hdfs()

        # TeraGen
        tg_command = (
            f"docker exec namenode hadoop jar "
            f"/opt/hadoop-3.2.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar teragen "
            f"-Dmapreduce.map.tasks={MAPPERS} "
            f"-Ddfs.blocksize={BLOCK_SIZE} "
            f"{DATA_SIZE} {HDFS_PATH}/teragen-1GB"
        )
        tg_time, tg_cpu, tg_mem = run_benchmark(tg_command, f"{HDFS_PATH}/teragen-1GB")

        # TeraSort
        ts_command = (
            f"docker exec namenode hadoop jar "
            f"/opt/hadoop-3.2.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar terasort "
            f"-Dmapreduce.job.reduces={REDUCERS} "
            f"{HDFS_PATH}/teragen-1GB {HDFS_PATH}/terasort-1GB"
        )
        ts_time, ts_cpu, ts_mem = run_benchmark(ts_command, f"{HDFS_PATH}/terasort-1GB")

        # TeraValidate
        tv_command = (
            f"docker exec namenode hadoop jar "
            f"/opt/hadoop-3.2.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar teravalidate "
            f"-Dmapreduce.job.reduces={REDUCERS} "
            f"{HDFS_PATH}/terasort-1GB {HDFS_PATH}/teravalidate-1GB"
        )
        tv_time, tv_cpu, tv_mem = run_benchmark(tv_command, f"{HDFS_PATH}/teravalidate-1GB")

        results.append((tg_time, tg_cpu, tg_mem,
                        ts_time, ts_cpu, ts_mem,
                        tv_time, tv_cpu, tv_mem))

        f.write(f"Iteration {i} Results:\n")
        f.write(f"TeraGen: Time = {tg_time}s, CPU = {tg_cpu}%, Memory = {tg_mem}%\n")
        f.write(f"TeraSort: Time = {ts_time}s, CPU = {ts_cpu}%, Memory = {ts_mem}%\n")
        f.write(f"TeraValidate: Time = {tv_time}s, CPU = {tv_cpu}%, Memory = {tv_mem}%\n\n")

print("\nBenchmarking completed.")

# Data extraction
iterations = np.arange(1, ITERATIONS + 1)

teragen_times = [r[0] for r in results]
terasort_times = [r[3] for r in results]
teravalidate_times = [r[6] for r in results]

teragen_cpu = [r[1] for r in results]
terasort_cpu = [r[4] for r in results]
teravalidate_cpu = [r[7] for r in results]

teragen_mem = [r[2] for r in results]
terasort_mem = [r[5] for r in results]
teravalidate_mem = [r[8] for r in results]

# Visualization
fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=True)

axs[0].plot(iterations, teragen_times, marker='o', label="TeraGen")
axs[0].plot(iterations, terasort_times, marker='s', label="TeraSort")
axs[0].plot(iterations, teravalidate_times, marker='^', label="TeraValidate")
axs[0].set_ylabel("Time (s)")
axs[0].set_title("Execution Time")
axs[0].legend()
axs[0].grid(True)

axs[1].plot(iterations, teragen_cpu, marker='o', label="TeraGen")
axs[1].plot(iterations, terasort_cpu, marker='s', label="TeraSort")
axs[1].plot(iterations, teravalidate_cpu, marker='^', label="TeraValidate")
axs[1].set_ylabel("CPU (%)")
axs[1].set_title("CPU Usage")
axs[1].legend()
axs[1].grid(True)

axs[2].plot(iterations, teragen_mem, marker='o', label="TeraGen")
axs[2].plot(iterations, terasort_mem, marker='s', label="TeraSort")
axs[2].plot(iterations, teravalidate_mem, marker='^', label="TeraValidate")
axs[2].set_ylabel("Memory (%)")
axs[2].set_xlabel("Iteration")
axs[2].set_title("Memory Usage")
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.savefig("docker_1gb.png")
plt.close()
