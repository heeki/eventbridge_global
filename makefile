include etc/environment.sh

ddb: ddb.package ddb.deploy
ddb.package:
	sam package -t ${DYNAMODB_TEMPLATE} --region ${P_REGION1} --output-template-file ${DYNAMODB_OUTPUT} --s3-bucket ${S3BUCKET_REGION1}
ddb.deploy:
	sam deploy -t ${DYNAMODB_OUTPUT} --region ${P_REGION1} --stack-name ${DYNAMODB_STACK} --parameter-overrides ${DYNAMODB_PARAMS} --capabilities CAPABILITY_NAMED_IAM

eb: eb.region1 eb.region2
eb.region1:
	sam package -t ${EVENTBRIDGE1_TEMPLATE} --region ${P_REGION1} --output-template-file ${EVENTBRIDGE1_OUTPUT} --s3-bucket ${S3BUCKET_REGION1}
	sam deploy -t ${EVENTBRIDGE1_OUTPUT} --region ${P_REGION1} --stack-name ${EVENTBRIDGE1_STACK} --parameter-overrides ${EVENTBRIDGE1_PARAMS} --capabilities CAPABILITY_NAMED_IAM
eb.region2:
	sam package -t ${EVENTBRIDGE2_TEMPLATE} --region ${P_REGION2} --output-template-file ${EVENTBRIDGE2_OUTPUT} --s3-bucket ${S3BUCKET_REGION2}
	sam deploy -t ${EVENTBRIDGE2_OUTPUT} --region ${P_REGION2} --stack-name ${EVENTBRIDGE2_STACK} --parameter-overrides ${EVENTBRIDGE2_PARAMS} --capabilities CAPABILITY_NAMED_IAM
	
ebg: ebg.package ebg.deploy
ebg.package:
	sam package -t ${EVENTBRIDGE_GLOBAL_TEMPLATE} --region ${P_REGION1} --output-template-file ${EVENTBRIDGE_GLOBAL_OUTPUT} --s3-bucket ${S3BUCKET_REGION1}
ebg.deploy:
	sam deploy -t ${EVENTBRIDGE_GLOBAL_OUTPUT} --region ${P_REGION1} --stack-name ${EVENTBRIDGE_GLOBAL_STACK} --parameter-overrides ${EVENTBRIDGE_GLOBAL_PARAMS} --capabilities CAPABILITY_NAMED_IAM

eb.test:
	python3 src/put_event.py --endpoint ${O_ENDPOINTID} --bus ${P_NAME} --type "demo" --message "hello world" | jq
eb.test.id:
	python3 src/put_event.py --endpoint ${O_ENDPOINTID} --bus ${P_NAME} --idempotence_token ${P_IDEMPOTENCE_TOKEN} --type "demo" --message "hello world" | jq
eb.validate:
	date
	python3 src/validate_event.py --table ${O_TABLE} --idempotence_token ${P_IDEMPOTENCE_TOKEN} | jq
eb.loop:
	while true; do date; python3 src/put_event.py --endpoint ${O_ENDPOINTID} --bus ${P_NAME} --idempotence_token ${P_IDEMPOTENCE_TOKEN} --type "demo" --message "hello world" | jq; python3 src/validate_event.py --table ${O_TABLE} --idempotence_token ${P_IDEMPOTENCE_TOKEN} | jq; done
r53.config:
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'
r53.status:
	aws route53 get-health-check-status --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheckObservations[] | select(.Region | contains("${P_REGION1}", "${P_REGION2}"))'
r53.inverted:
	date
	aws route53 update-health-check --health-check-id ${O_HEALTHCHECK} --inverted | jq
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'
r53.noinverted:
	date
	aws route53 update-health-check --health-check-id ${O_HEALTHCHECK} --no-inverted | jq
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'

lambda.local1:
	sam local invoke -t ${EVENTBRIDGE1_TEMPLATE} --region ${P_REGION1} --parameter-overrides ${EVENTBRIDGE1_PARAMS} --env-vars etc/envvars.json -e etc/event.json Fn | jq
lambda.local2:
	sam local invoke -t ${EVENTBRIDGE2_TEMPLATE} --region ${P_REGION2} --parameter-overrides ${EVENTBRIDGE2_PARAMS} --env-vars etc/envvars.json -e etc/event.json Fn | jq
lambda.invoke.sync:
	aws --profile ${PROFILE} lambda invoke --function-name ${O_FN} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode
	cat tmp/fn.json | jq
lambda.invoke.async:
	aws --profile ${PROFILE} lambda invoke --function-name ${O_FN} --invocation-type Event --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "."
