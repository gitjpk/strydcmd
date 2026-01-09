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

## Structure du projet

```
strydcmd/
├── strydcmd/           # Package principal
│   ├── __init__.py     # Initialisation du package
│   ├── stryd_api.py    # Client API Stryd
│   └── main.py         # Point d'entrée CLI
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
- ✅ Affichage des détails des activités (distance, allure, puissance, fréquence cardiaque)
- ✅ Téléchargement des fichiers FIT des activités
- ✅ Export aux formats CSV/JSON
- ✅ Calcul et distribution des zones d'entraînement

## Prochaines étapes

- 🔜 Carte d'activité (polyline)
- 🔜 Graphiques d'activité

## API Stryd

L'outil utilise les endpoints suivants de l'API Stryd:
- `POST /b/email/signin` - Authentification
- `GET /b/api/v1/users/calendar` - Récupération des activités
- `GET /b/api/v1/activities/{id}/fit` - Téléchargement du fichier FIT

## Développement

Pour contribuer ou modifier le code:

1. Le code principal est dans `strydcmd/stryd_api.py`
2. Le point d'entrée CLI est dans `strydcmd/main.py`
3. Les tests peuvent être lancés avec la commande `stryd`

## Licence

À définir
