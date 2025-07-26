from app import create_app

app = create_app()

# Export the Flask app for Vercel
handler = app 