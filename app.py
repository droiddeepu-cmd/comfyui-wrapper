from fastapi import FastAPI, Request
import subprocess
import os
import json
import threading

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

# store last run logs
last_logs = {"stdout": "", "stderr": ""}

@app.get("/")
def health():
    return {"status": "ok", "message": "ComfyUI wrapper is running"}

@app.post("/run")
async def run_notebook(request: Request):
    global last_logs
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

    def worker():
        global last_logs
        try:
            cmd = [
                "kernel-run",
                notebook_url,
                "--no-browser"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            last_logs = {"stdout": result.stdout, "stderr": result.stderr}
        except Exception as e:
            last_logs = {"stdout": "", "stderr": str(e)}

    # run kernel in background thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return {
        "status": "started",
        "message": f"Notebook execution started for {notebook_url}"
    }

@app.get("/logs")
def get_logs():
    return last_logs

@app.get("/comfyui-url")
def get_comfyui_url():
    """Return stored ComfyUI public URL and IP if written by the notebook"""
    json_path = "/kaggle/working/comfyui_url.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            return {"status": "ok", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "pending", "message": "No ComfyUI URL found yet"}
