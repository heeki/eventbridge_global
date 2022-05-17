## Overview
This repository implements global endpoints for Amazon EventBridge.

## Implementation
To conduct deployments with the make commands below, the `etc/environment.template` file needs to be copied to `etc/environment.sh` and updated with your configuration parameters. Then the following commands can be used to deploy the endpoints in each of the regions. After the regional deployments are completed, deploy the global endpoint.

* `make eb`: deploy to both regions
* `make eb.region1`: if regional deployment is needed, deploy to the primary region
* `make eb.region2`: if regional deployment is needed, deploy to the secondary region
* `make ebg`: deploy the global endpoint

## Pre-requisites
In order to use the provided helper file, which makes `put_events` API calls to global endpoints, you will need to install the `awscrt` library. This can be done using the provided requirements.txt file. The commands also make use of `jq`.

```bash
pip install -r requirements.txt
brew install jq
```

## Testing
Test events can be sent to the global endpoint using the provided `put_event.py` helper code and can be executed with the provided make directive.

* `make eb.test`: send events to the global endpoint
* `make r53.config`: get configuration for the health check (inverted=true|false)
* `make r53.status`: get status of regional health checks
* `make r53.inverted`: set health check to inverted (fails over to the secondary region)
* `make r53.noinverted`: set health check to no-inverted (fails back to the primary region)
