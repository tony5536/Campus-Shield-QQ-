"""
Top-level entry point for CampusShield AI backend.

This file exposes `app` so both `uvicorn app:app` and `python app.py` work.
It imports the FastAPI application implemented under Backend/app/main.py.
"""
import os
import sys

try:
    # Primary location used in this repository
    from Backend.app.main import app  # type: ignore
except Exception:
    try:
        # Fallback (some environments use lowercase folder)
        from backend.app.main import app  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Failed to import FastAPI app from Backend.app.main: %s" % exc
        )


if __name__ == "__main__":
    # Allow running with: python app.py
    import uvicorn

    # Read PORT from environment (used by hosting platforms). Be robust against
    # empty strings and non-integer values. Fall back to 8000 locally.
    port_env = os.environ.get("PORT")
    try:
        port = int(port_env) if port_env else 8000
    except (TypeError, ValueError):
        port = 8000

    # Use import-string when enabling reload so the reloader can import the
    # application module in the subprocess. This avoids the warning about
    # passing the app instance directly when using autoreload/workers.
    import_string = "app:app"
    print(f"Starting CampusShield AI on 0.0.0.0:{port} (reload=True) using {import_string}")
    uvicorn.run(import_string, host="0.0.0.0", port=port, reload=True)
