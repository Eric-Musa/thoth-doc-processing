
from dotenv import load_dotenv
load_dotenv()
import mdpd
import os
import pandas as pd

## connect to local Elastic Search instance
from elasticsearch import Elasticsearch

es = Elasticsearch(
    os.getenv('ELASTICSEARCH_URL'), 
    api_key=os.getenv('ELASTICSEARCH_API_KEY'),
    # basic_auth=(
    #     os.getenv('ELASTICSEARCH_USERNAME'), 
    #     os.getenv('ELASTICSEARCH_PASSWORD')
    # ),  # both work
)

def node_report(client=es):
    nodes = client.nodes.info()
    report = f'Total nodes: {nodes["_nodes"]["total"]}, successful: {nodes["_nodes"]["successful"]}, failed: {nodes["_nodes"]["failed"]}'
    for node_id, node in nodes['nodes'].items():
        report += f'\nNode ID: {node_id}, Name: {node["name"]}, Host: {node["host"]}, IP: {node["ip"]}'
    return report


if __name__ == "__main__":
    print(node_report())