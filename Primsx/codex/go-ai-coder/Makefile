all: build test lint

build:
	go build -o bin/server ./cmd/server

test:
	go test ./...

lint:
	golangci-lint run ./...

docker-build:
	docker build -t go-ai-coder:latest .

docker-run:
	docker run -p 8080:8080 go-ai-coder:latest

clean:
	rm -rf bin/*
