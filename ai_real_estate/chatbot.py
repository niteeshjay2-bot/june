"""
AI Real Estate Chatbot
Rule-based NLP chatbot for real estate queries.
Handles property searches, price inquiries, amenity questions,
city recommendations, and general real estate advice.
"""

import re
import json
import os
import random


class ChatBot:
    """AI-powered real estate chatbot using rule-based NLP"""

    def __init__(self):
        self.context = {}
        self._load_data()
        self._build_patterns()

    def _load_data(self):
        """Load reference data"""
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

        states_path = os.path.join(data_dir, 'indian_states_cities.json')
        with open(states_path, 'r', encoding='utf-8') as f:
            self.states_cities = json.load(f)

        amenities_path = os.path.join(data_dir, 'amenities.json')
        with open(amenities_path, 'r', encoding='utf-8') as f:
            self.amenities = json.load(f)

        self.all_cities = []
        for cities in self.states_cities.values():
            self.all_cities.extend(cities)

        self.all_states = list(self.states_cities.keys())


    def _build_patterns(self):
        """Build regex patterns for intent recognition"""
        self.intents = {
            'greeting': {
                'patterns': [
                    r'\b(hi|hello|hey|good morning|good evening|namaste|howdy)\b',
                    r'^(hi|hello|hey)$',
                ],
                'responses': [
                    "Hello! Welcome to PropAI India. I'm your AI real estate assistant. How can I help you find your dream property today?",
                    "Namaste! I'm here to help you with your property search across India. What are you looking for?",
                    "Hi there! Ready to find your perfect home? Tell me about your preferences - city, budget, or property type!",
                    "Hello! I can help you search properties, compare prices, check amenities, and more. What would you like to know?",
                ]
            },
            'farewell': {
                'patterns': [
                    r'\b(bye|goodbye|see you|thanks bye|quit|exit)\b',
                ],
                'responses': [
                    "Thank you for using PropAI India! Good luck with your property search. Feel free to come back anytime!",
                    "Goodbye! I hope I was helpful. May you find your dream home soon!",
                    "See you later! Remember, I'm always here to help with your real estate queries.",
                ]
            },
            'thanks': {
                'patterns': [
                    r'\b(thank|thanks|thank you|thx|appreciate)\b',
                ],
                'responses': [
                    "You're welcome! Is there anything else I can help you with regarding properties?",
                    "Happy to help! Let me know if you have any more questions about real estate.",
                    "My pleasure! Feel free to ask about any property, city, or amenity.",
                ]
            },

            'price_query': {
                'patterns': [
                    r'\b(price|cost|budget|rate|expensive|cheap|affordable)\b',
                    r'\b(how much|what.*(price|cost))\b',
                    r'\b(\d+)\s*(lakh|lac|cr|crore)\b',
                ],
                'responses': []  # Dynamic responses
            },
            'property_type': {
                'patterns': [
                    r'\b(apartment|flat|villa|house|penthouse|duplex|studio|farmhouse|plot|row house|builder floor)\b',
                ],
                'responses': []  # Dynamic
            },
            'city_query': {
                'patterns': [
                    r'\b(which city|best city|recommend.*city|city.*recommend|where.*buy|where.*invest)\b',
                ],
                'responses': [
                    "For investment, I'd recommend:\n- **Bengaluru** - IT hub with great appreciation\n- **Hyderabad** - Fastest growing market\n- **Pune** - Affordable with good returns\n- **Gurugram** - Premium properties near Delhi\n- **Ahmedabad** - Emerging market with GIFT City\n\nWould you like details about any specific city?",
                ]
            },
            'amenity_query': {
                'patterns': [
                    r'\b(amenit|facility|facilities|feature|lift|elevator|parking|pool|swimming|gym|garden|security|power backup|club house|pet)\b',
                ],
                'responses': []  # Dynamic
            },

            'bhk_query': {
                'patterns': [
                    r'\b([1-6])\s*bhk\b',
                    r'\b(one|two|three|four|five)\s*bhk\b',
                    r'\bbhk\b',
                ],
                'responses': []  # Dynamic
            },
            'location_query': {
                'patterns': [],  # Built dynamically from cities/states
                'responses': []  # Dynamic
            },
            'investment_advice': {
                'patterns': [
                    r'\b(invest|investment|roi|return|appreciation|profit|growth)\b',
                ],
                'responses': [
                    "Here are my top real estate investment tips for India:\n\n"
                    "1. **Location**: Choose areas with upcoming metro/infrastructure projects\n"
                    "2. **RERA Registered**: Always verify RERA registration\n"
                    "3. **Builder Reputation**: Research the builder's track record\n"
                    "4. **Rental Yield**: Look for 3-5% annual rental yield\n"
                    "5. **Future Development**: Check nearby upcoming developments\n\n"
                    "Top cities for investment: Bengaluru, Hyderabad, Pune, Gurugram\n\n"
                    "Would you like me to search properties in any of these cities?",
                ]
            },
            'loan_query': {
                'patterns': [
                    r'\b(loan|emi|home loan|mortgage|interest rate|bank|finance|down payment)\b',
                ],
                'responses': [
                    "Here's a quick guide on home loans in India:\n\n"
                    "**Current Interest Rates (approx.):**\n"
                    "- SBI: 8.40% - 9.65%\n"
                    "- HDFC: 8.45% - 9.60%\n"
                    "- ICICI: 8.45% - 9.50%\n"
                    "- Axis Bank: 8.50% - 9.65%\n\n"
                    "**EMI Calculator tip:**\n"
                    "For Rs. 50 Lakh loan at 8.5% for 20 years = ~Rs. 43,391/month\n\n"
                    "**Documents needed:**\n"
                    "- PAN Card, Aadhaar\n"
                    "- Income proof (salary slips / ITR)\n"
                    "- Property documents\n"
                    "- Bank statements (6 months)\n\n"
                    "Would you like help finding properties within a specific budget?",
                ]
            },

            'vastu_query': {
                'patterns': [
                    r'\b(vastu|vaastu|feng shui|direction|facing|north|south|east|west)\b',
                ],
                'responses': [
                    "Vastu Shastra tips for property buying:\n\n"
                    "**Best Facing Directions:**\n"
                    "- **North-East**: Most auspicious for main entrance\n"
                    "- **East**: Brings prosperity and positivity\n"
                    "- **North**: Good for career growth\n\n"
                    "**Tips:**\n"
                    "- Master bedroom in South-West\n"
                    "- Kitchen in South-East\n"
                    "- Living room in North-East\n"
                    "- Avoid properties on T-junctions\n\n"
                    "I can filter Vastu-compliant properties for you. Which city are you interested in?",
                ]
            },
            'comparison': {
                'patterns': [
                    r'\b(compare|vs|versus|difference|better|which is better)\b',
                ],
                'responses': [
                    "I can help you compare! Here's what to consider:\n\n"
                    "**Apartment vs Villa:**\n"
                    "- Apartment: Lower cost, better security, amenities included\n"
                    "- Villa: More space, privacy, higher maintenance\n\n"
                    "**New vs Resale:**\n"
                    "- New: Modern amenities, warranty, higher price\n"
                    "- Resale: Negotiable price, ready to move, established locality\n\n"
                    "Tell me which specific properties or types you'd like to compare!",
                ]
            },
            'help': {
                'patterns': [
                    r'\b(help|what can you do|options|features|capabilities)\b',
                ],
                'responses': [
                    "I'm your AI Real Estate Assistant! Here's what I can help you with:\n\n"
                    "- **Search Properties**: By city, state, budget, BHK, type\n"
                    "- **Amenity Filter**: Lift, parking, pool, gym, garden, etc.\n"
                    "- **Price Guidance**: Budget ranges for different cities\n"
                    "- **Investment Advice**: Best cities and areas to invest\n"
                    "- **Loan Information**: EMI, interest rates, documents\n"
                    "- **Vastu Guidance**: Direction and layout tips\n"
                    "- **City Comparison**: Compare cities for buying\n"
                    "- **Property Types**: Explain apartment, villa, duplex, etc.\n\n"
                    "Just type your question naturally! For example:\n"
                    "- 'Show 3 BHK in Mumbai under 1 crore'\n"
                    "- 'Properties with swimming pool in Bengaluru'\n"
                    "- 'Best city for investment'",
                ]
            },
        }


    def _find_city_in_message(self, message):
        """Find any city name mentioned in the message"""
        message_lower = message.lower()
        for city in self.all_cities:
            if city.lower() in message_lower:
                return city
        return None

    def _find_state_in_message(self, message):
        """Find any state name mentioned in the message"""
        message_lower = message.lower()
        for state in self.all_states:
            if state.lower() in message_lower:
                return state
        return None

    def _extract_bhk(self, message):
        """Extract BHK number from message"""
        word_to_num = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
        match = re.search(r'(\d)\s*bhk', message.lower())
        if match:
            return int(match.group(1))
        for word, num in word_to_num.items():
            if re.search(rf'\b{word}\s*bhk', message.lower()):
                return num
        return None

    def _extract_budget(self, message):
        """Extract budget from message"""
        message_lower = message.lower()
        # Check for crore
        match = re.search(r'(\d+\.?\d*)\s*(cr|crore)', message_lower)
        if match:
            return float(match.group(1)) * 100  # Convert to lakhs

        # Check for lakhs
        match = re.search(r'(\d+\.?\d*)\s*(lakh|lac|l)\b', message_lower)
        if match:
            return float(match.group(1))

        return None


    def _extract_amenities(self, message):
        """Extract amenity requests from message"""
        message_lower = message.lower()
        found = []
        amenity_keywords = {
            'lift': 'Lift', 'elevator': 'Lift',
            'parking': 'Car Parking', 'car parking': 'Car Parking',
            'swimming': 'Swimming Pool', 'pool': 'Swimming Pool',
            'gym': 'Gym', 'fitness': 'Gym',
            'power backup': 'Power Backup', 'generator': 'Power Backup',
            'security': 'Security Guard', 'guard': 'Security Guard', 'cctv': 'CCTV',
            'garden': 'Garden', 'park': 'Garden',
            'club': 'Club House', 'clubhouse': 'Club House',
            'pet': 'Pet Friendly', 'dog': 'Pet Friendly',
            'vastu': 'Vastu Compliant',
            'play area': 'Children Play Area', 'children': 'Children Play Area',
            'jogging': 'Jogging Track',
            'solar': 'Solar Panel',
            'ev charging': 'EV Charging', 'electric vehicle': 'EV Charging',
            'modular kitchen': 'Modular Kitchen',
            'balcony': 'Balcony',
            'terrace': 'Terrace',
        }
        for keyword, amenity in amenity_keywords.items():
            if keyword in message_lower:
                found.append(amenity)
        return list(set(found))

    def _extract_property_type(self, message):
        """Extract property type from message"""
        message_lower = message.lower()
        types = {
            'apartment': 'Apartment', 'flat': 'Apartment',
            'villa': 'Villa', 'bungalow': 'Villa',
            'independent house': 'Independent House', 'house': 'Independent House',
            'penthouse': 'Penthouse',
            'studio': 'Studio Apartment',
            'duplex': 'Duplex',
            'row house': 'Row House', 'townhouse': 'Row House',
            'farmhouse': 'Farmhouse', 'farm house': 'Farmhouse',
            'builder floor': 'Builder Floor',
            'plot': 'Plot', 'land': 'Plot',
        }
        for keyword, ptype in types.items():
            if keyword in message_lower:
                return ptype
        return None


    def _search_properties(self, city=None, state=None, bhk=None, budget=None,
                           property_type=None, amenities=None, db_session=None):
        """Search properties based on extracted parameters"""
        if not db_session:
            return None

        from models import Property
        query = db_session.query(Property)

        if city:
            query = query.filter(Property.city == city)
        if state:
            query = query.filter(Property.state == state)
        if bhk:
            query = query.filter(Property.bhk == bhk)
        if budget:
            query = query.filter(Property.price_lakhs <= budget)
        if property_type:
            query = query.filter(Property.property_type == property_type)

        # Amenity filters
        if amenities:
            for amenity in amenities:
                if amenity == 'Lift':
                    query = query.filter(Property.lift == True)
                elif amenity == 'Car Parking':
                    query = query.filter(Property.car_parking == True)
                elif amenity == 'Swimming Pool':
                    query = query.filter(Property.swimming_pool == True)
                elif amenity == 'Gym':
                    query = query.filter(Property.gym == True)
                elif amenity == 'Power Backup':
                    query = query.filter(Property.power_backup == True)
                elif amenity == 'Security Guard':
                    query = query.filter(Property.security == True)
                elif amenity == 'Garden':
                    query = query.filter(Property.garden == True)
                elif amenity == 'Club House':
                    query = query.filter(Property.club_house == True)
                elif amenity == 'Pet Friendly':
                    query = query.filter(Property.pet_friendly == True)
                elif amenity == 'Vastu Compliant':
                    query = query.filter(Property.vastu_compliant == True)

        results = query.order_by(Property.rating.desc()).limit(5).all()
        return results


    def _format_property_results(self, properties):
        """Format property results for chat display"""
        if not properties:
            return "\n\nNo properties found matching your criteria. Try adjusting your filters!"

        response = f"\n\nI found **{len(properties)}** properties for you:\n\n"
        for i, prop in enumerate(properties, 1):
            price_str = f"{prop.price_lakhs/100:.2f} Cr" if prop.price_lakhs >= 100 else f"{prop.price_lakhs:.1f} L"
            response += (
                f"**{i}. {prop.property_name}** - {prop.city}, {prop.state}\n"
                f"   Type: {prop.property_type} | {prop.bhk} BHK | {prop.area_sqft} sq.ft\n"
                f"   Price: Rs. {price_str} | Furnished: {prop.furnishing}\n"
                f"   Rating: {'*' * int(prop.rating)} ({prop.rating}/5)\n\n"
            )

        response += "Use the **Search** page for more detailed filtering and results!"
        return response

    def get_response(self, message, db_session=None):
        """Get chatbot response for a user message"""
        message = message.strip()
        if not message:
            return "Please type a message! I'm here to help you find properties across India."

        message_lower = message.lower()

        # Check for greetings first
        for pattern in self.intents['greeting']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['greeting']['responses'])

        # Check farewell
        for pattern in self.intents['farewell']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['farewell']['responses'])

        # Check thanks
        for pattern in self.intents['thanks']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['thanks']['responses'])

        # Check help
        for pattern in self.intents['help']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['help']['responses'])


        # Extract search parameters
        city = self._find_city_in_message(message)
        state = self._find_state_in_message(message)
        bhk = self._extract_bhk(message)
        budget = self._extract_budget(message)
        property_type = self._extract_property_type(message)
        amenities = self._extract_amenities(message)

        # If we have search parameters, do a property search
        has_search_params = any([city, state, bhk, budget, property_type, amenities])

        if has_search_params and db_session:
            # Build response prefix
            response = "Let me search for properties"
            params = []
            if bhk:
                params.append(f"{bhk} BHK")
            if property_type:
                params.append(property_type)
            if city:
                params.append(f"in {city}")
            elif state:
                params.append(f"in {state}")
            if budget:
                budget_str = f"{budget/100:.1f} Cr" if budget >= 100 else f"{budget:.0f} Lakhs"
                params.append(f"under Rs. {budget_str}")
            if amenities:
                params.append(f"with {', '.join(amenities)}")

            if params:
                response += " - " + ", ".join(params)
            response += "..."

            # Search database
            results = self._search_properties(
                city=city, state=state, bhk=bhk,
                budget=budget, property_type=property_type,
                amenities=amenities, db_session=db_session
            )

            response += self._format_property_results(results)
            return response

        # Check other intents
        # Investment advice
        for pattern in self.intents['investment_advice']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['investment_advice']['responses'])

        # Loan query
        for pattern in self.intents['loan_query']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['loan_query']['responses'])

        # Vastu query
        for pattern in self.intents['vastu_query']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['vastu_query']['responses'])

        # City recommendation
        for pattern in self.intents['city_query']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['city_query']['responses'])

        # Comparison
        for pattern in self.intents['comparison']['patterns']:
            if re.search(pattern, message_lower):
                return random.choice(self.intents['comparison']['responses'])


        # Amenity-specific responses
        if amenities:
            amenity_info = {
                'Lift': "Lift/elevator is essential for high-rise apartments. Most properties above 4 floors have lifts. I can filter properties with lifts for you!",
                'Car Parking': "Car parking is a must in metro cities! Most new projects offer 1-2 dedicated parking spots. Want me to find properties with parking?",
                'Swimming Pool': "Swimming pool is a premium amenity, usually found in luxury apartments and gated communities. Shall I search for properties with pools?",
                'Gym': "A gym/fitness center is common in modern residential complexes. Great for health-conscious buyers!",
                'Garden': "Properties with gardens offer better air quality and green views. Very popular with families!",
                'Pet Friendly': "Not all societies allow pets. I can specifically filter pet-friendly properties for you!",
                'Club House': "Club houses offer social spaces, party halls, and recreation areas. Common in premium townships.",
            }
            for amenity in amenities:
                if amenity in amenity_info:
                    return amenity_info[amenity] + "\n\nTell me a city and I'll find properties with this amenity!"

        # Price-related questions
        for pattern in self.intents['price_query']['patterns']:
            if re.search(pattern, message_lower):
                return (
                    "Here's a general price guide for Indian cities:\n\n"
                    "**Metro Cities (per sq.ft approx.):**\n"
                    "- Mumbai: Rs. 15,000 - 50,000+\n"
                    "- Delhi/NCR: Rs. 8,000 - 25,000+\n"
                    "- Bengaluru: Rs. 6,000 - 18,000\n"
                    "- Hyderabad: Rs. 5,000 - 15,000\n"
                    "- Chennai: Rs. 5,000 - 14,000\n\n"
                    "**Tier 2 Cities (per sq.ft approx.):**\n"
                    "- Pune: Rs. 5,000 - 15,000\n"
                    "- Jaipur: Rs. 3,000 - 8,000\n"
                    "- Lucknow: Rs. 3,000 - 7,000\n"
                    "- Kochi: Rs. 4,000 - 10,000\n\n"
                    "Tell me your budget and preferred city for personalized results!"
                )

        # Property type info
        for pattern in self.intents['property_type']['patterns']:
            if re.search(pattern, message_lower):
                return (
                    "Here's a guide to property types in India:\n\n"
                    "- **Apartment/Flat**: Multi-story building, shared amenities\n"
                    "- **Villa**: Independent luxury home with garden\n"
                    "- **Independent House**: Standalone house, full ownership\n"
                    "- **Penthouse**: Top-floor luxury with terrace\n"
                    "- **Studio**: Single room with kitchenette (ideal for singles)\n"
                    "- **Duplex**: Two-floor apartment\n"
                    "- **Row House**: Attached houses in a row\n"
                    "- **Farmhouse**: Rural/semi-urban large property\n"
                    "- **Builder Floor**: Independent floor in a building\n"
                    "- **Plot**: Empty land for construction\n\n"
                    "Which type interests you? I can search specific properties!"
                )

        # Default response
        default_responses = [
            "I'd be happy to help! Try asking me about:\n"
            "- Properties in a specific city (e.g., '3 BHK in Pune')\n"
            "- Budget-based search (e.g., 'flats under 50 lakhs in Jaipur')\n"
            "- Amenities (e.g., 'properties with swimming pool in Bengaluru')\n"
            "- Investment advice, home loans, or Vastu tips\n\n"
            "What would you like to know?",

            "I'm not sure I understood that. Here are some things you can ask:\n"
            "- 'Show me villas in Goa'\n"
            "- 'Properties with lift and parking in Mumbai'\n"
            "- '2 BHK under 40 lakhs in Hyderabad'\n"
            "- 'Best areas to invest in India'\n\n"
            "How can I assist you?",

            "Could you please rephrase that? I can help you with:\n"
            "- Property search by location, type, budget\n"
            "- Amenity-specific searches (lift, parking, gym, etc.)\n"
            "- City recommendations for buying/investing\n"
            "- Home loan and EMI information\n\n"
            "Try something like: 'Find 3 BHK apartments in Chennai with parking'",
        ]
        return random.choice(default_responses)
