import uvicorn

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(
        "cart_service.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )
