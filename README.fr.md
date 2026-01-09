# Stryd Command Line Tool

[🇬🇧 English version](README.md)

Un outil en ligne de commande pour se connecter à l'API Stryd et récupérer vos données d'entraînement.

## Installation

1. Cloner ou créer le projet dans votre environnement

2. Activer l'environnement virtuel (déjà créé):
```bash
source .venv/bin/activate
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Installer le package en mode développement:
```bash
pip install -e .
```

## Configuration

1. Copier le fichier d'exemple de configuration:
```bash
cp .env.example .env
```

2. Éditer le fichier `.env` et ajouter vos identifiants Stryd:
```
STRYD_EMAIL=votre.email@exemple.com
STRYD_PASSWORD=votre_mot_de_passe
```

## Utilisation

### Tester l'authentification

Assurez-vous que l'environnement virtuel est activé:
```bash
source .venv/bin/activate
stryd
```

Ou utilisez le chemin complet sans activer:
```bash
.venv/bin/stryd
```

Ou directement avec Python:
```bash
.venv/bin/python -m strydcmd.main
```

### Récupérer les activités

Récupérer les activités des 30 derniers jours (par défaut):
```bash
stryd -g
# ou
stryd --get
```

Spécifier un nombre de jours personnalisé:
```bash
stryd -g 7    # 7 derniers jours
stryd -g 20   # 20 derniers jours
stryd --get 60  # 60 derniers jours
```

### Récupérer les activités d'une date spécifique

Récupérer les activités d'une date précise (format: AAAAMMJJ):
```bash
stryd -d 20260108          # Activités du 8 janvier 2026
stryd --date 20251225      # Activités du 25 décembre 2025
```

### Filtrer les activités par tag

Filtrer les activités par un tag spécifique (doit être combiné avec -g):
```bash
stryd -g 30 -t "barcelona 26"        # Activités des 30 derniers jours avec le tag "barcelona 26"
stryd -g 7 --tag "entraînement marathon" # Activités des 7 derniers jours avec un tag spécifique
```

Si le tag n'est pas trouvé, l'outil affichera les tags disponibles dans vos activités récentes.

### Télécharger les fichiers FIT

Télécharger les fichiers FIT des activités récupérées:
```bash
stryd -g 7 -f                    # Télécharger les FIT des 7 derniers jours
stryd -g 30 --fit                # Télécharger les FIT des 30 derniers jours
stryd -d 20260108 -f             # Télécharger les FIT d'une date spécifique
stryd -g 7 -t "barcelona 26" -f  # Télécharger les FIT des activités avec un tag spécifique
```

Spécifier un répertoire de destination personnalisé:
```bash
stryd -g 7 -f -o mes_fichiers_fit/    # Sauvegarder dans un répertoire personnalisé
```

### Exporter en CSV ou JSON

Exporter les activités au format CSV ou JSON:
```bash
stryd -g 30 -e activites.csv     # Export CSV
stryd -g 7 -e donnees.json       # Export JSON
stryd -d 20260108 -e jour.csv    # Export date spécifique
```

### Synchroniser les activités dans une base de données

La commande `strydsync` synchronise les données détaillées des activités dans une base SQLite locale, incluant toutes les séries temporelles (puissance, fréquence cardiaque, GPS, etc.):

```bash
# Synchroniser les 30 derniers jours (par défaut)
strydsync

# Synchroniser un nombre de jours personnalisé
strydsync 60     # 60 derniers jours
strydsync 90     # 90 derniers jours

# Synchroniser une date spécifique
strydsync -d 20260108     # 8 janvier 2026

# Forcer la resynchronisation (écraser les données existantes)
strydsync --force         # Resync 30 derniers jours
strydsync 90 --force      # Resync 90 derniers jours

# Taille de lot personnalisée (par défaut: 10 activités par lot)
strydsync 30 --batch-size 5

