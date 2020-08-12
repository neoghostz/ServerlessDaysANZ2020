pyCheck:
	PYTHONPATH=src:$PYTHONPATH pipenv run pytest --cov=src --cov-report term-missing
	flake8 --ignore=E501,E402 ./src
.PHONY: pyCheck

genReqs:
	pipenv lock -r > requirements.txt
.PHONY: genReqs

samBuild: genReqs
	sam build -t .sam/template.yaml -m ./requirements.txt -b ./build -s .
.PHONY: samBuild

samPackage: samBuild
	sam package --template-file ./build/template.yaml --s3-bucket versent-innovation-2019-lambda-ap-southeast-2 --s3-prefix Serverless-Days-2020-Demo --output-template-file ./build/sam-template.yaml --profile saml
.PHONY: samPackage

samDeploy: samPackage
	sam deploy --template-file ./build/sam-template.yaml --stack-name Serverless-Days-2020-Demo --capabilities CAPABILITY_IAM --region ap-southeast-2 --profile saml
.PHONY: samDeploy

samDestroy:
	aws cloudformation delete-stack --stack-name Serverless-Days-2020-Demo --region ap-southeast-2 --profile saml