import os
import subprocess
import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files first (if any, though not strictly needed for just index.html via templates)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Ensure the templates directory and index.html exist
if not os.path.isdir('templates'):
    logger.error("The 'templates' directory does not exist. Please create it.")
    # Potentially exit or raise a configuration error
if not os.path.exists('templates/index.html'):
    logger.error("templates/index.html not found!")
    # Potentially exit or raise a configuration error

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if not os.path.exists('templates/index.html'):
        raise HTTPException(status_code=500, detail="index.html not found in templates directory.")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=PlainTextResponse)
async def run_search(pattern: str = Form(...)):
    if not pattern:
        raise HTTPException(status_code=400, detail="No pattern provided.")

    try:
        all_files = []
        # Walk through current directory, excluding .git, venv-like dirs, and app-specific files
        excluded_dirs = ['.git', 'venv', 'env', '.venv', '.env', 'node_modules', '__pycache__']
        excluded_files = ['app.py', 'requirements.txt'] # Add other app-specific files if any

        for root, dirs, files in os.walk('.'):
            # Modify dirs in place to exclude specified directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file_name in files:
                # Skip files in the templates directory and other excluded files
                if root.startswith('./templates') or file_name in excluded_files:
                    continue
                if os.path.join(root, file_name) == './app.py': # ensure app.py is excluded
                    continue

                all_files.append(os.path.join(root, file_name))

        logger.info(f"Searching for pattern '{pattern}' in {len(all_files)} files.")
        # Filter out files that might have been caught by os.walk before dir exclusion took full effect for root
        all_files = [f for f in all_files if not any(excluded_dir in f for excluded_dir in excluded_dirs)]


        if not all_files:
            return "No files to search in the repository (after exclusions)."

        # Construct the grep command
        # -I: Process a binary file as if it did not contain matching data.
        # -H: Print the filename for each match. (Default for multiple files)
        # -n: Print line number with output lines.
        # -e PATTERN: Use PATTERN as a pattern. Useful if pattern starts with '-'.
        command = ['grep', '-I', '-H', '-n', '-e', pattern] + all_files

        # Using subprocess.run for simplicity
        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode == 0: # Match found
            return process.stdout
        elif process.returncode == 1: # No match found
            return "No results found."
        else: # Error
            logger.error(f"Grep stderr: {process.stderr}")
            # Sanitize stderr before returning to client, or return a generic error
            # For now, returning a generic error for security.
            raise HTTPException(status_code=500, detail=f"Error during search. Grep exited with code {process.returncode}.")

    except FileNotFoundError:
        logger.error("Grep command not found.")
        raise HTTPException(status_code=500, detail="Server error: Grep command not found. Ensure grep is installed and in PATH.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

if __name__ == '__main__':
    # This part is for local development. For deployment, use Uvicorn directly.
    # Example: uvicorn app:app --reload
    import uvicorn
    if not os.path.exists('templates/index.html'):
        print("CRITICAL ERROR: templates/index.html not found! The app cannot start correctly.")
        print("Please ensure the HTML file is in the 'templates' directory adjacent to app.py.")
    else:
        print("Starting FastAPI app with Uvicorn. Access at http://127.0.0.1:8000")
        print("To run for development: uvicorn app:app --reload --port 8000")
        uvicorn.run(app, host="127.0.0.1", port=8000)
