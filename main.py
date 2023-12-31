from fastapi import FastAPI
from routers.users import users_router
from routers.tournaments import tournaments_router
from routers.matches import match_router
from routers.admin import admin_router
from routers.players import players_router
from services.user_service import initiate_registration
import uvicorn

app = FastAPI(debug=True)
app.include_router(users_router)
app.include_router(tournaments_router)
app.include_router(match_router)
app.include_router(admin_router)
app.include_router(players_router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, reload=True)

initiate_registration()