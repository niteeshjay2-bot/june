"""
INFY Nest AI - Property Price Prediction Engine
Uses statistical model trained on 19,891 real property records.
Predicts price based on city, area, BHK, property type, floor, amenities, etc.
"""

import csv
import os
import json
import math


class PricePredictor:
    """AI-powered property price prediction based on dataset analysis"""

    def __init__(self):
        self.city_rates = {}       # city -> avg price per sqft
        self.type_multipliers = {} # property_type -> multiplier
        self.bhk_factors = {}      # bhk -> price factor
        self.furnishing_factors = {}
        self.possession_factors = {}
        self.floor_factor = 0.01   # per floor premium
        self.amenity_premiums = {}
        self.state_rates = {}
        self._train()

    def _train(self):
        """Train the model on actual dataset"""
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        csv_path = os.path.join(data_dir, 'indian_real_estate_dataset.csv')

        # Collect data for analysis
        city_prices = {}    # city -> list of price_per_sqft
        type_prices = {}    # type -> list of price_per_sqft
        state_prices = {}   # state -> list of price_per_sqft
        bhk_prices = {}     # bhk -> list of price_per_sqft
        furnishing_prices = {}
        possession_prices = {}
        amenity_price_diff = {}

        all_prices = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ppsf = float(row['price_per_sqft'])
                city = row['city']
                state = row['state']
                ptype = row['property_type']
                bhk = int(row['bhk'])
                furnishing = row['furnishing']
                possession = row['possession']

                all_prices.append(ppsf)

                # City rates
                if city not in city_prices:
                    city_prices[city] = []
                city_prices[city].append(ppsf)

                # State rates
                if state not in state_prices:
                    state_prices[state] = []
                state_prices[state].append(ppsf)

                # Type rates
                if ptype not in type_prices:
                    type_prices[ptype] = []
                type_prices[ptype].append(ppsf)

                # BHK rates
                if bhk not in bhk_prices:
                    bhk_prices[bhk] = []
                bhk_prices[bhk].append(ppsf)

                # Furnishing
                if furnishing not in furnishing_prices:
                    furnishing_prices[furnishing] = []
                furnishing_prices[furnishing].append(ppsf)

                # Possession
                if possession not in possession_prices:
                    possession_prices[possession] = []
                possession_prices[possession].append(ppsf)

                # Amenity impact
                amenities_list = row['amenities'].split('|') if row['amenities'] else []
                for amenity in amenities_list:
                    if amenity not in amenity_price_diff:
                        amenity_price_diff[amenity] = []
                    amenity_price_diff[amenity].append(ppsf)

        # Calculate averages
        global_avg = sum(all_prices) / len(all_prices)

        # City average price per sqft
        self.city_rates = {c: sum(v)/len(v) for c, v in city_prices.items()}

        # State average
        self.state_rates = {s: sum(v)/len(v) for s, v in state_prices.items()}

        # Type multipliers (relative to global average)
        type_avgs = {t: sum(v)/len(v) for t, v in type_prices.items()}
        self.type_multipliers = {t: avg/global_avg for t, avg in type_avgs.items()}

        # BHK factors
        bhk_avgs = {b: sum(v)/len(v) for b, v in bhk_prices.items()}
        base_bhk = bhk_avgs.get(2, global_avg)
        self.bhk_factors = {b: avg/base_bhk for b, avg in bhk_avgs.items()}

        # Furnishing factors
        furn_avgs = {f: sum(v)/len(v) for f, v in furnishing_prices.items()}
        base_furn = furn_avgs.get('Unfurnished', global_avg)
        self.furnishing_factors = {f: avg/base_furn for f, avg in furn_avgs.items()}

        # Possession factors
        poss_avgs = {p: sum(v)/len(v) for p, v in possession_prices.items()}
        base_poss = poss_avgs.get('Ready to Move', global_avg)
        self.possession_factors = {p: avg/base_poss for p, avg in poss_avgs.items()}

        # Amenity premiums (percentage premium for having each amenity)
        for amenity, prices in amenity_price_diff.items():
            amenity_avg = sum(prices) / len(prices)
            premium = (amenity_avg - global_avg) / global_avg
            self.amenity_premiums[amenity] = max(0, premium * 0.3)  # Scale down

        self.global_avg = global_avg

    def predict(self, city, state, property_type, area_sqft, bhk,
                floor=0, total_floors=1, furnishing='Unfurnished',
                possession='Ready to Move', amenities=None, age_years=0):
        """
        Predict property price based on input parameters.
        Returns dict with predicted price and breakdown.
        """
        # Base rate from city (most important factor)
        if city in self.city_rates:
            base_rate = self.city_rates[city]
        elif state in self.state_rates:
            base_rate = self.state_rates[state]
        else:
            base_rate = self.global_avg

        # Apply property type multiplier
        type_mult = self.type_multipliers.get(property_type, 1.0)

        # Apply BHK factor
        bhk_factor = self.bhk_factors.get(bhk, 1.0)

        # Apply furnishing factor
        furn_factor = self.furnishing_factors.get(furnishing, 1.0)

        # Apply possession factor
        poss_factor = self.possession_factors.get(possession, 1.0)

        # Floor premium (higher floors cost more in apartments)
        if total_floors > 3 and floor > 0:
            floor_premium = 1 + (floor / total_floors) * 0.08
        else:
            floor_premium = 1.0

        # Age depreciation (older properties cost less)
        if age_years > 0:
            age_factor = max(0.75, 1 - (age_years * 0.012))
        else:
            age_factor = 1.0

        # Amenity premium
        amenity_premium = 1.0
        if amenities:
            for amenity in amenities:
                amenity_premium += self.amenity_premiums.get(amenity, 0)

        # Calculate predicted price per sqft
        predicted_ppsf = (base_rate * type_mult * bhk_factor *
                          furn_factor * poss_factor * floor_premium *
                          age_factor * amenity_premium)

        # Calculate total price
        total_price_lakhs = (predicted_ppsf * area_sqft) / 100000

        # Price range (±12%)
        price_low = total_price_lakhs * 0.88
        price_high = total_price_lakhs * 1.12

        # Format prices
        def format_price(lakhs):
            if lakhs >= 100:
                return f"Rs. {lakhs/100:.2f} Crore"
            else:
                return f"Rs. {lakhs:.1f} Lakhs"

        # Confidence score based on how much data we have for this city
        if city in self.city_rates:
            confidence = 88
        elif state in self.state_rates:
            confidence = 72
        else:
            confidence = 60

        return {
            'predicted_price': total_price_lakhs,
            'predicted_price_formatted': format_price(total_price_lakhs),
            'price_low': price_low,
            'price_low_formatted': format_price(price_low),
            'price_high': price_high,
            'price_high_formatted': format_price(price_high),
            'price_per_sqft': round(predicted_ppsf, 0),
            'confidence': round(confidence),
            'breakdown': {
                'base_rate': f"Rs. {base_rate:.0f}/sqft (city average)",
                'type_effect': f"{(type_mult-1)*100:+.1f}% ({property_type})",
                'bhk_effect': f"{(bhk_factor-1)*100:+.1f}% ({bhk} BHK)",
                'furnishing_effect': f"{(furn_factor-1)*100:+.1f}% ({furnishing})",
                'possession_effect': f"{(poss_factor-1)*100:+.1f}% ({possession})",
                'floor_effect': f"{(floor_premium-1)*100:+.1f}% (Floor {floor}/{total_floors})",
                'age_effect': f"{(age_factor-1)*100:+.1f}% ({age_years} years old)",
                'amenity_effect': f"{(amenity_premium-1)*100:+.1f}% ({len(amenities) if amenities else 0} amenities)",
            },
            'market_insight': self._get_market_insight(city, property_type, total_price_lakhs),
        }

    def _get_market_insight(self, city, property_type, predicted_price):
        """Generate market insight text"""
        if city in self.city_rates:
            city_avg = self.city_rates[city]
            if city_avg > self.global_avg * 1.3:
                market = "premium"
            elif city_avg > self.global_avg:
                market = "above average"
            else:
                market = "affordable"
        else:
            market = "emerging"

        insights = []
        insights.append(f"{city} is a {market} market for real estate.")

        if predicted_price > 100:
            insights.append("This falls in the luxury segment. Consider negotiating 5-8% below asking price.")
        elif predicted_price > 50:
            insights.append("This is in the mid-premium range. Good investment potential with 8-12% annual appreciation expected.")
        else:
            insights.append("This is in the affordable segment. Ideal for first-time buyers. Expected appreciation: 6-10% annually.")

        return " ".join(insights)

    def get_city_stats(self, city):
        """Get price statistics for a city"""
        if city in self.city_rates:
            avg_rate = self.city_rates[city]
            return {
                'avg_price_per_sqft': round(avg_rate),
                'for_1000_sqft': round(avg_rate * 1000 / 100000, 1),
                'for_1500_sqft': round(avg_rate * 1500 / 100000, 1),
                'for_2000_sqft': round(avg_rate * 2000 / 100000, 1),
            }
        return None
