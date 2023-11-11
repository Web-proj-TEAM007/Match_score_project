from fastapi import FastAPI
from routers.user import users_router
from routers.tournaments import tournaments_router
from routers.matches import match_router
import uvicorn

app = FastAPI(debug=True)
app.include_router(users_router)
app.include_router(tournaments_router)
app.include_router(match_router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, reload=True)
