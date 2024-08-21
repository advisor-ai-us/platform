import os
from dotenv import load_dotenv

load_dotenv()

# Get OpenAI API key and model from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')
FREE_CHAT_COUNT = os.getenv('FREE_CHAT_COUNT')
TAVUS_API_KEY = os.getenv('TAVUS_API_KEY')
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

TAVUS_API_URL = "https://tavusapi.com/v2/videos"

SERVER_ENV = os.getenv('SERVER_ENV', 'development')

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the parent directory
parent_dir = os.path.dirname(current_dir)

if SERVER_ENV == 'development':
    DATABASE_PATH = os.path.join(parent_dir, 'data', 'dev')
else:
    DATABASE_PATH = os.path.join(parent_dir, 'data', 'prod')