import json
import os
import requests


def query_subgraph(query):
    subgraph_url = os.getenv("SUBGRAPH_URL")
    request = requests.post(subgraph_url, "", json={"query": query})
    if request.status_code != 200:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Query failed. Return code is {request.status_code}\n{query}")
    result = request.json()
    return result

def get_all_interesting_prediction_contracts():
    chunk_size = 1000  # max for subgraph = 1000
    offset = 0
    contracts={}
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
        result = query_subgraph(query)
        if "errors" in result:
            raise AssertionError(result)
        new_orders = result["data"]["predictContracts"]
        if new_orders == []:
            break
        for order in new_orders:
            contracts[order["id"]] = {
                "name": order["token"]["name"],
                "symbol": order["token"]["symbol"],
                "blocks_per_epoch": order["blocksPerEpoch"],
                "blocks_per_subscription": order["blocksPerSubscription"],
                "last_submited_epoch":0
            }
    return contracts
