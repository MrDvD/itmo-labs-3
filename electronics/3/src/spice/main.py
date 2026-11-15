import json
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import common.config as config
import uvicorn
import os
from pathlib import Path

app = FastAPI()
cfg = config.load('config.yml')
api = cfg['api']

LTSPICE_EXE = os.getenv("LTSPICE_PATH", "")
SCHEMAS_DIR = Path('/schemas')

@app.get(f"{api['prefix']}{api['generate_images_endpoint']}")
def generate_images():
    subprocess.run(["bash", "/app/.devcontainer/screenshots.sh"], check=True)
    return

@app.get(f"{api['prefix']}{api['schemas_endpoint']}/{{schema_number}}")
async def get_schema_image(schema_number: int):
    if schema_number < 1 or schema_number > 3:
        raise HTTPException(404)

    filename = f"schema{schema_number}.png"
    target = (SCHEMAS_DIR / filename).resolve()

    return FileResponse(
        target,
        filename=filename,
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=api['port'])