include etc/environment.sh

eb: eb.region1 eb.region2
eb.region1:
	sam package -t ${EVENTBRIDGE1_TEMPLATE} --region ${P_REGION1} --output-template-file ${EVENTBRIDGE1_OUTPUT} --s3-bucket ${S3BUCKET_USE1}
	sam deploy -t ${EVENTBRIDGE1_OUTPUT} --region ${P_REGION1} --stack-name ${EVENTBRIDGE1_STACK} --parameter-overrides ${EVENTBRIDGE1_PARAMS} --capabilities CAPABILITY_NAMED_IAM
eb.region2:
	sam package -t ${EVENTBRIDGE2_TEMPLATE} --region ${P_REGION2} --output-template-file ${EVENTBRIDGE2_OUTPUT} --s3-bucket ${S3BUCKET_USW2}
	sam deploy -t ${EVENTBRIDGE2_OUTPUT} --region ${P_REGION2} --stack-name ${EVENTBRIDGE2_STACK} --parameter-overrides ${EVENTBRIDGE2_PARAMS} --capabilities CAPABILITY_NAMED_IAM
	
ebg: ebg.package ebg.deploy
ebg.package:
	sam package -t ${EVENTBRIDGE_GLOBAL_TEMPLATE} --region ${P_REGION1} --output-template-file ${EVENTBRIDGE_GLOBAL_OUTPUT} --s3-bucket ${S3BUCKET_USE1}
ebg.deploy:
	sam deploy -t ${EVENTBRIDGE_GLOBAL_OUTPUT} --region ${P_REGION1} --stack-name ${EVENTBRIDGE_GLOBAL_STACK} --parameter-overrides ${EVENTBRIDGE_GLOBAL_PARAMS} --capabilities CAPABILITY_NAMED_IAM

eb.test:
	python3 src/put_event.py --endpoint ${O_ENDPOINTID} --bus ${P_NAME} --message '{"type": "demo", "message": "hello world"}' | jq
r53.config:
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'
r53.status:
	aws route53 get-health-check-status --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheckObservations[] | select(.Region | contains("${P_REGION1}", "${P_REGION2}"))'
r53.inverted:
	aws route53 update-health-check --health-check-id ${O_HEALTHCHECK} --inverted | jq
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'
r53.noinverted:
	aws route53 update-health-check --health-check-id ${O_HEALTHCHECK} --no-inverted | jq
	aws route53 get-health-check --health-check-id ${O_HEALTHCHECK} | jq '.HealthCheck.HealthCheckConfig.Inverted'
