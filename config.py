"""
Configuration and constants for the Personalized Travel Itinerary Planner.
Skill Wallet Capstone Project 4.
"""

import os

# Safely load local .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def get_secret(key: str, default: str = "") -> str:
    """
    Safely retrieves a configuration key or API secret across deployment environments:
    1. Checks Streamlit Secrets (st.secrets) for Streamlit Community Cloud.
    2. Checks OS environment variables (e.g. loaded via local .env file).
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val).strip()
    except Exception:
        pass

    val = os.getenv(key)
    if val:
        return str(val).strip()
    return default


APP_TITLE = "RoamCraft AI"
APP_SUBTITLE = "Personalized Travel Itinerary Planner"
APP_CAPTION = "Skill Wallet Capstone Project 4 • Senior SaaS Travel Platform"

# Currency conversion baselines (USD to target)
EXCHANGE_RATES = {
    "USD": 1.0,
    "INR": 86.5,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 152.0,
    "THB": 35.0,
    "AED": 3.67,
    "AUD": 1.55,
    "SGD": 1.34,
    "IDR": 15800.0,
    "CAD": 1.39,
    "CHF": 0.88,
}

# Currency Symbols
CURRENCY_SYMBOLS = {
    "USD": "$",
    "INR": "₹",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "THB": "฿",
    "AED": "AED ",
    "AUD": "A$",
    "SGD": "S$",
    "IDR": "Rp ",
    "CAD": "C$",
    "CHF": "CHF ",
}

# Vibe choices for open-ended travel mood
TRAVEL_VIBES = [
    "🏖️ Beach & Coastal Escape",
    "⛰️ Mountain & Alpine Adventure",
    "🏛️ Cultural, Historic & Heritage",
    "🌆 Urban Metropolis & Vibrant City",
    "🌿 Tropical Eco-Retreat & Nature",
    "🍷 Culinary, Foodie & Wine Odyssey",
    "✨ Spiritual, Wellness & Slow Travel",
]

# Budget tiers
BUDGET_LEVELS = [
    "Budget (Backpacker / Value Stays)",
    "Moderate (Comfortable Boutique / 3-4★)",
    "Luxury (High-end Resorts / 5★)",
]

# Travel party configurations
TRAVEL_PARTIES = [
    "Solo Explorer",
    "Romantic Couple",
    "Family with Kids",
    "Group of Friends",
]

# Travel paces
TRAVEL_PACES = [
    "Relaxed (1-2 key activities/day + ample leisure)",
    "Moderate (Balanced exploration & cafe breaks)",
    "Fast-Paced (Maximum landmarks & packed days)",
]

# Popular interests
TRAVEL_INTERESTS = [
    "Street Food & Local Markets",
    "Fine Dining & Rooftop Bars",
    "Art Galleries & Historic Museums",
    "Iconic Landmarks & Architecture",
    "Hiking & Scenic Viewpoints",
    "Beaches & Water Sports",
    "Nightlife & Live Music",
    "Spas & Wellness Retreats",
    "Boutique Shopping & Crafts",
    "Photography & Instagram Spots",
]

# Dietary and special preferences
DIETARY_PREFERENCES = [
    "None / Flexible",
    "Vegetarian",
    "Vegan",
    "Halal",
    "Gluten-Free",
    "Pescatarian",
    "Kid-Friendly Options",
]

# Curated fallback destination matrix for Smart Destination Recommender
DESTINATION_CATALOG = [
    {
        "city": "Kyoto",
        "country": "Japan",
        "vibe": "🏛️ Cultural, Historic & Heritage",
        "budget_level": "Moderate (Comfortable Boutique / 3-4★)",
        "weather_season": "Spring (Mar-May) & Autumn (Sep-Nov)",
        "highlight_tags": ["UNESCO Heritage", "Bamboo Groves", "Matcha Cafes", "Zen Temples"],
        "avg_daily_usd": 125,
        "avg_daily_inr": 10800,
        "signature_experiences": [
            "Dawn walk through thousands of scarlet Torii gates at Fushimi Inari-taisha",
            "Serene bamboo path and traditional tea ceremonies in Arashiyama",
            "Evening geisha quarter walk through lantern-lit Gion alleys"
        ],
        "transit_style": "High-efficiency rail & picturesque walking loops",
        "currency": "JPY",
        "center_coords": [35.0116, 135.7681]
    },
    {
        "city": "Amalfi Coast & Positano",
        "country": "Italy",
        "vibe": "🏖️ Beach & Coastal Escape",
        "budget_level": "Luxury (High-end Resorts / 5★)",
        "weather_season": "Late Spring to Early Autumn (May-Oct)",
        "highlight_tags": ["Cliffside Vistas", "Limoncello Tastings", "Private Boat Charters", "Mediterranean Cuisine"],
        "avg_daily_usd": 310,
        "avg_daily_inr": 26800,
        "signature_experiences": [
            "Private gozzo boat cruise along hidden sea grottos towards Capri",
            "Sunset aperitivo overlooking Positano's pastel cascades",
            "Hiking the breathtaking Path of the Gods (Sentiero degli Dei)"
        ],
        "transit_style": "Ferry hops, scenic coastal shuttles & cliffside stairways",
        "currency": "EUR",
        "center_coords": [40.6281, 14.4850]
    },
    {
        "city": "Da Nang & Hoi An",
        "country": "Vietnam",
        "vibe": "🏖️ Beach & Coastal Escape",
        "budget_level": "Budget (Backpacker / Value Stays)",
        "weather_season": "Dry Season (Feb-Aug)",
        "highlight_tags": ["Lantern Festival", "White Sand Beaches", "Street Food Paradise", "Ancient Town"],
        "avg_daily_usd": 48,
        "avg_daily_inr": 4150,
        "signature_experiences": [
            "Evening lantern boat ride along the Thu Bon River in UNESCO Hoi An",
            "Sunrise walk across the Golden Hands Bridge in Ba Na Hills",
            "Bicycle tour through emerald rice paddies and Tra Que herb village"
        ],
        "transit_style": "Affordable ride-hailing (Grab), cycling & coastal walks",
        "currency": "USD",
        "center_coords": [15.8801, 108.3380]
    },
    {
        "city": "Banff & Lake Louise",
        "country": "Canada",
        "vibe": "⛰️ Mountain & Alpine Adventure",
        "budget_level": "Moderate (Comfortable Boutique / 3-4★)",
        "weather_season": "Summer (Jun-Aug) or Winter Ski (Dec-Mar)",
        "highlight_tags": ["Turquoise Glacial Lakes", "Rocky Mountain Trails", "Wildlife Spotting", "Hot Springs"],
        "avg_daily_usd": 175,
        "avg_daily_inr": 15100,
        "signature_experiences": [
            "Canoeing on the iridescent turquoise waters of Lake Louise",
            "Driving the breathtaking Icefields Parkway past ancient glaciers",
            "Soaking in mineral-rich Banff Upper Hot Springs surrounded by snowpeaks"
        ],
        "transit_style": "Scenic park shuttles & rental vehicle loops",
        "currency": "CAD",
        "center_coords": [51.1784, -115.5708]
    },
    {
        "city": "Lisbon",
        "country": "Portugal",
        "vibe": "🌆 Urban Metropolis & Vibrant City",
        "budget_level": "Moderate (Comfortable Boutique / 3-4★)",
        "weather_season": "Year-round (Best: Apr-Jun & Sep-Oct)",
        "highlight_tags": ["Historic Tram 28", "Pastel de Nata", "Fado Nights", "Miradouros Viewpoints"],
        "avg_daily_usd": 110,
        "avg_daily_inr": 9500,
        "signature_experiences": [
            "Wandering the steep cobblestone alleys of Alfama listening to soul-stirring Fado",
            "Tasting warm Pasteis de Belem straight from the 1837 bakery",
            "Sunset drinks at Miradouro de Santa Catarina overlooking the 25 de Abril Bridge"
        ],
        "transit_style": "Iconic vintage trams, funiculars and pedestrian promenades",
        "currency": "EUR",
        "center_coords": [38.7223, -9.1393]
    },
    {
        "city": "Ubud & Canggu",
        "country": "Indonesia",
        "vibe": "🌿 Tropical Eco-Retreat & Nature",
        "budget_level": "Budget (Backpacker / Value Stays)",
        "weather_season": "Dry Season (Apr-Oct)",
        "highlight_tags": ["Jungle Spas", "Tegalalang Rice Terraces", "Artisan Cafes", "Sunset Surfing"],
        "avg_daily_usd": 55,
        "avg_daily_inr": 4750,
        "signature_experiences": [
            "Sunrise yoga overlooking the lush Campuhan Ridge and jungle canopy",
            "Tasting artisan single-origin coffee amidst cascading rice terraces",
            "Traditional Balinese flower bath spa ritual and sound healing"
        ],
        "transit_style": "Local scooters, private driver day hires & jungle trail walks",
        "currency": "IDR",
        "center_coords": [-8.5069, 115.2625]
    },
    {
        "city": "San Sebastian & Basque Coast",
        "country": "Spain",
        "vibe": "🍷 Culinary, Foodie & Wine Odyssey",
        "budget_level": "Moderate (Comfortable Boutique / 3-4★)",
        "weather_season": "May to October",
        "highlight_tags": ["Pintxos Crawl", "Michelin Stars", "La Concha Bay", "Txakoli Vineyards"],
        "avg_daily_usd": 165,
        "avg_daily_inr": 14200,
        "signature_experiences": [
            "Hopping lively Parte Vieja bars for exquisite sea urchin and beef cheek pintxos",
            "Strolling the perfect golden crescent of La Concha beach at sunset",
            "Visiting rolling hillside Txakoli vineyards overlooking the dramatic Cantabrian Sea"
        ],
        "transit_style": "Compact walking old town & picturesque coastal funiculars",
        "currency": "EUR",
        "center_coords": [43.3183, -1.9812]
    }
]

# Emergency template presets
DEFAULT_EMERGENCY_INFO = {
    "Universal Emergency Hotline": "112 (Europe / International standard) or 911 (Americas) or 110/119 (Asia)",
    "Medical & Ambulance": "Check local guide & carry digital copy of Travel Medical Insurance Policy",
    "Tourist Police Helpline": "Available in most tourist hubs (Dial 1155 in SE Asia, 060 in Spain, 100 in India)",
    "Embassy Protocol": "Register with your home country's overseas citizen registration (e.g., STEP for USA, MADAD for India)",
}
