import logging
import json


logging.basicConfig(
    level=logging.INFO,
    filename='proxy.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def log_request_info(request_data: dict):
    logging.info("REQUEST: %s", json.dumps(_safe_serialize(request_data), ensure_ascii=False))

def log_response_info(response_data: dict):
    logging.info("RESPONSE: %s", json.dumps(_safe_serialize(response_data), ensure_ascii=False))

def _safe_serialize(data):
    def default(o):
        return str(o)
    return json.loads(json.dumps(data, default=default))
