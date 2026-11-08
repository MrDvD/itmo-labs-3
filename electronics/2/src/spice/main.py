import json
import shutil
import tempfile
import asyncio
from fastapi import FastAPI, HTTPException
import common.config as config
import uvicorn
import os

app = FastAPI()
cfg = config.load('config.yml')
api = cfg['api']
server = cfg['server']

@app.get(f"{api['prefix']}{api['circuit_endpoint']}")
def read_circuit():
    with open(server['circuit_init_data_path'], 'r') as f:
        return json.load(f)

CIRCUIT_FILE_PATH = cfg['server']['circuit_file_path']
LTSPICE_EXE = os.getenv("LTSPICE_PATH", "")

def parse_ltspice_log(log_content: str) -> dict:
    TARGET_MEASUREMENTS = {"v_out", "i_load", "p_load"}
    result = {}
    lines = log_content.replace('\xa0', ' ').splitlines()
    current_meas = None
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        if line_str.startswith("Measurement:"):
            meas_name = line_str.split(":", 1)[1].strip()
            if meas_name in TARGET_MEASUREMENTS:
                current_meas = meas_name
                result[current_meas] = {
                    "step": [],
                    "value": [],
                    "from": [],
                    "to": []
                }
            else:
                current_meas = None
            continue
            
        if current_meas:
            parts = line_str.split()
            if parts[0].lower() == "step":
                continue
                
            if len(parts) >= 4 and parts[0].isdigit():
                try:
                    step_num = int(parts[0])
                    val = float(parts[1])
                    from_val = float(parts[2])
                    to_val = float(parts[3])
                    
                    result[current_meas]["step"].append(step_num)
                    result[current_meas]["value"].append(val)
                    result[current_meas]["from"].append(from_val)
                    result[current_meas]["to"].append(to_val)
                except ValueError:
                    continue

    return result

@app.get(f"{api['prefix']}{api['measure_endpoint']}")
async def measure_circuit():
    if not os.path.exists(CIRCUIT_FILE_PATH):
        raise HTTPException(status_code=404, detail="File not found on server")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_asc_path = os.path.join(temp_dir, "circuit.asc")
        shutil.copyfile(CIRCUIT_FILE_PATH, temp_asc_path)

        net_path = os.path.join(temp_dir, "circuit.net")
        log_path = os.path.join(temp_dir, "circuit.log")

        proc_net = await asyncio.create_subprocess_exec(
            "xvfb-run", "-a", "wine", LTSPICE_EXE, "-netlist", "circuit.asc",
            cwd=temp_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr_net = await proc_net.communicate()

        if not os.path.exists(net_path):
            detail_msg = stderr_net.decode(errors="replace").strip() or "Failed to convert .asc to .net file"
            raise HTTPException(status_code=500, detail=detail_msg)

        proc_sim = await asyncio.create_subprocess_exec(
            "xvfb-run", "-a", "wine", LTSPICE_EXE, "-b", "circuit.net",
            cwd=temp_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr_sim = await proc_sim.communicate()

        if not os.path.exists(log_path):
            detail_msg = stderr_sim.decode(errors="replace").strip() or "Simulation completed but log file was not generated"
            raise HTTPException(status_code=500, detail=detail_msg)

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as log_file:
                log_content = log_file.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")

        parsed_data = parse_ltspice_log(log_content)
        return parsed_data

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=api['port'])