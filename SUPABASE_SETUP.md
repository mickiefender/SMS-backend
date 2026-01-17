# Supabase Database Setup Guide

This Django school management system uses Supabase PostgreSQL as the database. Follow these steps to set up the connection.

## Step 1: Get Your Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Project Settings > Database**
4. You'll find:
   - **Host**: Your project URL (e.g., `xxxxx.supabase.co`)
   - **Database**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: Your database password

5. Copy the full connection URI from the "URI" section

## Step 2: Configure Environment Variables

### Option A: Using Individual Variables (Recommended for Development)

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
# Database Configuration
POSTGRES_HOST=your-project.supabase.co
POSTGRES_PORT=5432
POSTGRES_DATABASE=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-actual-password

# Django
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Option B: Using DATABASE_URL (Recommended for Production)

The connection URL format is:
```
postgresql://postgres:password@host:5432/database?sslmode=require
```

Add to `.env`:
```env
DATABASE_URL=postgresql://postgres:your-password@your-project.supabase.co:5432/postgres?sslmode=require
```

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `dj-database-url` which parses the DATABASE_URL.

## Step 4: Run Migrations

Create all tables in your Supabase database:

```bash
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

## Step 5: Create a Superuser (Super Admin)

```bash
python manage.py createsuperuser
```

This will prompt you to enter:
- Email
- Password
- Confirm Password

## Step 6: Run the Development Server

```bash
python manage.py runserver
```

Your Django API should now be running at `http://localhost:8000`

## Verification

1. Check if migrations ran successfully:
   ```bash
   python manage.py showmigrations
   ```

2. Test the API:
   ```bash
   curl http://localhost:8000/api/health/
   ```

3. Access Django Admin:
   - Go to `http://localhost:8000/admin/`
   - Log in with your superuser credentials

## Supabase Dashboard

View your tables in the Supabase Dashboard:
1. Go to **Project Settings > Database > Tables**
2. You should see tables like:
   - `users_user` - User accounts and authentication
   - `schools_school` - School information
   - `academics_*` - Academic structure tables
   - `attendance_*` - Attendance records
   - `assignments_*` - Assignment and submission data
   - `billing_*` - Billing and subscription data

## Troubleshooting

### Connection Refused Error
- Make sure `POSTGRES_HOST` includes the full URL with `.supabase.co` domain
- Check that your Supabase project is running
- Verify your password doesn't contain special characters (if so, URL-encode them)

### SSL/TLS Error
- The settings already have `sslmode=require` configured
- Make sure you're using the correct host URL from Supabase

### Table Already Exists Error
- This means migrations were already run
- You can reset with `python manage.py migrate --zero` (caution: deletes data)

### No Such Module Error
- Make sure you've installed all requirements: `pip install -r requirements.txt`
- Verify you're in the correct Python virtual environment

## Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full PostgreSQL connection string | `postgresql://postgres:pass@host:5432/postgres?sslmode=require` |
| `POSTGRES_HOST` | Supabase host | `xxxxx.supabase.co` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `your-password` |
| `POSTGRES_DATABASE` | Database name | `postgres` |
| `POSTGRES_PORT` | Database port | `5432` |
| `DEBUG` | Debug mode | `True` or `False` |
| `DJANGO_SECRET_KEY` | Django secret key | Any random string |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |

## Next Steps

Once your database is set up:
1. Build the React frontend
2. Configure CORS_ALLOWED_ORIGINS to match your frontend URL
3. Set up authentication in the React app
4. Connect the role-based dashboards to the API

For API documentation, visit `http://localhost:8000/api/schema/` (if DRF schema is enabled).
