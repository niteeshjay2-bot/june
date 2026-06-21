"""
AI Real Estate India - Main Flask Application
A beautiful AI-powered real estate platform with chatbot,
authentication, and comprehensive Indian property listings.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from models import db, User, Property, Favorite, SearchHistory, ContactInquiry
from auth import auth_bp
from chatbot import ChatBot

# Initialize chatbot
chatbot = ChatBot()


def create_app():
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-real-estate-super-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data', 'real_estate.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Load states and cities data
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    states_cities_path = os.path.join(data_dir, 'indian_states_cities.json')
    with open(states_cities_path, 'r', encoding='utf-8') as f:
        STATES_CITIES = json.load(f)

    amenities_path = os.path.join(data_dir, 'amenities.json')
    with open(amenities_path, 'r', encoding='utf-8') as f:
        AMENITIES_LIST = json.load(f)

    # ==================== MAIN ROUTES ====================

    @app.route('/')
    def home():
        """Homepage with featured properties and search"""
        featured = Property.query.order_by(Property.rating.desc()).limit(12).all()
        states = sorted(STATES_CITIES.keys())
        total_properties = Property.query.count()
        total_cities = len(set(p.city for p in Property.query.with_entities(Property.city).distinct().all()))
        return render_template('home.html',
                               featured=featured,
                               states=states,
                               total_properties=total_properties,
                               total_cities=total_cities,
                               states_cities=STATES_CITIES)

    @app.route('/search')
    def search():
        """Search properties with filters"""
        # Get filter parameters
        state = request.args.get('state', '')
        city = request.args.get('city', '')
        property_type = request.args.get('property_type', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bhk = request.args.get('bhk', type=int)
        furnishing = request.args.get('furnishing', '')
        possession = request.args.get('possession', '')
        sort_by = request.args.get('sort_by', 'relevance')
        page = request.args.get('page', 1, type=int)

        # Amenity filters
        lift = request.args.get('lift', '')
        car_parking = request.args.get('car_parking', '')
        swimming_pool = request.args.get('swimming_pool', '')
        gym = request.args.get('gym', '')
        power_backup = request.args.get('power_backup', '')
        security = request.args.get('security', '')
        garden = request.args.get('garden', '')
        club_house = request.args.get('club_house', '')
        pet_friendly = request.args.get('pet_friendly', '')
        vastu_compliant = request.args.get('vastu_compliant', '')

        # Build query
        query = Property.query

        if state:
            query = query.filter(Property.state == state)
        if city:
            query = query.filter(Property.city == city)
        if property_type:
            query = query.filter(Property.property_type == property_type)
        if min_price:
            query = query.filter(Property.price_lakhs >= min_price)
        if max_price:
            query = query.filter(Property.price_lakhs <= max_price)
        if bhk:
            query = query.filter(Property.bhk == bhk)
        if furnishing:
            query = query.filter(Property.furnishing == furnishing)
        if possession:
            query = query.filter(Property.possession == possession)

        # Amenity filters
        if lift == 'yes':
            query = query.filter(Property.lift == True)
        if car_parking == 'yes':
            query = query.filter(Property.car_parking == True)
        if swimming_pool == 'yes':
            query = query.filter(Property.swimming_pool == True)
        if gym == 'yes':
            query = query.filter(Property.gym == True)
        if power_backup == 'yes':
            query = query.filter(Property.power_backup == True)
        if security == 'yes':
            query = query.filter(Property.security == True)
        if garden == 'yes':
            query = query.filter(Property.garden == True)
        if club_house == 'yes':
            query = query.filter(Property.club_house == True)
        if pet_friendly == 'yes':
            query = query.filter(Property.pet_friendly == True)
        if vastu_compliant == 'yes':
            query = query.filter(Property.vastu_compliant == True)

        # Sorting
        if sort_by == 'price_low':
            query = query.order_by(Property.price_lakhs.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Property.price_lakhs.desc())
        elif sort_by == 'area_high':
            query = query.order_by(Property.area_sqft.desc())
        elif sort_by == 'rating':
            query = query.order_by(Property.rating.desc())
        elif sort_by == 'newest':
            query = query.order_by(Property.age_years.asc())
        else:
            query = query.order_by(Property.rating.desc())

        # Pagination
        per_page = 12
        properties = query.paginate(page=page, per_page=per_page, error_out=False)

        # Save search history if user logged in
        if current_user.is_authenticated:
            search_record = SearchHistory(
                user_id=current_user.id,
                state=state,
                city=city,
                property_type=property_type,
                min_price=min_price,
                max_price=max_price,
                bhk=bhk
            )
            db.session.add(search_record)
            db.session.commit()

        states = sorted(STATES_CITIES.keys())
        property_types = [
            "Apartment", "Villa", "Independent House", "Penthouse",
            "Studio Apartment", "Duplex", "Row House", "Farmhouse",
            "Builder Floor", "Plot"
        ]

        return render_template('search.html',
                               properties=properties,
                               states=states,
                               states_cities=STATES_CITIES,
                               property_types=property_types,
                               amenities_list=AMENITIES_LIST,
                               # Pass current filters back
                               current_state=state,
                               current_city=city,
                               current_type=property_type,
                               current_min_price=min_price,
                               current_max_price=max_price,
                               current_bhk=bhk,
                               current_furnishing=furnishing,
                               current_possession=possession,
                               current_sort=sort_by,
                               current_lift=lift,
                               current_car_parking=car_parking,
                               current_swimming_pool=swimming_pool,
                               current_gym=gym,
                               current_power_backup=power_backup,
                               current_security=security,
                               current_garden=garden,
                               current_club_house=club_house,
                               current_pet_friendly=pet_friendly,
                               current_vastu_compliant=vastu_compliant)

    @app.route('/property/<int:property_id>')
    def property_detail(property_id):
        """Property detail page"""
        prop = Property.query.filter_by(property_id=property_id).first_or_404()

        # Get similar properties
        similar = Property.query.filter(
            Property.city == prop.city,
            Property.property_type == prop.property_type,
            Property.property_id != prop.property_id
        ).order_by(Property.rating.desc()).limit(4).all()

        # Check if favorited
        is_favorited = False
        if current_user.is_authenticated:
            is_favorited = Favorite.query.filter_by(
                user_id=current_user.id,
                property_id=prop.id
            ).first() is not None

        return render_template('property_detail.html',
                               property=prop,
                               similar=similar,
                               is_favorited=is_favorited)

    @app.route('/states')
    def states_list():
        """List all Indian states"""
        states = sorted(STATES_CITIES.keys())
        state_counts = {}
        for state in states:
            count = Property.query.filter_by(state=state).count()
            state_counts[state] = count
        return render_template('states.html', states=states, state_counts=state_counts)

    @app.route('/state/<state_name>')
    def state_detail(state_name):
        """Show cities in a state"""
        if state_name not in STATES_CITIES:
            flash('State not found.', 'error')
            return redirect(url_for('home'))

        cities = STATES_CITIES[state_name]
        city_counts = {}
        for city in cities:
            count = Property.query.filter_by(state=state_name, city=city).count()
            city_counts[city] = count

        return render_template('state_detail.html',
                               state_name=state_name,
                               cities=cities,
                               city_counts=city_counts)

    # ==================== API ROUTES ====================

    @app.route('/api/cities/<state>')
    def get_cities(state):
        """API to get cities for a given state (for dynamic dropdowns)"""
        cities = STATES_CITIES.get(state, [])
        return jsonify({'cities': sorted(cities)})

    @app.route('/api/chat', methods=['POST'])
    def chat():
        """AI Chatbot API endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'response': 'Please type a message to get started!'})

            user_message = data.get('message', '').strip()

            if not user_message:
                return jsonify({'response': 'Please type a message to get started!'})

            # Get chatbot response
            try:
                user_id = current_user.id if current_user.is_authenticated else None
            except Exception:
                user_id = None

            bot_response = chatbot.get_response(user_message, db_session=db.session, user_id=user_id)

            # Save chat history if user is logged in
            try:
                if current_user.is_authenticated:
                    from models import ChatMessage
                    chat_msg = ChatMessage(
                        user_id=current_user.id,
                        message=user_message,
                        response=bot_response
                    )
                    db.session.add(chat_msg)
                    db.session.commit()
            except Exception:
                pass  # Don't fail if saving history fails

            return jsonify({'response': bot_response})

        except Exception as e:
            print(f"[CHATBOT ERROR] {str(e)}")
            return jsonify({'response': "I apologize, but I encountered an issue processing your message. Could you please try rephrasing? You can ask me about properties, prices, investments, or home loans!"})

    @app.route('/api/favorite/<int:property_id>', methods=['POST'])
    @login_required
    def toggle_favorite(property_id):
        """Toggle property as favorite (form POST - no JS)"""
        prop = Property.query.filter_by(property_id=property_id).first_or_404()

        existing = Favorite.query.filter_by(
            user_id=current_user.id,
            property_id=prop.id
        ).first()

        if existing:
            db.session.delete(existing)
            db.session.commit()
            flash('Removed from favorites.', 'info')
        else:
            fav = Favorite(user_id=current_user.id, property_id=prop.id)
            db.session.add(fav)
            db.session.commit()
            flash('Added to favorites!', 'success')

        return redirect(url_for('property_detail', property_id=property_id))

    @app.route('/favorites')
    @login_required
    def favorites():
        """User's favorite properties"""
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        property_ids = [f.property_id for f in favs]
        properties = Property.query.filter(Property.id.in_(property_ids)).all()
        return render_template('favorites.html', properties=properties)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact page"""
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            message = request.form.get('message', '').strip()
            prop_id = request.form.get('property_id', type=int)

            if name and email and message:
                inquiry = ContactInquiry(
                    name=name,
                    email=email,
                    phone=phone if phone else None,
                    property_id=prop_id,
                    message=message
                )
                db.session.add(inquiry)
                db.session.commit()
                flash('Your inquiry has been submitted successfully! We will get back to you soon.', 'success')
            else:
                flash('Please fill in all required fields.', 'error')

            return redirect(url_for('contact'))

        return render_template('contact.html')

    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    @app.route('/chatbot', methods=['GET', 'POST'])
    def chatbot_page():
        """Chatbot full page - pure Python, no JavaScript"""
        import re

        # Initialize chat history in session
        if 'chat_history' not in session:
            session['chat_history'] = []

        # Handle form POST
        if request.method == 'POST':
            user_message = request.form.get('message', '').strip()
            if user_message:
                # Get bot response
                try:
                    user_id = current_user.id if current_user.is_authenticated else None
                except Exception:
                    user_id = None

                try:
                    bot_response = chatbot.get_response(user_message, db_session=db.session, user_id=user_id)
                except Exception as e:
                    bot_response = "I apologize, I encountered an issue. Please try rephrasing your question!"

                # Format response for HTML display
                formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', bot_response)
                formatted_response = formatted_response.replace('\n', '<br>')

                # Get current history, append, save back
                history = list(session.get('chat_history', []))
                history.append({'role': 'user', 'content': user_message})
                history.append({'role': 'bot', 'content': formatted_response})

                # Keep only last 20 messages
                if len(history) > 20:
                    history = history[-20:]

                session['chat_history'] = history
                session.modified = True

                # Save to DB if logged in
                try:
                    if current_user.is_authenticated:
                        from models import ChatMessage
                        chat_msg = ChatMessage(
                            user_id=current_user.id,
                            message=user_message,
                            response=bot_response
                        )
                        db.session.add(chat_msg)
                        db.session.commit()
                except Exception:
                    pass

            return redirect(url_for('chatbot_page'))

        # Handle suggestion chip clicks (GET with query param)
        if request.args.get('message'):
            user_message = request.args.get('message', '').strip()
            if user_message:
                try:
                    user_id = current_user.id if current_user.is_authenticated else None
                except Exception:
                    user_id = None

                try:
                    bot_response = chatbot.get_response(user_message, db_session=db.session, user_id=user_id)
                except Exception:
                    bot_response = "I apologize, I encountered an issue. Please try rephrasing your question!"

                formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', bot_response)
                formatted_response = formatted_response.replace('\n', '<br>')

                history = list(session.get('chat_history', []))
                history.append({'role': 'user', 'content': user_message})
                history.append({'role': 'bot', 'content': formatted_response})

                if len(history) > 20:
                    history = history[-20:]

                session['chat_history'] = history
                session.modified = True

                return redirect(url_for('chatbot_page'))

        chat_history = session.get('chat_history', [])
        return render_template('chatbot.html',
                               chat_history=chat_history,
                               prefill_message='')

    @app.route('/chatbot/clear')
    def chatbot_clear():
        """Clear chat history"""
        session.pop('chat_history', None)
        return redirect(url_for('chatbot_page'))

    # ==================== ERROR HANDLERS ====================

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    # ==================== CONTEXT PROCESSORS ====================

    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        # Curated property images from Unsplash (free to use)
        property_images = {
            'Apartment': [
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1567496898669-ee935f5f647a?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&h=250&fit=crop',
            ],
            'Villa': [
                'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=400&h=250&fit=crop',
            ],
            'Independent House': [
                'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1598228723793-52759bba239c?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=400&h=250&fit=crop',
            ],
            'Penthouse': [
                'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600607687644-c7171b42498f?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=400&h=250&fit=crop',
            ],
            'Studio Apartment': [
                'https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1554995207-c18c203602cb?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=400&h=250&fit=crop',
            ],
            'Duplex': [
                'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600585153490-76fb20a32601?w=400&h=250&fit=crop',
            ],
            'Row House': [
                'https://images.unsplash.com/photo-1600047509358-9dc75507daeb?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=400&h=250&fit=crop',
            ],
            'Farmhouse': [
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1605146769289-440113cc3d00?w=400&h=250&fit=crop',
            ],
            'Builder Floor': [
                'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1600210492493-0946911123ea?w=400&h=250&fit=crop',
            ],
            'Plot': [
                'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1628624747186-a941c476b7ef?w=400&h=250&fit=crop',
                'https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=400&h=250&fit=crop',
            ],
        }

        def get_property_image(property_type, property_id):
            """Get a consistent image for a property based on its type and ID"""
            images = property_images.get(property_type, property_images['Apartment'])
            return images[property_id % len(images)]

        return {
            'states_list': sorted(STATES_CITIES.keys()),
            'app_name': 'INFY Nest AI',
            'app_tagline': 'AI-Powered Real Estate Platform',
            'get_property_image': get_property_image,
        }

    return app


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app = create_app()

    # Initialize database on first run
    from init_db import init_database
    init_database(app)

    app.run(debug=True, host='0.0.0.0', port=5000)
