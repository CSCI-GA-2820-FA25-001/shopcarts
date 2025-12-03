# These can be overidden with env vars.
REGISTRY ?= cluster-registry:5000
IMAGE_NAME ?= shopcarts
IMAGE_TAG ?= 1.0
SHOPCARTS_IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
PLATFORM ?= "linux/amd64,linux/arm64"
CLUSTER ?= nyu-devops

.SILENT:

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

##@ Development

.PHONY: clean
clean:	## Removes all dangling build cache
	$(info Removing all dangling build cache..)
	-docker rmi $(SHOPCARTS_IMAGE)
	docker image prune -f
	docker buildx prune -f

.PHONY: install
install: ## Install Python dependencies
	$(info Installing dependencies...)
	sudo pipenv install --system --dev

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	-flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
	-flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
	-pylint service tests --max-line-length=127

.PHONY: test
test: ## Run the unit tests
	$(info Running tests...)
	export RETRY_COUNT=1; pytest --pspec --cov=service --cov-fail-under=95 --disable-warnings

.PHONY: run
run: ## Run the service
	$(info Starting service...)
	honcho start

.PHONY: secret
secret: ## Generate a secret hex key
	$(info Generating a new secret key...)
	python3 -c 'import secrets; print(secrets.token_hex())'

##@ Kubernetes

.PHONY: cluster
cluster: ## Create a K3D Kubernetes cluster with load balancer and registry
	$(info Creating Kubernetes cluster $(CLUSTER) with a registry and 2 worker nodes...)
	k3d cluster create $(CLUSTER) --agents 2 --registry-create cluster-registry:0.0.0.0:5000 --port '8080:80@loadbalancer'

.PHONY: cluster-rm
cluster-rm: ## Remove a K3D Kubernetes cluster
	$(info Removing Kubernetes cluster...)
	k3d cluster delete nyu-devops

.PHONY: deploy
deploy: ## Deploy the service on local Kubernetes
	$(info Deploying service locally...)
	kubectl apply -R -f k8s/

##@ OpenShift

.PHONY: oc-login
oc-login: ## Login to OpenShift cluster (requires OC_SERVER and OC_TOKEN environment variables)
	$(info Logging into OpenShift cluster...)
	@if [ -z "$(OC_SERVER)" ]; then \
		echo "Error: OC_SERVER environment variable not set"; \
		echo "Usage: OC_SERVER=https://api.cluster.com:6443 OC_TOKEN=sha256~... make oc-login"; \
		exit 1; \
	fi
	@if [ -z "$(OC_TOKEN)" ]; then \
		echo "Error: OC_TOKEN environment variable not set"; \
		echo "Usage: OC_SERVER=https://api.cluster.com:6443 OC_TOKEN=sha256~... make oc-login"; \
		exit 1; \
	fi
	oc login --token=$(OC_TOKEN) --server=$(OC_SERVER)

.PHONY: oc-status
oc-status: ## Check OpenShift cluster status
	$(info Checking OpenShift status...)
	oc status
	oc get pods

.PHONY: oc-deploy-db
oc-deploy-db: ## Deploy PostgreSQL database to OpenShift
	$(info Deploying PostgreSQL to OpenShift...)
	oc apply -f k8s/postgresql/
	$(info Waiting for PostgreSQL pod to be ready...)
	oc wait --for=condition=ready pod -l app=postgres --timeout=300s
	$(info PostgreSQL deployed successfully!)
	@echo "\nTo verify the deployment:"
	@echo "  oc get pods -l app=postgres"
	@echo "  oc get svc postgres"
	@echo "  oc logs postgres-0"

.PHONY: oc-deploy-app
oc-deploy-app: ## Deploy the shopcarts application to OpenShift
	$(info Deploying shopcarts application to OpenShift...)
	oc apply -f k8s/deployment.yaml
	oc apply -f k8s/service.yaml
	oc apply -f k8s/ingress.yaml
	$(info Waiting for shopcarts deployment to be ready...)
	oc wait --for=condition=available deployment/shopcarts --timeout=300s
	$(info Shopcarts application deployed successfully!)
	@echo "\nTo access the application:"
	@echo "  oc get routes"
	@echo "  oc get pods -l app=shopcarts"

.PHONY: oc-deploy-all
oc-deploy-all: oc-deploy-db oc-deploy-app ## Deploy both database and application to OpenShift
	$(info All components deployed to OpenShift!)

