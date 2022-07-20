from fastapi import FastAPI

from routers import mattermost, line


app = FastAPI()
app.include_router(mattermost.router)
app.include_router(line.router)
