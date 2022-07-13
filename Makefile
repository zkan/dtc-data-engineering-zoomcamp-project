setup:
	mkdir -p mnt/dags mnt/logs mnt/plugins

up:
	docker-compose up

down:
	docker-compose down