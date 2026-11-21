# Grand Demo Hotel

A hotel booking website built with Python and Flask, using a Turso (SQLite-compatible) database and deployed on Vercel.

**Live demo:** https://grand-demo-hotel.vercel.app

## Features
- Sign up, login and logout (passwords are hashed)
- Rooms and facilities pages
- Booking flow
- Demo payment step (no real payment is taken)

## Tech stack
Python, Flask, SQL (Turso), HTML, CSS, Vercel

## Run it on your computer
1. `pip install -r requirements.txt`
2. Create a `.env` file with `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN` and `FLASK_SECRET_KEY` (this file is not in the repository)
3. `python app.py`

## Notes
This is a learning project. The hotel is fictional, and no real payment or personal data is used.
