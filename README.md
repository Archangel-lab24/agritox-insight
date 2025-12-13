
# AgriTox Insight (Railway-native)

## Deploy on Railway
1. Create new Railway project
2. Upload this repo or ZIP
3. Set Start Command:

uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1

4. Done.

The app sleeps automatically when idle.
