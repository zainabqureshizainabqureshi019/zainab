
"""Main FastAPI application for Smart Inventory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import check_database
from backend.products import router as products_router
from backend.inventory import router as inventory_router
from backend.suppliers import router as suppliers_router
from backend.purchases import router as purchases_router
from backend.sales import router as sales_router
from backend.customers import router as customers_router
from backend.users import router as users_router
from backend.auth import router as auth_router


app = FastAPI(
    title="Smart Inventory & Sales Management System",
    description="Backend API for Smart Inventory",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(suppliers_router)
app.include_router(purchases_router)
app.include_router(sales_router)
app.include_router(customers_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Smart Inventory API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Backend is working"
    }


@app.get("/health/database")
def database_health():
    try:
        connected = check_database()

        if connected:
            return {
                "status": "connected",
                "message": "Neon PostgreSQL database connected successfully"
            }

        return {
            "status": "failed",
            "message": "Database connection failed"
        }

    except Exception:
        return {
            "status": "error",
            "message": "Unable to connect to database"
        }
