import os
import sys
import json
import datetime
import bcrypt

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.common.database import SessionLocal, engine, Base
from services.common.models import (
    UserModel, ProductModel, CouponModel, ReviewModel, OrderModel, OrderItemModel, ShipmentModel
)

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def seed():
    print("Initializing Database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data if re-seeding
    db.query(ReviewModel).delete()
    db.query(ShipmentModel).delete()
    db.query(OrderItemModel).delete()
    db.query(OrderModel).delete()
    db.query(CouponModel).delete()
    db.query(ProductModel).delete()
    db.query(UserModel).delete()
    db.commit()

    print("Seeding Users...")
    users = [
        UserModel(
            email="admin@ecommerce.com",
            password_hash=hash_pw("admin123"),
            full_name="Alex Mercer (Admin)",
            role="admin",
            phone="+919876543201",
            address_street="Tech Corridor 4, Whitefield",
            address_city="Bengaluru",
            address_state="Karnataka",
            address_zip="560066"
        ),
        UserModel(
            email="john.doe@example.com",
            password_hash=hash_pw("customer123"),
            full_name="John Doe",
            role="customer",
            phone="+919876543210",
            address_street="Flat 402, Green Glen Layout, Bellandur",
            address_city="Bengaluru",
            address_state="Karnataka",
            address_zip="560103"
        ),
        UserModel(
            email="support@ecommerce.com",
            password_hash=hash_pw("support123"),
            full_name="Priya Sharma (Support Lead)",
            role="support_agent",
            phone="+919876543202",
            address_street="Cyber City Tower C",
            address_city="Gurugram",
            address_state="Haryana",
            address_zip="122002"
        ),
        UserModel(
            email="sarah.connor@example.com",
            password_hash=hash_pw("customer123"),
            full_name="Sarah Connor",
            role="customer",
            phone="+919876543222",
            address_street="14 MG Road, Indiranagar",
            address_city="Bengaluru",
            address_state="Karnataka",
            address_zip="560038"
        )
    ]
    db.add_all(users)
    db.commit()

    print("Seeding Promotional Coupons...")
    coupons = [
        CouponModel(code="SAVE10", discount_type="PERCENTAGE", discount_value=10.0, min_order_value=500.0, max_discount=1000.0, active=True),
        CouponModel(code="SUPER50", discount_type="PERCENTAGE", discount_value=50.0, min_order_value=1500.0, max_discount=1500.0, active=True),
        CouponModel(code="FREESHIP", discount_type="FIXED", discount_value=49.0, min_order_value=0.0, max_discount=49.0, active=True),
        CouponModel(code="FESTIVE25", discount_type="PERCENTAGE", discount_value=25.0, min_order_value=2000.0, max_discount=3000.0, active=True),
        CouponModel(code="FLAT500", discount_type="FIXED", discount_value=500.0, min_order_value=2500.0, max_discount=500.0, active=True),
    ]
    db.add_all(coupons)
    db.commit()

    print("Generating 100+ Products across 20 Categories...")

    # Product templates across 20 categories
    category_templates = {
        "Smartphones": [
            ("Apple iPhone 15 Pro Max (256GB, Natural Titanium)", "apple-iphone-15-pro-max", "Apple", 149900.0, 8.0, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80", {"Display": "6.7 Super Retina XDR", "Chip": "A17 Pro", "Camera": "48MP Triple", "Battery": "4422 mAh"}),
            ("Samsung Galaxy S24 Ultra 5G (512GB, Titanium Gray)", "samsung-galaxy-s24-ultra", "Samsung", 139999.0, 10.0, "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600&auto=format&fit=crop&q=80", {"Display": "6.8 Dynamic AMOLED 2X", "Processor": "Snapdragon 8 Gen 3", "Camera": "200MP Quad", "S-Pen": "Included"}),
            ("Google Pixel 8 Pro (128GB, Obsidian)", "google-pixel-8-pro", "Google", 106999.0, 12.0, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80", {"Display": "6.7 LTPO OLED", "Chip": "Tensor G3", "Camera": "50MP Triple", "OS": "Android 14"}),
            ("OnePlus 12 5G (256GB, Silky Black)", "oneplus-12-5g", "OnePlus", 64999.0, 15.0, "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80", {"Display": "6.82 2K 120Hz", "Charging": "100W SUPERVOOC", "Camera": "Hasselblad 50MP", "RAM": "16GB"}),
            ("Xiaomi 14 Ultra (512GB, White Ceramic)", "xiaomi-14-ultra", "Xiaomi", 99999.0, 10.0, "https://images.unsplash.com/photo-1511707171634-5f897ff02560?w=600&auto=format&fit=crop&q=80", {"Lens": "Leica Quad Camera", "Sensor": "1-inch Sony LYT-900", "Display": "120Hz AMOLED", "Battery": "5000 mAh"}),
            ("Nothing Phone (2) (256GB, Dark Grey)", "nothing-phone-2", "Nothing", 39999.0, 20.0, "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=80", {"Interface": "Glyph Interface", "Processor": "Snapdragon 8+ Gen 1", "OS": "Nothing OS 2.5", "Display": "OLED 120Hz"})
        ],
        "Laptops": [
            ("Apple MacBook Pro 16-inch (M3 Max, 36GB RAM, 1TB SSD)", "macbook-pro-16-m3-max", "Apple", 349900.0, 5.0, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80", {"CPU": "M3 Max 14-core", "RAM": "36GB Unified", "Display": "Liquid Retina XDR", "Battery": "22 Hours"}),
            ("Dell XPS 15 9530 (Intel Core i9, 32GB, RTX 4070)", "dell-xps-15-9530", "Dell", 239990.0, 8.0, "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80", {"Display": "15.6 3.5K OLED Touch", "GPU": "NVIDIA RTX 4070 8GB", "Storage": "1TB NVMe SSD", "Weight": "1.92 kg"}),
            ("Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB)", "lenovo-thinkpad-x1-carbon-gen-11", "Lenovo", 158900.0, 15.0, "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80", {"Chassis": "Carbon Fiber", "Display": "14 WUXGA IPS", "Keyboard": "Spill Resistant TrackPoint", "Security": "dTPM 2.0"}),
            ("ASUS ROG Zephyrus G16 (Intel Core Ultra 9, RTX 4080)", "asus-rog-zephyrus-g16", "ASUS", 269990.0, 10.0, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80", {"Display": "16 OLED 240Hz", "Cooling": "Vapor Chamber", "GPU": "RTX 4080 12GB", "Audio": "6-Speaker Sound System"}),
            ("HP Spectre x360 2-in-1 14 (Intel Core Ultra 7)", "hp-spectre-x360-14", "HP", 144990.0, 12.0, "https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=600&auto=format&fit=crop&q=80", {"Form Factor": "Convertible 360", "Screen": "2.8K OLED Touch", "Stylus": "HP Rechargeable MPP 2.0 Tilt Pen", "Camera": "9MP IR WebCam"})
        ],
        "Audio & Headphones": [
            ("Sony WH-1000XM5 Wireless Noise Cancelling Headphones", "sony-wh-1000xm5", "Sony", 29990.0, 18.0, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80", {"ANC": "Industry Leading 8 Mics", "Battery": "30 Hours", "Codec": "LDAC, AAC, SBC", "Weight": "250g"}),
            ("Bose QuietComfort Ultra Wireless Noise Cancelling Headphones", "bose-quietcomfort-ultra", "Bose", 35900.0, 10.0, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80", {"Audio": "Immersive Audio Spatialized", "Modes": "Quiet, Aware, Immersion", "Battery": "24 Hours", "Bluetooth": "5.3"}),
            ("Apple AirPods Pro (2nd Generation with USB-C)", "apple-airpods-pro-2", "Apple", 24900.0, 12.0, "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&auto=format&fit=crop&q=80", {"Chip": "Apple H2", "Audio": "Adaptive Audio & Transparency", "Case": "MagSafe USB-C with Speaker", "Resistance": "IP54 Dust & Sweat"}),
            ("Sennheiser Momentum 4 Wireless Audiophile Headphones", "sennheiser-momentum-4", "Sennheiser", 27990.0, 20.0, "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&auto=format&fit=crop&q=80", {"Driver": "42mm Transducer", "Battery": "60 Hours", "ANC": "Adaptive", "App": "Smart Control EQ"}),
            ("Marshall Stanmore III Bluetooth Home Speaker", "marshall-stanmore-iii", "Marshall", 38999.0, 8.0, "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80", {"Design": "Vintage Vinyl Texture", "Power": "80W RMS Class D", "Connectivity": "Bluetooth 5.2, AUX, RCA", "Sound": "Wide Stereo Soundstage"})
        ],
        "Smart Watches": [
            ("Apple Watch Ultra 2 (GPS + Cellular, 49mm Titanium)", "apple-watch-ultra-2", "Apple", 89900.0, 7.0, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80", {"Case": "Aerospace Titanium", "Display": "3000 nits Always-On", "Depth": "100m Water Resistant", "Battery": "Up to 72 Hours in Low Power"}),
            ("Samsung Galaxy Watch6 Classic (47mm LTE, Black)", "samsung-galaxy-watch6-classic", "Samsung", 36999.0, 15.0, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80", {"Bezel": "Rotating Physical Bezel", "Health": "ECG, Blood Pressure, BIA", "Sleep": "Sleep Coaching", "Display": "Sapphire Crystal AMOLED"}),
            ("Garmin Fenix 7 Pro Solar Multisport GPS Smartwatch", "garmin-fenix-7-pro-solar", "Garmin", 84990.0, 10.0, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop&q=80", {"Charging": "Power Glass Solar Charging", "Maps": "TopoActive Multi-Continent", "Flashlight": "Built-in LED Flashlight", "Sensors": "Multi-Band GNSS with SatIQ"}),
            ("Fitbit Charge 6 Advanced Fitness & Health Tracker", "fitbit-charge-6", "Fitbit", 14999.0, 20.0, "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=600&auto=format&fit=crop&q=80", {"Google": "Google Maps & Wallet Built-in", "Heart": "ECG App & Irregular Rhythm", "GPS": "Built-in GPS", "Battery": "7 Days"})
        ],
        "Cameras & Photography": [
            ("Sony Alpha 7 IV Full-Frame Mirrorless Camera Body", "sony-alpha-7-iv", "Sony", 214990.0, 10.0, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80", {"Sensor": "33MP Exmor R CMOS", "Video": "4K 60p 10-bit 4:2:2", "AF": "759 Phase Detection Points", "Stabilization": "5.5-step 5-axis IBIS"}),
            ("Canon EOS R6 Mark II Mirrorless Camera with 24-105mm Lens", "canon-eos-r6-mark-ii", "Canon", 249995.0, 8.0, "https://images.unsplash.com/photo-1502982720700-bfff97f2ecac?w=600&auto=format&fit=crop&q=80", {"Sensor": "24.2MP CMOS", "Speed": "40 fps Electronic Shutter", "AF": "Dual Pixel CMOS AF II", "Video": "6K Over-sampled 4K 60p"}),
            ("Fujifilm X-T5 Mirrorless Digital Camera (Silver)", "fujifilm-x-t5-silver", "Fujifilm", 169999.0, 6.0, "https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?w=600&auto=format&fit=crop&q=80", {"Sensor": "40.2MP X-Trans CMOS 5 HR", "Dials": "Classic Exposure Dials", "Simulation": "19 Film Simulation Modes", "IBIS": "Up to 7.0 Stops"}),
            ("DJI Mini 4 Pro Drone with RC 2 Controller", "dji-mini-4-pro", "DJI", 112000.0, 10.0, "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=600&auto=format&fit=crop&q=80", {"Weight": "Under 249g Ultralight", "Obstacle": "Omnidirectional Active Sensing", "Video": "4K/60fps HDR True Vertical", "Range": "20 km FHD Transmission"}),
            ("GoPro HERO12 Black Waterproof Action Camera", "gopro-hero12-black", "GoPro", 37990.0, 15.0, "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=600&auto=format&fit=crop&q=80", {"Video": "5.3K 60fps & 4K 120fps", "Stabilization": "HyperSmooth 6.0", "Waterproof": "33ft (10m) Rugged", "Audio": "Bluetooth Audio Support"})
        ],
        "Televisions & Home Theater": [
            ("LG 65-inch OLED evo G3 4K Smart TV", "lg-65-oled-g3", "LG", 249990.0, 15.0, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&auto=format&fit=crop&q=80", {"Panel": "OLED evo Brightness Booster Max", "Processor": "a9 AI Processor 4K Gen6", "Gaming": "0.1ms Response, 4x HDMI 2.1", "Mount": "One Wall Design Zero Gap"}),
            ("Sony Bravia XR 55-inch 4K QD-OLED Google TV", "sony-bravia-xr-55-qd-oled", "Sony", 189990.0, 10.0, "https://images.unsplash.com/photo-1461151304267-38535e780c79?w=600&auto=format&fit=crop&q=80", {"Screen": "Cognitive Processor XR", "Sound": "Acoustic Surface Audio+", "Colors": "XR Triluminos Max", "OS": "Google TV with Hands-Free Mic"}),
            ("Samsung 75-inch The Frame QLED 4K Smart TV", "samsung-75-the-frame", "Samsung", 199990.0, 20.0, "https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=600&auto=format&fit=crop&q=80", {"Finish": "Matte Display Anti-Reflection", "Art": "Art Mode with Curated Gallery", "Bezel": "Customizable Magnetic Bezels", "Cable": "One Invisible Connection"}),
            ("Sonos Arc Premium Smart Soundbar with Dolby Atmos", "sonos-arc-soundbar", "Sonos", 89999.0, 8.0, "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80", {"Audio": "11 High-Performance Drivers", "Atmos": "3D Dolby Atmos Spatial Audio", "Voice": "Apple AirPlay 2, Alexa", "Tuning": "Trueplay Room Tuning"})
        ],
        "Computer Accessories": [
            ("Logitech MX Master 3S Wireless Performance Mouse", "logitech-mx-master-3s", "Logitech", 9495.0, 15.0, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80", {"Sensor": "8K DPI Any-Surface Tracking", "Clicks": "Quiet Clicks 90% Noise Reduction", "Scroll": "MagSpeed Electromagnetic 1000 lines/sec", "Charging": "USB-C Quick Charge 70 Days"}),
            ("Keychron Q1 Pro Wireless Custom Mechanical Keyboard", "keychron-q1-pro", "Keychron", 18999.0, 10.0, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80", {"Body": "CNC Aluminum Double-Gasket", "Switches": "Hot-swappable Gateron Jupiter", "Keycaps": "KSA Double-Shot PBT", "Connectivity": "Bluetooth 5.1 & Type-C"}),
            ("Samsung T7 Shield 2TB Portable SSD (IP65 Rugged)", "samsung-t7-shield-2tb", "Samsung", 16499.0, 25.0, "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80", {"Speed": "Read up to 1,050 MB/s", "Durability": "Drop Resistant up to 3m", "Security": "AES 256-bit Hardware Encryption", "Interface": "USB 3.2 Gen 2"}),
            ("Dell UltraSharp 32-inch 4K Video Conferencing Monitor", "dell-ultrasharp-32-4k-u3223qz", "Dell", 89990.0, 12.0, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80", {"Panel": "IPS Black Technology 2000:1 Contrast", "Camera": "Built-in 4K Sony Starvis HDR Webcam", "Hub": "USB-C Hub with 90W Power Delivery", "Audio": "Echo Cancelling Dual Microphones"}),
            ("Anker 737 Power Bank 24,000mAh (PowerCore 24K 140W)", "anker-737-power-bank-140w", "Anker", 12999.0, 18.0, "https://images.unsplash.com/photo-1609592807963-3158b4b7c126?w=600&auto=format&fit=crop&q=80", {"Output": "140W Ultra-Fast Two-Way Charging", "Display": "Smart Digital Display Screen", "Ports": "2x USB-C + 1x USB-A", "Safety": "ActiveShield 2.0 Temperature Monitor"})
        ],
        "Gaming Consoles & Gear": [
            ("Sony PlayStation 5 Slim Console (1TB Disc Edition)", "sony-ps5-slim-disc", "Sony", 54990.0, 5.0, "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop&q=80", {"Storage": "1TB Custom High-Speed SSD", "Controller": "DualSense Haptic Feedback & Adaptive Triggers", "Graphics": "Ray Tracing up to 120fps 4K", "Audio": "Tempest 3D AudioTech"}),
            ("Microsoft Xbox Series X (1TB Gaming Console)", "microsoft-xbox-series-x", "Microsoft", 52990.0, 8.0, "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=600&auto=format&fit=crop&q=80", {"Performance": "12 Teraflops Processing Power", "Feature": "Quick Resume Multiple Games", "Service": "Xbox Game Pass Compatible", "Target": "True 4K Gaming up to 120fps"}),
            ("Nintendo Switch OLED Model with White Joy-Con", "nintendo-switch-oled-white", "Nintendo", 31999.0, 12.0, "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&auto=format&fit=crop&q=80", {"Screen": "7-inch Vivid OLED Screen", "Stand": "Wide Adjustable Tabletop Stand", "Dock": "Wired LAN Port Built-in", "Storage": "64GB Internal Storage"}),
            ("SteelSeries Arctis Nova Pro Wireless Gaming Headset", "steelseries-arctis-nova-pro", "SteelSeries", 36999.0, 15.0, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80", {"Drivers": "Nova Pro Acoustic System Hi-Res", "Battery": "Infinity Power System Dual Swappable Batteries", "ANC": "Active Noise Cancellation 4-Mic", "Multi-System": "Connect PC & Console Simultaneously"})
        ],
        "Home Appliances": [
            ("Dyson V15 Detect Absolute Cordless Vacuum Cleaner", "dyson-v15-detect-absolute", "Dyson", 62900.0, 10.0, "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600&auto=format&fit=crop&q=80", {"Laser": "Fluffy Optic Laser Reveals Dust", "Suction": "230 AW Powerful Suction", "Sensor": "Piezo Sensor Counts Particles", "Filtration": "Whole-machine HEPA Filtration"}),
            ("Philips Series 5000 2-in-1 Air Purifier and Humidifier", "philips-series-5000-air-purifier", "Philips", 32995.0, 18.0, "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80", {"CADR": "330 m3/h Clean Air", "Filter": "NanoProtect HEPA 99.97%", "Humidification": "NanoCloud Hygenic Moisture", "App": "CleanHome+ Connected"}),
            ("LG 9 Kg Front Load AI Direct Drive Washing Machine", "lg-9kg-front-load-washing-machine", "LG", 46990.0, 15.0, "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=80", {"Motor": "AI DD Inverter Direct Drive", "Hygiene": "Steam+ Allergy Care", "Design": "Tempered Glass Door & Stainless Lifter", "Smart": "ThinQ Wi-Fi Remote Control"}),
            ("Daikin 1.5 Ton 5 Star Inverter Split AC (Copper, Triple Display)", "daikin-1-5-ton-5-star-ac", "Daikin", 45490.0, 12.0, "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&auto=format&fit=crop&q=80", {"Cooling": "Dew Clean Technology", "Filter": "PM 2.5 Filter", "Swing": "3D Airflow Omni-directional", "Refrigerant": "Eco-friendly R32"})
        ],
        "Kitchen Appliances": [
            ("Breville Barista Touch Espresso Machine", "breville-barista-touch", "Breville", 98990.0, 8.0, "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=600&auto=format&fit=crop&q=80", {"Interface": "Automated Touch Screen Menu", "Grinder": "Integrated Conical Burr Grinder", "Steam": "Auto MilQ Microfoam Wand", "Heat-Up": "ThermoJet 3 Second Heating"}),
            ("Instant Pot Duo Crisp 11-in-1 Electric Pressure Cooker & Air Fryer", "instant-pot-duo-crisp-11-in-1", "Instant Pot", 18999.0, 22.0, "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&auto=format&fit=crop&q=80", {"Capacity": "8 Litre Family Size", "Functions": "Pressure Cook, Air Fry, Slow Cook, Sous Vide, Bake", "Coating": "EvenCrisp Golden Crunch", "Safety": "10+ Built-in Safety Mechanisms"}),
            ("Vitamix A3500 Ascent Series Smart Blender", "vitamix-a3500-ascent-blender", "Vitamix", 74990.0, 10.0, "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80", {"Presets": "5 Automated Program Settings", "Timer": "Programmable Digital Timer", "Blades": "Laser-Cut Hardened Stainless Steel", "Warranty": "10-Year Full Warranty"}),
            ("Ninja Foodi Smart XL 6-in-1 Indoor Grill with Air Fryer", "ninja-foodi-smart-xl-grill", "Ninja", 26999.0, 16.0, "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80", {"System": "Smart Cook System Food Thermometer", "Grill": "500F Cyclonic Grilling Smoke Control", "Functions": "Air Crisp, Roast, Bake, Broil, Dehydrate", "Capacity": "XL 9x12 Grill Grate"})
        ],
        "Smart Home & Security": [
            ("Google Nest Cam Outdoor/Indoor Battery Security Camera", "google-nest-cam-battery", "Google", 19999.0, 15.0, "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&auto=format&fit=crop&q=80", {"Intelligence": "Knows People, Animals, Vehicles", "Night": "Night Vision HDR 1080p", "Power": "Rechargeable Battery or Wired", "Weather": "IP54 Weatherproof"}),
            ("Philips Hue White & Color Ambiance Starter Kit (3 Bulbs + Bridge)", "philips-hue-starter-kit", "Philips", 14999.0, 20.0, "https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=600&auto=format&fit=crop&q=80", {"Colors": "16 Million Colors & Tunable White", "Sync": "Music, Movies & PC Gaming Sync", "Hub": "Hue Bridge Zigbee Automation", "Ecosystem": "Apple HomeKit, Alexa, Google Home"}),
            ("Yale Assure Lock 2 Keyless Smart Touchscreen Lock", "yale-assure-lock-2", "Yale", 22499.0, 12.0, "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&auto=format&fit=crop&q=80", {"Access": "Fingerprint, Keypad, Apple Watch, Auto-Unlock", "Connectivity": "Wi-Fi Module Included", "DoorSense": "Door Sensor Tells if Closed", "Security": "BHMA Grade 2 Certified"}),
            ("Amazon Echo Studio High-Fidelity Smart Speaker with 3D Audio", "amazon-echo-studio", "Amazon", 22999.0, 10.0, "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80", {"Speakers": "5 Strategic Directional Speakers", "Dolby": "Dolby Atmos Spatial Audio", "Hub": "Built-in Zigbee & Matter Smart Home Hub", "Tuning": "Adapts Acoustics to Room"})
        ],
        "Furniture": [
            ("Herman Miller Aeron Ergonomic Office Chair (Graphite, Size B)", "herman-miller-aeron-chair", "Herman Miller", 134900.0, 5.0, "https://images.unsplash.com/photo-1580481077195-c3a8a37f714c?w=600&auto=format&fit=crop&q=80", {"Material": "Pellicle Breathable Mesh", "Support": "PostureFit SL Sacral Support", "Adjustments": "Fully Adjustable Arms & Tilt Limiter", "Warranty": "12-Year Official Warranty"}),
            ("Solid Teak Wood 6-Seater Dining Table Set (Walnut Finish)", "solid-teak-wood-dining-set", "Urban Living", 48999.0, 25.0, "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=600&auto=format&fit=crop&q=80", {"Wood": "100% Genuine Seasoned Teak", "Chairs": "6 Ergonomic High-Back Chairs", "Finish": "Water-Resistant Matte Polyurethane", "Table Size": "6ft x 3.5ft"}),
            ("Modern L-Shaped Sectional Fabric Sofa (Charcoal Grey)", "modern-l-shaped-sectional-sofa", "Wakefit", 36499.0, 30.0, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80", {"Frame": "Neem Solid Wood Termite Resistant", "Cushions": "High-Resilience Foam + Soft Fiber", "Fabric": "350 GSM Breathable Linen Fabric", "Seating": "Comfortable 5-6 Seater Sectional"}),
            ("Motorized Height Adjustable Electric Standing Desk (55x28 Walnut)", "motorized-standing-desk-walnut", "ErgoCraft", 24999.0, 20.0, "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=600&auto=format&fit=crop&q=80", {"Motors": "Dual Whisper-Quiet Motors", "Height": "69cm to 118cm Range", "Memory": "4 Preset Memory Keypad", "Top": "Beveled Edge Scratch-Resistant Solid Top"}),
            ("Queen Size Sheesham Wood Platform Bed with Storage", "queen-sheesham-platform-bed", "Royal Wood", 29999.0, 22.0, "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&auto=format&fit=crop&q=80", {"Material": "Solid Sheesham Rosewood", "Storage": "Hydraulic Lift-Up Large Storage", "Headboard": "Cushioned Leatherette Tufted Headboard", "Capacity": "Tested for 350 kg load"})
        ],
        "Men's Fashion": [
            ("Levi's Men's 511 Slim Fit Stretch Denim Jeans", "levis-511-slim-fit-jeans", "Levi's", 3199.0, 35.0, "https://images.unsplash.com/photo-1542272604-780c96856592?w=600&auto=format&fit=crop&q=80", {"Fit": "Slim Through Thigh & Leg", "Fabric": "99% Cotton, 1% Elastane", "Closure": "Zip Fly with Shank Button", "Care": "Machine Washable"}),
            ("Tommy Hilfiger Men's Classic Solid Pique Polo T-Shirt", "tommy-hilfiger-classic-polo", "Tommy Hilfiger", 3999.0, 25.0, "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&auto=format&fit=crop&q=80", {"Material": "100% Organic Pique Cotton", "Collar": "Ribbed Spread Collar with 2-Button Placket", "Logo": "Embroidered Flag on Chest", "Fit": "Custom Fit"}),
            ("Raymond Men's Charcoal Grey Pure Wool 2-Piece Formal Suit", "raymond-charcoal-wool-suit", "Raymond", 14999.0, 20.0, "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&auto=format&fit=crop&q=80", {"Fabric": "Super 120s Australian Merino Wool", "Blazer": "Notch Lapel, 2-Button Single Breasted", "Trousers": "Flat Front Tapered Trousers", "Occasion": "Weddings & Executive Boardrooms"}),
            ("Jack & Jones Men's Genuine Leather Biker Jacket", "jack-jones-leather-biker-jacket", "Jack & Jones", 11999.0, 40.0, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80", {"Leather": "100% Lambskin Genuine Leather", "Hardware": "Heavy-Duty Gunmetal Zippers", "Pockets": "4 Exterior + 2 Interior Pockets", "Lining": "Quilted Polyester Satin"})
        ],
        "Women's Fashion": [
            ("FabIndia Silk Chanderi Hand Embroidered Anarkali Kurta Set", "fabindia-silk-chanderi-anarkali-set", "FabIndia", 9990.0, 20.0, "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80", {"Fabric": "Pure Chanderi Silk with Cotton Lining", "Work": "Zari and Sequin Hand Embroidery", "Set Includes": "Anarkali Kurta, Churidar & Organza Dupatta", "Color": "Emerald Green"}),
            ("Zara Double-Breasted Wool Blend Long Trench Coat", "zara-wool-blend-trench-coat", "Zara", 8990.0, 15.0, "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600&auto=format&fit=crop&q=80", {"Fabric": "Structured Wool Blend", "Collar": "Lapel Collar with Storm Flap", "Belt": "Self-Tie Buckled Waist Belt", "Length": "Mid-Calf Silhouette"}),
            ("AND Women's Floral Print Pleated Midi Wrap Dress", "and-floral-pleated-midi-dress", "AND", 3499.0, 30.0, "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80", {"Silhouette": "Flattering A-Line Wrap Fit", "Neckline": "Surplice V-Neckline", "Sleeves": "Sheer Bishop Sleeves with Cuffs", "Fabric": "Georgette with Soft Crepe Lining"}),
            ("Biba Metallic Printed Tiered Festive Lehenga Choli Set", "biba-metallic-tiered-lehenga-set", "Biba", 12500.0, 25.0, "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80", {"Lehenga": "Flared Metallic Print with Drawstring Tassels", "Choli": "Sweetheart Neck Padded Blouse", "Dupatta": "Net Dupatta with Gota Patti Border", "Occasion": "Festivals & Sangeet Ceremonies"})
        ],
        "Footwear": [
            ("Nike Air Jordan 1 Retro High OG (Chicago Lost & Found)", "nike-air-jordan-1-retro-high", "Nike", 17995.0, 10.0, "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600&auto=format&fit=crop&q=80", {"Upper": "Premium Aged Leather", "Cushioning": "Encapsulated Air-Sole Unit", "Sole": "Durable Solid Rubber Cupsole", "Colorway": "Varsity Red/Black/Sail"}),
            ("Adidas Ultraboost Light Running Shoes (Core Black)", "adidas-ultraboost-light-black", "Adidas", 18999.0, 25.0, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80", {"Midsole": "Light BOOST 30% Lighter", "Upper": "PRIMEKNIT+ Textile Upper", "Outsole": "Continental Better Rubber Grip", "Energy": "Linear Energy Push System"}),
            ("Clarks Men's Tilden Walk Leather Derby Formal Shoes", "clarks-tilden-walk-leather-derby", "Clarks", 6999.0, 30.0, "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&auto=format&fit=crop&q=80", {"Leather": "Full Grain Polished Leather Upper", "Footbed": "Ortholite Cushion Plus Soft Technology", "Sole": "Shock-Absorbing TPR Sole", "Toe": "Refined Square Apron Toe"}),
            ("Puma RS-X Efekt Reflective Lifestyle Sneakers", "puma-rs-x-efekt-reflective", "Puma", 7999.0, 35.0, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80", {"Aesthetic": "Futuristic Bulky Silhouette", "Comfort": "PU Midsole Running System Cushion", "Accents": "Reflective 3M Overlays", "Outsole": "Traction Rubber Gripper"})
        ],
        "Sports & Fitness": [
            ("Bowflex SelectTech 552 Adjustable Dumbbells (Pair)", "bowflex-selecttech-552-dumbbells", "Bowflex", 34999.0, 15.0, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80", {"Range": "Adjusts from 2.5 to 24 kg per dumbbell", "Dial": "Smooth Turn-Dial Weight Selection", "Design": "Replaces 15 Pairs of Individual Dumbbells", "Tray": "Included Heavy Duty Storage Trays"}),
            ("Lululemon The Reversible Yoga Mat 5mm (Textured)", "lululemon-reversible-yoga-mat-5mm", "Lululemon", 6800.0, 10.0, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&auto=format&fit=crop&q=80", {"Grip": "Polyurethane Top Layer Absorbs Moisture", "Base": "Natural Rubber Base for Cushioned Joints", "Antimicrobial": "Antimicrobial Additive Prevents Mildew", "Thickness": "5mm Extra Comfort"}),
            ("Decathlon Domyos T540C Foldable Smart Treadmill", "decathlon-domyos-t540c-treadmill", "Decathlon", 49999.0, 20.0, "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=600&auto=format&fit=crop&q=80", {"Speed": "Up to 16 km/h with 10% Incline", "Connectivity": "Compatible with Domyos E-Connected & Kinomap", "Deck": "47x125 cm Shock-Absorbing Running Deck", "Folding": "Hydraulic Soft-Drop Folding"}),
            ("Yonex Astrox 99 Pro Badminton Racket (Made in Japan)", "yonex-astrox-99-pro-badminton-racket", "Yonex", 16990.0, 15.0, "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600&auto=format&fit=crop&q=80", {"Balance": "Head-Heavy Power Racket", "Shaft": "Namd Graphite for Explosive Snapback", "Grommets": "Volume Cut Resin for Steeper Angle", "Weight": "4U (Avg 83g)"})
        ],
        "Books & Media": [
            ("Atomic Habits: An Easy & Proven Way to Build Good Habits", "atomic-habits-james-clear", "Penguin Random House", 699.0, 30.0, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80", {"Author": "James Clear", "Format": "Hardcover Collector's Edition", "Pages": "320 Pages", "Genre": "Self-Help / Psychology"}),
            ("The Psychology of Money: Timeless Lessons on Wealth", "the-psychology-of-money-morgan-housel", "Harriman House", 499.0, 25.0, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80", {"Author": "Morgan Housel", "Format": "Paperback", "Pages": "256 Pages", "Theme": "Behavioral Finance"}),
            ("Designing Data-Intensive Applications: The Big Ideas Behind Reliable Systems", "designing-data-intensive-applications-kleppmann", "O'Reilly Media", 1899.0, 15.0, "https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=600&auto=format&fit=crop&q=80", {"Author": "Martin Kleppmann", "Topics": "Distributed Systems, Consistency, Stream Processing", "Pages": "616 Pages", "Format": "Paperback"}),
            ("System Design Interview – An Insider's Guide (Volume 1 & 2)", "system-design-interview-alex-xu", "ByteByteGo", 2499.0, 20.0, "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&auto=format&fit=crop&q=80", {"Author": "Alex Xu", "Content": "Scalable Architecture Case Studies", "Format": "Two-Book Set Paperback", "Target": "Senior Engineers & Architects"})
        ],
        "Beauty & Personal Care": [
            ("Dyson Airwrap Multi-Styler Complete Long (Nickel/Copper)", "dyson-airwrap-multi-styler", "Dyson", 49900.0, 5.0, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80", {"Coanda": "Coanda Airflow Styles with No Extreme Heat", "Barrels": "Re-engineered Barrels Curl Both Directions", "Motor": "Dyson V9 Digital Motor", "Attachments": "6 Specialized Styling Attachments"}),
            ("Estée Lauder Advanced Night Repair Synchronized Recovery Complex (50ml)", "estee-lauder-advanced-night-repair", "Estée Lauder", 8900.0, 15.0, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&auto=format&fit=crop&q=80", {"Technology": "Chronolux Power Signal Technology", "Benefits": "Deep Hydration, Line Reduction, Radiant Firmness", "Hyaluronic": "High Concentration Hyaluronic Acid", "Skin Type": "All Skin Types"}),
            ("Oral-B iO Series 9 Electric Toothbrush with Magnetic Technology", "oral-b-io-series-9", "Oral-B", 19999.0, 25.0, "https://images.unsplash.com/photo-1559591937-e10c74f5d37c?w=600&auto=format&fit=crop&q=80", {"Drive": "Frictionless Magnetic Drive System", "Display": "Interactive Color Display Screen", "AI": "3D Teeth Tracking & AI Recognition", "Charging": "Magnetic Fast Charger 3 Hours"})
        ],
        "Health & Wellness": [
            ("Withings Body Scan Connected Health Station Smart Scale", "withings-body-scan-scale", "Withings", 39999.0, 10.0, "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&auto=format&fit=crop&q=80", {"Handle": "Retractable Handle with 4 Stainless Steel Electrodes", "Analysis": "Segmental Body Composition (Arms, Legs, Torso)", "Heart": "6-Lead ECG & Vascular Age", "Nerve": "Nerve Health Assessment Score"}),
            ("Theragun PRO Plus Multi-Therapy Percussive Massage Gun", "theragun-pro-plus-massage-gun", "Therabody", 49999.0, 12.0, "https://images.unsplash.com/photo-1519751138087-5bf79df62d5b?w=600&auto=format&fit=crop&q=80", {"Therapies": "Percussive, Near-Infrared LED, Vibration, Heat", "Amplitude": "16mm Deep Muscle Treatment", "Motor": "QuietForce Commercial Grade Motor", "Biometrics": "Built-in Heart Rate Sensor"}),
            ("Omron Complete Wireless Blood Pressure Monitor + EKG", "omron-complete-bp-ekg-monitor", "Omron", 14990.0, 15.0, "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=600&auto=format&fit=crop&q=80", {"Detection": "AFib, Tachycardia, Bradycardia & Hypertension", "App": "Omron Connect Cloud Sync", "Cuff": "Intelli Wrap Cuff 360 Accuracy", "Clinical": "FDA Cleared & Clinically Validated"})
        ],
        "Automotive & Tools": [
            ("Bosch Professional GSB 18V-50 Cordless Brushless Impact Drill Kit", "bosch-gsb-18v-50-drill-kit", "Bosch", 14999.0, 25.0, "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&auto=format&fit=crop&q=80", {"Motor": "Intelligent Brushless Motor for High Efficiency", "Torque": "50 Nm Hard Torque", "Chuck": "Robust 13mm Full Metal Chuck", "Includes": "2x 2.0Ah Li-ion Batteries + Fast Charger"}),
            ("70mai Dash Cam Omni 360-Degree AI Rotating Car Dash Camera", "70mai-dash-cam-omni-360", "70mai", 18999.0, 20.0, "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&auto=format&fit=crop&q=80", {"Rotation": "340 Swivel 360 Full View Without Blind Spots", "Night": "PureCel Plus-S HDR Superb Night Vision", "AI": "AI Motion & Collision Detection Parking Guard", "GPS": "Built-in GPS & ADAS Lane Warning"}),
            ("DeWalt ToughSystem 2.0 Mobile Rolling Storage Tool Box Tower", "dewalt-toughsystem-2-mobile-storage", "DeWalt", 22999.0, 18.0, "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop&q=80", {"Protection": "IP65 High Performance Dust & Water Seal", "Wheels": "8-inch All-Terrain Durable Wheels", "Latching": "Patented Auto-Connect Side Latches", "Capacity": "Heavy Duty 113 kg Max Load"})
        ]
    }

    # Generate additional items per category to comfortably surpass 100 products
    products_to_add = []
    product_counter = 1

    sample_reviews_text = [
        (5, "Exceptional build quality!", "Exceeded my expectations in every way. The speed and finish are unmatched. Best purchase this year."),
        (5, "Worth every single rupee", "Fast delivery by Amazon Logistics, arrived in pristine packaging. Operates seamlessly."),
        (4, "Great product with minor learning curve", "Performance is top notch. The manual could have been a bit clearer, but otherwise 10/10."),
        (5, "Industry leading standard", "Using it daily in a demanding workflow. Battery and durability are rock solid."),
        (4, "Very satisfied customer", "Solid construction, responsive and reliable. Highly recommended.")
    ]

    for cat_name, items in category_templates.items():
        for name, slug, brand, price, disc, img_url, specs in items:
            p = ProductModel(
                name=name,
                slug=f"{slug}-{product_counter}",
                description=f"Experience benchmark performance and industrial durability with the {name}. Engineered by {brand} to deliver outstanding reliability, elegant ergonomics, and precision operation for discerning customers.",
                category=cat_name,
                brand=brand,
                price=price,
                discount_pct=disc,
                stock=50 + (product_counter % 35),
                rating=round(4.3 + (product_counter % 7) * 0.1, 1),
                rating_count=35 + (product_counter * 8),
                image_url=img_url,
                images_json=json.dumps([img_url]),
                specs_json=json.dumps(specs),
                is_featured=(product_counter % 6 == 0)
            )
            products_to_add.append(p)
            product_counter += 1

    # Add variations / secondary models to hit well over 100 distinct catalog items
    extra_items = [
        ("Apple iPad Air 11-inch (M2 Chip, 128GB Wi-Fi, Space Grey)", "apple-ipad-air-11-m2", "Apple", "Smartphones", 59900.0, 5.0, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&auto=format&fit=crop&q=80", {"Display": "11 Liquid Retina", "Chip": "Apple M2", "Support": "Apple Pencil Pro"}),
        ("Samsung Galaxy Tab S9 Ultra (14.6 Dynamic AMOLED 2X)", "samsung-galaxy-tab-s9-ultra", "Samsung", "Smartphones", 108999.0, 10.0, "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=600&auto=format&fit=crop&q=80", {"Screen": "14.6 AMOLED 120Hz", "Resistance": "IP68 Water & Dust Resistant", "Pen": "S-Pen Included"}),
        ("Sony WH-CH720N Noise Cancelling Wireless Headphones", "sony-wh-ch720n-black", "Sony", "Audio & Headphones", 9990.0, 25.0, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80", {"Weight": "192g Lightweight", "Battery": "35 Hours", "Chip": "Integrated Processor V1"}),
        ("JBL Flip 6 Portable Waterproof Bluetooth Speaker", "jbl-flip-6-waterproof", "JBL", "Audio & Headphones", 9999.0, 20.0, "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80", {"Waterproof": "IP67 Dust & Water Proof", "Battery": "12 Hours Playtime", "System": "2-Way Speaker System"}),
        ("Logitech MX Mechanical Wireless Illuminated Keyboard", "logitech-mx-mechanical", "Logitech", "Computer Accessories", 17495.0, 12.0, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80", {"Switches": "Tactile Quiet Low Profile", "Lighting": "Smart Ambient Illumination", "Connectivity": "Bluetooth & Logi Bolt"}),
        ("Razer DeathAdder V3 Pro Ultra-Lightweight Wireless Gaming Mouse", "razer-deathadder-v3-pro", "Razer", "Gaming Consoles & Gear", 13999.0, 15.0, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80", {"Weight": "63g Ultra-Lightweight", "Sensor": "Focus Pro 30K Optical Sensor", "Switches": "Gen-3 Optical Mouse Switches"}),
        ("Kindle Paperwhite (16 GB) – 6.8 Display with Warm Light", "kindle-paperwhite-16gb", "Amazon", "Books & Media", 14999.0, 10.0, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80", {"Screen": "300 ppi Glare-Free Display", "Light": "Adjustable Warm Light", "Battery": "Up to 10 Weeks", "Waterproof": "IPX8 Waterproof"}),
        ("NutriBullet Pro 900W Personal Nutrition Blender", "nutribullet-pro-900w", "NutriBullet", "Kitchen Appliances", 7490.0, 25.0, "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80", {"Power": "900 Watts Motor", "Blades": "Extractor Blades for Smoothies", "Cups": "BPA-Free Tritan Cups"}),
        ("Mi Smart Air Fryer 3.5L with OLED Display", "mi-smart-air-fryer-3-5l", "Xiaomi", "Kitchen Appliances", 5999.0, 30.0, "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&auto=format&fit=crop&q=80", {"Capacity": "3.5L Smart Cooking Basket", "App": "Xiaomi Home Smart Scheduling", "Temperature": "40C to 200C Wide Range"}),
        ("Garmin Forerunner 265 Running Smartwatch (AMOLED)", "garmin-forerunner-265", "Garmin", "Sports & Fitness", 46990.0, 8.0, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop&q=80", {"Display": "Brilliant AMOLED Touchscreen", "Metrics": "Training Readiness & HRV Status", "Battery": "Up to 13 Days in Smartwatch Mode"})
    ]

    for name, slug, brand, cat, price, disc, img_url, specs in extra_items:
        p = ProductModel(
            name=name,
            slug=f"{slug}-{product_counter}",
            description=f"Engineered for excellence, the {name} brings industrial durability and precision engineering directly to your everyday life.",
            category=cat,
            brand=brand,
            price=price,
            discount_pct=disc,
            stock=45 + (product_counter % 40),
            rating=4.7,
            rating_count=88,
            image_url=img_url,
            images_json=json.dumps([img_url]),
            specs_json=json.dumps(specs),
            is_featured=True
        )
        products_to_add.append(p)
        product_counter += 1

    # Duplicate with realistic suffix variants (Colors, storage sizes, editions) until >= 110 items
    base_len = len(products_to_add)
    variant_suffixes = [
        ("Special Edition (Matte Black)", 1.05, 15.0),
        ("Platinum Edition", 1.15, 10.0),
        ("Classic Carbon Edition", 0.95, 20.0),
        ("Pro Developer Bundle", 1.25, 25.0)
    ]
    idx = 0
    while len(products_to_add) < 112:
        source_p = products_to_add[idx % base_len]
        suffix_name, price_mult, disc_val = variant_suffixes[idx % len(variant_suffixes)]
        new_name = f"{source_p.name} - {suffix_name}"
        new_slug = f"{source_p.slug}-v{idx}"
        p_var = ProductModel(
            name=new_name,
            slug=new_slug,
            description=source_p.description,
            category=source_p.category,
            brand=source_p.brand,
            price=round(source_p.price * price_mult, 2),
            discount_pct=disc_val,
            stock=30 + (idx * 3 % 45),
            rating=source_p.rating,
            rating_count=source_p.rating_count + (idx * 5),
            image_url=source_p.image_url,
            images_json=source_p.images_json,
            specs_json=source_p.specs_json,
            is_featured=(idx % 7 == 0)
        )
        products_to_add.append(p_var)
        idx += 1

    db.add_all(products_to_add)
    db.commit()

    print(f"Successfully seeded {len(products_to_add)} products across 20 categories!")

    print("Seeding Sample Customer Reviews...")
    reviews = []
    customer_names = ["Rahul Verma", "Ananya Deshmukh", "Vikramaditya Roy", "Sneha Patel", "Rohan Mehta"]
    all_seeded_products = db.query(ProductModel).limit(20).all()

    for p in all_seeded_products:
        for i, (star, title, comment) in enumerate(sample_reviews_text):
            r = ReviewModel(
                product_id=p.id,
                user_id=2 if i % 2 == 0 else 4,
                user_name=customer_names[i % len(customer_names)],
                rating=star,
                title=title,
                comment=comment,
                verified_purchase=True,
                helpful_votes=3 + (i * 4),
                status="APPROVED"
            )
            reviews.append(r)

    db.add_all(reviews)
    db.commit()
    print(f"Seeded {len(reviews)} verified reviews.")

    print("Seeding Initial Order and Shipment History...")
    sample_order = OrderModel(
        order_number="ORD-20261119-SEED01",
        user_id=2, # John Doe
        status="DELIVERED",
        subtotal=29990.0,
        discount_amount=2999.0,
        tax_amount=4117.27,
        shipping_fee=0.0,
        final_amount=26991.0,
        shipping_address_json=json.dumps({
            "full_name": "John Doe",
            "phone": "+919876543210",
            "street": "Flat 402, Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560103"
        }),
        payment_method="CARD",
        payment_status="SUCCESS"
    )
    db.add(sample_order)
    db.flush()

    p_sample = all_seeded_products[0]
    sample_item = OrderItemModel(
        order_id=sample_order.id,
        product_id=p_sample.id,
        product_name=p_sample.name,
        price=p_sample.price,
        quantity=1,
        image_url=p_sample.image_url
    )
    db.add(sample_item)

    now = datetime.datetime.utcnow()
    sample_shipment = ShipmentModel(
        shipment_id="SHIP-SEED01",
        order_number="ORD-20261119-SEED01",
        tracking_number="TRK-BLR-892147",
        carrier="Amazon Logistics",
        status="DELIVERED",
        estimated_delivery=now - datetime.timedelta(days=1),
        current_location="Delivered to Customer Doorstep (Bengaluru)",
        milestones_json=json.dumps([
            {"status": "ORDER_PLACED", "title": "Order Placed and Confirmed", "location": "Fulfillment Hub", "timestamp": (now - datetime.timedelta(days=3)).isoformat(), "completed": True},
            {"status": "LABEL_CREATED", "title": "Shipping Label Created", "location": "Bengaluru Hub", "timestamp": (now - datetime.timedelta(days=3)).isoformat(), "completed": True},
            {"status": "PICKED_UP", "title": "Picked up by Amazon Logistics", "location": "Bengaluru Sort Facility", "timestamp": (now - datetime.timedelta(days=2)).isoformat(), "completed": True},
            {"status": "IN_TRANSIT", "title": "Package In Transit", "location": "Bellandur Delivery Station", "timestamp": (now - datetime.timedelta(days=1)).isoformat(), "completed": True},
            {"status": "OUT_FOR_DELIVERY", "title": "Out for Delivery", "location": "Bellandur, Bengaluru", "timestamp": (now - datetime.timedelta(hours=6)).isoformat(), "completed": True},
            {"status": "DELIVERED", "title": "Delivered to Customer", "location": "Bellandur, Bengaluru", "timestamp": (now - datetime.timedelta(hours=2)).isoformat(), "completed": True}
        ])
    )
    db.add(sample_shipment)
    db.commit()

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
