import logging

import uvicorn

from controller import app

if __name__ == "__main__":
    logging.debug("Connect to http://localhost:3000/docs for docs")
    uvicorn.run(app, host="localhost", port=3000, log_level=logging.DEBUG)
