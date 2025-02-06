from setuptools import setup, find_packages

setup(
    name="chess-ai-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "gunicorn>=21.2.0",
        "flask-cors>=4.0.0",
        "openai>=1.0.0",
        "anthropic>=0.8.0",
        "google-generativeai>=0.3.0",
        "python-chess>=1.999",
        "python-dotenv>=1.0.0",
        "httpx>=0.26.0"
    ]
)
