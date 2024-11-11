all :
	mkdir ./postgres_data
	mkdir ./qdrant_storage
	docker compose up

down :
	docker compose down