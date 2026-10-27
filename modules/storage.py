"""
Storage module for Simulated Database Persistence.
Zero external database dependencies (uses local trips_db.json + session state).
Perfect for 1-click deployment on Streamlit Cloud.
"""

import json
import os
import uuid
from datetime import datetime, date

STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trips_db.json")


def _get_starter_trips():
    """Returns curated starter trips to populate simulated database if empty."""
    return {
        "trip_tokyo_sample_01": {
            "id": "trip_tokyo_sample_01",
            "title": "Tokyo Neon & Heritage Odyssey",
            "destination": "Tokyo, Japan",
            "duration_days": 4,
            "start_date": "2026-05-10",
            "end_date": "2026-05-13",
            "budget_level": "Moderate (Comfortable Boutique / 3-4★)",
            "travel_party": "Romantic Couple",
            "pace": "Moderate (Balanced exploration & cafe breaks)",
            "interests": ["Street Food & Local Markets", "Iconic Landmarks & Architecture", "Art Galleries & Historic Museums"],
            "dietary": "None / Flexible",
            "created_at": "2026-04-20 14:30:00",
            "currency": "JPY",
            "exchange_rate_to_usd": 152.0,
            "exchange_rate_to_inr": 0.57,
            "total_estimated_usd": 740.0,
            "total_estimated_inr": 63900.0,
            "overview": "A balanced 4-day Tokyo journey grouping historic Asakusa, buzzing Shibuya & Shinjuku, futuristic Odaiba, and artistic Roppongi with zero cross-city backtracking.",
            "emergency_contacts": {
                "police": "110",
                "ambulance": "119",
                "tourist_helpline": "+81 3 3201 3331 (Japan Visitor Hotline)",
                "embassy_note": "Locate in Minato City / Roppongi embassy quarter."
            },
            "packing_tips": [
                "Pasmo/Suica IC transport card or Apple Wallet transit pass",
                "Comfortable slip-on walking shoes (temples require shoes-off)",
                "Universal power adapter (Type A/B 100V)",
                "Small hand towel and pocket trash bag"
            ],
            "days": [
                {
                    "day_number": 1,
                    "day_theme": "Historic Edo & Asakusa Heritage",
                    "cluster_neighborhood": "Asakusa & Ueno Cultural Cluster",
                    "transit_fatigue_score": "Low (All locations within 1.5 km walking & 1 subway stop)",
                    "day_total_usd": 165.0,
                    "day_total_inr": 14250.0,
                    "slots": {
                        "morning": {
                            "time": "09:00 - 12:00",
                            "title": "Senso-ji Temple & Nakamise-dori Exploration",
                            "category": "Sightseeing / Culture",
                            "description": "Walk through the iconic Kaminarimon thunder gate, browse artisan craft and snack stalls along Nakamise, and draw an omikuji fortune at Senso-ji.",
                            "location_name": "Senso-ji, Asakusa",
                            "lat": 35.7148,
                            "lng": 139.7967,
                            "cost_local": 2000,
                            "cost_usd": 15.0,
                            "cost_inr": 1300.0,
                            "pro_tip": "Visit before 9:30 AM to photograph the temple grounds before tour crowds arrive."
                        },
                        "lunch": {
                            "time": "12:30 - 14:00",
                            "title": "Tempura Daikokuya or Asakusa Imahan",
                            "category": "Dining / Food Experience",
                            "cuisine": "Traditional Tokyo Tempura & Sukiyaki",
                            "description": "Savor crispy sesame-oil fried prawn tempura over warm rice in a heritage tatami setting established in 1887.",
                            "location_name": "Daikokuya Tempura, Asakusa",
                            "lat": 35.7126,
                            "lng": 139.7949,
                            "cost_local": 4500,
                            "cost_usd": 30.0,
                            "cost_inr": 2600.0,
                            "dietary_tags": "Vegetarian tempura sets available upon request"
                        },
                        "afternoon": {
                            "time": "14:30 - 17:30",
                            "title": "Ueno Park, Tokyo National Museum & Shinobazu Pond",
                            "category": "Leisure / Immersion",
                            "description": "Stroll through peaceful Ueno Onshi Park, inspect priceless samurai armor and woodblock prints, and paddle on Shinobazu Pond.",
                            "location_name": "Tokyo National Museum, Ueno",
                            "lat": 35.7189,
                            "lng": 139.7765,
                            "cost_local": 3000,
                            "cost_usd": 20.0,
                            "cost_inr": 1730.0,
                            "pro_tip": "The gallery gardens behind the main building are a peaceful hidden oasis."
                        },
                        "evening": {
                            "time": "18:30 - 21:30",
                            "title": "Tokyo Skytree Sunset & Solamachi Riverside Dining",
                            "category": "Dining & Nightlife",
                            "description": "Witness the glowing Tokyo megalopolis from the 350m Tembo Deck, followed by dinner and craft beer along the Sumida river promenade.",
                            "location_name": "Tokyo Skytree & Solamachi",
                            "lat": 35.7101,
                            "lng": 139.8107,
                            "cost_local": 15000,
                            "cost_usd": 100.0,
                            "cost_inr": 8620.0,
                            "pro_tip": "Book Tembo Deck timed tickets 3 days in advance to catch golden hour sunset."
                        }
                    }
                },
                {
                    "day_number": 2,
                    "day_theme": "Modern Pop-Culture & Shibuya Energy",
                    "cluster_neighborhood": "Shibuya & Harajuku Western Cluster",
                    "transit_fatigue_score": "Low (Continuous pedestrian walk from Harajuku to Shibuya)",
                    "day_total_usd": 190.0,
                    "day_total_inr": 16400.0,
                    "slots": {
                        "morning": {
                            "time": "09:30 - 12:00",
                            "title": "Meiji Jingu Shrine & Forest Walk",
                            "category": "Sightseeing / Culture",
                            "description": "Escape the bustle through towering cedar groves leading to Tokyo's grandest Shinto shrine dedicated to Emperor Meiji.",
                            "location_name": "Meiji Shrine, Yoyogi",
                            "lat": 35.6764,
                            "lng": 139.6993,
                            "cost_local": 1000,
                            "cost_usd": 8.0,
                            "cost_inr": 690.0,
                            "pro_tip": "Write an Ema wooden prayer tablet at the sacred camphor trees."
                        },
                        "lunch": {
                            "time": "12:30 - 14:00",
                            "title": "Afuri Harajuku (Yuzu Shio Ramen)",
                            "category": "Dining / Food Experience",
                            "cuisine": "Contemporary Citrus Ramen & Vegan Broth",
                            "description": "Famous light broth infused with fresh yuzu citrus, charcoal-grilled chashu pork, and crisp bamboo shoots.",
                            "location_name": "Afuri, Harajuku",
                            "lat": 35.6712,
                            "lng": 139.7045,
                            "cost_local": 3500,
                            "cost_usd": 24.0,
                            "cost_inr": 2070.0,
                            "dietary_tags": "Outstanding seasonal vegan ramen bowl on menu"
                        },
                        "afternoon": {
                            "time": "14:30 - 17:30",
                            "title": "Cat Street Boutiques & Miyashita Park Rooftop",
                            "category": "Leisure / Immersion",
                            "description": "Wander trendsetting indie boutiques along Cat Street connecting Harajuku to Shibuya, ending with matcha soft-serve on Miyashita Park's elevated lawns.",
                            "location_name": "Miyashita Park & Cat Street",
                            "lat": 35.6622,
                            "lng": 139.7020,
                            "cost_local": 4000,
                            "cost_usd": 28.0,
                            "cost_inr": 2420.0,
                            "pro_tip": "Great vintage fashion and local Japanese sneaker concept stores."
                        },
                        "evening": {
                            "time": "18:30 - 21:30",
                            "title": "Shibuya Sky Observation & Nonbei Yokocho Izakaya",
                            "category": "Dining & Nightlife",
                            "description": "Stand atop Shibuya Sky 360-degree open-air glass deck overlooking the famous Scramble Crossing, then enjoy yakitori skewers in vintage lantern alley.",
                            "location_name": "Shibuya Sky & Nonbei Yokocho",
                            "lat": 35.6580,
                            "lng": 139.7016,
                            "cost_local": 19500,
                            "cost_usd": 130.0,
                            "cost_inr": 11220.0,
                            "pro_tip": "Lock coats and bags in lockers before stepping onto the Shibuya Sky roof."
                        }
                    }
                },
                {
                    "day_number": 3,
                    "day_theme": "Digital Art, Waterfront & Odaiba",
                    "cluster_neighborhood": "Toyosu & Odaiba Bay Cluster",
                    "transit_fatigue_score": "Low (Yurikamone Monorail scenic transit)",
                    "day_total_usd": 195.0,
                    "day_total_inr": 16850.0,
                    "slots": {
                        "morning": {
                            "time": "09:30 - 12:30",
                            "title": "teamLab Planets Tokyo Immersive Sensory Art",
                            "category": "Sightseeing / Culture",
                            "description": "Wade through knee-deep water, walk through infinite crystal mirrors, and float among virtual floating orchids in this world-renowned digital museum.",
                            "location_name": "teamLab Planets, Toyosu",
                            "lat": 35.6493,
                            "lng": 139.7904,
                            "cost_local": 8000,
                            "cost_usd": 55.0,
                            "cost_inr": 4750.0,
                            "pro_tip": "Wear pants that easily roll above the knees."
                        },
                        "lunch": {
                            "time": "13:00 - 14:15",
                            "title": "Toyosu Fish Market Senkyaku Banrai Dining",
                            "category": "Dining / Food Experience",
                            "cuisine": "Ultra-fresh Edomae Sushi & Seafood Bowls",
                            "description": "Sample melt-in-your-mouth bluefin Otoro sushi and grilled scallops freshly landed from Tokyo Bay.",
                            "location_name": "Senkyaku Banrai, Toyosu",
                            "lat": 35.6468,
                            "lng": 139.7852,
                            "cost_local": 6500,
                            "cost_usd": 45.0,
                            "cost_inr": 3890.0,
                            "dietary_tags": "Fish, shellfish and tamago specialties"
                        },
                        "afternoon": {
                            "time": "14:45 - 17:30",
                            "title": "Odaiba Seaside Promenade & Life-Sized Unicorn Gundam",
                            "category": "Leisure / Immersion",
                            "description": "Watch the transforming Unicorn Gundam statue, explore Aqua City waterfront, and snap photos of the mini Statue of Liberty framed against Rainbow Bridge.",
                            "location_name": "DiverCity Tokyo & Seaside Park",
                            "lat": 35.6247,
                            "lng": 139.7755,
                            "cost_local": 3000,
                            "cost_usd": 20.0,
                            "cost_inr": 1730.0,
                            "pro_tip": "Gundam transformation show runs every hour on the hour."
                        },
                        "evening": {
                            "time": "18:00 - 21:00",
                            "title": "Tokyo Bay Himiko Water Bus Cruise & Ginza Dinner",
                            "category": "Dining & Nightlife",
                            "description": "Board the futuristic Leiji Matsumoto-designed boat to Hinode pier, then dine on wagyu beef in glamorous Ginza.",
                            "location_name": "Ginza Shopping & Dining District",
                            "lat": 35.6719,
                            "lng": 139.7650,
                            "cost_local": 11500,
                            "cost_usd": 75.0,
                            "cost_inr": 6480.0,
                            "pro_tip": "Window-shopping flagship architect-designed boutique buildings in Ginza is stunning by night."
                        }
                    }
                },
                {
                    "day_number": 4,
                    "day_theme": "Imperial Elegance & Roppongi Panorama",
                    "cluster_neighborhood": "Chiyoda & Roppongi Central Cluster",
                    "transit_fatigue_score": "Moderate (Short direct subway links)",
                    "day_total_usd": 190.0,
                    "day_total_inr": 16400.0,
                    "slots": {
                        "morning": {
                            "time": "09:00 - 11:30",
                            "title": "Tokyo Imperial Palace East Gardens & Nijubashi Bridge",
                            "category": "Sightseeing / Culture",
                            "description": "Stroll ancient stone castle foundation moats, meticulously manicured bonsai trees, and the iconic Nijubashi double bridge.",
                            "location_name": "Imperial Palace, Chiyoda",
                            "lat": 35.6852,
                            "lng": 139.7528,
                            "cost_local": 1500,
                            "cost_usd": 10.0,
                            "cost_inr": 860.0,
                            "pro_tip": "East Gardens are closed Mondays and Fridays."
                        },
                        "lunch": {
                            "time": "12:00 - 13:30",
                            "title": "Marunouchi Brick Square Terrace Bistro",
                            "category": "Dining / Food Experience",
                            "cuisine": "Franco-Japanese Bistro & Patisserie",
                            "description": "Enjoy a garden patio lunch with freshly baked baguettes, seasonal salads, and artisan gateaux.",
                            "location_name": "Marunouchi Brick Square",
                            "lat": 35.6789,
                            "lng": 139.7634,
                            "cost_local": 5000,
                            "cost_usd": 35.0,
                            "cost_inr": 3020.0,
                            "dietary_tags": "Vegetarian quiche and garden salads available"
                        },
                        "afternoon": {
                            "time": "14:00 - 17:00",
                            "title": "Mori Art Museum & Roppongi Hills Architecture",
                            "category": "Leisure / Immersion",
                            "description": "Discover contemporary global exhibitions on the 53rd floor of Roppongi Hills Mori Tower and pose with Louise Bourgeois' giant Maman spider sculpture.",
                            "location_name": "Mori Art Museum, Roppongi",
                            "lat": 35.6605,
                            "lng": 139.7292,
                            "cost_local": 4500,
                            "cost_usd": 30.0,
                            "cost_inr": 2600.0,
                            "pro_tip": "Museum ticket includes admission to the 52F Tokyo City View indoor observation deck."
                        },
                        "evening": {
                            "time": "18:00 - 21:30",
                            "title": "Tokyo Tower Twilight Illuminations & Farewell Kaiseki",
                            "category": "Dining & Nightlife",
                            "description": "Gaze up at Tokyo Tower glowing in warm orange lights from Shiba Park, followed by a celebratory multi-course seasonal Japanese kaiseki dinner.",
                            "location_name": "Shiba Park & Tokyo Tower",
                            "lat": 35.6586,
                            "lng": 139.7454,
                            "cost_local": 17500,
                            "cost_usd": 115.0,
                            "cost_inr": 9920.0,
                            "pro_tip": "Prince Park Tower hotel basement lawn provides the most postcard-perfect angle of Tokyo Tower."
                        }
                    }
                }
            ]
        }
    }


