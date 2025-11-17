import subprocess
import json
from pathlib import Path


def _build_image(image: str = "apex-scraper:latest") -> dict:
    """
    Builds the scraper Docker image using the repo layout:
    - Context: apex/
    - Dockerfile: apex/DockerFiles/Dockerfile.scraper
    """
    apex_dir = Path(__file__).resolve().parent.parent
    dockerfile = apex_dir / "DockerFiles" / "Dockerfile.scraper"
    cmd = [
        "docker", "build",
        "-t", image,
        "-f", str(dockerfile),
        ".",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(apex_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return {"status": "error", "error": proc.stderr or proc.stdout}
    return {"status": "success"}

def run_scraper_in_container(url: str, timeout: int = 10, image: str = "apex-scraper:latest") -> dict:
    """
    Builds (if needed) and runs the scraper Docker container with --rm, passing URL and timeout as args.
    Returns a JSON dict from container stdout.
    """
    build = _build_image(image=image)
    if build.get("status") != "success":
        return build

    cmd = [
        "docker", "run", "--rm",
        image,
        url,
        str(timeout)
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return {
            "status": "error",
            "error": result.stderr or result.stdout
        }
    try:
        return json.loads(result.stdout)
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to decode JSON: {e}\nRaw: {result.stdout}"
        }
