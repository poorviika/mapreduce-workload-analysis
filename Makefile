PYTHON=python3
PIP=$(PYTHON) -m pip
HADOOP_JAR_PATH ?= /path/to/hadoop-mapreduce-examples-3.2.1.jar

.PHONY: install up down bench-docker bench-vm

install:
	$(PIP) install -r requirements.txt

up:
	docker-compose up -d

down:
	docker-compose down

bench-docker:
	$(PYTHON) hadoop_benchmark_docker.py

bench-vm:
	$(PYTHON) hadoop_benchmark_vm.py --hadoop-jar-path $(HADOOP_JAR_PATH)
