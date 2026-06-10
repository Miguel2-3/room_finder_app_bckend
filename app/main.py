import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base, SessionLocal

from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.boarding_house_controller import router as bh_router
from app.models import user
from app.models import boarding_house
from app.models import report
from app.models import favorite
from app.models import boarding_house_image
from app.models import inquiry

from app.controllers.inquiry_controller import router as inquiry_router
from app.controllers.review_controller import router as review_router
from app.controllers.report_controller import router as report_router
from app.controllers.favorite_controller import router as favorite_router
from app.controllers.message_controller import router as message_router

from app.services.boarding_house_service import process_update_reminders

from fastapi.middleware.cors import CORSMiddleware

# --- SCHEDULER LOGIC ---
async def monthly_reminder_task():
    while True:
        # Use run_in_executor to avoid blocking the main event loop
        # with synchronous database operations
        loop = asyncio.get_event_loop()
        def run_sync_task():
            db = SessionLocal()
            try:
                # This function processes reminders for houses not updated in 30 days.
                # The task runs daily, but the service logic determines monthly relevance.
                process_update_reminders(db)
            finally:
                db.close()
        
        await loop.run_in_executor(None, run_sync_task)
        
        # The task is named 'monthly_reminder_task' but currently sleeps for 24 hours (daily execution).
        # If truly monthly, adjust sleep to 30 * 24 * 3600 seconds (approx. 2,592,000 seconds).
        # For daily checks that trigger monthly logic, 24 hours is appropriate.
        await asyncio.sleep(24 * 60 * 60) # Wait for 24 hours (86400 seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    task = asyncio.create_task(monthly_reminder_task())
    yield
    # Shutdown logic
    task.cancel()

app = FastAPI(title="Room Finder API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)


# REGISTER ROUTES

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(bh_router)
app.include_router(review_router)
app.include_router(inquiry_router)
app.include_router(report_router)
app.include_router(favorite_router)
app.include_router(message_router)


@app.get("/")
def root():
    return {"message": "Room Finder Backend is running. Have fun!"}