"""
INFY Nest AI - Intelligent Real Estate Chatbot
Advanced NLP-based chatbot with context memory, intent classification,
entity extraction, and human-like conversational abilities.
"""

import re
import json
import os
import random
from datetime import datetime


class ChatBot:
    """Advanced AI chatbot with context memory and smart NLP"""

    def __init__(self):
        self.conversations = {}  # user_id -> conversation context
        self._load_data()

    def _load_data(self):
        """Load reference data"""
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

        with open(os.path.join(data_dir, 'indian_states_cities.json'), 'r', encoding='utf-8') as f:
            self.states_cities = json.load(f)

        with open(os.path.join(data_dir, 'amenities.json'), 'r', encoding='utf-8') as f:
            self.amenities = json.load(f)

        self.all_cities = []
        for cities in self.states_cities.values():
            self.all_cities.extend(cities)
        self.all_states = list(self.states_cities.keys())

        # Build city-to-state mapping
        self.city_to_state = {}
        for state, cities in self.states_cities.items():
            for city in cities:
                self.city_to_state[city.lower()] = state

    def _get_context(self, user_id=None):
        """Get or create conversation context for a user"""
        uid = user_id or 'anonymous'
        if uid not in self.conversations:
            self.conversations[uid] = {
                'history': [],
                'preferences': {},
                'last_city': None,
                'last_state': None,
                'last_bhk': None,
                'last_budget': None,
                'last_type': None,
                'last_amenities': [],
                'turn_count': 0,
            }
        return self.conversations[uid]


    def _classify_intent(self, message):
        """Classify user intent using pattern matching and keyword analysis"""
        msg = message.lower().strip()

        # Greeting
        if re.search(r'^(hi|hello|hey|namaste|good\s*(morning|evening|afternoon)|howdy|sup|yo)\b', msg):
            return 'greeting'
        if re.search(r'^(hi|hello|hey)$', msg):
            return 'greeting'

        # Farewell
        if re.search(r'\b(bye|goodbye|see you|quit|exit|tata|later)\b', msg):
            return 'farewell'

        # Thanks
        if re.search(r'\b(thank|thanks|thx|appreciate|great|awesome|perfect)\b', msg):
            return 'thanks'

        # Help
        if re.search(r'\b(help|what can you|capabilities|features|options|menu)\b', msg):
            return 'help'

        # EMI/Loan calculation
        if re.search(r'\b(emi|loan|mortgage|interest|bank|finance|down\s*payment|home\s*loan)\b', msg):
            return 'loan_query'

        # Investment
        if re.search(r'\b(invest|investment|roi|return|appreciation|profit|growth|best.*buy)\b', msg):
            return 'investment'

        # Vastu
        if re.search(r'\b(vastu|vaastu|feng\s*shui|direction|north.*facing|east.*facing)\b', msg):
            return 'vastu'

        # Comparison
        if re.search(r'\b(compare|vs|versus|difference|better|which.*better|or)\b', msg):
            return 'comparison'

        # Price inquiry
        if re.search(r'\b(price|cost|rate|how\s*much|budget|affordable|cheap|expensive)\b', msg):
            return 'price_query'

        # Property type info
        if re.search(r'\b(what\s*is|tell.*about|explain|type|types|kind)\b.*\b(apartment|villa|house|penthouse|duplex|studio|plot|farmhouse)\b', msg):
            return 'property_info'

        # Amenity query
        if re.search(r'\b(amenity|amenities|facility|facilities|feature)\b', msg):
            return 'amenity_info'

        # Property search (catch-all for property-related queries)
        if any([
            re.search(r'\d\s*bhk', msg),
            re.search(r'\b(show|find|search|looking|want|need|get|list)\b', msg),
            re.search(r'\b(apartment|flat|villa|house|penthouse|duplex|studio|plot|farmhouse)\b', msg),
            re.search(r'\b(under|below|above|between|within|budget)\b.*\b(\d+)\b', msg),
            self._find_city(msg),
            self._find_state(msg),
            re.search(r'\b(lift|parking|pool|swimming|gym|garden|security|pet)\b', msg),
        ]):
            return 'property_search'

        # General conversation / unknown
        return 'general'


    def _find_city(self, message):
        """Find city in message"""
        msg = message.lower()
        for city in self.all_cities:
            if city.lower() in msg:
                return city
        return None

    def _find_state(self, message):
        """Find state in message"""
        msg = message.lower()
        for state in self.all_states:
            if state.lower() in msg:
                return state
        return None

    def _extract_bhk(self, message):
        """Extract BHK from message"""
        msg = message.lower()
        word_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
                    'single': 1, 'double': 2, 'triple': 3}
        match = re.search(r'(\d)\s*bhk', msg)
        if match:
            return int(match.group(1))
        for word, num in word_map.items():
            if re.search(rf'\b{word}\s*bhk', msg):
                return num
        return None

    def _extract_budget(self, message):
        """Extract budget from message"""
        msg = message.lower()
        # Crore
        match = re.search(r'(\d+\.?\d*)\s*(cr|crore|crores)', msg)
        if match:
            return float(match.group(1)) * 100
        # Lakhs
        match = re.search(r'(\d+\.?\d*)\s*(lakh|lakhs|lac|lacs|l)\b', msg)
        if match:
            return float(match.group(1))
        # Plain number with context (e.g. "under 50", "below 80")
        match = re.search(r'\b(under|below|within|upto|up\s*to|less\s*than|max)\s*(\d+)', msg)
        if match:
            val = float(match.group(2))
            if val > 500:
                return val / 100000  # Assume rupees, convert to lakhs
            return val
        return None

    def _extract_property_type(self, message):
        """Extract property type"""
        msg = message.lower()
        types = {
            'apartment': 'Apartment', 'flat': 'Apartment', 'flats': 'Apartment',
            'villa': 'Villa', 'villas': 'Villa', 'bungalow': 'Villa',
            'independent house': 'Independent House', 'house': 'Independent House',
            'penthouse': 'Penthouse',
            'studio': 'Studio Apartment', 'studio apartment': 'Studio Apartment',
            'duplex': 'Duplex',
            'row house': 'Row House', 'townhouse': 'Row House', 'row houses': 'Row House',
            'farmhouse': 'Farmhouse', 'farm house': 'Farmhouse',
            'builder floor': 'Builder Floor',
            'plot': 'Plot', 'land': 'Plot', 'plots': 'Plot',
        }
        for keyword, ptype in types.items():
            if keyword in msg:
                return ptype
        return None

    def _extract_amenities(self, message):
        """Extract amenities from message"""
        msg = message.lower()
        found = []
        keywords = {
            'lift': 'Lift', 'elevator': 'Lift',
            'parking': 'Car Parking', 'car parking': 'Car Parking',
            'swimming': 'Swimming Pool', 'pool': 'Swimming Pool',
            'gym': 'Gym', 'fitness': 'Gym', 'workout': 'Gym',
            'power backup': 'Power Backup', 'generator': 'Power Backup', 'backup': 'Power Backup',
            'security': 'Security Guard', 'guard': 'Security Guard', 'cctv': 'CCTV',
            'garden': 'Garden', 'park': 'Garden', 'green': 'Garden',
            'club': 'Club House', 'clubhouse': 'Club House',
            'pet': 'Pet Friendly', 'dog': 'Pet Friendly', 'pets': 'Pet Friendly',
            'vastu': 'Vastu Compliant',
            'play area': 'Children Play Area', 'children': 'Children Play Area', 'kids': 'Children Play Area',
            'jogging': 'Jogging Track', 'running': 'Jogging Track',
            'solar': 'Solar Panel',
            'ev charging': 'EV Charging', 'electric vehicle': 'EV Charging',
            'modular kitchen': 'Modular Kitchen',
            'balcony': 'Balcony',
            'terrace': 'Terrace',
        }
        for keyword, amenity in keywords.items():
            if keyword in msg:
                found.append(amenity)
        return list(set(found))


    def _search_properties(self, city=None, state=None, bhk=None, budget=None,
                           property_type=None, amenities=None, db_session=None):
        """Search properties from database"""
        if not db_session:
            return []

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

        return query.order_by(Property.rating.desc()).limit(5).all()

    def _format_results(self, properties, context):
        """Format property results in a natural, AI-like way"""
        if not properties:
            parts = []
            if context.get('last_city'):
                parts.append(f"in {context['last_city']}")
            if context.get('last_bhk'):
                parts.append(f"with {context['last_bhk']} BHK")
            if context.get('last_budget'):
                b = context['last_budget']
                parts.append(f"under {'%.1f Cr' % (b/100) if b >= 100 else '%.0f Lakhs' % b}")

            location = ' '.join(parts) if parts else 'matching your criteria'
            return (
                f"I couldn't find properties {location} right now. "
                f"This could mean the combination is too specific. "
                f"Would you like me to:\n"
                f"• Expand the budget range?\n"
                f"• Look in nearby cities?\n"
                f"• Remove some filters?\n\n"
                f"Just let me know how I can adjust the search for you!"
            )

        count = len(properties)
        response = f"Great news! I found **{count} properties** that match your preferences:\n\n"

        for i, prop in enumerate(properties, 1):
            price = f"{prop.price_lakhs/100:.2f} Cr" if prop.price_lakhs >= 100 else f"{prop.price_lakhs:.1f} Lakhs"
            amenity_highlights = []
            if prop.lift:
                amenity_highlights.append("Lift")
            if prop.car_parking:
                amenity_highlights.append("Parking")
            if prop.swimming_pool:
                amenity_highlights.append("Pool")
            if prop.gym:
                amenity_highlights.append("Gym")
            if prop.garden:
                amenity_highlights.append("Garden")

            amenity_str = " | " + ", ".join(amenity_highlights[:3]) if amenity_highlights else ""

            response += (
                f"**{i}. {prop.property_name}**\n"
                f"   {prop.property_type} • {prop.bhk} BHK • {prop.area_sqft} sq.ft\n"
                f"   {prop.city}, {prop.state}\n"
                f"   **Rs. {price}**{amenity_str}\n"
                f"   Rating: {'⭐' * min(int(prop.rating), 5)} ({prop.rating}/5)\n\n"
            )

        response += (
            "---\n"
            "Would you like me to:\n"
            "• Show more details about any of these?\n"
            "• Narrow down with more filters (amenities, furnishing)?\n"
            "• Search in a different budget range?\n\n"
            "Just ask! You can also visit the **Search** page for full filtering options."
        )
        return response


    def _handle_greeting(self, context):
        """Handle greeting with context awareness"""
        turn = context['turn_count']
        if turn == 0:
            responses = [
                "Hello! 👋 I'm your INFY Nest AI assistant. I can help you find the perfect property anywhere in India — across all 36 states and 180+ cities.\n\nTell me what you're looking for! For example:\n• \"3 BHK apartment in Mumbai under 1 crore\"\n• \"Villas with swimming pool in Goa\"\n• \"Best areas to invest in Bengaluru\"\n\nWhat's on your mind?",
                "Namaste! 🏠 Welcome to INFY Nest AI. I'm here to make your property search effortless.\n\nI understand natural language — just tell me what you need like you'd tell a friend:\n• Your preferred city or state\n• Budget range\n• Property type & size\n• Must-have amenities\n\nHow can I help you today?",
            ]
        else:
            city = context.get('last_city')
            responses = [
                f"Hey, welcome back! 👋 {'Still looking in ' + city + '?' if city else 'Ready to continue your property search?'} What can I help with?",
                f"Hi again! {'I remember you were interested in ' + city + '. ' if city else ''}What would you like to explore today?",
            ]
        return random.choice(responses)

    def _handle_farewell(self, context):
        """Handle farewell"""
        city = context.get('last_city', '')
        responses = [
            f"Goodbye! 👋 {'Best of luck finding your dream home in ' + city + '!' if city else 'Best of luck with your property search!'} Feel free to come back anytime.",
            "See you later! 🏠 Remember, I'm available 24/7 to help with your real estate queries. Happy house hunting!",
            "Take care! If you need help later — comparing properties, checking prices, or anything else — I'm just a message away. 😊",
        ]
        return random.choice(responses)

    def _handle_thanks(self, context):
        """Handle thanks naturally"""
        responses = [
            "You're welcome! 😊 Is there anything else I can help you with? Maybe compare neighborhoods or check price trends?",
            "Happy to help! Let me know if you want to explore more options or need any other information about properties.",
            "Glad I could assist! Feel free to ask me anything else — whether it's about home loans, amenities, or finding a different property.",
            "My pleasure! 🙌 I'm here whenever you need help. Want me to search for something else?",
        ]
        return random.choice(responses)

    def _handle_help(self, context):
        """Show capabilities in a natural way"""
        return (
            "I'm INFY Nest AI — your intelligent real estate assistant! Here's what I can do:\n\n"
            "🔍 **Property Search**\n"
            "Tell me your city, budget, BHK, or property type and I'll find matching properties instantly.\n"
            "_Example: \"2 BHK in Pune under 60 lakhs with parking\"_\n\n"
            "🏘️ **Amenity Filtering**\n"
            "Need specific amenities? I can filter by lift, parking, swimming pool, gym, garden, security, pet-friendly, vastu-compliant, and more.\n\n"
            "💰 **Price & Investment Advice**\n"
            "Ask me about price ranges in any city, best areas for investment, or market trends.\n\n"
            "🏦 **Home Loan & EMI Info**\n"
            "I can give you current interest rates, EMI estimates, and document requirements.\n\n"
            "🧭 **Vastu Tips**\n"
            "Need vastu guidance? I know the best directions and layouts.\n\n"
            "📊 **Comparisons**\n"
            "Compare cities, property types, or new vs resale properties.\n\n"
            "---\n"
            "💡 **Pro tip:** Just chat naturally! I understand sentences like:\n"
            "• \"I want a 3 BHK flat in Chennai with lift and gym\"\n"
            "• \"What's the price range in Hyderabad?\"\n"
            "• \"Compare Mumbai and Pune for buying\"\n\n"
            "What would you like to explore?"
        )


    def _handle_loan_query(self, context):
        """Handle loan/EMI queries with detailed info"""
        return (
            "Here's your comprehensive home loan guide 🏦\n\n"
            "**Current Interest Rates (2024-25):**\n"
            "| Bank | Rate |\n"
            "| SBI | 8.40% - 9.65% |\n"
            "| HDFC | 8.45% - 9.60% |\n"
            "| ICICI | 8.45% - 9.50% |\n"
            "| Axis | 8.50% - 9.65% |\n"
            "| Bank of Baroda | 8.40% - 10.65% |\n\n"
            "**Quick EMI Estimates:**\n"
            "• Rs. 30L loan @ 8.5% for 20 yrs = ~Rs. 26,035/month\n"
            "• Rs. 50L loan @ 8.5% for 20 yrs = ~Rs. 43,391/month\n"
            "• Rs. 75L loan @ 8.5% for 20 yrs = ~Rs. 65,087/month\n"
            "• Rs. 1Cr loan @ 8.5% for 20 yrs = ~Rs. 86,782/month\n\n"
            "**Eligibility Tips:**\n"
            "• Banks typically lend 60-80% of property value\n"
            "• EMI should not exceed 40-50% of monthly income\n"
            "• Good CIBIL score (750+) gets better rates\n\n"
            "**Documents Required:**\n"
            "• PAN Card & Aadhaar\n"
            "• Salary slips (3-6 months) / ITR (2-3 years)\n"
            "• Bank statements (6 months)\n"
            "• Property documents & agreement\n\n"
            "Would you like me to find properties within a specific EMI budget? "
            "Just tell me your monthly budget and preferred city!"
        )

    def _handle_investment(self, context):
        """Handle investment advice"""
        return (
            "Here's my analysis on the best real estate investments in India 📈\n\n"
            "**Top Cities for Investment (2024-25):**\n\n"
            "🥇 **Hyderabad** — High appreciation, IT corridor growth\n"
            "   • Avg. price: Rs. 5,500-12,000/sq.ft\n"
            "   • Hot areas: Gachibowli, Madhapur, Kokapet\n\n"
            "🥈 **Bengaluru** — Consistent demand from IT sector\n"
            "   • Avg. price: Rs. 6,000-15,000/sq.ft\n"
            "   • Hot areas: Whitefield, Sarjapur, Electronic City\n\n"
            "🥉 **Pune** — Affordable + high rental yield\n"
            "   • Avg. price: Rs. 5,000-12,000/sq.ft\n"
            "   • Hot areas: Hinjewadi, Wakad, Kharadi\n\n"
            "4️⃣ **Gurugram/NCR** — Premium market, metro connectivity\n"
            "   • Avg. price: Rs. 7,000-20,000/sq.ft\n"
            "   • Hot areas: Dwarka Expressway, Golf Course Rd\n\n"
            "5️⃣ **Ahmedabad** — GIFT City effect, affordable entry\n"
            "   • Avg. price: Rs. 3,500-8,000/sq.ft\n"
            "   • Hot areas: SG Highway, Science City Rd\n\n"
            "**Investment Tips:**\n"
            "✅ Look for RERA-registered projects\n"
            "✅ Check builder track record\n"
            "✅ Prefer areas with upcoming metro/infrastructure\n"
            "✅ Target 3-5% annual rental yield\n"
            "✅ Hold for 5-7 years for best appreciation\n\n"
            "Want me to search properties in any of these cities? Just tell me your budget!"
        )

    def _handle_vastu(self, context):
        """Handle vastu queries"""
        return (
            "Here's your Vastu Shastra guide for property buying 🧭\n\n"
            "**Best Directions:**\n"
            "• 🚪 **Main Entrance:** North-East (most auspicious) or East\n"
            "• 🛏️ **Master Bedroom:** South-West (stability & prosperity)\n"
            "• 🍳 **Kitchen:** South-East (fire element)\n"
            "• 🛋️ **Living Room:** North or East (positivity)\n"
            "• 🚿 **Bathroom:** North-West or West\n"
            "• 📚 **Study/Office:** North-East or East\n\n"
            "**Property Selection Tips:**\n"
            "• ✅ Regular-shaped plots (square/rectangle)\n"
            "• ✅ North-East slope is ideal\n"
            "• ✅ Open space in North-East direction\n"
            "• ❌ Avoid T-junction facing properties\n"
            "• ❌ Avoid South-West entrance\n"
            "• ❌ Avoid properties near temples/hospitals on south side\n\n"
            "**Floor Selection (Apartments):**\n"
            "• Ground floor: Earth element, good for elderly\n"
            "• Middle floors: Balanced energy\n"
            "• Top floors: Fire element, good for young professionals\n\n"
            "I can filter **Vastu-compliant properties** for you! Which city are you interested in?"
        )

    def _handle_comparison(self, message, context):
        """Handle comparison queries"""
        msg = message.lower()

        # Detect what's being compared
        if re.search(r'(apartment|flat).*vs.*(villa|house)', msg) or re.search(r'(villa|house).*vs.*(apartment|flat)', msg):
            return (
                "**Apartment vs Villa — Detailed Comparison** 🏠\n\n"
                "| Factor | Apartment | Villa |\n"
                "| Price | Lower (20L-2Cr) | Higher (80L-10Cr+) |\n"
                "| Area | 600-2500 sq.ft | 2000-8000 sq.ft |\n"
                "| Privacy | Shared walls | Complete privacy |\n"
                "| Security | Community security | Self-managed |\n"
                "| Maintenance | Society handles | Owner's responsibility |\n"
                "| Amenities | Pool, gym included | Need to build yourself |\n"
                "| Resale | High liquidity | Moderate liquidity |\n"
                "| Appreciation | 8-12% per year | 10-15% per year |\n\n"
                "**My Recommendation:**\n"
                "• 👨‍👩‍👧 Family with kids → Villa (space + garden)\n"
                "• 👨‍💼 Working professional → Apartment (low maintenance)\n"
                "• 📈 Investment → Apartment (higher rental yield)\n"
                "• 🧓 Retired → Ground floor apartment or villa\n\n"
                "Want me to search for either type? Tell me your city and budget!"
            )

        if re.search(r'(new|under construction).*vs.*(resale|old|ready)', msg) or re.search(r'(resale|ready).*vs.*(new|under construction)', msg):
            return (
                "**New Property vs Resale — What's Better?** 🏗️\n\n"
                "| Factor | New/Under Construction | Resale/Ready |\n"
                "| Price | 10-20% cheaper | Market rate |\n"
                "| Possession | Wait 2-4 years | Immediate |\n"
                "| Customization | Choose floor/unit | What's available |\n"
                "| Risk | Delay risk | No delay |\n"
                "| Loan | Higher interest | Normal rates |\n"
                "| Tax benefit | After possession | Immediate |\n\n"
                "**Choose New if:** You can wait, want lower price, have flexibility\n"
                "**Choose Resale if:** Need immediate possession, want to see actual property\n\n"
                "Want me to filter by possession status? I can show Ready-to-Move or Under Construction properties!"
            )

        # Generic comparison
        cities_found = []
        for city in self.all_cities:
            if city.lower() in msg:
                cities_found.append(city)

        if len(cities_found) >= 2:
            c1, c2 = cities_found[0], cities_found[1]
            return (
                f"**{c1} vs {c2} — Property Market Comparison** 🏙️\n\n"
                f"Both are excellent choices! Here's a quick comparison:\n\n"
                f"I'd recommend visiting the Search page to compare properties side-by-side in both cities. "
                f"Want me to search properties in **{c1}** or **{c2}** first? Just tell me your budget and preferences!"
            )

        return (
            "I'd be happy to help you compare! What would you like to compare?\n\n"
            "I can compare:\n"
            "• **Apartment vs Villa** — pros and cons\n"
            "• **New vs Resale** — which is better for you\n"
            "• **City vs City** — e.g., Mumbai vs Pune\n"
            "• **Rent vs Buy** — financial analysis\n\n"
            "Just tell me what you're deciding between!"
        )

    def _handle_price_query(self, message, context):
        """Handle price-related queries"""
        city = self._find_city(message) or context.get('last_city')

        if city:
            # Give city-specific info
            tier1 = ['Mumbai', 'New Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Gurugram', 'Noida']
            if city in tier1:
                price_range = "Rs. 6,000 - 25,000+ per sq.ft"
                apartment = "50L - 5Cr+"
                villa = "1.5Cr - 15Cr+"
            else:
                price_range = "Rs. 2,500 - 10,000 per sq.ft"
                apartment = "15L - 1.5Cr"
                villa = "40L - 5Cr"

            return (
                f"**Property Prices in {city}** 💰\n\n"
                f"**Average Rate:** {price_range}\n\n"
                f"**By Property Type:**\n"
                f"• Apartments: {apartment}\n"
                f"• Villas: {villa}\n"
                f"• Studio: 15L - 50L\n"
                f"• Plots: Varies by area\n\n"
                f"**Factors Affecting Price:**\n"
                f"• Location within city (prime vs suburb)\n"
                f"• Floor number (higher = premium)\n"
                f"• Builder reputation\n"
                f"• Amenities available\n"
                f"• Furnishing status\n\n"
                f"Want me to find specific properties in {city}? "
                f"Tell me your budget and I'll show you the best options!"
            )

        return (
            "Here's a general price guide across Indian cities 💰\n\n"
            "**Tier 1 Metro Cities (per sq.ft):**\n"
            "• Mumbai: Rs. 15,000 - 50,000+\n"
            "• Delhi/NCR: Rs. 8,000 - 25,000+\n"
            "• Bengaluru: Rs. 6,000 - 18,000\n"
            "• Hyderabad: Rs. 5,000 - 15,000\n"
            "• Chennai: Rs. 5,000 - 14,000\n\n"
            "**Tier 2 Cities (per sq.ft):**\n"
            "• Pune: Rs. 5,000 - 15,000\n"
            "• Jaipur: Rs. 3,000 - 8,000\n"
            "• Lucknow: Rs. 3,000 - 7,000\n"
            "• Kochi: Rs. 4,000 - 10,000\n"
            "• Ahmedabad: Rs. 3,500 - 9,000\n\n"
            "Tell me a **specific city** and I'll give you detailed pricing!"
        )


    def _handle_property_search(self, message, context, db_session):
        """Handle property search with context awareness"""
        # Extract all entities
        city = self._find_city(message)
        state = self._find_state(message)
        bhk = self._extract_bhk(message)
        budget = self._extract_budget(message)
        property_type = self._extract_property_type(message)
        amenities = self._extract_amenities(message)

        # Use context for missing info (remember previous conversation)
        if not city and context.get('last_city'):
            city = context['last_city']
        if not state and context.get('last_state'):
            state = context['last_state']
        if not bhk and context.get('last_bhk'):
            bhk = context['last_bhk']
        if not budget and context.get('last_budget'):
            budget = context['last_budget']
        if not property_type and context.get('last_type'):
            property_type = context['last_type']
        if not amenities and context.get('last_amenities'):
            amenities = context['last_amenities']

        # Update context with new info
        if city:
            context['last_city'] = city
        if state:
            context['last_state'] = state
        if bhk:
            context['last_bhk'] = bhk
        if budget:
            context['last_budget'] = budget
        if property_type:
            context['last_type'] = property_type
        if amenities:
            context['last_amenities'] = amenities

        # If we still don't have enough info, ask
        if not city and not state:
            return (
                "I'd love to help you find properties! 🔍\n\n"
                "Which **city** or **state** are you interested in? "
                "I cover all 36 states and 180+ cities across India.\n\n"
                "You can say something like:\n"
                "• \"Show me properties in Mumbai\"\n"
                "• \"3 BHK in Bengaluru under 80 lakhs\"\n"
                "• \"Villas in Kerala\""
            )

        # Build search description
        parts = []
        if property_type:
            parts.append(f"**{property_type}**")
        if bhk:
            parts.append(f"**{bhk} BHK**")
        if city:
            parts.append(f"in **{city}**")
        elif state:
            parts.append(f"in **{state}**")
        if budget:
            budget_str = f"{budget/100:.1f} Cr" if budget >= 100 else f"{budget:.0f} Lakhs"
            parts.append(f"under **Rs. {budget_str}**")
        if amenities:
            parts.append(f"with **{', '.join(amenities[:3])}**")

        search_desc = " ".join(parts) if parts else "matching your criteria"

        # Search database
        results = self._search_properties(
            city=city, state=state, bhk=bhk,
            budget=budget, property_type=property_type,
            amenities=amenities, db_session=db_session
        )

        intro = f"🔍 Searching for properties {search_desc}...\n\n"
        return intro + self._format_results(results, context)

    def _handle_general(self, message, context):
        """Handle general/unknown queries with helpful fallback"""
        msg = message.lower()

        # Check if it's a yes/no or follow-up
        if re.search(r'^(yes|yeah|yep|sure|ok|okay|please|go ahead)\b', msg):
            if context.get('last_city'):
                return f"Great! What would you like to know about properties in {context['last_city']}? I can search by budget, BHK, property type, or amenities."
            return "Sure! What kind of property are you looking for? Tell me the city, budget, and any preferences."

        if re.search(r'^(no|nope|nah|not really|maybe later)\b', msg):
            return "No problem! 😊 I'm here whenever you need me. Feel free to ask about any property, city, or real estate topic anytime."

        # Smart fallback with suggestions based on context
        city = context.get('last_city', '')
        suggestions = []
        if city:
            suggestions = [
                f"• \"Show me 2 BHK apartments in {city}\"",
                f"• \"Villas under 1 crore in {city}\"",
                f"• \"Properties with swimming pool in {city}\"",
            ]
        else:
            suggestions = [
                "• \"3 BHK in Mumbai under 1 crore\"",
                "• \"Villas with pool in Goa\"",
                "• \"Best city for investment\"",
                "• \"Properties with lift and parking in Delhi\"",
                "• \"Tell me about home loans\"",
            ]

        return (
            f"I'm not quite sure what you mean, but I'm here to help with real estate! 🏠\n\n"
            f"Try asking me something like:\n"
            + "\n".join(suggestions) + "\n\n"
            "Or type **\"help\"** to see everything I can do!"
        )


    def get_response(self, message, db_session=None, user_id=None):
        """Main method - Get intelligent response for user message"""
        message = message.strip()
        if not message:
            return "I'm listening! 👂 Type your question about properties, prices, or any real estate topic."

        # Get/create conversation context
        context = self._get_context(user_id)
        context['turn_count'] += 1
        context['history'].append({'role': 'user', 'message': message, 'time': datetime.now().isoformat()})

        # Classify intent
        intent = self._classify_intent(message)

        # Route to handler
        if intent == 'greeting':
            response = self._handle_greeting(context)
        elif intent == 'farewell':
            response = self._handle_farewell(context)
        elif intent == 'thanks':
            response = self._handle_thanks(context)
        elif intent == 'help':
            response = self._handle_help(context)
        elif intent == 'loan_query':
            response = self._handle_loan_query(context)
        elif intent == 'investment':
            response = self._handle_investment(context)
        elif intent == 'vastu':
            response = self._handle_vastu(context)
        elif intent == 'comparison':
            response = self._handle_comparison(message, context)
        elif intent == 'price_query':
            response = self._handle_price_query(message, context)
        elif intent == 'property_search':
            response = self._handle_property_search(message, context, db_session)
        elif intent == 'property_info':
            response = self._handle_property_info(message)
        elif intent == 'amenity_info':
            response = self._handle_amenity_info(message)
        else:
            response = self._handle_general(message, context)

        # Save to history
        context['history'].append({'role': 'bot', 'message': response, 'time': datetime.now().isoformat()})

        # Keep history manageable
        if len(context['history']) > 20:
            context['history'] = context['history'][-20:]

        return response

    def _handle_property_info(self, message):
        """Handle property type information queries"""
        msg = message.lower()

        if 'villa' in msg:
            return (
                "**Villa** — Your Private Paradise 🏡\n\n"
                "A villa is an independent luxury home, typically with:\n"
                "• 3-6 bedrooms with en-suite bathrooms\n"
                "• Private garden/lawn\n"
                "• Parking for 2+ cars\n"
                "• 2000-8000+ sq.ft area\n"
                "• Price: 80L - 15Cr+ depending on city\n\n"
                "**Best for:** Families wanting space, privacy, and a garden.\n"
                "**Popular in:** Goa, Bengaluru, Hyderabad, Pune outskirts\n\n"
                "Want me to search villas in a specific city?"
            )
        elif 'penthouse' in msg:
            return (
                "**Penthouse** — Luxury Living on Top 🌆\n\n"
                "A penthouse is the topmost floor of a building, featuring:\n"
                "• Expansive terrace/rooftop access\n"
                "• 3-6 BHK with premium finishes\n"
                "• 2500-6000+ sq.ft\n"
                "• Panoramic city views\n"
                "• Price: 1.5Cr - 20Cr+\n\n"
                "**Best for:** Luxury seekers, professionals wanting premium living.\n"
                "**Popular in:** Mumbai, Delhi, Bengaluru, Hyderabad\n\n"
                "Interested? I can search penthouses in any city!"
            )
        elif 'duplex' in msg:
            return (
                "**Duplex** — Two Floors, One Home 🏠\n\n"
                "A duplex is a two-story apartment within a building:\n"
                "• Internal staircase connecting 2 floors\n"
                "• 3-5 BHK typically\n"
                "• 1500-4000 sq.ft\n"
                "• Living area on one floor, bedrooms on another\n"
                "• Price: 60L - 5Cr+\n\n"
                "**Best for:** Families wanting separation between living and sleeping areas.\n\n"
                "Want me to find duplexes in your preferred city?"
            )
        elif 'plot' in msg or 'land' in msg:
            return (
                "**Plot/Land** — Build Your Dream 🌳\n\n"
                "Buying a plot gives you complete freedom:\n"
                "• Build exactly what you want\n"
                "• Higher appreciation potential (10-20%/year in good areas)\n"
                "• 1000-10000+ sq.ft available\n"
                "• Price: 10L - 10Cr+ depending on location\n\n"
                "**Things to Check:**\n"
                "• Clear title & ownership documents\n"
                "• RERA registration\n"
                "• Zoning regulations\n"
                "• Access to roads & utilities\n\n"
                "**Best for:** Long-term investors, people wanting custom homes.\n\n"
                "Which city are you looking for plots in?"
            )
        else:
            return (
                "**Property Types in India** 🏘️\n\n"
                "• **Apartment/Flat** — Multi-story, shared amenities, 15L-5Cr\n"
                "• **Villa** — Independent luxury home, garden, 80L-15Cr\n"
                "• **Independent House** — Standalone home, 30L-5Cr\n"
                "• **Penthouse** — Top-floor luxury, terrace, 1.5Cr-20Cr\n"
                "• **Studio** — Single room + kitchen, ideal for singles, 10L-50L\n"
                "• **Duplex** — Two-floor apartment, 60L-5Cr\n"
                "• **Row House** — Attached houses in a row, 40L-3Cr\n"
                "• **Farmhouse** — Large rural/semi-urban property, 50L-20Cr\n"
                "• **Builder Floor** — Independent floor in building, 30L-3Cr\n"
                "• **Plot** — Empty land, build your own, 10L-10Cr\n\n"
                "Which type interests you? I can search specific properties!"
            )

    def _handle_amenity_info(self, message):
        """Handle amenity information queries"""
        return (
            "**Amenities Guide** — What to Look For 🏊‍♂️\n\n"
            "**Essential (must-have):**\n"
            "• 🛗 Lift/Elevator — Critical for 4+ floor buildings\n"
            "• 🚗 Car Parking — Dedicated spot (1-2 per unit)\n"
            "• ⚡ Power Backup — Generator for common areas + homes\n"
            "• 🔒 24x7 Security — Guards + CCTV\n\n"
            "**Premium (nice-to-have):**\n"
            "• 🏊 Swimming Pool — Great for fitness & relaxation\n"
            "• 🏋️ Gym/Fitness Center — Save on membership costs\n"
            "• 🌳 Garden/Park — Fresh air & kids play area\n"
            "• 🎉 Club House — Party hall & social space\n"
            "• 🏃 Jogging Track — Morning walks within society\n\n"
            "**Lifestyle:**\n"
            "• 🐾 Pet Friendly — Not all societies allow pets!\n"
            "• 🧭 Vastu Compliant — Important for many buyers\n"
            "• ☀️ Solar Panels — Reduced electricity bills\n"
            "• 🔌 EV Charging — Future-ready for electric cars\n"
            "• 🍳 Modular Kitchen — Ready-to-use kitchen\n\n"
            "I can filter properties by ANY of these amenities! "
            "Just say something like \"apartments with pool and gym in Pune\"."
        )
