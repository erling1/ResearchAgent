
IMAGE_NAME := research-agent
DOCKERFILE := Dockerfile
APP_NAME := research-agent-container

build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .


run:
	docker run --name $(APP_NAME) -p 8080:8000 -p 3001:3001 $(IMAGE_NAME)


stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

# Remove the Docker image
clean:
	docker builder prune --force --all
	docker system prune --volumes -f --all

