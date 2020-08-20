# Makefile for building publishing container
PROJECT = ServerlessDaysANZ-Demo-API
VERSION = $(shell whoami)
#AUTH = $(shell aws --profile build --region ap-southeast-2 secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-southeast-2:264748061542:secret:github/versent-builder-foTpJN | jq -r '.SecretString | fromjson | .OAuthKey')
PWD = $(shell pwd)
GITSHORTHASH = $(shell git rev-parse HEAD | cut -c 1-7)
BUCKET = ap.southeast.2.lambda.functions.elendel.com.au
REGION = ap-southeast-2

genReqs:
	pipenv lock -r > requirements.txt
.PHONY: genReqs

genTestReqs:
	pipenv lock -r --dev > requirements.txt
.PHONY: genTestReqs

buildLocal: genReqs
	docker build -t $(APP_IMAGE) -f Dockerfile.alpine .
.PHONY: build

build: genReqs
	docker build -t $(APP_IMAGE_AWS) -f Dockerfile.ubuntu .
.PHONY: build

test: genTestReqs
	docker build -f Dockerfile.test -t $(PROJECT)-test .
.PHONY: test

ecrLogin:
	aws ecr get-login --no-include-email  --profile $(PROFILE) --region $(REGION) | bash
.PHONY: ecrLogin

ecrPush: ecrLogin
	docker tag $(APP_IMAGE) $(REGISTRY)/$(APP_IMAGE)
	docker tag $(APP_IMAGE) $(REGISTRY)/$(PROJECT):$(CONTAINER_TAG)
	docker push $(REGISTRY)/$(APP_IMAGE)
	docker push $(REGISTRY)/$(PROJECT):$(CONTAINER_TAG)
.PHONY: ecrPush

buildRequirements:
	pipenv lock -r > requirements.txt
.PHONY: buildRequirements

lint:
	flake8 --ignore=E501,E402 ./src
.PHONY: lint

pytest:
	PYTHONPATH=src/layers/python/:$PYTHONPATH pipenv run pytest --cov=src --cov-report term-missing
.PHONY: pytest

samBuild: genReqs
	sam build -t .sam/template.yaml -m ./requirements.txt -b ./build -s .
.PHONY: samBuild

samPackage: samBuild
	sam package --template-file ./build/template.yaml --s3-bucket $(BUCKET) --s3-prefix $(PROJECT) --output-template-file ./build/sam-template.yaml
.PHONY: samPackage

samDeploy: samPackage
	sam deploy --template-file ./build/sam-template.yaml --stack-name $(PROJECT)-$(GITSHORTHASH) --capabilities CAPABILITY_IAM --region $(REGION) --parameter-overrides GitHash=$(GITSHORTHASH)
.PHONY: samDeploy

samDestroy:
	aws cloudformation delete-stack --stack-name $(PROJECT)-$(GITSHORTHASH) --region ap-southeast-2