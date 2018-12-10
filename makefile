AUTH=ocramz
NAME=docker-openmpi
TAG=${AUTH}/${NAME}

export NNODES=4

.DEFAULT_GOAL := help

help:
	@echo "Use \`make <target>\` where <target> is one of"
	@echo "  help     display this help message"
	@echo "  build   build from Dockerfile"
	@echo "  rebuild rebuild from Dockerfile (ignores cached layers)"
	@echo "  main    build and docker-compose the whole thing"

build:
	docker build -t $(TAG) .

rebuild:
	docker build --no-cache -t $(TAG) .

main:
	# 1 worker node
	docker-compose up --scale mpi_head=1 --scale mpi_node=1 -d
	docker-compose exec --user mpirun --privileged mpi_head mpirun -n 1 python /home/mpirun/mpi4py_benchmarks/all_tests.py
	docker-compose down

	# 2 worker nodes
	docker-compose up --scale mpi_head=1 --scale mpi_node=2 -d
	docker-compose exec --user mpirun --privileged mpi_head mpirun -n 2 python /home/mpirun/mpi4py_benchmarks/all_tests.py
	docker-compose down

	# ${NNODES} worker nodes
	docker-compose up --scale mpi_head=1 --scale mpi_node=${NNODES} -d
	docker-compose exec --user mpirun --privileged mpi_head mpirun -n ${NNODES} python /home/mpirun/mpi4py_benchmarks/all_tests.py
	docker-compose down
