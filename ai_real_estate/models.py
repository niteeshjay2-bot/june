"""
Database Models for AI Real Estate Application
Uses Flask-SQLAlchemy with SQLite database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    profile_pic = db.Column(db.String(256), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='buyer')  # 'buyer', 'seller', or 'admin'

    # Relationships
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    searches = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    listings = db.relationship('SellerListing', backref='seller', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    """Property listing model"""
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, unique=True, nullable=False)
    property_name = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(100), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    locality = db.Column(db.String(200), nullable=True)
    price_lakhs = db.Column(db.Float, nullable=False)
    price_per_sqft = db.Column(db.Float, nullable=True)
    area_sqft = db.Column(db.Integer, nullable=False)
    bhk = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    total_floors = db.Column(db.Integer, nullable=True)
    age_years = db.Column(db.Integer, nullable=True)
    facing = db.Column(db.String(20), nullable=True)
    furnishing = db.Column(db.String(30), nullable=True)
    transaction_type = db.Column(db.String(30), nullable=True)
    possession = db.Column(db.String(30), nullable=True)
    builder = db.Column(db.String(100), nullable=True)
    amenities = db.Column(db.Text, nullable=True)  # Pipe-separated list

    # Individual amenity flags for quick filtering
    lift = db.Column(db.Boolean, default=False)
    car_parking = db.Column(db.Boolean, default=False)
    swimming_pool = db.Column(db.Boolean, default=False)
    gym = db.Column(db.Boolean, default=False)
    power_backup = db.Column(db.Boolean, default=False)
    security = db.Column(db.Boolean, default=False)
    garden = db.Column(db.Boolean, default=False)
    club_house = db.Column(db.Boolean, default=False)
    pet_friendly = db.Column(db.Boolean, default=False)
    vastu_compliant = db.Column(db.Boolean, default=False)

    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    favorites = db.relationship('Favorite', backref='property', lazy=True, cascade='all, delete-orphan')

    def get_amenities_list(self):
        """Return amenities as a list"""
        if self.amenities:
            return self.amenities.split('|')
        return []

    def get_price_formatted(self):
        """Return price in formatted string"""
        if self.price_lakhs >= 100:
            return f"{self.price_lakhs / 100:.2f} Cr"
        return f"{self.price_lakhs:.2f} L"

    def __repr__(self):
        return f'<Property {self.property_name} - {self.city}>'


class Favorite(db.Model):
    """User's favorite/saved properties"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'property_id'),)


class SearchHistory(db.Model):
    """User search history for recommendations"""
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_query = db.Column(db.String(500), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    property_type = db.Column(db.String(50), nullable=True)
    min_price = db.Column(db.Float, nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    bhk = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    """Chat messages for the AI chatbot"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactInquiry(db.Model):
    """Contact inquiries for properties"""
    __tablename__ = 'contact_inquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class SellerListing(db.Model):
    """Seller's property listings"""
    __tablename__ = 'seller_listings'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(200), nullable=True)
    price_lakhs = db.Column(db.Float, nullable=False)
    area_sqft = db.Column(db.Integer, nullable=False)
    bhk = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, default=1)
    floor = db.Column(db.Integer, default=0)
    total_floors = db.Column(db.Integer, default=1)
    facing = db.Column(db.String(20), nullable=True)
    furnishing = db.Column(db.String(30), nullable=True)
    possession = db.Column(db.String(30), nullable=True)
    description = db.Column(db.Text, nullable=True)
    amenities = db.Column(db.Text, nullable=True)  # comma separated
    contact_phone = db.Column(db.String(15), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, sold, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views_count = db.Column(db.Integer, default=0)
    inquiries_count = db.Column(db.Integer, default=0)

    def get_price_formatted(self):
        if self.price_lakhs >= 100:
            return f"{self.price_lakhs / 100:.2f} Cr"
        return f"{self.price_lakhs:.1f} L"

    def __repr__(self):
        return f'<SellerListing {self.title} - {self.city}>'
