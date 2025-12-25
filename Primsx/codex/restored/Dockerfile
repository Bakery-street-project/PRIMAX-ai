FROM golang:1.22-alpine
WORKDIR /app
COPY . .
RUN go mod tidy && go build -o superbrain ./cmd/server/main.go
EXPOSE 8080
CMD ["./superbrain"]
