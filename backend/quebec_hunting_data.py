"""
Base de données des territoires de chasse du Québec
Sources: Réseau ZEC, FédéCP, Gouvernement du Québec, Sépaq, Pourvoiries.com
"""

# ===========================================
# ZONES D'EXPLOITATION CONTRÔLÉE (ZECs)
# ===========================================
QUEBEC_ZECS = [
    # Abitibi-Témiscamingue
    {"name": "Zec Capitachouane", "region": "Abitibi-Témiscamingue", "lat": 47.8, "lng": -77.5, "species": ["orignal", "ours", "petit gibier"], "website": "https://zeccapitachouane.reseauzec.com/"},
    {"name": "Zec Dumoine", "region": "Abitibi-Témiscamingue", "lat": 46.8, "lng": -78.2, "species": ["orignal", "ours", "petit gibier"], "website": "https://zecdumoine.reseauzec.com/"},
    {"name": "Zec Festubert", "region": "Abitibi-Témiscamingue", "lat": 48.5, "lng": -77.8, "species": ["orignal", "ours"], "website": "https://zecfestubert.reseauzec.com/"},
    {"name": "Zec Kipawa", "region": "Abitibi-Témiscamingue", "lat": 47.0, "lng": -79.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://zeckipawa.reseauzec.com/"},
    {"name": "Zec Maganasipi", "region": "Abitibi-Témiscamingue", "lat": 47.2, "lng": -78.5, "species": ["orignal", "ours"], "website": "https://zecmaganasipi.reseauzec.com/"},
    {"name": "Zec Restigo", "region": "Abitibi-Témiscamingue", "lat": 48.2, "lng": -78.0, "species": ["orignal", "ours", "petit gibier"], "website": "https://zecrestigo.reseauzec.com/"},
    
    # Bas-Saint-Laurent
    {"name": "Zec Bas-St-Laurent", "region": "Bas-Saint-Laurent", "lat": 47.8, "lng": -68.5, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecbasstlaurent.reseauzec.com/"},
    {"name": "Zec Casault", "region": "Bas-Saint-Laurent", "lat": 47.5, "lng": -67.8, "species": ["orignal", "chevreuil"], "website": "https://zeccasault.reseauzec.com/"},
    {"name": "Zec Chapais", "region": "Bas-Saint-Laurent", "lat": 47.3, "lng": -68.2, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecchapais.reseauzec.com/"},
    {"name": "Zec Owen", "region": "Bas-Saint-Laurent", "lat": 47.6, "lng": -67.5, "species": ["orignal", "chevreuil"], "website": "https://zecowen.reseauzec.com/"},
    
    # Capitale-Nationale
    {"name": "Zec Batiscan-Neilson", "region": "Capitale-Nationale", "lat": 47.2, "lng": -72.0, "species": ["orignal", "ours", "petit gibier"], "website": "https://zecbatiscanneilson.reseauzec.com/"},
    {"name": "Zec Buteux-Bas-Saguenay", "region": "Capitale-Nationale", "lat": 47.8, "lng": -70.2, "species": ["orignal", "ours"], "website": "https://zecbuteux.reseauzec.com/"},
    {"name": "Zec Des Martres", "region": "Capitale-Nationale", "lat": 47.5, "lng": -71.5, "species": ["orignal", "ours", "chevreuil"], "website": "https://zecdesmartres.reseauzec.com/"},
    {"name": "Zec Lac-au-Sable", "region": "Capitale-Nationale", "lat": 46.9, "lng": -72.3, "species": ["orignal", "chevreuil"], "website": "https://zeclacausable.reseauzec.com/"},
    {"name": "Zec Rivière-Blanche", "region": "Capitale-Nationale", "lat": 47.3, "lng": -71.8, "species": ["orignal", "ours"], "website": "https://zecriviereblanche.reseauzec.com/"},
    
    # Chaudière-Appalaches & Estrie
    {"name": "Zec Jaro", "region": "Chaudière-Appalaches", "lat": 46.3, "lng": -70.8, "species": ["chevreuil", "orignal"], "website": "https://zecjaro.reseauzec.com/"},
    {"name": "Zec Louise-Gosford", "region": "Chaudière-Appalaches", "lat": 45.6, "lng": -71.0, "species": ["chevreuil", "orignal", "ours"], "website": "https://zeclouisegosford.reseauzec.com/"},
    {"name": "Zec Saint-Romain", "region": "Estrie", "lat": 45.8, "lng": -71.2, "species": ["chevreuil", "petit gibier"], "website": "https://zecsaintromain.reseauzec.com/"},
    
    # Côte-Nord
    {"name": "Zec Forestville", "region": "Côte-Nord", "lat": 48.7, "lng": -69.0, "species": ["orignal", "ours"], "website": "https://zecforestville.reseauzec.com/"},
    {"name": "Zec Iberville", "region": "Côte-Nord", "lat": 49.5, "lng": -67.5, "species": ["orignal", "ours", "caribou"], "website": "https://zeciberville.reseauzec.com/"},
    {"name": "Zec Labrieville", "region": "Côte-Nord", "lat": 49.8, "lng": -68.8, "species": ["orignal", "ours"], "website": "https://zeclabrieville.reseauzec.com/"},
    {"name": "Zec Matimek", "region": "Côte-Nord", "lat": 50.2, "lng": -66.5, "species": ["orignal", "caribou"], "website": "https://zecmatimek.reseauzec.com/"},
    {"name": "Zec Nordique", "region": "Côte-Nord", "lat": 50.5, "lng": -65.0, "species": ["orignal", "caribou", "ours"], "website": "https://zecnordique.reseauzec.com/"},
    {"name": "Zec Trinité", "region": "Côte-Nord", "lat": 49.3, "lng": -67.2, "species": ["orignal", "ours"], "website": "https://zectrinite.reseauzec.com/"},
    {"name": "Zec Varin", "region": "Côte-Nord", "lat": 48.9, "lng": -68.5, "species": ["orignal", "ours"], "website": "https://zecvarin.reseauzec.com/"},
    
    # Gaspésie
    {"name": "Zec Baillargeon", "region": "Gaspésie", "lat": 48.8, "lng": -66.0, "species": ["orignal", "chevreuil"], "website": "https://zecbaillargeon.reseauzec.com/"},
    {"name": "Zec Cap-Chat", "region": "Gaspésie", "lat": 49.1, "lng": -66.5, "species": ["orignal", "chevreuil"], "website": "https://zeccapchat.reseauzec.com/"},
    {"name": "Zec Des Anses", "region": "Gaspésie", "lat": 48.5, "lng": -64.8, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecdesanses.reseauzec.com/"},
    
    # Hautes-Laurentides
    {"name": "Zec Lesueur", "region": "Laurentides", "lat": 46.8, "lng": -75.5, "species": ["orignal", "ours", "chevreuil"], "website": "https://zeclesueur.reseauzec.com/"},
    {"name": "Zec Maison-de-Pierre", "region": "Laurentides", "lat": 47.0, "lng": -75.8, "species": ["orignal", "ours"], "website": "https://zecmaisondepierre.reseauzec.com/"},
    {"name": "Zec Mazana", "region": "Laurentides", "lat": 47.2, "lng": -76.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://zecmazana.reseauzec.com/"},
    {"name": "Zec Mitchinamecus", "region": "Laurentides", "lat": 47.5, "lng": -75.2, "species": ["orignal", "ours"], "website": "https://zecmitchinamecus.reseauzec.com/"},
    {"name": "Zec Normandie", "region": "Laurentides", "lat": 46.5, "lng": -75.0, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecnormandie.reseauzec.com/"},
    {"name": "Zec Petawaga", "region": "Laurentides", "lat": 47.3, "lng": -76.2, "species": ["orignal", "ours"], "website": "https://zecpetawaga.reseauzec.com/"},
    
    # Lanaudière
    {"name": "Zec Boullé", "region": "Lanaudière", "lat": 46.8, "lng": -73.8, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecboulle.reseauzec.com/"},
    {"name": "Zec Collin", "region": "Lanaudière", "lat": 46.5, "lng": -73.5, "species": ["orignal", "chevreuil"], "website": "https://zeccollin.reseauzec.com/"},
    {"name": "Zec Des Nymphes", "region": "Lanaudière", "lat": 46.6, "lng": -74.0, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecdesnymphes.reseauzec.com/"},
    {"name": "Zec Lavigne", "region": "Lanaudière", "lat": 46.9, "lng": -74.2, "species": ["orignal", "chevreuil"], "website": "https://zeclavigne.reseauzec.com/"},
    
    # Mauricie
    {"name": "Zec Bessonne", "region": "Mauricie", "lat": 47.0, "lng": -73.2, "species": ["orignal", "ours"], "website": "https://zecdelabessonne.reseauzec.com/"},
    {"name": "Zec Borgia", "region": "Mauricie", "lat": 47.2, "lng": -73.5, "species": ["orignal", "ours"], "website": "https://zecborgia.reseauzec.com/"},
    {"name": "Zec Chapeau-de-Paille", "region": "Mauricie", "lat": 47.5, "lng": -73.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://zecchapeaudepaille.reseauzec.com/"},
    {"name": "Zec Frémont", "region": "Mauricie", "lat": 47.8, "lng": -73.8, "species": ["orignal", "ours"], "website": "https://zecfremont.reseauzec.com/"},
    {"name": "Zec Gros-Brochet", "region": "Mauricie", "lat": 46.8, "lng": -72.8, "species": ["orignal", "chevreuil"], "website": "https://zecgrosbrochet.reseauzec.com/"},
    {"name": "Zec Jeannotte", "region": "Mauricie", "lat": 47.3, "lng": -72.5, "species": ["orignal", "ours"], "website": "https://zecjeannotte.reseauzec.com/"},
    {"name": "Zec Kiskissink", "region": "Mauricie", "lat": 47.6, "lng": -72.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://zeckiskissink.reseauzec.com/"},
    {"name": "Zec La Croche", "region": "Mauricie", "lat": 47.4, "lng": -73.2, "species": ["orignal", "ours"], "website": "https://zeclacroche.reseauzec.com/"},
    {"name": "Zec Menokeosawin", "region": "Mauricie", "lat": 47.7, "lng": -74.0, "species": ["orignal", "ours"], "website": "https://zecmenokeosawin.reseauzec.com/"},
    {"name": "Zec Tawachiche", "region": "Mauricie", "lat": 46.7, "lng": -72.5, "species": ["orignal", "chevreuil", "ours"], "website": "https://zectawachiche.reseauzec.com/"},
    {"name": "Zec Wessonneau", "region": "Mauricie", "lat": 47.1, "lng": -73.0, "species": ["orignal", "ours"], "website": "https://zecwessonneau.reseauzec.com/"},
    
    # Outaouais
    {"name": "Zec Bras-Coupé-Désert", "region": "Outaouais", "lat": 46.5, "lng": -76.0, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecbrascoupedesert.reseauzec.com/"},
    {"name": "Zec Pontiac", "region": "Outaouais", "lat": 46.2, "lng": -77.5, "species": ["orignal", "chevreuil", "ours"], "website": "https://zecpontiac.reseauzec.com/"},
    {"name": "Zec Rapides-des-Joachims", "region": "Outaouais", "lat": 46.3, "lng": -77.8, "species": ["orignal", "chevreuil"], "website": "https://zecrapidesdesjoachims.reseauzec.com/"},
    {"name": "Zec St-Patrice", "region": "Outaouais", "lat": 46.0, "lng": -76.5, "species": ["chevreuil", "petit gibier"], "website": "https://zecstpatrice.reseauzec.com/"},
    
    # Saguenay-Lac-Saint-Jean
    {"name": "Zec Anse-Saint-Jean", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.2, "lng": -70.2, "species": ["orignal", "ours"], "website": "https://zecansestjean.reseauzec.com/"},
    {"name": "Zec Chauvin", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.8, "lng": -71.5, "species": ["orignal", "ours"], "website": "https://zecchauvin.reseauzec.com/"},
    {"name": "Zec Des Passes", "region": "Saguenay-Lac-Saint-Jean", "lat": 49.0, "lng": -72.0, "species": ["orignal", "ours", "caribou"], "website": "https://zecdespasses.reseauzec.com/"},
    {"name": "Zec La Lièvre", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.5, "lng": -71.8, "species": ["orignal", "ours"], "website": "https://zeclalievre.reseauzec.com/"},
    {"name": "Zec Lac-Brébeuf", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.3, "lng": -70.8, "species": ["orignal", "ours"], "website": "https://zecdulacbrebeuf.reseauzec.com/"},
    {"name": "Zec Lac-de-la-Boiteuse", "region": "Saguenay-Lac-Saint-Jean", "lat": 49.2, "lng": -71.0, "species": ["orignal", "ours", "caribou"], "website": "https://zeclacdelaboiteuse.reseauzec.com/"},
    {"name": "Zec Mars-Moulin", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.0, "lng": -70.5, "species": ["orignal", "ours"], "website": "https://zecmarsmoulin.reseauzec.com/"},
    {"name": "Zec Martin-Valin", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.6, "lng": -70.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://zecmartinvalin.com/"},
    {"name": "Zec Onatchiway", "region": "Saguenay-Lac-Saint-Jean", "lat": 49.5, "lng": -71.5, "species": ["orignal", "ours", "caribou"], "website": "https://zeconatchiwayest.reseauzec.com/"},
    {"name": "Zec Rivière-aux-Rats", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.4, "lng": -72.5, "species": ["orignal", "ours"], "website": "https://zecriviereauxrats.reseauzec.com/"},
]

# ===========================================
# RÉSERVES FAUNIQUES (SÉPAQ)
# ===========================================
QUEBEC_RESERVES_FAUNIQUES = [
    {"name": "Réserve faunique des Laurentides", "region": "Capitale-Nationale/Saguenay", "lat": 47.5, "lng": -71.2, "species": ["orignal", "ours", "petit gibier"], "website": "https://www.sepaq.com/rf/lau/"},
    {"name": "Réserve faunique de Portneuf", "region": "Capitale-Nationale", "lat": 47.0, "lng": -72.0, "species": ["orignal", "ours", "chevreuil"], "website": "https://www.sepaq.com/rf/por/"},
    {"name": "Réserve faunique de Papineau-Labelle", "region": "Laurentides/Outaouais", "lat": 46.2, "lng": -75.2, "species": ["orignal", "chevreuil", "ours"], "website": "https://www.sepaq.com/rf/pal/"},
    {"name": "Réserve faunique Rouge-Matawin", "region": "Lanaudière", "lat": 46.8, "lng": -74.5, "species": ["orignal", "ours", "chevreuil"], "website": "https://www.sepaq.com/rf/rom/"},
    {"name": "Réserve faunique Mastigouche", "region": "Mauricie/Lanaudière", "lat": 46.7, "lng": -73.3, "species": ["orignal", "ours", "chevreuil"], "website": "https://www.sepaq.com/rf/mas/"},
    {"name": "Réserve faunique du Saint-Maurice", "region": "Mauricie", "lat": 47.5, "lng": -73.5, "species": ["orignal", "ours"], "website": "https://www.sepaq.com/rf/stm/"},
    {"name": "Réserve faunique La Vérendrye", "region": "Outaouais/Abitibi", "lat": 47.5, "lng": -77.0, "species": ["orignal", "ours"], "website": "https://www.sepaq.com/rf/lav/"},
    {"name": "Réserve faunique de Rimouski", "region": "Bas-Saint-Laurent", "lat": 48.0, "lng": -68.5, "species": ["orignal", "chevreuil", "ours"], "website": "https://www.sepaq.com/rf/rim/"},
    {"name": "Réserve faunique de Matane", "region": "Bas-Saint-Laurent/Gaspésie", "lat": 48.8, "lng": -67.0, "species": ["orignal", "chevreuil"], "website": "https://www.sepaq.com/rf/mat/"},
    {"name": "Réserve faunique de Dunière", "region": "Bas-Saint-Laurent", "lat": 47.8, "lng": -68.0, "species": ["orignal", "chevreuil", "ours"], "website": "https://cgrmp.com/duniere/"},
    {"name": "Réserve faunique Port-Cartier-Sept-Îles", "region": "Côte-Nord", "lat": 50.5, "lng": -66.5, "species": ["orignal", "ours", "caribou"], "website": "https://www.sepaq.com/rf/pcs/"},
    {"name": "Réserve faunique des Chic-Chocs", "region": "Gaspésie", "lat": 49.0, "lng": -66.0, "species": ["orignal", "caribou"], "website": "https://www.sepaq.com/rf/chc/"},
    {"name": "Réserve faunique Ashuapmushuan", "region": "Saguenay-Lac-Saint-Jean", "lat": 49.5, "lng": -73.5, "species": ["orignal", "ours", "caribou"], "website": "https://www.sepaq.com/rf/ash/"},
    {"name": "Réserve faunique Duchénier", "region": "Bas-Saint-Laurent", "lat": 47.2, "lng": -68.8, "species": ["orignal", "chevreuil", "ours"], "website": "https://www.terfa.ca/fr/terfa/reserve-faunique-duchenier/"},
]

# ===========================================
# POURVOIRIES POPULAIRES
# ===========================================
QUEBEC_POURVOIRIES = [
    {"name": "Pourvoirie du Lac Blanc", "region": "Mauricie", "lat": 47.3, "lng": -73.0, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "La Seigneurie du Triton", "region": "Mauricie", "lat": 47.5, "lng": -73.2, "species": ["orignal", "ours", "chevreuil"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie Air Mont-Laurier", "region": "Laurentides", "lat": 46.8, "lng": -75.5, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie Domaine Lounan", "region": "Laurentides", "lat": 46.5, "lng": -75.0, "species": ["orignal", "chevreuil", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie Mekoos", "region": "Laurentides", "lat": 47.0, "lng": -76.0, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie Club Gatineau", "region": "Laurentides", "lat": 46.3, "lng": -75.8, "species": ["orignal", "chevreuil", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Rabaska Lodge", "region": "Laurentides", "lat": 47.2, "lng": -75.5, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie des 100 Lacs Sud", "region": "Laurentides", "lat": 46.7, "lng": -75.2, "species": ["orignal", "chevreuil", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoiries Essipit", "region": "Côte-Nord", "lat": 48.3, "lng": -69.5, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie du Lac Dionne", "region": "Côte-Nord", "lat": 49.0, "lng": -68.0, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Pourvoirie des Grands-Ducs", "region": "Côte-Nord", "lat": 49.5, "lng": -67.5, "species": ["orignal", "ours", "caribou"], "type": "avec_droits_exclusifs"},
    {"name": "Club Tadoussac", "region": "Côte-Nord", "lat": 48.1, "lng": -69.7, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Chalets Villégiature & Pourvoirie Daaquam", "region": "Chaudière-Appalaches", "lat": 46.5, "lng": -70.0, "species": ["chevreuil", "orignal", "ours"], "type": "sans_droits_exclusifs"},
    {"name": "Domaine Lac Brouillard", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.5, "lng": -71.0, "species": ["orignal", "ours"], "type": "avec_droits_exclusifs"},
    {"name": "Les pourvoiries de Charlevoix", "region": "Charlevoix", "lat": 47.5, "lng": -70.5, "species": ["orignal", "ours", "chevreuil"], "type": "avec_droits_exclusifs"},
]

# ===========================================
# REFUGES FAUNIQUES
# ===========================================
QUEBEC_REFUGES_FAUNIQUES = [
    {"name": "Refuge faunique de la Grande-Île", "region": "Montérégie", "lat": 46.0, "lng": -73.1, "description": "Îles de Berthier-Sorel, grande héronnière"},
    {"name": "Refuge faunique de la Rivière-des-Mille-Îles", "region": "Laval/Laurentides", "lat": 45.6, "lng": -73.8, "description": "10 îles sur terres privées"},
    {"name": "Refuge faunique de Pointe-de-l'Est", "region": "Îles-de-la-Madeleine", "lat": 47.5, "lng": -61.5, "description": "Site de nidification du pluvier siffleur"},
    {"name": "Refuge faunique de Deux-Montagnes", "region": "Laurentides", "lat": 45.5, "lng": -74.0, "description": "Habitat de la couleuvre brune"},
    {"name": "Refuge faunique de l'Îlet-aux-Alouettes", "region": "Côte-Nord", "lat": 48.2, "lng": -69.7, "description": "Colonie d'oiseaux à l'embouchure du Saguenay"},
    {"name": "Refuge faunique de l'Île-Laval", "region": "Côte-Nord", "lat": 48.7, "lng": -69.1, "description": "Héronnière et colonie de mouettes"},
    {"name": "Refuge faunique Pierre-Étienne-Fortin", "region": "Montérégie", "lat": 45.4, "lng": -73.3, "description": "Rivière Richelieu, habitat du fouille-roche gris"},
    {"name": "Refuge faunique des Battures-de-Saint-Fulgence", "region": "Saguenay-Lac-Saint-Jean", "lat": 48.4, "lng": -70.9, "description": "Halte migratoire pour la sauvagine"},
    {"name": "Refuge faunique de Pointe-du-Lac", "region": "Mauricie", "lat": 46.3, "lng": -72.7, "description": "Habitat pour la sauvagine, canards plongeurs"},
]

# ===========================================
# RÉGIONS DE CHASSE DU QUÉBEC
# ===========================================
QUEBEC_HUNTING_REGIONS = [
    {"id": 1, "name": "Bas-Saint-Laurent", "center_lat": 48.0, "center_lng": -68.5},
    {"id": 2, "name": "Saguenay-Lac-Saint-Jean", "center_lat": 48.5, "center_lng": -71.5},
    {"id": 3, "name": "Capitale-Nationale", "center_lat": 47.0, "center_lng": -71.5},
    {"id": 4, "name": "Mauricie", "center_lat": 47.0, "center_lng": -73.0},
    {"id": 5, "name": "Estrie", "center_lat": 45.5, "center_lng": -71.5},
    {"id": 6, "name": "Montréal", "center_lat": 45.5, "center_lng": -73.6},
    {"id": 7, "name": "Outaouais", "center_lat": 46.5, "center_lng": -76.0},
    {"id": 8, "name": "Abitibi-Témiscamingue", "center_lat": 48.5, "center_lng": -78.0},
    {"id": 9, "name": "Côte-Nord", "center_lat": 50.0, "center_lng": -66.0},
    {"id": 10, "name": "Nord-du-Québec", "center_lat": 53.0, "center_lng": -75.0},
    {"id": 11, "name": "Gaspésie-Îles-de-la-Madeleine", "center_lat": 48.8, "center_lng": -65.0},
    {"id": 12, "name": "Chaudière-Appalaches", "center_lat": 46.5, "center_lng": -70.5},
    {"id": 13, "name": "Laval", "center_lat": 45.6, "center_lng": -73.7},
    {"id": 14, "name": "Lanaudière", "center_lat": 46.5, "center_lng": -73.5},
    {"id": 15, "name": "Laurentides", "center_lat": 46.5, "center_lng": -75.0},
    {"id": 16, "name": "Montérégie", "center_lat": 45.5, "center_lng": -73.0},
    {"id": 17, "name": "Centre-du-Québec", "center_lat": 46.0, "center_lng": -72.0},
]

# ===========================================
# ESPÈCES CHASSABLES AU QUÉBEC
# ===========================================
QUEBEC_HUNTABLE_SPECIES = {
    "orignal": {
        "name_fr": "Orignal",
        "name_en": "Moose",
        "emoji": "🫎",
        "season": "Septembre - Octobre",
        "zones": "Toutes les zones sauf exceptions",
        "regulations_url": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse/gibiers/orignal"
    },
    "chevreuil": {
        "name_fr": "Cerf de Virginie",
        "name_en": "White-tailed Deer",
        "emoji": "🦌",
        "season": "Octobre - Novembre",
        "zones": "Zones 4 à 20 (sud du Québec)",
        "regulations_url": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse/gibiers/cerf-de-virginie"
    },
    "ours": {
        "name_fr": "Ours noir",
        "name_en": "Black Bear",
        "emoji": "🐻",
        "season": "Printemps (Mai-Juin) et Automne (Août-Octobre)",
        "zones": "Toutes les zones",
        "regulations_url": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse/gibiers/ours-noir"
    },
    "caribou": {
        "name_fr": "Caribou",
        "name_en": "Caribou",
        "emoji": "🦌",
        "season": "Août - Janvier (selon zone)",
        "zones": "Zones nordiques (23, 24)",
        "regulations_url": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse/gibiers/caribou"
    },
    "dindon": {
        "name_fr": "Dindon sauvage",
        "name_en": "Wild Turkey",
        "emoji": "🦃",
        "season": "Printemps (Avril-Mai) et Automne (Octobre)",
        "zones": "Zones 5 à 10 (sud du Québec)",
        "regulations_url": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse/gibiers/dindon-sauvage"
    },
    "petit_gibier": {
        "name_fr": "Petit gibier",
        "name_en": "Small Game",
        "emoji": "🐰",
        "season": "Septembre - Mars",
        "zones": "Toutes les zones",
        "description": "Lièvre, perdrix, gélinotte, tétras"
    },
    "sauvagine": {
        "name_fr": "Sauvagine",
        "name_en": "Waterfowl",
        "emoji": "🦆",
        "season": "Septembre - Décembre",
        "zones": "Zones de passage migratoire",
        "description": "Canards, oies, bernaches"
    }
}

# ===========================================
# LIENS UTILES
# ===========================================
QUEBEC_HUNTING_RESOURCES = {
    "reseauzec": {
        "name": "Réseau ZEC",
        "url": "https://reseauzec.com/",
        "description": "63 zones d'exploitation contrôlée au Québec"
    },
    "sepaq": {
        "name": "Sépaq - Réserves fauniques",
        "url": "https://www.sepaq.com/rf/",
        "description": "Réserves fauniques gérées par la Sépaq"
    },
    "pourvoiries": {
        "name": "Pourvoiries du Québec",
        "url": "https://www.pourvoiries.com/",
        "description": "Plus de 350 pourvoiries au Québec"
    },
    "fedecp": {
        "name": "FédéCP - Où chasser",
        "url": "https://fedecp.com/la-chasse/je-pratique/ou-chasser/",
        "description": "Guide pour trouver où chasser au Québec"
    },
    "gouv_qc": {
        "name": "Gouvernement du Québec - Chasse",
        "url": "https://www.quebec.ca/tourisme-loisirs-sport/activites-sportives-et-de-plein-air/chasse-sportive",
        "description": "Réglementation officielle de la chasse"
    },
    "foret_ouverte": {
        "name": "Forêt ouverte - Carte interactive",
        "url": "https://www.foretouverte.gouv.qc.ca/",
        "description": "Carte interactive des territoires fauniques"
    }
}

def get_all_hunting_territories():
    """Retourne tous les territoires de chasse combinés"""
    territories = []
    
    for zec in QUEBEC_ZECS:
        territories.append({
            **zec,
            "type": "ZEC",
            "icon": "🏕️"
        })
    
    for rf in QUEBEC_RESERVES_FAUNIQUES:
        territories.append({
            **rf,
            "type": "Réserve faunique",
            "icon": "🦌"
        })
    
    for pourv in QUEBEC_POURVOIRIES:
        territories.append({
            **pourv,
            "type": "Pourvoirie",
            "icon": "🏠"
        })
    
    return territories

def search_territories(query: str = None, region: str = None, species: str = None, territory_type: str = None):
    """Recherche de territoires avec filtres"""
    territories = get_all_hunting_territories()
    
    if query:
        query_lower = query.lower()
        territories = [t for t in territories if query_lower in t.get("name", "").lower() or query_lower in t.get("region", "").lower()]
    
    if region:
        territories = [t for t in territories if region.lower() in t.get("region", "").lower()]
    
    if species:
        territories = [t for t in territories if species in t.get("species", [])]
    
    if territory_type:
        type_map = {
            "zec": "ZEC",
            "reserve": "Réserve faunique",
            "pourvoirie": "Pourvoirie"
        }
        target_type = type_map.get(territory_type.lower(), territory_type)
        territories = [t for t in territories if t.get("type") == target_type]
    
    return territories

def get_nearest_territories(lat: float, lng: float, limit: int = 10):
    """Trouve les territoires les plus proches d'une position"""
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Rayon de la Terre en km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    territories = get_all_hunting_territories()
    
    for t in territories:
        t["distance_km"] = haversine(lat, lng, t["lat"], t["lng"])
    
    territories.sort(key=lambda x: x["distance_km"])
    
    return territories[:limit]