.PHONY: oc-delete-db
oc-delete-db: ## Remove PostgreSQL database from OpenShift
	$(info Removing PostgreSQL from OpenShift...)
	-oc delete -f k8s/postgresql/
	$(info PostgreSQL removed from OpenShift)

.PHONY: oc-delete-app
oc-delete-app: ## Remove shopcarts application from OpenShift
	$(info Removing shopcarts application from OpenShift...)
	-oc delete -f k8s/deployment.yaml
	-oc delete -f k8s/service.yaml
	-oc delete -f k8s/ingress.yaml
	$(info Shopcarts application removed from OpenShift)

.PHONY: oc-delete-all
oc-delete-all: oc-delete-app oc-delete-db ## Remove all components from OpenShift
	$(info All components removed from OpenShift)

.PHONY: oc-logs-db
oc-logs-db: ## Show PostgreSQL logs
	$(info Showing PostgreSQL logs...)
	oc logs postgres-0 --tail=50 -f

.PHONY: oc-logs-app
oc-logs-app: ## Show shopcarts application logs
	$(info Showing shopcarts application logs...)
	oc logs -l app=shopcarts --tail=50 -f

.PHONY: oc-exec-db
oc-exec-db: ## Open a shell in the PostgreSQL pod
	$(info Opening shell in PostgreSQL pod...)
	oc exec -it postgres-0 -- psql -U postgres -d shopcarts

.PHONY: oc-export-db
oc-export-db: ## Export PostgreSQL manifests from OpenShift (for updating repository)
	$(info Exporting PostgreSQL manifests from OpenShift...)
	@mkdir -p exported-manifests
	oc get statefulset postgres -o yaml > exported-manifests/statefulset.yaml
	oc get service postgres -o yaml > exported-manifests/service.yaml
	oc get secret shopcarts-creds -o yaml > exported-manifests/secret.yaml
	oc get configmap postgres-config -o yaml > exported-manifests/configmap.yaml
	oc get pvc postgres-pvc -o yaml > exported-manifests/pvc.yaml
	$(info Manifests exported to exported-manifests/ directory)
	@echo "\nNext steps:"
	@echo "1. Clean the manifests: ./scripts/clean-k8s-manifests.sh exported-manifests"
	@echo "2. Review the cleaned manifests"
	@echo "3. Copy to repository: cp exported-manifests/*.yaml k8s/postgresql/"
	@echo "4. Commit the changes"

.PHONY: oc-verify-db
oc-verify-db: ## Verify PostgreSQL deployment is working
	$(info Verifying PostgreSQL deployment...)
	@echo "\n=== Pod Status ==="
	oc get pods -l app=postgres
	@echo "\n=== Service Status ==="
	oc get svc postgres
	@echo "\n=== Testing Database Connection ==="
	oc run -i --tty --rm debug --image=postgres:15-alpine --restart=Never -- \
		psql -h postgres -U postgres -d shopcarts -c '\l' || true
	@echo "\n=== Checking Secret ==="
	@echo "DATABASE_URI:"
	@oc get secret shopcarts-creds -o jsonpath='{.data.database-uri}' | base64 -d
	@echo "\n"

############################################################
# COMMANDS FOR BUILDING THE IMAGE
############################################################

##@ Image Build and Push

.PHONY: init
init: export DOCKER_BUILDKIT=1
init:	## Creates the buildx instance
	$(info Initializing Builder...)
	-docker buildx create --use --name=qemu
	docker buildx inspect --bootstrap

.PHONY: build
build:	## Build the project container image for local platform
	$(info Building $(SHOPCARTS_IMAGE)...)
	docker build --rm --pull --tag $(SHOPCARTS_IMAGE) .

.PHONY: push
push:	## Push the image to the container registry
	$(info Pushing $(SHOPCARTS_IMAGE)...)
	docker push $(SHOPCARTS_IMAGE)

.PHONY: buildx
buildx:	## Build multi-platform image with buildx
	$(info Building multi-platform image $(SHOPCARTS_IMAGE) for $(PLATFORM)...)
	docker buildx build --file Dockerfile --pull --platform=$(PLATFORM) --tag $(SHOPCARTS_IMAGE) --push .

.PHONY: remove
remove:	## Stop and remove the buildx builder
	$(info Stopping and removing the builder image...)
	docker buildx stop
	docker buildx rm