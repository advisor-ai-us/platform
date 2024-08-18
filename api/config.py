import os

SERVER_ENV = os.getenv('SERVER_ENV', 'development')

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the parent directory
parent_dir = os.path.dirname(current_dir)

if SERVER_ENV == 'development':
    DATABASE_PATH = os.path.join(parent_dir, 'data', 'dev')
else:
    DATABASE_PATH = os.path.join(parent_dir, 'data', 'prod')