FROM golang:1.24-alpine
RUN apk add curl python3 py3-pip
WORKDIR /app
COPY . .
RUN pip install brian2 nest-simulator matplotlib scipy numpy
RUN go mod tidy && go build -o superbrain ./cmd/server/main.go
CMD ["./superbrain"]
