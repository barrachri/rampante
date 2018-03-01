# Some simple testing tasks (sorry, UNIX only).

SERVICE=rampante

lint:
	@tox -e isort,flake8,mypy

run-streams:
	@docker run -d --name streams -p 4222:4222 nats-streaming:0.7.0

test:
	@docker network create test
	@docker run -d --name streams --network test -p 4222:4222 nats-streaming:0.7.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker run --rm --network test -e STREAM_URI=nats://streams:4222 $(SERVICE)

clean-docker:
	@docker rm -f streams
	@docker network rm test
	@docker rm $(SERVICE)

.PHONY: lint run-streams test clean-docker
