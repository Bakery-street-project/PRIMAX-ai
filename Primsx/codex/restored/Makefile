build:
	go mod tidy
	docker build -t gcr.io/mythicnode/go-ai-superbrain:latest .

push:
	docker push gcr.io/mythicnode/go-ai-superbrain:latest

deploy:
	cd deploy/terraform && terraform init -reconfigure && terraform apply -auto-approve

run:
	gcloud run deploy go-ai-superbrain --image gcr.io/mythicnode/go-ai-superbrain:latest --platform managed --region europe-west1 --allow-unauthenticated
