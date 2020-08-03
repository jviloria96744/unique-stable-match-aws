import os
import json
import uuid
import random
import itertools as it
import re
from copy import deepcopy
import logging
from unique_stable_match import has_unique_stable_match
import boto3
from pythonjsonlogger import jsonlogger

dynamodb = boto3.resource("dynamodb", os.environ["AWS_REGION"])
table = dynamodb.Table(os.environ["TABLE_NAME"])


def setup_logging(log_level):
    logger = logging.getLogger()
 
    logger.setLevel(log_level)
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)

    # Testing showed lambda sets up one default handler.
    # Removing default handler in the event there is one
    # During testing handler isn't created so local tests should pass
    if len(logger.handlers) > 1:
        logger.removeHandler(logger.handlers[0])


def generate_samples_from_seed(seed, seed_id, num_samples, include_seed=True):
    num_workers = len(seed["workers"])
    num_firms = len(seed["firms"])

    samples = {}
    id_set = set()
    if include_seed:
        start_index = 1
        samples[seed_id] = seed
        id_set.add(seed_id)
    else:
        start_index = 0

    for i in range(start_index, num_samples):
        while True:
            new_sample = deepcopy(seed)

            sampling_param = .25
            new_sample = sample_from_seed("workers", num_workers, seed, new_sample, sampling_param)
            new_sample = sample_from_seed("firms", num_firms, seed, new_sample, sampling_param)

            market_id = create_id_from_market(new_sample)

            if market_id not in id_set:
                samples[market_id] = new_sample
                id_set.add(market_id)
                break

    return samples


def sample_from_seed(side_key, num_side, seed, new_sample, sampling_param):
    side_id = "W" if side_key == "workers" else "F"
    items_to_change = [
        f'{side_id}{random.randint(1, num_side)}' 
        for _ in range(int((num_side + 1) * sampling_param))
    ]
    for item in items_to_change:
        new_sample[side_key][item] = random.sample(seed[side_key][item], len(seed[side_key][item]))

    return new_sample


def create_id_from_market(market):

    market_id = "".join(k + "".join(v) for k, v in it.chain(market["workers"].items(), market["firms"].items()))
    market_id = re.sub('[^0-9]','', market_id)
    
    return market_id


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required

    context: object, required

    Returns
    ------
    
    """

    setup_logging(logging.INFO)
    logger = logging.getLogger()
    logger.info({"DynamoDB Table Name": os.environ["TABLE_NAME"]})

    count = 0
    for record in event['Records']:
        body = json.loads(record["body"])
        logger.info(body)


        samples_dict = generate_samples_from_seed(body["preferences"], body["id"], body["num_samples"], True)
        for k, v in samples_dict.items():
            if has_unique_stable_match(v):
                count += 1
                table.put_item(Item={
                    "MarketId": k,
                    "MarketSize": str(body["num_side"]),
                    "preferences": v
                })

    logger.info({"Unique_Stable_Matches": count})    
    return {
        "statusCode": 200,
        "body": json.dumps({"unique_count": count}),
    }