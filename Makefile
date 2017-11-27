# Some simple testing tasks (sorry, UNIX only).

SERVICE=service-email

lint:
	@tox -e isort,flake8,mypy

run-streams:
	@docker run -d --name streams -p 4222:4222 nats-streaming:0.6.0

test:
	@docker network create test
	@docker run -d --name streams --network test -p 4222:4222 nats-streaming:0.6.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker run --rm --network test -e STREAM_URI=streams:4222 $(SERVICE)

clean-docker:
	@docker rm -f streams
	@docker network rm test
	@docker rmi $(SERVICE)


.PHONY: lint test clean-docker build
