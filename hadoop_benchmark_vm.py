import argparse
import os
import subprocess
import time

import matplotlib.pyplot as plt
import psutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run VM-based Hadoop MapReduce benchmarks."
    )
    parser.add_argument(
        "--hadoop-jar-path",
        required=True,
        help="Local path to hadoop-mapreduce-examples-3.2.1.jar",
    )
    parser.add_argument(
        "--data-size",
        type=int,
        default=10000000,
        help="Number of rows to generate for TeraGen.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of benchmark iterations.",
    )
    parser.add_argument(
        "--results-dir",
        default="vm_results",
        help="Directory where benchmark results and graphs are saved.",
    )
    return parser.parse_args()


def run_command(command, cleanup_path=None):
    if cleanup_path:
        subprocess.run(
            f"hadoop fs -rm -r -skipTrash {cleanup_path}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    start_time = time.time()
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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


def print_and_plot(label, times, cpus, mems, results_dir):
    avg_time = sum(times) / len(times)
    avg_cpu = sum(cpus) / len(cpus)
    avg_mem = sum(mems) / len(mems)

    print(f"\n{label} averages")
    print(f"Time: {avg_time:.2f} sec")
    print(f"CPU: {avg_cpu:.2f}%")
    print(f"Memory: {avg_mem:.2f} MB")

    iterations = list(range(1, len(times) + 1))
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(iterations, times, marker="o")
    plt.title(f"{label} metrics")
    plt.ylabel("Time (s)")
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(iterations, cpus, marker="o")
    plt.ylabel("CPU (%)")
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(iterations, mems, marker="o")
    plt.xlabel("Iteration")
    plt.ylabel("Memory (MB)")
    plt.grid(True)

    plt.tight_layout()
    output_path = os.path.join(results_dir, f"vm_{label}.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {label} graph to {output_path}")


if __name__ == "__main__":
    args = parse_args()
    os.makedirs(args.results_dir, exist_ok=True)
    results_file = os.path.join(args.results_dir, "vm_results.txt")

    teragen_times, teragen_cpus, teragen_mems = [], [], []
    terasort_times, terasort_cpus, terasort_mems = [], [], []
    teraval_times, teraval_cpus, teraval_mems = [], [], []

    with open(results_file, "w") as f:
        f.write("Hadoop Benchmark Results (VM)\n\n")
        f.write("TeraGen Results\n")

        for i in range(1, args.iterations + 1):
            print(f"Running TeraGen {i}/{args.iterations}")
            input_path = f"/tmp/teragen_output_{i}"
            cmd = f"hadoop jar {args.hadoop_jar_path} teragen {args.data_size} {input_path}"
            t, c, m = run_command(cmd, input_path)
            teragen_times.append(t)
            teragen_cpus.append(c)
            teragen_mems.append(m)
            f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        print_and_plot("TeraGen", teragen_times, teragen_cpus, teragen_mems, args.results_dir)

        f.write("\nTeraSort Results\n")
        for i in range(1, args.iterations + 1):
            print(f"Running TeraSort {i}/{args.iterations}")
            input_path = f"/tmp/teragen_output_{i}"
            output_path = f"/tmp/terasort_output_{i}"
            cmd = f"hadoop jar {args.hadoop_jar_path} terasort {input_path} {output_path}"
            t, c, m = run_command(cmd, output_path)
            terasort_times.append(t)
            terasort_cpus.append(c)
            terasort_mems.append(m)
            f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        print_and_plot("TeraSort", terasort_times, terasort_cpus, terasort_mems, args.results_dir)

        f.write("\nTeraValidate Results\n")
        for i in range(1, args.iterations + 1):
            print(f"Running TeraValidate {i}/{args.iterations}")
            input_path = f"/tmp/terasort_output_{i}"
            output_path = f"/tmp/teravalidate_output_{i}"
            cmd = f"hadoop jar {args.hadoop_jar_path} teravalidate {input_path} {output_path}"
            t, c, m = run_command(cmd, output_path)
            teraval_times.append(t)
            teraval_cpus.append(c)
            teraval_mems.append(m)
            f.write(f"{i}  {t:.2f} sec  {c:.2f}%  {m:.2f} MB\n")

        print_and_plot("TeraValidate", teraval_times, teraval_cpus, teraval_mems, args.results_dir)

    print(f"Results saved in {results_file}")
    cleanup_command = (
        "hadoop fs -rm -r -skipTrash /tmp/teragen_output_* "
        "/tmp/terasort_output_* /tmp/teravalidate_output_*"
    )
    subprocess.run(cleanup_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Benchmark completed")
