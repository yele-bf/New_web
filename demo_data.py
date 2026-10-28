#!/usr/bin/env python3
"""Données fictives de démonstration pour le dashboard Yélé.

Injecte des tests réalistes en base (MongoDB locale) pour montrer à quoi
ressemble le dashboard avec du monde : réseau MOBILE (2G, 3G, 4G, 4G+, 5G)
ET réseau FIXE (WiFi), 3 opérateurs mobiles, 4 FAI fixe, 20 lieux du
Burkina Faso (Ouagadougou, grandes villes, communes rurales), des périodes
étalées sur un an (pour les grains heure/jour/semaine/mois/années).

Chaque document fictif porte `fiction: true` : les vrais tests restent
intacts et tout le jeu peut être retiré du coup :

    python demo_data.py           # injecte (~430 tests fictifs)
    python demo_data.py --clean   # supprime TOUS les documents fictifs

Schéma : miroir de mobiletest/database/mongodb/mongodb.go (Document) —
dl/ul/ping/jitter stockés en TEXTE, timestamp naive UTC (le Burkina est en
GMT+0, l'affichage serveur est donc direct).
"""
import datetime as dt
import random
import sys

from pymongo import MongoClient

DB = "yele_speedtest"
COLL = "speedtest_results"
SERVER = "http://192.168.11.131:8989"
random.seed(42)

# ─── Lieux ───────────────────────────────────────────────────────────────────
# (libellé, ville ou '', lat, lng, classe) — classe: urbain | ville | rural
ZONES = [
    # Ouagadougou (quartiers documentés par le géocodage)
    ("Patte d'Oie", "Ouagadougou", 12.3711, -1.5683, "urbain"),
    ("Karpala", "Ouagadougou", 12.3978, -1.5452, "urbain"),
    ("Gounghin", "Ouagadougou", 12.3813, -1.4789, "urbain"),
    ("Dassasgho", "Ouagadougou", 12.4066, -1.5559, "urbain"),
    ("Tanghin", "Ouagadougou", 12.4167, -1.5231, "urbain"),
    ("Zone du Bois", "Ouagadougou", 12.3572, -1.5410, "urbain"),
    ("Somgandé", "Ouagadougou", 12.3301, -1.5055, "urbain"),
    ("Cissin", "Ouagadougou", 12.3444, -1.5852, "urbain"),
    ("Kossodo", "Ouagadougou", 12.3497, -1.5556, "urbain"),
    # Grandes villes (2 quartiers chacune)
    ("Accart-Ville", "Bobo-Dioulasso", 11.1850, -4.3020, "ville"),
    ("Sarfalao", "Bobo-Dioulasso", 11.1650, -4.2800, "ville"),
    ("Secteur 4", "Koudougou", 12.2530, -2.3620, "ville"),
    ("Pissy", "Koudougou", 12.2700, -2.4100, "ville"),
    ("Secteur 6", "Ouahigouya", 13.5830, -2.4220, "ville"),
    ("Secteur 7", "Kaya", 13.0920, -1.0840, "ville"),
    ("Secteur 5", "Banfora", 10.6330, -4.7670, "ville"),
    ("Secteur 3", "Fada N'Gourma", 12.0620, 0.3590, "ville"),
    ("Secteur 4", "Tenkodogo", 11.7800, -0.3690, "ville"),
    ("Secteur 2", "Dédougou", 12.4630, -3.4640, "ville"),
    # Communes rurales (2G/3G attendues)
    ("Rollo", "", 12.4800, -2.3800, "rural"),
    ("Sabou", "", 12.0500, -2.2200, "rural"),
    ("Yako", "", 12.9600, -2.2600, "rural"),
    ("Réo", "", 12.3200, -2.4700, "rural"),
    ("Léo", "", 11.1000, -2.1000, "rural"),
    ("Pô", "", 11.1700, -1.1500, "rural"),
    ("Dori", "", 14.0300, -0.0300, "rural"),
    ("Gaoua", "", 10.3300, -3.1800, "rural"),
    ("Nouna", "", 12.7300, -3.8700, "rural"),
]

