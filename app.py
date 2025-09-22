from fastapi import FastAPI, Request
import subprocess
import os
import json

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "message": "ComfyUI wrapper is running"}

@app.post("/validate")
async def validate_notebook(request: Request):
    """
    Safe endpoint: checks JSON only. Does NOT start Kaggle or use quota.
    """
    data = await request.json()
    notebook_url = data.get("notebook_url")
    if not notebook_url:
        return {"error": "Missing notebook_url"}
    return {
        "status": "ok",
        "notebook_url": notebook_url,
        "message": "Validated — no kernel started."
    }

@app.post("/run")
async def run_notebook(request: Request):
    """
    Actually starts the Kaggle notebook via kernel-run.
    Needs {"notebook_url": "...", "confirm": true}.
    """
    data = await request.json()
    notebook_url = data.get("notebook_url")
    confirm = bool(data.get("confirm", False))

    if not notebook_url:
        return {"error": "Missing notebook_url"}

    if not confirm:
        return {
            "status": "preview",
            "message": "Preview only. To start the kernel, add \"confirm\": true",
            "notebook_url": notebook_url
        }

    # Ensure kaggle.json from env vars
    kaggle_user = os.environ.get("KAGGLE_USERNAME")
    kaggle_key = os.environ.get("KAGGLE_KEY")
    if kaggle_user and kaggle_key:
        kaggle_dir = "/root/.kaggle"
        os.makedirs(kaggle_dir, exist_ok=True)
        cred_path = os.path.join(kaggle_dir, "kaggle.json")
        with open(cred_path, "w") as f:
            json.dump({"username": kaggle_user, "key": kaggle_key}, f)
        try:
            os.chmod(cred_path, 0o600)
        except Exception:
            pass

    try:
        cmd = ["kernel-run", notebook_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "kernel-run timed out (1h)"}
    except Exception as e:
        return {"error": str(e)}
