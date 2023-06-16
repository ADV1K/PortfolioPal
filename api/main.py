from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .database import Base, engine
from .routers import alphastreet

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI()

# Add the routers
app.include_router(alphastreet.router)

# Add pagination to the app. This must be done after all routes are defined.
add_pagination(app)


# Add a heartbeat route
@app.get("/")
def heartbeat():
    return {"status": "ok"}
