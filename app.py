from fastapi import FastAPI, Request
import subprocess
import os

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "message": "ComfyUI wrapper is running"}

@app.post("/run")
async def run_notebook(request: Request):
    data = await request.json()
    notebook_url = data.get("notebook_url")
    if not notebook_url:
        return {"error": "Missing notebook_url"}

    try:
        # Run kernel-run
        cmd = [
            "kernel-run",
            notebook_url,
            "--no-browser",
            "--rm"  # optional: removes container after run
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}