# ─── Profils de mesure ──────────────────────────────────────────────────────
# Plages (min, max) réalistes observées sur le terrain burkinabè.
TECH_PROFILE = {
    "2G":  dict(dl=(0.08, 0.6),  ul=(0.04, 0.3),  ping=(320, 720), st=(4, 22),  bl=(6000, 14000)),
    "3G":  dict(dl=(0.8, 4.5),   ul=(0.3, 1.8),   ping=(90, 260),   st=(15, 45), bl=(4000, 9500)),
    "4G":  dict(dl=(6, 48),      ul=(2, 18),      ping=(25, 95),    st=(40, 90), bl=(900, 4200)),
    "4G+": dict(dl=(25, 95),     ul=(8, 35),      ping=(15, 55),    st=(60, 95), bl=(600, 2600)),
    "5G":  dict(dl=(120, 450),   ul=(40, 120),    ping=(8, 28),     st=(75, 99), bl=(450, 1600)),
}
# Pondérations techno par opérateur mobile (Ouaga, urbain).
TECH_WEIGHTS = {
    "Orange Burkina Faso": {"2G": 5, "3G": 15, "4G": 45, "4G+": 25, "5G": 10},
    "Telecel Faso":        {"2G": 15, "3G": 35, "4G": 40, "4G+": 10, "5G": 0},
    "Moov Africa":         {"2G": 10, "3G": 25, "4G": 48, "4G+": 14, "5G": 3},
}
# Ajustement selon la classe de lieu.
CLASS_FACTOR = {
    "urbain": {"2G": 1.0, "3G": 1.0, "4G": 1.0, "4G+": 1.0, "5G": 1.0},
    "ville":  {"2G": 1.2, "3G": 1.7, "4G": 1.0, "4G+": 0.6, "5G": 0.2},
    "rural":  {"2G": 3.0, "3G": 2.2, "4G": 0.5, "4G+": 0.15, "5G": 0.0},
}
FAI_PROFILE = {  # réseau FIXE (box / connexion filaire)
    "ONATEL (Office National des Telecommunications, PTT)": dict(dl=(6, 45),   ul=(1.5, 12), ping=(18, 70)),
    "Orange Burkina Faso":                                 dict(dl=(25, 220), ul=(5, 60),   ping=(7, 40)),
    "Moov Africa":                                         dict(dl=(12, 95),  ul=(3, 35),   ping=(10, 55)),
    "GVA":                                                 dict(dl=(8, 60),   ul=(2, 20),   ping=(15, 80)),
}
FAI_WEIGHTS = [45, 25, 20, 10]
SIM_OPERATORS = ["Orange Burkina Faso", "Moov Africa BF", "Telecel Faso"]
DEVICES = ["Tecno Spark 20 Pro", "Samsung Galaxy A15", "Infinix Hot 40",
           "Xiaomi Redmi 13C", "itel A60s", "Realme C53", "Oppo A18",
           "Tecno Camon 20", "Samsung Galaxy A05", "Infinix Note 40"]

# ─── Périodes (grains heure/jour/semaine/mois/années tous exercés) ──────────
TIME_BUCKETS = [
    (dt.date(2025, 11, 1), dt.date(2025, 12, 31), 0.04),
    (dt.date(2026, 6, 1), dt.date(2026, 7, 31), 0.10),
    (dt.date(2026, 8, 1), dt.date(2026, 8, 31), 0.18),
    (dt.date(2026, 9, 1), dt.date(2026, 9, 30), 0.56),
    (dt.date(2026, 10, 1), dt.date(2026, 10, 2), 0.12),
]

def rand_time() -> dt.datetime:
    r = random.random()
    acc = 0.0
    start, end = TIME_BUCKETS[0][0], TIME_BUCKETS[0][1]
    for s, e, w in TIME_BUCKETS:
        acc += w
        start, end = s, e
        if r <= acc:
            break
    days = (end - start).days
    day = start + dt.timedelta(days=random.randint(0, max(days, 0)))
    return dt.datetime(day.year, day.month, day.day,
                       random.randint(5, 23), random.randint(0, 59),
                       random.randint(0, 59))

def pick_zone(classes=("urbain", "ville", "rural"), weights=(0.40, 0.40, 0.20)):
    # On choisit d'abord la classe de lieu, puis un lieu dans cette classe.
    classe = random.choices(classes, weights=weights, k=1)[0]
    pool = [z for z in ZONES if z[4] == classe]
    return random.choice(pool)

def pick_tech(op: str, classe: str) -> str:
    base = TECH_WEIGHTS[op]
    f = CLASS_FACTOR[classe]
    techs, weights = [], []
    for t, w in base.items():
        v = w * f[t]
        if v > 0:
            techs.append(t)
            weights.append(v)
    return random.choices(techs, weights=weights, k=1)[0]

def rnd(a, b, digits=2):
    return round(random.uniform(a, b), digits)

def build_common(ts, op, net, loc, city, lat, lng, device):
    return {
        "uuid": f"DEMO{random.randint(10**15, 10**16 - 1)}",
        "timestamp": ts,
        "server": SERVER,
        "operator": op,
        "network_type": net,
        "device_model": device,
        "location": loc,
        "latitude": lat,
        "longitude": lng,
        "city": city,
        "country": "Burkina Faso",
        "measurement_type": "active",
        "fiction": True,
    }

