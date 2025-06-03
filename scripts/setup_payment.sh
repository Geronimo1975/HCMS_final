#!/bin/bash

# Install required packages
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your credentials."
fi

# Start Redis server if not running
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis server..."
    redis-server &
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A config worker -l info &

# Start Celery beat
echo "Starting Celery beat..."
celery -A config beat -l info &

echo "Setup complete! Please make sure to:"
echo "1. Update your .env file with your Stripe API keys"
echo "2. Configure your email settings in .env"
echo "3. Set up your Stripe webhook endpoint" 