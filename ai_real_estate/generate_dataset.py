"""
AI Real Estate Dataset Generator
Generates realistic Indian real estate data with 100+ properties per city
across all Indian states. Mimics Kaggle-style dataset structure.
"""

import random
import csv
import os
import json

# All Indian States and Union Territories with major cities
INDIAN_STATES_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kakinada"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat", "Tawang", "Ziro"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Karnal"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan", "Mandi"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubli", "Belgaum"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Manipur": ["Imphal", "Thoubal", "Bishnupur", "Churachandpur", "Kakching"],
    "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongstoin", "Williamnagar"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Kolasib"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Sikkim": ["Gangtok", "Namchi", "Gyalshing", "Mangan", "Rangpo"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailashahar", "Ambassa"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Varanasi", "Agra", "Kanpur"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Nainital", "Mussoorie"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket", "Connaught Place"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Udhampur"],
    "Ladakh": ["Leh", "Kargil", "Diskit", "Padum", "Nyoma"],
    "Puducherry": ["Puducherry", "Karaikal", "Mahe", "Yanam", "Ozhukarai"],
    "Chandigarh": ["Chandigarh Sector 17", "Chandigarh Sector 22", "Chandigarh Sector 35", "Manimajra", "Panchkula"],
    "Andaman and Nicobar Islands": ["Port Blair", "Havelock Island", "Neil Island", "Diglipur", "Rangat"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Silvassa", "Daman", "Diu", "Amli", "Khanvel"],
    "Lakshadweep": ["Kavaratti", "Agatti", "Minicoy", "Amini", "Andrott"],
}

# Property types
PROPERTY_TYPES = [
    "Apartment", "Villa", "Independent House", "Penthouse",
    "Studio Apartment", "Duplex", "Row House", "Farmhouse",
    "Builder Floor", "Plot"
]

# Amenities list
AMENITIES = [
    "Lift", "Car Parking", "Swimming Pool", "Gym", "Power Backup",
    "Security Guard", "CCTV", "Children Play Area", "Garden",
    "Club House", "Jogging Track", "Indoor Games", "Intercom",
    "Fire Safety", "Rain Water Harvesting", "Waste Management",
    "Visitor Parking", "Servant Room", "Vastu Compliant",
    "Gas Pipeline", "Wi-Fi", "Solar Panel", "EV Charging",
    "Pet Friendly", "Modular Kitchen", "Air Conditioning",
    "Water Purifier", "Balcony", "Terrace", "Store Room"
]

# Localities/Areas common suffixes
LOCALITY_PREFIXES = [
    "Green", "Royal", "Sun", "Lake", "Hill", "Garden", "Park",
    "City", "Golden", "Silver", "Diamond", "Palm", "Rose",
    "Lotus", "Orchid", "Maple", "Cedar", "Heritage", "Pride",
    "Elite", "Premium", "Grand", "Classic", "Modern", "Smart"
]

LOCALITY_SUFFIXES = [
    "Residency", "Heights", "Towers", "Enclave", "Colony",
    "Apartments", "Villas", "Gardens", "Park", "City",
    "Township", "Meadows", "Valley", "Springs", "Nest",
    "Haven", "Square", "Plaza", "Court", "Estate"
]

# Builder names
BUILDERS = [
    "DLF Homes", "Godrej Properties", "Prestige Group", "Sobha Limited",
    "Lodha Group", "Tata Housing", "Mahindra Lifespaces", "Brigade Group",
    "Puravankara", "Oberoi Realty", "Hiranandani", "Shapoorji Pallonji",
    "L&T Realty", "Raheja Developers", "Unitech", "Jaypee Group",
    "Supertech", "ATS Infrastructure", "Emaar India", "Kalpataru",
    "Nirala Group", "Gaurs Group", "Mahagun", "Ajnara India",
    "Omaxe", "Ansal API", "Parsvnath Developers", "Vatika Group",
    "M3M India", "Adani Realty"
]

# Facing directions
FACING = ["North", "South", "East", "West", "North-East", "North-West", "South-East", "South-West"]

# Furnishing status
FURNISHING = ["Fully Furnished", "Semi Furnished", "Unfurnished"]

# Transaction type
TRANSACTION_TYPE = ["New Property", "Resale"]

# Possession status
POSSESSION = ["Ready to Move", "Under Construction", "Upcoming"]

# Price ranges per city tier (in lakhs)
TIER_1_CITIES = ["Mumbai", "New Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Gurugram", "Noida"]
TIER_2_CITIES = ["Jaipur", "Lucknow", "Chandigarh", "Kochi", "Indore", "Coimbatore", "Visakhapatnam", "Mysuru", "Nagpur", "Vadodara"]


def get_price_range(city, property_type):
    """Get realistic price range based on city tier and property type"""
    if city in TIER_1_CITIES:
        base_min, base_max = 40, 500
    elif city in TIER_2_CITIES:
        base_min, base_max = 20, 200
    else:
        base_min, base_max = 10, 100

    multipliers = {
        "Apartment": (1.0, 1.2),
        "Villa": (2.5, 4.0),
        "Independent House": (1.5, 3.0),
        "Penthouse": (3.0, 5.0),
        "Studio Apartment": (0.5, 0.8),
        "Duplex": (2.0, 3.5),
        "Row House": (1.8, 2.8),
        "Farmhouse": (3.0, 6.0),
        "Builder Floor": (1.2, 2.0),
        "Plot": (0.8, 2.5),
    }

    mult_min, mult_max = multipliers.get(property_type, (1.0, 1.5))
    price_min = int(base_min * mult_min)
    price_max = int(base_max * mult_max)
    return price_min, price_max


def get_area_range(property_type):
    """Get realistic area range based on property type (in sq ft)"""
    area_ranges = {
        "Apartment": (600, 2500),
        "Villa": (2000, 8000),
        "Independent House": (1000, 5000),
        "Penthouse": (2500, 6000),
        "Studio Apartment": (300, 600),
        "Duplex": (1500, 4000),
        "Row House": (1200, 3500),
        "Farmhouse": (5000, 20000),
        "Builder Floor": (800, 3000),
        "Plot": (1000, 10000),
    }
    return area_ranges.get(property_type, (500, 3000))


def generate_property(property_id, state, city):
    """Generate a single property record"""
    property_type = random.choice(PROPERTY_TYPES)
    price_min, price_max = get_price_range(city, property_type)
    area_min, area_max = get_area_range(property_type)

    price = round(random.uniform(price_min, price_max), 2)
    area = random.randint(area_min, area_max)
    price_per_sqft = round((price * 100000) / area, 2)

    # BHK based on property type
    if property_type == "Studio Apartment":
        bhk = 1
    elif property_type == "Plot":
        bhk = 0
    elif property_type in ["Villa", "Farmhouse", "Penthouse"]:
        bhk = random.choice([3, 4, 5, 6])
    else:
        bhk = random.choice([1, 2, 3, 4])

    # Bathrooms
    bathrooms = max(1, bhk - random.choice([0, 1]))

    # Floor
    if property_type in ["Villa", "Independent House", "Row House", "Farmhouse", "Plot"]:
        floor = random.randint(0, 3)
        total_floors = floor + random.randint(0, 1)
    else:
        total_floors = random.randint(5, 40)
        floor = random.randint(1, total_floors)

    # Age of property
    age = random.choice([0, 1, 2, 3, 5, 7, 10, 15, 20])

    # Generate amenities (random subset)
    num_amenities = random.randint(3, 15)
    selected_amenities = random.sample(AMENITIES, num_amenities)

    # Generate property name
    prefix = random.choice(LOCALITY_PREFIXES)
    suffix = random.choice(LOCALITY_SUFFIXES)
    property_name = f"{prefix} {suffix}"

    # Generate description
    builder = random.choice(BUILDERS)

    property_data = {
        "property_id": property_id,
        "property_name": property_name,
        "property_type": property_type,
        "state": state,
        "city": city,
        "locality": f"{random.choice(LOCALITY_PREFIXES)} Nagar",
        "price_lakhs": price,
        "price_per_sqft": price_per_sqft,
        "area_sqft": area,
        "bhk": bhk,
        "bathrooms": bathrooms,
        "floor": floor,
        "total_floors": total_floors,
        "age_years": age,
        "facing": random.choice(FACING),
        "furnishing": random.choice(FURNISHING),
        "transaction_type": random.choice(TRANSACTION_TYPE),
        "possession": random.choice(POSSESSION),
        "builder": builder,
        "amenities": "|".join(selected_amenities),
        "lift": "Yes" if "Lift" in selected_amenities else "No",
        "car_parking": "Yes" if "Car Parking" in selected_amenities else "No",
        "swimming_pool": "Yes" if "Swimming Pool" in selected_amenities else "No",
        "gym": "Yes" if "Gym" in selected_amenities else "No",
        "power_backup": "Yes" if "Power Backup" in selected_amenities else "No",
        "security": "Yes" if "Security Guard" in selected_amenities else "No",
        "garden": "Yes" if "Garden" in selected_amenities else "No",
        "club_house": "Yes" if "Club House" in selected_amenities else "No",
        "pet_friendly": "Yes" if "Pet Friendly" in selected_amenities else "No",
        "vastu_compliant": "Yes" if "Vastu Compliant" in selected_amenities else "No",
        "rating": round(random.uniform(3.0, 5.0), 1),
        "reviews_count": random.randint(5, 500),
        "latitude": round(random.uniform(8.0, 37.0), 6),
        "longitude": round(random.uniform(68.0, 97.0), 6),
    }

    return property_data


def generate_dataset():
    """Generate the complete dataset"""
    print("=" * 60)
    print("   AI Real Estate India - Dataset Generator")
    print("=" * 60)

    all_properties = []
    property_id = 1

    total_states = len(INDIAN_STATES_CITIES)
    state_count = 0

    for state, cities in INDIAN_STATES_CITIES.items():
        state_count += 1
        print(f"\n[{state_count}/{total_states}] Generating properties for {state}...")

        for city in cities:
            # Generate 100-120 properties per city
            num_properties = random.randint(100, 120)
            print(f"  -> {city}: {num_properties} properties")

            for _ in range(num_properties):
                prop = generate_property(property_id, state, city)
                all_properties.append(prop)
                property_id += 1

    # Save as CSV
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "indian_real_estate_dataset.csv")
    if all_properties:
        fieldnames = all_properties[0].keys()
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_properties)

    # Save states and cities as JSON for the app
    states_json_path = os.path.join(data_dir, "indian_states_cities.json")
    with open(states_json_path, "w", encoding="utf-8") as f:
        json.dump(INDIAN_STATES_CITIES, f, indent=2, ensure_ascii=False)

    # Save amenities list
    amenities_json_path = os.path.join(data_dir, "amenities.json")
    with open(amenities_json_path, "w", encoding="utf-8") as f:
        json.dump(AMENITIES, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"   Dataset Generation Complete!")
    print(f"{'=' * 60}")
    print(f"   Total Properties: {len(all_properties)}")
    print(f"   Total States/UTs: {total_states}")
    print(f"   Total Cities: {sum(len(c) for c in INDIAN_STATES_CITIES.values())}")
    print(f"   CSV saved to: {csv_path}")
    print(f"   States JSON saved to: {states_json_path}")
    print(f"   Amenities JSON saved to: {amenities_json_path}")
    print(f"{'=' * 60}")

    return all_properties


if __name__ == "__main__":
    generate_dataset()
