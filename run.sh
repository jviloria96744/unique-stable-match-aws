#!/bin/bash
aws lambda invoke --function-name unique-stable-match-SeedMarketGeneratorFunction-1NDFQN2L2UIEU --invocation-type Event --payload fileb://events/event.json response.json