# Emplacement de base de données personnalisé
strydsync --db /chemin/vers/ma_base.db
```

**Structure de la base de données:**
- `activities`: Métadonnées principales des activités (87 champs)
- `zones_distribution`: Distribution des zones de puissance par activité
- `timeseries_power`: Données de puissance dans le temps (5 métriques)
- `timeseries_kinematics`: Vitesse, distance, cadence, longueur de foulée
- `timeseries_cardio`: Fréquence cardiaque et intervalles RR
- `timeseries_biomechanics`: Temps de contact, oscillation, spring de jambe, etc.
- `timeseries_elevation`: Données d'élévation et de pente
- `gps_points`: Coordonnées GPS pour la cartographie
- `laps`: Marqueurs de tours et étapes d'entraînement

Le processus de synchronisation:
- ✅ Ignore automatiquement les activités déjà synchronisées
- ✅ Affiche la progression avec traitement par lots (10 activités par défaut)
- ✅ Stocke les détails complets incluant toutes les séries temporelles
- ✅ Supporte le mode force pour mettre à jour les activités existantes
- ✅ Crée une base SQLite avec des tables indexées pour des requêtes efficaces

**Exemple de sortie:**
```
============================================================
Début de la synchronisation: 30 activités à traiter
Taille de lot: 10 activités
Mode force: OFF
============================================================

--- Lot 1/3 (activités 1-10) ---
  [1/30] → Récupération des détails pour Course matinale (2026-01-08)...
  [1/30] ✓ Course matinale (2026-01-08) - sauvegardée
  [2/30] ✓ Entraînement soir (2026-01-07) - déjà synchronisée, ignorée
  ...

============================================================
Synchronisation terminée!
  • Nouvelles/Mises à jour: 15
  • Ignorées:              12
  • Échouées:              3
  • Total en base:         1234
============================================================
```

## Structure du projet

```
strydcmd/
├── strydcmd/           # Package principal
│   ├── __init__.py     # Initialisation du package
│   ├── stryd_api.py    # Client API Stryd
│   ├── main.py         # Point d'entrée CLI pour la commande stryd
│   ├── sync.py         # Point d'entrée CLI pour la commande strydsync
│   └── database.py     # Gestion de la base de données SQLite
├── .env.example        # Exemple de configuration
├── .gitignore          # Fichiers à ignorer par Git
├── pyproject.toml      # Configuration du projet
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```

## Fonctionnalités actuelles

- ✅ Authentification avec l'API Stryd
- ✅ Gestion du token de session
- ✅ Récupération de l'ID utilisateur
- ✅ Récupération des activités sur une période personnalisée
- ✅ Récupération des activités d'une date spécifique
- ✅ Filtrage des activités par tag
- ✅ Affichage détaillé des activités (distance, allure, puissance, FC, zones, etc.)
- ✅ Téléchargement des fichiers FIT des activités
- ✅ Export aux formats CSV/JSON avec zones de puissance
- ✅ Calcul et distribution des zones d'entraînement
- ✅ **Synchronisation des données détaillées dans une base SQLite**
- ✅ **Stockage complet des séries temporelles (puissance, cinématique, cardio, biomécanique, GPS)**
- ✅ **Synchronisation intelligente avec détection des doublons et saut**
- ✅ **Traitement par lots avec suivi de progression**

## Prochaines étapes

- 🔜 Interrogation et analyse des données de la base
- 🔜 Visualisation des activités depuis la base
- 🔜 Analyse de charge d'entraînement et tendances
- 🔜 Rendu de carte d'activité (depuis les points GPS)
- 🔜 Graphiques d'activité (puissance, FC, allure, élévation)

## API Stryd

L'outil utilise les endpoints suivants de l'API Stryd:
- `POST /b/email/signin` - Authentification
- `GET /b/api/v1/users/calendar` - Récupération des résumés d'activités
- `GET /b/api/v1/activities/{id}` - Récupération des données détaillées (139 champs, séries temporelles)
- `GET /b/api/v1/activities/{id}/fit` - Téléchargement du fichier FIT

## Développement

Pour contribuer ou modifier le code:

1. Le code principal est dans `strydcmd/stryd_api.py`
2. Le point d'entrée CLI est dans `strydcmd/main.py`
3. Les tests peuvent être lancés avec la commande `stryd`

## Licence

À définir
