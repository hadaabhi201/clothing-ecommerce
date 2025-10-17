import uvicorn
from inventory_service.main import app

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(
        "inventory_service.main:app", 
        host="0.0.0.0",
        port=8000, 
        reload=True,
    )