def load_all_trips() -> dict:
    """Loads all saved trips from simulated storage file."""
    if not os.path.exists(STORAGE_FILE):
        starter = _get_starter_trips()
        save_all_trips(starter)
        return starter
    
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return _get_starter_trips()
            return data
    except Exception:
        return _get_starter_trips()


def save_all_trips(trips_dict: dict) -> bool:
    """Persists all trips to JSON file."""
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(trips_dict, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving trips: {e}")
        return False


def save_trip(trip_data: dict) -> str:
    """Saves or updates a trip in storage. Returns trip_id."""
    trips = load_all_trips()
    trip_id = trip_data.get("id")
    if not trip_id:
        trip_id = f"trip_{uuid.uuid4().hex[:8]}"
        trip_data["id"] = trip_id

    if "created_at" not in trip_data:
        trip_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    trips[trip_id] = trip_data
    save_all_trips(trips)
    return trip_id


def delete_trip(trip_id: str) -> bool:
    """Deletes a trip from storage by ID."""
    trips = load_all_trips()
    if trip_id in trips:
        del trips[trip_id]
        return save_all_trips(trips)
    return False


def get_trip(trip_id: str) -> dict:
    """Retrieves a single trip by ID."""
    trips = load_all_trips()
    return trips.get(trip_id)
