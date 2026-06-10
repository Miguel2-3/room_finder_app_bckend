# Room Finder Backend

A FastAPI-based REST API for managing boarding house listings, inquiries, and reviews.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (Hosted on Neon)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** Supabase Auth Integration

## Local Setup
1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Migrations:**
   ```bash
   alembic upgrade head
   ```
4. **Run Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Deployment (Render)
1. Push this repository to GitHub.
2. Create a "Web Service" on Render.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - `DATABASE_URL`: Your Neon PostgreSQL connection string.
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_ANON_KEY`: Your Supabase Anon Key.

## API Documentation
Once running, access the interactive docs at `/docs`.