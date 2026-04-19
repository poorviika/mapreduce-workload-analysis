Performance Evaluation of Hadoop MapReduce Workloads in Containerized and Virtual Machine Environments

1.Overview
This initiative undertakes an examination of Hadoop MapReduce workload performance across two distinct operational settings:

  * A containerized framework leveraging Docker technology and A virtualized infrastructure employing a Virtual Machine
The primary aim of this analysis is to ascertain the differentials in execution time, CPU utilization, and memory consumption when operating within these contrasting 
environments.

2. Experimental Setup

The experimental design ensured comparable conditions across both environments. Specifically, each environment was provisioned with analogous system resources, and to preclude 
any potential operational interference, only one setup was active at any given moment. For a rigorous comparative analysis, consistent MapReduce workloads were employed 
throughout the evaluations.

Regarding deployment specifics, the containerized configuration facilitated Hadoop's orchestration through Docker Compose. Conversely, within the virtual machine environment, 
the Hadoop services necessitated manual initialization and ongoing management.

3. System Architecture

The implemented Hadoop cluster incorporates several core components, each fulfilling a specific function:

  NameNode – responsible for the management of file system metadata
  DataNode – tasked with the storage of data blocks
  ResourceManager – facilitates the scheduling of jobs across the cluster
  NodeManager – designated for the execution of individual tasks
  HistoryServer – maintains a record of completed job histories

4. Execution Procedure

4.1 Docker Environment

Cluster initialization:

docker-compose up -d

Verification of container status:

docker ps

Web interface access points:

  NameNode → http://localhost:9870
  ResourceManager → http://localhost:8088

Execution of MapReduce workloads:

docker exec -it namenode bash

hadoop jar ... teragen 10000 /input
hadoop jar ... terasort /input /output
hadoop jar ... teravalidate /output /validate

4.2 Virtual Machine Environment

Hadoop service activation:

start-all.sh

Process verification:

jps

Execution of MapReduce workloads:

hadoop jar ... teragen 10000 /input
hadoop jar ... terasort /input /output
hadoop jar ... teravalidate /output /validate

5. Automated Execution

To ensure consistency and efficiency in workload management, a custom Python script was developed for automated execution.

This script is engineered to carry out several key functions:

  Systematic execution of the TeraGen, TeraSort, and TeraValidate benchmark suite
  Completion of multiple iterative runs to gather comprehensive data
  Precise measurement of critical performance metrics, including execution time, CPU utilization, and memory consumption
  Automated generation of graphical representations for the collected results

To initiate the automation process, execute:

python3 hadoop_benchmark.py

6. Performance Metrics Monitored

The evaluation focused on the collection and analysis of the following key performance indicators:

  Execution Time
  CPU Utilization
  Memory Consumption

7. Results Documentation

Benchmark results and corresponding visualizations are included in the repository.
They demonstrate the performance differences between containerized and virtualized environments under identical workloads.

8. Principal Observations

Analysis of the collected data revealed several critical distinctions between the environments:

  Containerized environments consistently demonstrated superior execution speeds.
  The operation within virtual machines was associated with discernible additional overhead.
  Overall, containers exhibited enhanced efficiency for the specific MapReduce workload under investigation.

9. Technological Framework

The implementation and analysis of this project relied upon the following key technologies:

  Docker and Docker Compose, for containerization and orchestration
  Apache Hadoop, as the distributed computing framework
  Python, utilized for both workload automation and data visualization
  Virtual Machine platforms, specifically VirtualBox or UTM, for the virtualized environment

10. Concluding Remarks

This investigation successfully illustrated the tangible performance disparities inherent between containerized and virtualized infrastructures when executing Hadoop 
workloads. The findings indicate that containers generally afford superior performance and operational efficiency. Conversely, virtual machines retain an advantage in 
providing a more robust level of isolation.

11. Recommendations for Further Research

Building upon the insights gained from this study, several avenues for future work are identified to broaden the scope and depth of analysis:

  Implementation of multi-node cluster configurations for more distributed testing
  Evaluation with significantly larger datasets to assess scalability
  Expansion of testing to cloud-based environments, such as AWS or GCP
  Integration with advanced monitoring and observability tools for enhanced data collection
