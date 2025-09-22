from fastapi import FastAPI, Request
import subprocess
import os
import json

# ✅ Ensure kaggle.json exists
os.makedirs("/root/.kaggle", exist_ok=True)
kaggle_json_path = "/root/.kaggle/kaggle.json"

if not os.path.exists(kaggle_json_path):
    creds = {
        "username": os.getenv("KAGGLE_USERNAME"),
        "key": os.getenv("KAGGLE_KEY")
    }
    with open(kaggle_json_path, "w") as f:
        json.dump(creds, f)

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "message": "ComfyUI wrapper is running"}

@app.post("/run")
async def run_notebook(request: Request):
    data = await request.json()
    notebook_url = data.get("notebook_url")
    confirm = data.get("confirm", False)

    if not notebook_url:
        return {"error": "Missing notebook_url"}

    # First return preview unless confirm = true
    if not confirm:
        return {
            "status": "preview",
            "message": "Preview only. To start the kernel, add \"confirm\": true",
            "notebook_url": notebook_url
        }

    try:
        # Run kernel-run with the notebook
        cmd = [
            "kernel-run",
            notebook_url,
            "--no-browser"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}
