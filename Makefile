setup:
	mkdir -p mnt/dags mnt/logs mnt/plugins tmp

up:
	docker-compose up

down:
	docker-compose down