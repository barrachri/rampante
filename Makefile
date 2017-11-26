# Some simple testing tasks (sorry, UNIX only).

SERVICE=service-email

lint:
	@tox -e isort,flake8,mypy

run-kafka:
	@docker run -d --name kafka -p 9092:9092 -e ADVERTISED_HOST=localhost -e ADVERTISED_PORT=9092  cassinyio/kafka:2.11_1.0.0

clean-kafka:
	@docker stop kafka
	@docker rm kafka


test:
	@docker network create test
	@docker run -d --name kafka --network test -e ADVERTISED_HOST=kafka -e ADVERTISED_PORT=9092  cassinyio/kafka:2.11_1.0.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker run --rm --network test -e KAFKA_URI=kafka:9092 $(SERVICE)

clean-docker:
	@docker rm -f kafka
	@docker network rm test
	@docker rmi $(SERVICE)


.PHONY: lint test clean-docker build
