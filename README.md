# MapReduce Workload Analysis

Performance evaluation of Hadoop MapReduce workloads in Docker container and VM environments.

## Project overview

This repository compares Hadoop MapReduce performance across two execution environments:

- Docker containerized cluster using Docker Compose
- Local virtual machine environment using a standalone Hadoop installation

The benchmark suite uses standard Hadoop examples: `TeraGen`, `TeraSort`, and `TeraValidate`.

## Repository contents

- `docker-compose.yml` — Hadoop cluster definitions for Docker
- `hadoop.env` — environment config for the Docker cluster
- `hadoop_benchmark_docker.py` — automated Docker benchmark script
- `hadoop_benchmark_vm.py` — automated VM benchmark script
- `docker_results/` — saved Docker benchmark graphs
- `vm_results/` — saved VM benchmark graphs

## Prerequisites

1. Docker Engine
2. Docker Compose
3. Python 3.8+
4. Local Hadoop installation for VM benchmarking

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Or use the provided Makefile:

```bash
make install
```

## Makefile commands

Use these make commands to run the benchmark and manage the cluster:

```bash
make up           # start Docker Hadoop cluster
make down         # stop Docker Hadoop cluster
make bench-docker # run Docker benchmark
make bench-vm     # run VM benchmark (requires HADOOP_JAR_PATH)
```

## Docker benchmark instructions

### Start the Hadoop Docker cluster

```bash
docker-compose up -d
```

### Confirm the cluster is running

```bash
docker ps
```

### Run the Docker benchmark

```bash
python3 hadoop_benchmark_docker.py
```

### Expected output

- `docker_results/benchmark_results_docker.txt`
- `docker_results/docker_benchmark.png`

### Default Docker benchmark settings

- Iterations: 5
- TeraGen data size: 1,000,000,000 rows
- HDFS path: `/user/hadoop`
- Container name: `namenode`

## VM benchmark instructions

Update the local JAR path and run the VM benchmark with:

```bash
python3 hadoop_benchmark_vm.py --hadoop-jar-path /path/to/hadoop-mapreduce-examples-3.2.1.jar
```

### Expected output

- `vm_results/vm_results.txt`
- `vm_results/vm_TeraGen.png`
- `vm_results/vm_TeraSort.png`
- `vm_results/vm_TeraValidate.png`

## What to expect from the benchmarks

The benchmark scripts generate:

- execution time per iteration
- average CPU utilization
- memory usage metrics
- graphical visualizations of trends across iterations

## How to interpret the results

- Lower execution time means better throughput
- Lower average CPU% can indicate underutilization or more efficient execution
- Memory trends show whether the workload is stable or spiking between runs