def mobile_doc(i):
    op = random.choices(list(TECH_WEIGHTS), weights=[50, 25, 25], k=1)[0]
    z = pick_zone(("urbain", "ville", "rural"), (0.35, 0.45, 0.20))
    tech = pick_tech(op, z[4])
    p = TECH_PROFILE[tech]
    dl, ul = rnd(*p["dl"]), rnd(*p["ul"])
    ping = rnd(*p["ping"], 1)
    loc = f"{z[0]}, {z[1]}, Burkina Faso" if z[1] else f"{z[0]}, Burkina Faso"
    d = build_common(rand_time(), op, tech, loc, z[1] or z[0],
                     z[2] + random.uniform(-0.004, 0.004),
                     z[3] + random.uniform(-0.004, 0.004),
                     random.choice(DEVICES))
    d.update({
        "dl": f"{dl:.2f}", "ul": f"{ul:.2f}",
        "ping": f"{ping:.1f}", "jitter": f"{rnd(1, max(ping / 4, 2), 1):.1f}",
        "sim_operator": op, "cellular_tech": tech, "sim_slot": random.randint(0, 1),
        "signal_dbm": random.randint(-105, -65), "signal_level": random.randint(1, 4),
        "qoe_rating": random.choices([5, 4, 3, 2, 1], weights=[25, 35, 25, 10, 5])[0],
        "qoe_sat": random.choice(["very_satisfied", "satisfied", "neutral", "neutral"]),
    })
    if tech in ("4G", "4G+", "5G"):  # RSRP/RSRQ inexistants en 2G/3G (comme en prod)
        d["rsrp"] = random.randint(-115, -75)
        d["rsrq"] = random.randint(-15, -6)
    add_streaming_browse(d, p)
    return d

def fixe_doc(i):
    op = random.choices(list(FAI_PROFILE), weights=FAI_WEIGHTS, k=1)[0]
    z = pick_zone(("urbain", "ville", "rural"), (0.50, 0.40, 0.10))
    p = FAI_PROFILE[op]
    dl, ul = rnd(*p["dl"]), rnd(*p["ul"])
    ping = rnd(*p["ping"], 1)
    loc = f"{z[0]}, {z[1]}, Burkina Faso" if z[1] else f"{z[0]}, Burkina Faso"
    d = build_common(rand_time(), op, "WiFi", loc, z[1] or z[0],
                     z[2] + random.uniform(-0.004, 0.004),
                     z[3] + random.uniform(-0.004, 0.004),
                     random.choice(DEVICES))
    d.update({
        "dl": f"{dl:.2f}", "ul": f"{ul:.2f}",
        "ping": f"{ping:.1f}", "jitter": f"{rnd(1, max(ping / 5, 1), 1):.1f}",
        # La SIM reste renseignée même en WiFi (comme les vrais tests) :
        # c'est réseau_type = 'WiFi' qui fait la distinction mobile/fixe.
        "sim_operator": random.choice(SIM_OPERATORS), "cellular_tech": "4G",
        "signal_dbm": random.randint(-75, -40), "signal_level": random.randint(3, 4),
        "qoe_rating": random.choices([5, 4, 3, 2, 1], weights=[30, 35, 25, 7, 3])[0],
        "qoe_sat": random.choice(["very_satisfied", "satisfied", "satisfied", "neutral"]),
    })
    add_streaming_browse(d, dict(st=(45, 95), bl=(500, 3800)))
    return d

def add_streaming_browse(d, p):
    # 20 % des tests sans streaming et 20 % sans navigation : le dashboard
    # traite 0 comme « test non effectué » (niveau gris), pas comme échec.
    if random.random() < 0.80:
        st = rnd(*p["st"], 1)
        d["streaming_startup_ms"] = random.randint(600, 3500)
        d["streaming_rebuffer_count"] = random.choices([0, 1, 2, 3], weights=[50, 25, 15, 10])[0]
        d["streaming_rebuffer_ratio"] = rnd(0, 0.25, 3)
        d["streaming_max_resolution"] = "2160p" if st >= 85 else ("1080p" if st >= 60 else "720p")
        d["streaming_score"] = st
    else:
        d["streaming_score"] = 0.0
        d["streaming_max_resolution"] = ""
    if random.random() < 0.80:
        bl = rnd(*p["bl"], 0)
        d["browsing_avg_load_ms"] = bl
        d["browsing_success_rate"] = round(random.uniform(0.8, 1.0), 2)
        d["browsing_pages_tested"] = random.randint(5, 7)
        d["browsing_score"] = round(max(20, min(99, 100 - bl / 150)), 1)
    else:
        d["browsing_avg_load_ms"] = 0.0
        d["browsing_score"] = 0.0

def main():
    coll = MongoClient("mongodb://localhost:27017/")[DB][COLL]
    if "--clean" in sys.argv:
        res = coll.delete_many({"fiction": True})
        print(f"{res.deleted_count} documents fictifs supprimés.")
        return
    docs = [mobile_doc(i) for i in range(850)] + [fixe_doc(i) for i in range(300)]
    random.shuffle(docs)
    coll.insert_many(docs)
    total = coll.count_documents({})
    print(f"{len(docs)} tests fictifs insérés (850 mobile + 300 fixe).")
    print(f"Total en base : {total} documents ({coll.count_documents({'fiction': True})} fictifs).")

if __name__ == "__main__":
    main()
