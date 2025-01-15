from fastapi import FastAPI 
from api.v1 import api_router
from fastapi.middleware.cors import CORSMiddleware

# Create a FastAPI application instance
app = FastAPI()

# Include the API routes from the v1 submodule
app.include_router(api_router)

# Define allowed origins for CORS
origins = ["*"]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Allow requests from any origin
    allow_credentials=True,        # Allow including cookies in requests
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers in requests
)

# Define a route for the root endpoint
@app.get("/")
def root():
    """
    Handler for the root endpoint.

    Returns:
        dict: A dictionary indicating the status of the service.
    """
    return {"status": "hello world "}  # Return a JSON response indicating status

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port=8000)