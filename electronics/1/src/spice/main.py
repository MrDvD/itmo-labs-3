import yaml
from fastapi import FastAPI
import common.config as config

app = FastAPI()
cfg = config.load('config.yml')

@app.get("{cfg['url']}{cfg['prefix']}{cfg['circuit_endpoint']}")
def read_circuit():
    # Placeholder for the actual circuit generation logic
    return {"message": "Circuit generation endpoint"}