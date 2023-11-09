from fastapi import FastAPI
from routers.user import users_router
import uvicorn



app = FastAPI(debug=True)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, reload=True)
