import json
import os
import requests


def query_subgraph(query):
    subgraph_url = os.getenv("SUBGRAPH_URL")
    request = requests.post(subgraph_url, "", json={"query": query}, timeout=1.5)
    if request.status_code != 200:
        # pylint: disable=broad-exception-raised
        raise Exception(
            f"Query failed. Url: {subgraph_url}. Return code is {request.status_code}\n{query}"
        )
    result = request.json()
    return result


def get_all_interesting_prediction_contracts():
    chunk_size = 1000  # max for subgraph = 1000
    offset = 0
    contracts = {}

    try:
        # e.g. export CONTRACTS_TO_SUBMIT='["ETH-BTC", "ETH-USDT"]'
        contracts_to_submit = json.loads(os.getenv("CONTRACTS_TO_SUBMIT", "[]"))
    except json.decoder.JSONDecodeError:
        contracts_to_submit = []

    while True:
        query = """
        {
            predictContracts(skip:%s, first:%s){
                id
                token {
                    id
                    name
                    symbol
                }
                blocksPerEpoch
                blocksPerSubscription
                truevalSubmitTimeoutBlock
            }
        }
        """ % (
            offset,
            chunk_size,
        )
        offset += chunk_size
        try:
            result = query_subgraph(query)

            if contracts_to_submit:
                new_orders = [
                    result_item
                    for result_item in result["data"]["predictContracts"]
                    if result_item["token"]["symbol"] in contracts_to_submit
                ]
            else:
                new_orders = result["data"]["predictContracts"]

            if new_orders == []:
                break
            for order in new_orders:
                contracts[order["id"]] = {
                    "name": order["token"]["name"],
                    "address": order["id"],
                    "symbol": order["token"]["symbol"],
                    "blocks_per_epoch": order["blocksPerEpoch"],
                    "blocks_per_subscription": order["blocksPerSubscription"],
                    "last_submited_epoch": 0,
                }
        except Exception as e:
            print(e)
            return {}
    return contracts
