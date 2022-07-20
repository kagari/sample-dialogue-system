from fastapi import FastAPI

import mattermost
import line


app = FastAPI()
app.include_router(mattermost.router)
app.include_router(line.router)
