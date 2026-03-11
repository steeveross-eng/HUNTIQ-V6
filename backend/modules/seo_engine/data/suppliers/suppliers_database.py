"""
BIONIC SEO Engine - LISTE FOURNISSEURS ULTIME
==============================================

Base de données exhaustive des fournisseurs mondiaux par catégorie.
Intégration SEO SUPRÊME - Chasse & Outdoors.

Catégories:
- Caméras de chasse
- Arcs & Arbalètes
- Treestands & Saddles
- Urines & Attractants
- Vêtements techniques
- Optiques
- Bottes
- Backpacks
- Knives
- Boats / Kayaks / Motors
- Electronics
- Coolers
- Processing

Architecture LEGO V5 - Module isolé.
"""

from typing import Dict, List, Any
from datetime import datetime

# ============================================
# LISTE FOURNISSEURS ULTIME - SEO SUPRÊME
# ============================================

SUPPLIERS_DATABASE: Dict[str, List[Dict[str, Any]]] = {
    
    # ==========================================
    # CAMÉRAS DE CHASSE
    # ==========================================
    "cameras": [
        {
            "company": "Reolink",
            "country": "USA",
            "official_url": "https://reolink.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Trail cameras", "Security cameras", "4K cameras"],
            "seo_priority": "high"
        },
        {
            "company": "Spypoint",
            "country": "Canada",
            "official_url": "https://www.spypoint.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Cellular trail cameras", "Solar cameras"],
            "seo_priority": "high"
        },
        {
            "company": "Suntek",
            "country": "International",
            "official_url": "https://suntekcam.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Budget trail cameras", "Night vision"],
            "seo_priority": "medium"
        },
        {
            "company": "Swann",
            "country": "USA",
            "official_url": "https://www.swann.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Security cameras", "DVR systems"],
            "seo_priority": "medium"
        },
        {
            "company": "Browning Trail Cameras",
            "country": "USA",
            "official_url": "https://browningtrailcameras.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Premium trail cameras", "Dark Ops series"],
            "seo_priority": "high"
        },
        {
            "company": "Exodus Outdoor Gear",
            "country": "USA",
            "official_url": "https://exodusoutdoorgear.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Render cameras", "Low glow technology"],
            "seo_priority": "medium"
        },
        {
            "company": "Covert Scouting Cameras",
            "country": "USA",
            "official_url": "https://covertscoutingcameras.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Cellular cameras", "Wireless scouting"],
            "seo_priority": "medium"
        },
        {
            "company": "Moultrie",
            "country": "USA",
            "official_url": "https://www.moultriefeeders.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Trail cameras", "Feeders", "Mobile app"],
            "seo_priority": "high"
        },
        {
            "company": "Stealth Cam",
            "country": "USA",
            "official_url": "https://stealthcam.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Trail cameras", "Fusion cellular"],
            "seo_priority": "high"
        },
        {
            "company": "Tasco",
            "country": "USA",
            "official_url": "https://www.tasco.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Budget cameras", "Optics"],
            "seo_priority": "low"
        },
        # Additional cameras suppliers
        {
            "company": "Reconyx",
            "country": "USA",
            "official_url": "https://www.reconyx.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Professional trail cameras", "Research grade"],
            "seo_priority": "high"
        },
        {
            "company": "Bushnell",
            "country": "USA",
            "official_url": "https://www.bushnell.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Trail cameras", "Optics", "Core series"],
            "seo_priority": "high"
        },
        {
            "company": "Tactacam",
            "country": "USA",
            "official_url": "https://www.tactacam.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Action cameras", "Reveal cellular"],
            "seo_priority": "high"
        },
    ],
    
    # ==========================================
    # ARCS & ARBALÈTES
    # ==========================================
    "arcs_arbaletes": [
        {
            "company": "Bear Archery",
            "country": "USA",
            "official_url": "https://beararchery.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Compound bows", "Traditional bows", "Crossbows"],
            "seo_priority": "high"
        },
        {
            "company": "TenPoint Crossbows",
            "country": "USA",
            "official_url": "https://tenpointcrossbows.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Premium crossbows", "ACUslide technology"],
            "seo_priority": "high"
        },
        {
            "company": "Ravin Crossbows",
            "country": "USA",
            "official_url": "https://ravincrossbows.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Helicoil technology", "Compact crossbows"],
            "seo_priority": "high"
        },
        {
            "company": "Lancaster Archery",
            "country": "USA",
            "official_url": "https://lancasterarchery.com",
            "free_shipping": "Parfois",
            "type": "retailer",
            "specialty": ["Full archery supply", "Target archery", "Bowhunting"],
            "seo_priority": "high"
        },
        {
            "company": "Excalibur Crossbow",
            "country": "Canada",
            "official_url": "https://excaliburcrossbow.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Recurve crossbows", "Canadian made"],
            "seo_priority": "high"
        },
        {
            "company": "PSE Archery",
            "country": "USA",
            "official_url": "https://psearchery.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Compound bows", "Evolve series"],
            "seo_priority": "high"
        },
        {
            "company": "Hoyt Archery",
            "country": "USA",
            "official_url": "https://hoyt.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Premium compound bows", "Target archery"],
            "seo_priority": "high"
        },
        # Additional archery suppliers
        {
            "company": "Mathews Archery",
            "country": "USA",
            "official_url": "https://www.mathewsinc.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Premium compound bows", "Phase 4"],
            "seo_priority": "high"
        },
        {
            "company": "Bowtech",
            "country": "USA",
            "official_url": "https://bowtecharchery.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Compound bows", "Binary cam system"],
            "seo_priority": "high"
        },
        {
            "company": "Elite Archery",
            "country": "USA",
            "official_url": "https://elitearchery.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Compound bows", "ASYM technology"],
            "seo_priority": "medium"
        },
        {
            "company": "Mission Archery",
            "country": "USA",
            "official_url": "https://missionarchery.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Entry-level bows", "Youth bows"],
            "seo_priority": "medium"
        },
        {
            "company": "Killer Instinct",
            "country": "USA",
            "official_url": "https://killerinstinctcrossbows.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Budget crossbows", "Value hunting"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # TREESTANDS & SADDLES
    # ==========================================
    "treestands": [
        {
            "company": "XOP Outdoors",
            "country": "USA",
            "official_url": "https://xopoutdoors.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Treestands", "Climbing sticks", "Ultralight"],
            "seo_priority": "high"
        },
        {
            "company": "Lone Wolf Custom Gear",
            "country": "USA",
            "official_url": "https://lonewolfcustomgear.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Cast aluminum stands", "Premium treestands"],
            "seo_priority": "high"
        },
        {
            "company": "Tethrd",
            "country": "USA",
            "official_url": "https://tethrdnation.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Saddle hunting", "Platforms", "Saddles"],
            "seo_priority": "high"
        },
        {
            "company": "Trophyline",
            "country": "USA",
            "official_url": "https://trophyline.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Saddle hunting", "Ultralight platforms"],
            "seo_priority": "high"
        },
        {
            "company": "Muddy Outdoors",
            "country": "USA",
            "official_url": "https://gomuddy.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Treestands", "Blinds", "Accessories"],
            "seo_priority": "high"
        },
        {
            "company": "Hawk Hunting",
            "country": "USA",
            "official_url": "https://hawkhunting.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Hang-on stands", "Climbing sticks"],
            "seo_priority": "medium"
        },
        # Additional treestand suppliers
        {
            "company": "Millennium Treestands",
            "country": "USA",
            "official_url": "https://millenniumstands.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Hang-on stands", "Ladder stands"],
            "seo_priority": "high"
        },
        {
            "company": "Summit Treestands",
            "country": "USA",
            "official_url": "https://summitstands.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Climbing stands", "Viper series"],
            "seo_priority": "high"
        },
        {
            "company": "Novix",
            "country": "USA",
            "official_url": "https://novixoutdoors.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Ultralight stands", "Platforms"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # URINES & ATTRACTANTS
    # ==========================================
    "urines_attractants": [
        {
            "company": "Dead Down Wind",
            "country": "USA",
            "official_url": "https://deaddownwind.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Scent elimination", "Laundry detergents"],
            "seo_priority": "high"
        },
        {
            "company": "Code Blue Scents",
            "country": "USA",
            "official_url": "https://codebluescents.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Deer scents", "Estrus", "Tarsal gland"],
            "seo_priority": "high"
        },
        {
            "company": "Wildlife Research Center",
            "country": "USA",
            "official_url": "https://wildlife.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Golden Estrus", "Scent Killer"],
            "seo_priority": "high"
        },
        {
            "company": "Ferme Monette",
            "country": "Canada",
            "official_url": "https://ferme-monette.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Canadian deer urine", "Moose urine"],
            "seo_priority": "high"
        },
        {
            "company": "Proxpedition",
            "country": "Canada",
            "official_url": "https://proxpedition.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Quebec attractants", "Bear baits"],
            "seo_priority": "medium"
        },
        {
            "company": "Buck Expert",
            "country": "Canada",
            "official_url": "https://buckexpert.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Deer calls", "Scents", "Decoys"],
            "seo_priority": "high"
        },
        # Additional attractant suppliers
        {
            "company": "Tink's",
            "country": "USA",
            "official_url": "https://tinks.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Deer lures", "#69 Doe-in-Rut"],
            "seo_priority": "high"
        },
        {
            "company": "ConQuest Scents",
            "country": "USA",
            "official_url": "https://conquestscents.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["EverCalm", "VS-1"],
            "seo_priority": "medium"
        },
        {
            "company": "Mrs. Doe Pee",
            "country": "USA",
            "official_url": "https://mrsdoepee.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Premium deer urine", "Fresh scents"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # VÊTEMENTS TECHNIQUES
    # ==========================================
    "vetements": [
        {
            "company": "Kryptek",
            "country": "USA",
            "official_url": "https://kryptek.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Camo patterns", "Technical hunting apparel"],
            "seo_priority": "high"
        },
        {
            "company": "Huntworth Gear",
            "country": "USA",
            "official_url": "https://huntworthgear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Budget hunting clothing", "Heat Boost"],
            "seo_priority": "medium"
        },
        # Additional clothing suppliers
        {
            "company": "Sitka Gear",
            "country": "USA",
            "official_url": "https://www.sitkagear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Premium hunting systems", "Optifade camo"],
            "seo_priority": "high"
        },
        {
            "company": "First Lite",
            "country": "USA",
            "official_url": "https://www.firstlite.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Merino wool", "Technical hunting"],
            "seo_priority": "high"
        },
        {
            "company": "KUIU",
            "country": "USA",
            "official_url": "https://www.kuiu.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Mountain hunting", "Ultralight systems"],
            "seo_priority": "high"
        },
        {
            "company": "Under Armour Hunting",
            "country": "USA",
            "official_url": "https://www.underarmour.com/hunting",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Base layers", "Ridge Reaper"],
            "seo_priority": "high"
        },
        {
            "company": "Badlands",
            "country": "USA",
            "official_url": "https://www.badlandsgear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Packs", "Clothing", "Approach camo"],
            "seo_priority": "high"
        },
        {
            "company": "Cabela's",
            "country": "USA",
            "official_url": "https://www.cabelas.com",
            "free_shipping": "Parfois",
            "type": "retailer",
            "specialty": ["Full hunting supply", "Outdoor gear"],
            "seo_priority": "high"
        },
        {
            "company": "Bass Pro Shops",
            "country": "USA",
            "official_url": "https://www.basspro.com",
            "free_shipping": "Parfois",
            "type": "retailer",
            "specialty": ["Full hunting supply", "Outdoor retail"],
            "seo_priority": "high"
        },
    ],
    
    # ==========================================
    # OPTIQUES
    # ==========================================
    "optiques": [
        {
            "company": "Vortex Optics",
            "country": "USA",
            "official_url": "https://vortexoptics.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Riflescopes", "Binoculars", "VIP warranty"],
            "seo_priority": "high"
        },
        {
            "company": "Leupold",
            "country": "USA",
            "official_url": "https://www.leupold.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Premium optics", "Made in USA"],
            "seo_priority": "high"
        },
        {
            "company": "Swarovski Optik",
            "country": "Austria",
            "official_url": "https://www.swarovskioptik.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Luxury optics", "EL binoculars"],
            "seo_priority": "high"
        },
        {
            "company": "Zeiss",
            "country": "Germany",
            "official_url": "https://www.zeiss.com/consumer-products/hunting",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["German precision", "Victory series"],
            "seo_priority": "high"
        },
        {
            "company": "Athlon Optics",
            "country": "USA",
            "official_url": "https://athlonoptics.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Budget-friendly", "Lifetime warranty"],
            "seo_priority": "medium"
        },
        {
            "company": "Sig Sauer Optics",
            "country": "USA",
            "official_url": "https://www.sigsauer.com/optics",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Tactical optics", "BDX system"],
            "seo_priority": "high"
        },
        {
            "company": "Maven",
            "country": "USA",
            "official_url": "https://www.mavenbuilt.com",
            "free_shipping": "Oui",
            "type": "manufacturer",
            "specialty": ["Direct-to-consumer", "Custom optics"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # BOTTES
    # ==========================================
    "bottes": [
        {
            "company": "Irish Setter",
            "country": "USA",
            "official_url": "https://www.irishsetterboots.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Hunting boots", "Work boots"],
            "seo_priority": "high"
        },
        {
            "company": "Danner",
            "country": "USA",
            "official_url": "https://www.danner.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Premium boots", "Pronghorn series"],
            "seo_priority": "high"
        },
        {
            "company": "LaCrosse",
            "country": "USA",
            "official_url": "https://www.lacrossefootwear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Rubber boots", "Alphaburly Pro"],
            "seo_priority": "high"
        },
        {
            "company": "Muck Boot",
            "country": "USA",
            "official_url": "https://www.muckbootcompany.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Rubber boots", "Wetland series"],
            "seo_priority": "high"
        },
        {
            "company": "Crispi",
            "country": "Italy",
            "official_url": "https://www.crispi.it",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Mountain boots", "Italian craftsmanship"],
            "seo_priority": "high"
        },
        {
            "company": "Kenetrek",
            "country": "USA",
            "official_url": "https://kenetrek.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Mountain hunting boots", "Hardscrabble"],
            "seo_priority": "high"
        },
        {
            "company": "Schnee's",
            "country": "USA",
            "official_url": "https://schnees.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Pac boots", "Extreme cold"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # BACKPACKS
    # ==========================================
    "backpacks": [
        {
            "company": "Mystery Ranch",
            "country": "USA",
            "official_url": "https://www.mysteryranch.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Hunting packs", "Military grade"],
            "seo_priority": "high"
        },
        {
            "company": "Exo Mountain Gear",
            "country": "USA",
            "official_url": "https://exomtngear.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Modular systems", "K3 frame"],
            "seo_priority": "high"
        },
        {
            "company": "Stone Glacier",
            "country": "USA",
            "official_url": "https://www.stoneglacier.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Ultralight packs", "Krux frame"],
            "seo_priority": "high"
        },
        {
            "company": "Kifaru",
            "country": "USA",
            "official_url": "https://kifaru.net",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Heavy haulers", "Custom packs"],
            "seo_priority": "high"
        },
        {
            "company": "Eberlestock",
            "country": "USA",
            "official_url": "https://eberlestock.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Hunting packs", "Scabbard integration"],
            "seo_priority": "high"
        },
        {
            "company": "Alps OutdoorZ",
            "country": "USA",
            "official_url": "https://alpsoutdoorz.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Budget packs", "Pursuit series"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # KNIVES
    # ==========================================
    "knives": [
        {
            "company": "Benchmade",
            "country": "USA",
            "official_url": "https://www.benchmade.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Premium knives", "Saddle Mountain"],
            "seo_priority": "high"
        },
        {
            "company": "Buck Knives",
            "country": "USA",
            "official_url": "https://www.buckknives.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Classic hunting knives", "110 Folding Hunter"],
            "seo_priority": "high"
        },
        {
            "company": "Havalon",
            "country": "USA",
            "official_url": "https://havalon.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Replaceable blade knives", "Piranta"],
            "seo_priority": "high"
        },
        {
            "company": "Outdoor Edge",
            "country": "USA",
            "official_url": "https://www.outdooredge.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Game processing", "RazorSafe system"],
            "seo_priority": "high"
        },
        {
            "company": "Gerber",
            "country": "USA",
            "official_url": "https://www.gerbergear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Multi-tools", "Fixed blade hunting"],
            "seo_priority": "high"
        },
        {
            "company": "Böker",
            "country": "Germany",
            "official_url": "https://www.bokerusa.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["German knives", "Arbolito series"],
            "seo_priority": "medium"
        },
        {
            "company": "Cold Steel",
            "country": "USA",
            "official_url": "https://www.coldsteel.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Heavy duty knives", "Machetes"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # BOATS / KAYAKS / MOTORS
    # ==========================================
    "boats_kayaks": [
        {
            "company": "Old Town Canoe",
            "country": "USA",
            "official_url": "https://www.oldtowncanoe.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Kayaks", "Canoes", "Sportsman series"],
            "seo_priority": "high"
        },
        {
            "company": "Perception Kayaks",
            "country": "USA",
            "official_url": "https://www.perceptionkayaks.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Fishing kayaks", "Outlaw series"],
            "seo_priority": "medium"
        },
        {
            "company": "Hobie",
            "country": "USA",
            "official_url": "https://www.hobie.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Pedal kayaks", "MirageDrive"],
            "seo_priority": "high"
        },
        {
            "company": "NuCanoe",
            "country": "USA",
            "official_url": "https://nucanoe.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Hybrid kayaks", "Stand-up fishing"],
            "seo_priority": "medium"
        },
        {
            "company": "Pelican",
            "country": "Canada",
            "official_url": "https://www.pelicansport.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Budget kayaks", "Catch series"],
            "seo_priority": "medium"
        },
        {
            "company": "Minn Kota",
            "country": "USA",
            "official_url": "https://www.minnkotamotors.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Trolling motors", "Spot-Lock"],
            "seo_priority": "high"
        },
        {
            "company": "MotorGuide",
            "country": "USA",
            "official_url": "https://www.motorguide.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Trolling motors", "Xi5"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # ELECTRONICS
    # ==========================================
    "electronics": [
        {
            "company": "Garmin",
            "country": "USA",
            "official_url": "https://www.garmin.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["GPS devices", "Dog tracking", "Watches"],
            "seo_priority": "high"
        },
        {
            "company": "onX Hunt",
            "country": "USA",
            "official_url": "https://www.onxmaps.com",
            "free_shipping": "N/A",
            "type": "software",
            "specialty": ["Mapping software", "Land ownership"],
            "seo_priority": "high"
        },
        {
            "company": "Ozonics",
            "country": "USA",
            "official_url": "https://www.ozonics.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Scent elimination", "Ozone generators"],
            "seo_priority": "high"
        },
        {
            "company": "FLIR",
            "country": "USA",
            "official_url": "https://www.flir.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Thermal imaging", "Scout series"],
            "seo_priority": "high"
        },
        {
            "company": "Pulsar",
            "country": "USA",
            "official_url": "https://www.pulsarnv.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Night vision", "Thermal scopes"],
            "seo_priority": "high"
        },
        {
            "company": "Walker's Game Ear",
            "country": "USA",
            "official_url": "https://walkersgameear.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Hearing protection", "Electronic muffs"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # COOLERS
    # ==========================================
    "coolers": [
        {
            "company": "YETI",
            "country": "USA",
            "official_url": "https://www.yeti.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Premium coolers", "Tundra series"],
            "seo_priority": "high"
        },
        {
            "company": "RTIC",
            "country": "USA",
            "official_url": "https://rticoutdoors.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Value coolers", "Ultra-Light"],
            "seo_priority": "high"
        },
        {
            "company": "Pelican Products",
            "country": "USA",
            "official_url": "https://www.pelican.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Elite coolers", "Indestructible"],
            "seo_priority": "high"
        },
        {
            "company": "Igloo",
            "country": "USA",
            "official_url": "https://www.igloocoolers.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Budget coolers", "BMX series"],
            "seo_priority": "medium"
        },
        {
            "company": "Canyon Coolers",
            "country": "USA",
            "official_url": "https://canyoncoolers.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Rotomolded coolers", "Outfitter"],
            "seo_priority": "medium"
        },
        {
            "company": "Engel Coolers",
            "country": "USA",
            "official_url": "https://www.engelcoolers.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Dry boxes", "Live bait"],
            "seo_priority": "medium"
        },
    ],
    
    # ==========================================
    # PROCESSING
    # ==========================================
    "processing": [
        {
            "company": "LEM Products",
            "country": "USA",
            "official_url": "https://www.lemproducts.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Meat grinders", "Sausage stuffers"],
            "seo_priority": "high"
        },
        {
            "company": "Weston",
            "country": "USA",
            "official_url": "https://www.westonsupply.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Processing equipment", "Vacuum sealers"],
            "seo_priority": "high"
        },
        {
            "company": "Cabela's",
            "country": "USA",
            "official_url": "https://www.cabelas.com/meat-processing",
            "free_shipping": "Parfois",
            "type": "retailer",
            "specialty": ["Processing supplies", "Seasonings"],
            "seo_priority": "high"
        },
        {
            "company": "Hi Mountain Seasonings",
            "country": "USA",
            "official_url": "https://himtnjerky.com",
            "free_shipping": "Parfois",
            "type": "manufacturer",
            "specialty": ["Jerky kits", "Seasonings"],
            "seo_priority": "medium"
        },
        {
            "company": "Excalibur",
            "country": "USA",
            "official_url": "https://www.excaliburdehydrator.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Food dehydrators", "Jerky making"],
            "seo_priority": "medium"
        },
        {
            "company": "Bradley Smoker",
            "country": "Canada",
            "official_url": "https://www.bradleysmoker.com",
            "free_shipping": "Non",
            "type": "manufacturer",
            "specialty": ["Electric smokers", "Bisquettes"],
            "seo_priority": "medium"
        },
    ],
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_suppliers() -> List[Dict[str, Any]]:
    """Retourne tous les fournisseurs avec leur catégorie"""
    all_suppliers = []
    for category, suppliers in SUPPLIERS_DATABASE.items():
        for supplier in suppliers:
            all_suppliers.append({
                **supplier,
                "category": category
            })
    return all_suppliers


