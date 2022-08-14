from app import index
import json

f = open('sample_put.json')
event_json = json.load(f)

index.scrape_conns(event=event_json, context=None)