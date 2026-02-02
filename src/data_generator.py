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
    """Generate a single fake e-commerce event with enhanced fields."""
    event_types = ['view', 'click', 'purchase', 'add_to_cart']
    
    # Product categories for e-commerce
    product_categories = [
        'Electronics', 'Clothing', 'Home & Garden', 'Books',
        'Sports & Outdoors', 'Toys & Games', 'Beauty & Personal Care', 'Food & Beverages'
    ]
    
    event_type = random.choice(event_types)
    
    # Generate realistic quantity based on event type
    if event_type in ['purchase', 'add_to_cart']:
        quantity = random.randint(1, 10)
    else:
        quantity = 1  # For view/click, quantity is always 1
    
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": fake.uuid4(),
        "product_id": fake.uuid4(),
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "device": random.choice(['mobile', 'desktop', 'tablet']),
            "browser": random.choice(['chrome', 'firefox', 'safari']),
            "location": fake.country_code()
        },
        # New fields for enhanced analytics
        "price": round(random.uniform(9.99, 999.99), 2),
        "quantity": quantity,
        "discount_applied": random.choice([True, False, False]),  # 33% chance of discount
        "product_category": random.choice(product_categories),
        "session_id": fake.uuid4()  # Each event gets a session_id
    }
    return event

def save_batch_to_file(events):
    """Save a list of events to a single JSON file (NDJSON format)."""
    # Ensure input directory exists
    os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
    
    batch_id = str(uuid.uuid4())
    filename = f"batch_{batch_id}.jsonl"
    filepath = os.path.join(settings.INPUT_DATA_DIR, filename)
    
    with open(filepath, 'w') as f:
        for event in events:
            json.dump(event, f)
            f.write('\n')
    
    print(f"Generated batch: {filename} ({len(events)} events)")

def main():
    print(f"Starting data generator. Writing to {settings.INPUT_DATA_DIR}")
    
    # Ensure input directory exists
    os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
    
    print(f"Rate: One batch every {1.0/settings.EVENTS_PER_SECOND:.2f} seconds.")
    print("Batch size: Random (1-5 events).")
    print("Press Ctrl+C to stop.")
    
    delay = 1.0 / settings.EVENTS_PER_SECOND
    
    try:
        while True:
            # Generate random batch size between 1 and 5
            batch_size = random.randint(1, 100)
            batch = [generate_event() for _ in range(batch_size)]
            
            save_batch_to_file(batch)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopping data generator.")

if __name__ == "__main__":
    main()
