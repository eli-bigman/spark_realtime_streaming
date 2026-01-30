import os
import sys
import time
import json
import uuid
import random
from datetime import datetime
from faker import Faker

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings

# Initialize Faker
fake = Faker()

def generate_event():
    """Generate a single fake e-commerce event."""
    event_types = ['view', 'click', 'purchase', 'add_to_cart']
    
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(event_types),
        "user_id": fake.uuid4(),
        "product_id": fake.uuid4(),
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "device": random.choice(['mobile', 'desktop', 'tablet']),
            "browser": random.choice(['chrome', 'firefox', 'safari']),
            "location": fake.country_code()
        }
    }
    return event

def save_event_to_file(event):
    """Save event to a JSON file in the input directory."""
    # Ensure input directory exists
    os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
    
    filename = f"event_{event['event_id']}.json"
    filepath = os.path.join(settings.INPUT_DATA_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(event, f)
    
    print(f"Generated event: {filename}")

def main():
    print(f"Starting data generator. Writing to {settings.INPUT_DATA_DIR}")
    
    # Ensure input directory exists
    os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
    
    print(f"Rate: {settings.EVENTS_PER_SECOND} events/second. Press Ctrl+C to stop.")
    
    delay = 1.0 / settings.EVENTS_PER_SECOND
    
    try:
        while True:
            event = generate_event()
            save_event_to_file(event)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopping data generator.")

if __name__ == "__main__":
    main()