def get_suppliers_by_category(category: str) -> List[Dict[str, Any]]:
    """Retourne les fournisseurs d'une catégorie spécifique"""
    return SUPPLIERS_DATABASE.get(category, [])


def get_categories() -> List[str]:
    """Retourne la liste des catégories"""
    return list(SUPPLIERS_DATABASE.keys())


def get_suppliers_count() -> Dict[str, int]:
    """Retourne le nombre de fournisseurs par catégorie"""
    return {cat: len(suppliers) for cat, suppliers in SUPPLIERS_DATABASE.items()}


def get_total_suppliers() -> int:
    """Retourne le nombre total de fournisseurs"""
    return sum(len(suppliers) for suppliers in SUPPLIERS_DATABASE.values())


def search_suppliers(query: str) -> List[Dict[str, Any]]:
    """Recherche de fournisseurs par nom"""
    query_lower = query.lower()
    results = []
    for category, suppliers in SUPPLIERS_DATABASE.items():
        for supplier in suppliers:
            if query_lower in supplier["company"].lower():
                results.append({**supplier, "category": category})
    return results


def get_suppliers_by_country(country: str) -> List[Dict[str, Any]]:
    """Retourne les fournisseurs par pays"""
    results = []
    for category, suppliers in SUPPLIERS_DATABASE.items():
        for supplier in suppliers:
            if supplier["country"].lower() == country.lower():
                results.append({**supplier, "category": category})
    return results


def export_to_excel_format() -> List[Dict[str, str]]:
    """Export pour format Excel"""
    export = []
    for category, suppliers in SUPPLIERS_DATABASE.items():
        for supplier in suppliers:
            export.append({
                "Catégorie": category,
                "Compagnie": supplier["company"],
                "Pays": supplier["country"],
                "Lien officiel": supplier["official_url"],
                "Livraison gratuite": supplier["free_shipping"],
                "Type": supplier.get("type", ""),
                "Spécialités": ", ".join(supplier.get("specialty", [])),
                "Priorité SEO": supplier.get("seo_priority", "medium")
            })
    return export


# Statistics
SUPPLIERS_STATS = {
    "total_suppliers": get_total_suppliers(),
    "categories_count": len(SUPPLIERS_DATABASE),
    "by_category": get_suppliers_count(),
    "last_updated": datetime.now().isoformat(),
    "version": "1.0.0"
}
