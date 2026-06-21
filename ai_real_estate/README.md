# PropAI India - AI-Powered Real Estate Platform

A beautiful, full-featured AI-powered real estate web application built entirely in **Python (Flask)**. Features an intelligent chatbot, user authentication, comprehensive Indian property listings across all 36 states/UTs, and advanced amenity-based filtering.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Features

### Core Features
- **AI Chatbot** - Rule-based NLP chatbot that understands property queries, budget, amenities, cities, and provides intelligent responses
- **User Authentication** - Complete login, register, logout with session management and password hashing
- **Advanced Search** - Filter by state, city, property type, BHK, budget, furnishing, possession status
- **Amenity Filters** - Filter properties by: Lift, Car Parking, Swimming Pool, Gym, Power Backup, Security, Garden, Club House, Pet Friendly, Vastu Compliant
- **All Indian States** - Coverage across all 36 states & union territories with 180+ cities
- **100+ Properties Per City** - Realistic dataset with ~19,891 property listings

### Additional Features
- Save favorite properties
- User profile management
- Property detail pages with similar property recommendations
- Contact inquiry system
- Responsive design (mobile-friendly)
- Floating chatbot widget on all pages
- Dynamic state-city dropdown (cascading)
- Pagination and sorting
- Search history tracking

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.8+, Flask |
| Database | SQLite + SQLAlchemy ORM |
| Auth | Flask-Login + Werkzeug |
| Frontend | Jinja2 Templates, CSS3 |
| Chatbot | Custom Python NLP (rule-based) |
| Dataset | Custom generator (Kaggle-style CSV) |
| Icons | Font Awesome 6 |
| Fonts | Google Fonts (Poppins) |

---

## Project Structure

```
ai_real_estate/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy database models
├── auth.py                 # Authentication blueprint
├── chatbot.py              # AI chatbot module
├── init_db.py              # Database initialization
├── generate_dataset.py     # Dataset generator script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── data/
│   ├── indian_real_estate_dataset.csv  # ~19,891 properties
│   ├── indian_states_cities.json       # States & cities mapping
│   ├── amenities.json                  # Amenities list
│   └── real_estate.db                  # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css       # Complete stylesheet
└── templates/
    ├── base.html           # Base template with nav & footer
    ├── home.html           # Homepage with hero & featured
    ├── search.html         # Advanced search with filters
    ├── property_detail.html # Property details page
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── chatbot.html        # Full-page chatbot
    ├── states.html         # All states listing
    ├── state_detail.html   # Cities in a state
    ├── profile.html        # User profile
    ├── favorites.html      # Saved properties
    ├── contact.html        # Contact form
    ├── about.html          # About page
    ├── 404.html            # Not found error
    └── 500.html            # Server error
```

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ai_real_estate
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or
venv\Scripts\activate           # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Dataset (Optional - already included)
```bash
python generate_dataset.py
```
This creates ~19,891 property listings across 180 cities in all Indian states.

### Step 5: Run the Application
```bash
python app.py
```

The application will:
1. Automatically create the SQLite database
2. Load all property data from CSV
3. Start the Flask server on `http://localhost:5000`

---

## Usage

### Homepage
- Browse featured properties
- Use the hero search to find properties by state, city, type, and budget

### Search
- Apply advanced filters including amenities (lift, parking, pool, etc.)
- Sort by price, area, rating, or newest
- Paginated results

### AI Chatbot
- Click the floating robot icon (bottom-right) on any page
- Or visit the full chatbot page via navigation
- Try queries like:
  - "Show me 3 BHK apartments in Mumbai"
  - "Properties with swimming pool in Bengaluru under 1 crore"
  - "Best city for investment"
  - "Tell me about home loans"
  - "Pet friendly properties in Pune"

### Authentication
- Register with email, username, and password
- Login to save favorites and track search history
- Manage profile and change password

---

## Dataset Details

The dataset mimics Kaggle-style real estate data with these columns:

| Field | Description |
|-------|-------------|
| property_id | Unique identifier |
| property_name | Name of the property/project |
| property_type | Apartment, Villa, Duplex, etc. |
| state | Indian state/UT |
| city | City name |
| price_lakhs | Price in Indian Lakhs |
| area_sqft | Area in square feet |
| bhk | Number of bedrooms |
| bathrooms | Number of bathrooms |
| amenities | Pipe-separated amenity list |
| lift, car_parking, etc. | Individual amenity flags |
| rating | Property rating (3.0-5.0) |
| builder | Builder/developer name |
| ... | And many more fields |

---

## Screenshots (Pages)

1. **Home** - Hero search, stats, featured properties, features section
2. **Search** - Advanced filters with amenity checkboxes, property grid
3. **Property Detail** - Full details, amenities list, similar properties
4. **AI Chat** - Full-page chatbot with suggestion chips
5. **States** - Browse all 36 states with property counts
6. **Login/Register** - Beautiful auth forms

---

## License

MIT License - Feel free to use this project for learning and development.

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Built with Python & Flask | No JavaScript frameworks used
