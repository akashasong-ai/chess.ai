from app import create_app, db
from app.models import LLM, Game  # Import the models

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Optionally, add some initial LLMs
        initial_llms = [
            LLM(name='GPT-4', api_type='openai'),
            LLM(name='Gemini Pro', api_type='gemini'),
            LLM(name='Claude 3', api_type='claude')
        ]
        
        for llm in initial_llms:
            db.session.add(llm)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()
            
    app.run(debug=True) 