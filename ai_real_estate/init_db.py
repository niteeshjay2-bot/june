"""
Database Initialization Script
Loads the generated CSV dataset into SQLite database
"""

import csv
import os
import sys


def init_database(app):
    """Initialize database and load data from CSV"""
    from models import db, Property

    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if data already loaded
        if Property.query.first():
            print("[INFO] Database already contains data. Skipping import.")
            return

        # Load CSV data
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "indian_real_estate_dataset.csv")

        if not os.path.exists(csv_path):
            print("[ERROR] Dataset CSV not found. Run generate_dataset.py first!")
            sys.exit(1)

        print("[INFO] Loading dataset into database...")
        count = 0
        batch_size = 500
        batch = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                prop = Property(
                    property_id=int(row['property_id']),
                    property_name=row['property_name'],
                    property_type=row['property_type'],
                    state=row['state'],
                    city=row['city'],
                    locality=row['locality'],
                    price_lakhs=float(row['price_lakhs']),
                    price_per_sqft=float(row['price_per_sqft']),
                    area_sqft=int(row['area_sqft']),
                    bhk=int(row['bhk']),
                    bathrooms=int(row['bathrooms']),
                    floor=int(row['floor']),
                    total_floors=int(row['total_floors']),
                    age_years=int(row['age_years']),
                    facing=row['facing'],
                    furnishing=row['furnishing'],
                    transaction_type=row['transaction_type'],
                    possession=row['possession'],
                    builder=row['builder'],
                    amenities=row['amenities'],
                    lift=(row['lift'] == 'Yes'),
                    car_parking=(row['car_parking'] == 'Yes'),
                    swimming_pool=(row['swimming_pool'] == 'Yes'),
                    gym=(row['gym'] == 'Yes'),
                    power_backup=(row['power_backup'] == 'Yes'),
                    security=(row['security'] == 'Yes'),
                    garden=(row['garden'] == 'Yes'),
                    club_house=(row['club_house'] == 'Yes'),
                    pet_friendly=(row['pet_friendly'] == 'Yes'),
                    vastu_compliant=(row['vastu_compliant'] == 'Yes'),
                    rating=float(row['rating']),
                    reviews_count=int(row['reviews_count']),
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                )
                batch.append(prop)
                count += 1

                if len(batch) >= batch_size:
                    db.session.bulk_save_objects(batch)
                    db.session.commit()
                    batch = []
                    print(f"  -> Loaded {count} properties...")

            # Save remaining
            if batch:
                db.session.bulk_save_objects(batch)
                db.session.commit()

        print(f"[SUCCESS] Loaded {count} properties into database!")


if __name__ == "__main__":
    # For standalone execution
    from app import create_app
    app = create_app()
    init_database(app)
