from fastapi import FastAPI
import common.config as config
import uvicorn
import subprocess
from pathlib import Path

app = FastAPI()
cfg = config.load('config.yml')
api = cfg['api']

@app.get(f"{api['prefix']}{api['probs_endpoint']}")
def get_probabilities():
    subprocess.run(["bash", "/app/.devcontainer/mark/exe/run.sh"], check=True)
    
    def extract_numbers(filepath):
        nums = []
        path = Path(filepath)
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line:
                    try:
                        nums.append(float(line) if '.' in line else int(line))
                    except ValueError:
                        pass
        return nums

    run1_array = extract_numbers("/exe/run1_extracted.txt")
    run2_array = extract_numbers("/exe/run2_extracted.txt")

    print(run1_array)
    print(run2_array)

    probs_info = [
        run1_array,
        run2_array,
    ]
    
    return probs_info

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=api['port'])