import os

import uvicorn

from app.main import app

if __name__ == "__main__":
    port = os.environ.get("PORT", 5050)
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=False, log_level="warning")
