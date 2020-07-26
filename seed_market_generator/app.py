import os
import json
import random
import itertools as it
import re
import logging
import boto3
from pythonjsonlogger import jsonlogger


sqs = boto3.client('sqs')


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


def generate_seed(workers, firms):
    return {
        "workers": {worker: random.sample(firms, len(firms)) for worker in workers},
        "firms": {firm: random.sample(workers, len(workers)) for firm in firms}
    }


def generate_seeds(num_workers, num_firms, num_seeds):
    workers = [f'W{worker + 1}' for worker in range(num_workers)]
    firms = [f'F{firm + 1}' for firm in range(num_firms)]

    seed_markets = []
    id_set = set()
    for i in range(num_seeds):
        while True:
            
            potential_seed = generate_seed(workers, firms)
            market_id = create_id_from_market(potential_seed)

            if market_id not in id_set:
                seed_markets.append({
                    "id": market_id,
                    "preferences": potential_seed
                })
                id_set.add(market_id)
                break
            
    return seed_markets


def create_id_from_market(market):

    market_id = "".join(k + "".join(v) for k, v in it.chain(market["workers"].items(), market["firms"].items()))
    market_id = re.sub('[^0-9]','', market_id)
    
    return market_id


def send_messages(seed_markets):
    for market in seed_markets:
        response = sqs.send_message(QueueUrl=os.environ["QUEUE_URL"], MessageBody=json.dumps(market))


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

    logger.info(os.environ["QUEUE_URL"])

    data = json.loads(event["body"])

    logger.info(data)

    seed_markets = generate_seeds(data["num_workers"], data["num_firms"], data["num_seeds"])

    logger.info(len(seed_markets))

    send_messages(seed_markets)

    return {
        "statusCode": 200,
        "body": json.dumps(data),
    }
