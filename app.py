from fastapi import FastAPI, HTTPException
from kernel_run import create_kernel
import os

app = FastAPI()

# Ensure Kaggle API credentials are set
os.environ['KAGGLE_CONFIG_DIR'] = '/root/.kaggle'

@app.post("/run_comfyui")
async def run_comfyui(notebook_url: str):
    try:
        kernel_url = create_kernel(notebook_url, public=True, no_browser=True)
        return {"kernel_url": kernel_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))