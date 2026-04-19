import subprocess
import time
import psutil
import matplotlib.pyplot as plt

# Configuration
HADOOP_JAR_PATH = "/home/poorvika/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar"
TERAGEN_ROWS = 10000000
ITERATIONS = 5
RESULTS_FILE = "vm_results.txt"


def run_command(command, cleanup_path=None):
    if cleanup_path:
        subprocess.run(
            f"hadoop fs -rm -r {cleanup_path}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    start_time = time.time()
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    end_time = time.time()

    if process.returncode != 0:
        print(f"Error running command: {command}")
        print(process.stderr)
        return None, 0.0, 0.0

    cpu_usage, mem_usage = get_resource_usage()
    return round(end_time - start_time, 2), cpu_usage, mem_usage


def get_resource_usage():
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().used / (1024 * 1024)
        return cpu, mem
    except Exception:
        return 0.0, 0.0


def print_and_plot(label, times, cpus, mems):
    avg_time = sum(times) / len(times)
    avg_cpu = sum(cpus) / len(cpus)
    avg_mem = sum(mems) / len(mems)

    print(f"\n{label} averages")
    print(f"Time: {avg_time:.2f} sec")
    print(f"CPU: {avg_cpu:.2f}%")
    print(f"Memory: {avg_mem:.2f} MB")

    iterations = list(range(1, ITERATIONS + 1))
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(iterations, times, marker='o')
    plt.title(f"{label} metrics")
    plt.ylabel("Time (s)")
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(iterations, cpus, marker='o')
    plt.ylabel("CPU (%)")
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(iterations, mems, marker='o')
    plt.xlabel("Iteration")
    plt.ylabel("Memory (MB)")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(f"{label.lower()}_metrics.png")
    plt.close()


teragen_times, teragen_cpus, teragen_mems = [], [], []
terasort_times, terasort_cpus, terasort_mems = [], [], []
teraval_times, teraval_cpus, teraval_mems = [], [], []


with open(RESULTS_FILE, "w") as f:
    f.write("Hadoop Benchmark Results (VM - 1GB)\n\n")

    f.write("TeraGen Results\n")
    for i in range(1, ITERATIONS + 1):
        print(f"Running TeraGen {i}/{ITERATIONS}")
        cmd = f"hadoop jar {HADOOP_JAR_PATH} teragen {TERAGEN_ROWS} /tmp/teragen_output_{i}"
        t, c, m = run_command(cmd, f"/tmp/teragen_output_{i}")

        f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        teragen_times.append(t)
        teragen_cpus.append(c)
        teragen_mems.append(m)

    print_and_plot("TeraGen", teragen_times, teragen_cpus, teragen_mems)

    f.write("\nTeraSort Results\n")
    for i in range(1, ITERATIONS + 1):
        print(f"Running TeraSort {i}/{ITERATIONS}")
        cmd = f"hadoop jar {HADOOP_JAR_PATH} terasort /tmp/teragen_output_{i} /tmp/terasort_output_{i}"
        t, c, m = run_command(cmd, f"/tmp/terasort_output_{i}")

        f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        terasort_times.append(t)
        terasort_cpus.append(c)
        terasort_mems.append(m)

    print_and_plot("TeraSort", terasort_times, terasort_cpus, terasort_mems)

    f.write("\nTeraValidate Results\n")
    for i in range(1, ITERATIONS + 1):
        print(f"Running TeraValidate {i}/{ITERATIONS}")
        cmd = f"hadoop jar {HADOOP_JAR_PATH} teravalidate /tmp/terasort_output_{i} /tmp/teravalidate_output_{i}"
        t, c, m = run_command(cmd, f"/tmp/teravalidate_output_{i}")

        f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        teraval_times.append(t)
        teraval_cpus.append(c)
        teraval_mems.append(m)

    print_and_plot("TeraValidate", teraval_times, teraval_cpus, teraval_mems)


print("Cleaning HDFS temporary files")
subprocess.run(
    "hadoop fs -rm -r /tmp/teragen_output_* /tmp/terasort_output_* /tmp/teravalidate_output_*",
    shell=True
)

print("Benchmark completed")
