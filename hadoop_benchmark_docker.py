import argparse
import os
import subprocess
import time

import matplotlib.pyplot as plt
import numpy as np
import psutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Docker-based Hadoop MapReduce benchmarks."
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of benchmark iterations."
    )
    parser.add_argument(
        "--data-size",
        type=int,
        default=1000000000,
        help="Number of rows to generate for TeraGen."
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=134217728,
        help="HDFS block size in bytes."
    )
    parser.add_argument(
        "--mappers",
        type=int,
        default=4,
        help="Number of mapper tasks for TeraGen."
    )
    parser.add_argument(
        "--reducers",
        type=int,
        default=4,
        help="Number of reducer tasks for TeraSort and TeraValidate."
    )
    parser.add_argument(
        "--hdfs-path",
        default="/user/hadoop",
        help="Base HDFS path for benchmark input/output."
    )
    parser.add_argument(
        "--jar-path",
        default="/opt/hadoop-3.2.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar",
        help="Path to the Hadoop examples JAR inside the namenode container."
    )
    parser.add_argument(
        "--compose-file",
        default="docker-compose.yml",
        help="Docker Compose file used to start the cluster."
    )
    parser.add_argument(
        "--output-dir",
        default="docker_results",
        help="Directory where benchmark output files are saved."
    )
    return parser.parse_args()


def run_command(command):
    print(f"\nRunning: {command}")
    start_time = time.time()
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    cpu_usage = []
    mem_usage = []

    while process.poll() is None:
        cpu_usage.append(psutil.cpu_percent(interval=1))
        mem_usage.append(psutil.virtual_memory().percent)

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Command failed with exit code {process.returncode}")
        print(stderr)

    elapsed_time = round(time.time() - start_time, 2)
    avg_cpu = round(sum(cpu_usage) / len(cpu_usage), 2) if cpu_usage else 0
    avg_mem = round(sum(mem_usage) / len(mem_usage), 2) if mem_usage else 0

    return elapsed_time, avg_cpu, avg_mem


def cleanup_hdfs(path, namenode):
    command = f"docker exec {namenode} hdfs dfs -rm -r -skipTrash {path}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cleanup_all(hdfs_path, namenode):
    command = f"docker exec {namenode} hdfs dfs -rm -r -skipTrash {hdfs_path}/*"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_cluster(compose_file):
    print("\nRestarting Hadoop cluster...")
    subprocess.run(
        f"docker-compose -f {compose_file} down && docker-compose -f {compose_file} up -d",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    start_cluster(args.compose_file)
    time.sleep(60)

    results = []
    output_file = os.path.join(args.output_dir, "benchmark_results_docker.txt")

    with open(output_file, "w") as f:
        f.write("Hadoop Benchmark Results (Docker)\n\n")

        for i in range(1, args.iterations + 1):
            print(f"\nIteration {i}/{args.iterations}")
            cleanup_all(args.hdfs_path, "namenode")

            teragen_path = f"{args.hdfs_path}/teragen-{args.data_size}"
            terasort_path = f"{args.hdfs_path}/terasort-{args.data_size}"
            teravalidate_path = f"{args.hdfs_path}/teravalidate-{args.data_size}"

            tg_command = (
                f"docker exec namenode hadoop jar {args.jar_path} teragen "
                f"-Dmapreduce.map.tasks={args.mappers} "
                f"-Ddfs.blocksize={args.block_size} "
                f"{args.data_size} {teragen_path}"
            )
            tg_time, tg_cpu, tg_mem = run_command(tg_command)
            cleanup_hdfs(teragen_path, "namenode")

            ts_command = (
                f"docker exec namenode hadoop jar {args.jar_path} terasort "
                f"-Dmapreduce.job.reduces={args.reducers} "
                f"{teragen_path} {terasort_path}"
            )
            ts_time, ts_cpu, ts_mem = run_command(ts_command)
            cleanup_hdfs(terasort_path, "namenode")

            tv_command = (
                f"docker exec namenode hadoop jar {args.jar_path} teravalidate "
                f"-Dmapreduce.job.reduces={args.reducers} "
                f"{terasort_path} {teravalidate_path}"
            )
            tv_time, tv_cpu, tv_mem = run_command(tv_command)
            cleanup_hdfs(teravalidate_path, "namenode")

            results.append(
                (
                    tg_time,
                    tg_cpu,
                    tg_mem,
                    ts_time,
                    ts_cpu,
                    ts_mem,
                    tv_time,
                    tv_cpu,
                    tv_mem,
                )
            )

            f.write(f"Iteration {i} Results:\n")
            f.write(f"TeraGen: Time = {tg_time}s, CPU = {tg_cpu}%, Memory = {tg_mem}%\n")
            f.write(f"TeraSort: Time = {ts_time}s, CPU = {ts_cpu}%, Memory = {ts_mem}%\n")
            f.write(f"TeraValidate: Time = {tv_time}s, CPU = {tv_cpu}%, Memory = {tv_mem}%\n\n")

    print("\nBenchmarking completed.")

    iterations = np.arange(1, args.iterations + 1)
    teragen_times = [r[0] for r in results]
    terasort_times = [r[3] for r in results]
    teravalidate_times = [r[6] for r in results]
    teragen_cpu = [r[1] for r in results]
    terasort_cpu = [r[4] for r in results]
    teravalidate_cpu = [r[7] for r in results]
    teragen_mem = [r[2] for r in results]
    terasort_mem = [r[5] for r in results]
    teravalidate_mem = [r[8] for r in results]

    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    axs[0].plot(iterations, teragen_times, marker="o", label="TeraGen")
    axs[0].plot(iterations, terasort_times, marker="s", label="TeraSort")
    axs[0].plot(iterations, teravalidate_times, marker="^", label="TeraValidate")
    axs[0].set_ylabel("Time (s)")
    axs[0].set_title("Execution Time")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(iterations, teragen_cpu, marker="o", label="TeraGen")
    axs[1].plot(iterations, terasort_cpu, marker="s", label="TeraSort")
    axs[1].plot(iterations, teravalidate_cpu, marker="^", label="TeraValidate")
    axs[1].set_ylabel("CPU (%)")
    axs[1].set_title("CPU Usage")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(iterations, teragen_mem, marker="o", label="TeraGen")
    axs[2].plot(iterations, terasort_mem, marker="s", label="TeraSort")
    axs[2].plot(iterations, teravalidate_mem, marker="^", label="TeraValidate")
    axs[2].set_ylabel("Memory (%)")
    axs[2].set_xlabel("Iteration")
    axs[2].set_title("Memory Usage")
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    output_plot = os.path.join(args.output_dir, "docker_benchmark.png")
    plt.savefig(output_plot)
    plt.close()
    print(f"Saved benchmark graph to {output_plot}")
