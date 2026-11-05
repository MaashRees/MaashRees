<p align="center">
  <img src="assets/banner.svg" alt="maashrees, Ingénieur Logiciel et Solutions IA" width="100%">
</p>

<p align="center">
  <img src="assets/terminal.svg" alt="Terminal : agents, connecteur MCP en lecture seule, tests et déploiement" width="100%">
</p>

<p align="center">
  <a href="https://www.maashrees.com"><img alt="Portfolio" src="https://img.shields.io/badge/PORTFOLIO-maashrees.com-00b8db?style=for-the-badge&labelColor=030303"></a>
  <a href="https://www.linkedin.com/in/seer-mensah-assiakoley-542628198/"><img alt="LinkedIn" src="https://img.shields.io/badge/LINKEDIN-Seer_Mensah--Assiakoley-ad46ff?style=for-the-badge&labelColor=030303"></a>
  <a href="mailto:seer.mensaha@maashrees.com"><img alt="Mail" src="https://img.shields.io/badge/MAIL-seer.mensaha%40maashrees.com-fdc700?style=for-the-badge&labelColor=030303"></a>
</p>

```bash
$ whoami
Seer MENSAH-ASSIAKOLEY   # alias maashrees

$ pwd
Paris, France

$ cat mission.txt
Livrer des produits logiciels et des systèmes d'IA qui servent un usage métier réel,
du prototype à la mise en production.

$ ls ~/focus
agents/   mcp/   donnees/   plateformes-metier/   mobile/
```

<img src="assets/divider.svg" alt="" width="100%">

## 💡 À propos

Ingénieur logiciel, je construis des **solutions d'IA appliquées** et des **plateformes métier** : applications web et mobiles, automatisations, pipelines de données et agents IA branchés sur les outils de l'entreprise. J'opère de bout en bout : cadrage du besoin, architecture, développement, déploiement auto-hébergé, documentation et suivi.

Ma façon de travailler :

- **Partir du besoin métier**, pas de la techno : cadrer, documenter les décisions (ADR), livrer par petits incréments mesurables.
- **Rendre l'IA utile et fiable** : agents supervisés, lecture seule d'abord, validation humaine avant toute action sensible, traçabilité de chaque décision.
- **Livrer pour de vrai** : intégration et déploiement continus, sécurité des données au niveau base, tests et documentation maintenue.

<img src="assets/divider.svg" alt="" width="100%">

## 🧭 Ce sur quoi je travaille

### 🤖 Solutions IA & agents
Plateforme d'agents IA pour une holding et ses filiales (retail de vélos électriques, restauration) : un orchestrateur qui route sans agir, des agents spécialisés par domaine, une couche de supervision qui relit tout avant envoi externe, une mémoire de travail et une mémoire à long terme. Connecteurs **MCP** pour ouvrir les applications internes aux assistants IA, avec des garde-fous stricts : jetons personnels, écritures validées par un administrateur, lecture seule par défaut. Outil de tickets internes où l'IA propose une priorisation et l'humain décide, avec création automatique d'issues.

```mermaid
flowchart LR
    U["Utilisateur<br/>(messagerie)"] --> A["Orchestrateur<br/>route sans agir"]
    A --> D1["Agent support"]
    A --> D2["Agent documents"]
    A --> D3["Agent logistique"]
    A --> D4["Agents de veille"]
    D1 --> P["Supervision<br/>relecture obligatoire"]
    D2 --> P
    D3 --> P
    D4 --> P
    P --> O["Envoi externe validé"]
    D1 -.-> M[("Mémoire<br/>Redis, PostgreSQL, pgvector")]
```

Principe des connecteurs MCP : l'assistant n'écrit jamais directement dans les données métier.

```mermaid
flowchart LR
    AI["Assistant IA"] -->|jeton personnel| C["Connecteur MCP"]
    C -->|lecture seule| V[("Vues durcies")]
    C -->|demande d'écriture| Q["File d'attente"]
    Q -->|validation par un admin| W[("Données métier")]
```

### 🏢 Plateformes métier & data
Applications internes pour une holding qui regroupe un réseau de boutiques de vélos électriques et un restaurant : gestion RH et planning, émargement et éléments variables de paie, **réconciliation de stock** à partir d'exports avec relecture assistée par IA, **réconciliation de paiements** entre caisse, plateformes de paiement et comptabilité, commandes fournisseurs et suivi client, SAV et atelier, tableaux de bord de ventes multi-boutiques, gestion de tâches multi-projets avec génération de projets par IA. Pipelines d'import avec quarantaine des données invalides, contrôle d'écarts, et hub de documentation synchronisé automatiquement.

### 📱 Produits web & mobile
Application mobile multiplateforme de mise en relation (Flutter, back-end Spring Boot, paiement en ligne, géolocalisation, notifications, pipeline Python d'analyse), PWA métier, sites vitrines et outils de réservation légers.

### 🧠 Data science & machine learning
Classification de texte par transformers, prédiction de prix, prédiction sportive (XGBoost), graphes de connaissances, vision et OCR, compression de modèles, clonage et traduction de voix, scraping et veille automatisée.

### ⚙️ Infrastructure & automatisation
Hébergement auto-hébergé sur VPS (Coolify, Docker, reverse proxy, HTTPS automatique), workflows **n8n** versionnés, Supabase auto-hébergé, CI GitHub Actions, observabilité (logs centralisés).

<img src="assets/divider.svg" alt="" width="100%">

## 🛠 Stack technique

<p align="center">
  <img src="assets/stack-3d.svg" alt="Graphe 3D en rotation du stack : IA et LLM (API Anthropic, OpenRouter, MCP), backend et données, front et mobile, DevOps" width="100%">
</p>

### Utilisation des API d'IA

| API | Ce que j'en fais | Détails |
| :-- | :-- | :-- |
| **API Anthropic** (Claude) | Agents d'orchestration, de domaine et de supervision, analyse de tickets, génération de projets, relecture assistée de rapprochements | L'IA propose, l'humain décide ; relecture avant tout envoi externe |
| **OpenRouter** | Accès à plusieurs modèles par une seule API : vision et conseils personnalisés, traduction | Choix du fournisseur par configuration, avec bascule entre cloud et modèle local |
| **MCP** | Exposer des applications métier aux assistants IA | Lecture seule par défaut, écritures en file d'attente validées, jeton personnel par utilisateur |

### IA & Agents
![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API_multi--modèles-6467F2?style=for-the-badge)
![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-black?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-337AB7?style=for-the-badge)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)

### Backend & Data
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

### Frontend & Mobile
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Kotlin](https://img.shields.io/badge/Kotlin-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

### Cloud & DevOps
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Netlify](https://img.shields.io/badge/Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Azure](https://img.shields.io/badge/Azure_AI-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![OVH](https://img.shields.io/badge/Cloud-OVH-123f6e?style=for-the-badge)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

### Bases solides
C · C++ · Algorithmique · Compilation (Flex/Bison) · Programmation réseau · Systèmes distribués · Architecture microservices

<img src="assets/divider.svg" alt="" width="100%">

## 📊 En chiffres

Statistiques calculées sur l'ensemble de mes dépôts, privés comme publics (64 dépôts analysés, dont 58 privés).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/langages-dark.svg">
    <img alt="Répartition du code par langage" src="assets/langages-light.svg" width="760">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/rythme-dark.svg">
    <img alt="Nombre de dépôts créés par trimestre" src="assets/rythme-light.svg" width="760">
  </picture>
</p>

<p align="center">
  <img alt="Graphique de contributions GitHub" src="https://ghchart.rshah.org/0969da/MaashRees" width="760">
</p>

<img src="assets/divider.svg" alt="" width="100%">

## 📂 Réalisations

### Professionnelles (détails confidentiels)

| Domaine | Ce que j'ai construit |
| :-- | :-- |
| **Agents IA** | Plateforme d'agents Claude (orchestrateur, agents par domaine, supervision), mémoire Redis et PostgreSQL, intégrations messagerie, documents et courriel, centre de contrôle d'administration |
| **MCP** | Connecteurs pour exposer des applications métier aux assistants IA, avec jeton par utilisateur et file d'écriture validée |
| **RH & paie** | PWA de planning, congés, émargement et préparation de la paie, sécurité des données par rôle et périmètre au niveau base |
| **Stocks & achats** | Réconciliation hebdomadaire du stock avec comptages physiques et avis IA, commandes fournisseurs, suivi de colis et notifications clients |
| **Finance** | Réconciliation de paiements multi-sources avec détection d'écarts |
| **Ventes** | Pipeline d'import, détection d'écarts et tableaux de bord de ventes multi-boutiques |
| **SAV & atelier** | Prise en charge SAV, suivi de réparation et de montage, boîte de réception assistée par IA |
| **Pilotage** | Tickets internes avec priorisation IA, plateforme de tâches multi-projets, hub de documentation synchronisé quotidiennement |
| **Mobile** | Application mobile multiplateforme de mise en relation avec paiement et alertes, et son back-end |
| **Opérations** | Mise en route de vélos avec signature du client et envoi de documents, outil de réservation pour la restauration, déploiement et durcissement de serveurs |

### Projets personnels & produits

| Projet | Description |
| :-- | :-- |
| **Hub capillaire IA** | Catalogue visuel de coiffures avec clustering IA (HDBSCAN, embeddings), OCR, conseils météo et agenda (React, FastAPI, Supabase, n8n) |
| **Vision board 3D** | PWA personnelle où chaque rêve est une étoile dans un ciel 3D interactif, avec étapes, inspirations intégrées et partage depuis les réseaux sociaux (Next.js, Supabase, Docker) |
| **Nutrition & sport** | Journal de repas multimodal (photo et OCR, code-barres, saisie vocale), cibles adaptatives et moteur d'entraînement (React, FastAPI, Supabase) |
| **Agrégateur de plannings** | Centralise Google Sheets, Google Calendar et iCal, détecte les changements d'horaires et notifie |
| **Gouvernance multi-agents** | Un agent supérieur pilote, délègue et génère des sous-agents, avec cockpit de monitoring |
| **Finances personnelles** | Import CSV et Excel multi-banques avec détection de doublons et tableau de bord |
| **Prédiction Coupe du monde 2026** | Modèle XGBoost combinant statistiques de clubs et classements Elo |
| **Planificateur de voyages** | Optimisation d'itinéraire (Haversine), scraping de tarifs et veille des prix |
| **Suivi de candidatures** | Application MERN multi-utilisateur avec JWT, Docker et déploiement sur VPS |
| **Voix** | Clonage de voix en local et traducteur vocal temps réel (Whisper, LLM, synthèse vocale) |
| **Serveur de logs** | Collecte centralisée de logs par API HTTP, image Docker |
| **Portfolios créatifs** | Plusieurs portfolios photo, dont des versions 3D et plein écran (Next.js, Lovable, Figma) |
| **Automatisation** | Bibliothèque de workflows n8n versionnés par domaine |

### Projets de formation & collaboration

| Projet | Description |
| :-- | :-- |
| **Routage de tickets (NLP)** | DistilBERT fine-tuné, API FastAPI conteneurisée, déployée en ligne, F1 pondéré de 0,77 |
| **Graphe de musées** | 137 000 œuvres et leurs artistes dans Neo4j, ETL Joconde et Wikidata, API et carte interactive |
| **Plateforme IA de documents** | Hackathon : traitement de documents administratifs avec Azure Document Intelligence |
| **Semaine immersive IA** | Plateforme de révision personnalisée par IA (React, Python) |
| **Prix Airbnb** | Pipeline scikit-learn servi par API sur 84 000 logements parisiens, front React/TypeScript |
| **Réservation en microservices** | Architecture C4, MongoDB, Cassandra et verrous Redis contre le surbooking |
| **Assistant de garde-robe** | Application React Native, suggestion de tenue par IA selon la météo |
| **Dépenses partagées** | API REST Django/DRF avec JWT et calcul des remboursements minimaux |
| **Scraping e-commerce** | Collecte de données produits |

### Fondamentaux (licence & master)

Compilateur d'un sous-langage C (Flex/Bison), approximation d'images par algorithme génétique en C, compression d'images par réseaux génératifs (PyTorch, TensorFlow, C++), programmation réseau en Java, jeux et solveurs algorithmiques (Snake, Reversi, Boggle, Slitherlink, taquin, voyageur de commerce) en C et programmation fonctionnelle.

### Veille open source

Je suis et expérimente des projets comme le Google Agent Development Kit, n8n-as-code, des skills de prompting pour Claude, des composants cartographiques MapLibre et des templates Streamlit.

<img src="assets/divider.svg" alt="" width="100%">

## 💼 Expérience

**Ingénieur Logiciel & Solutions IA** · MJY Holding (retail de vélos électriques multi-boutiques et restauration) · alternance · *depuis 11/2026*

- Conception d'une plateforme d'agents IA (orchestrateur, agents de domaine, supervision) et de connecteurs MCP en lecture seule.
- Développement d'applications métier : RH et paie, stocks, réconciliation de paiements, SAV et atelier, tickets internes avec priorisation par IA.
- Déploiement auto-hébergé (VPS, Coolify, Docker), intégration continue, sécurité des données par rôle, documentation et décisions d'architecture.

**Stagiaire Ingénieur Logiciel & Solutions IA** · MJY Holding · stage · *07/2026 – 11/2026*

- Développement d'applications métier internes (RH et planning, SAV et atelier, stocks) et mise en place de l'infrastructure auto-hébergée.
- Premiers automatismes n8n et premières briques de la plateforme d'agents IA.

**Ingénieur logiciel** · VisioTerra · alternance · *10/2024 – 09/2025* · Champs-sur-Marne

- Entraînement de modèles de compression sur images satellites Sentinel-1 (Python, PyTorch, CUDA, OVH Cloud).
- Migration vers PyTorch 2.3 : **-30 % de temps d'exécution**, compression jusqu'à **×250**.
- Scripts de gestion de stockage objet S3, travail en autonomie avec GitLab et Docker.

**Stagiaire ingénieur recherche & développement informatique** · VisioTerra · stage · *05/2024 – 08/2024* · Champs-sur-Marne

- Traitement d'images satellitaires, avec GitLab et Docker.

## 🎓 Formation

- **Master Développeur Big Data & IA** · IPSSI Paris · *2025 – 2027* · en apprentissage
- **Master 2 Logiciel & ingénierie de données** · Université Gustave Eiffel · *2024 – 2025*
- **Master 1 Informatique** · Université Gustave Eiffel · *2023 – 2024*
- **Licence Informatique** · Université Gustave Eiffel · *2020 – 2023*
- **Baccalauréat, spécialité mathématiques, mention Bien** · *2020*

```mermaid
timeline
    title Parcours
    2020 : Baccalauréat mathématiques, mention Bien
    2020 - 2023 : Licence Informatique, Université Gustave Eiffel
    2023 - 2024 : Master 1 Informatique
    2024 - 2025 : Master 2 Logiciel et ingénierie de données
                : Stage puis alternance, ingénieur logiciel, VisioTerra, modèles de compression, PyTorch 2.3
    2025 - 2027 : Master Développeur Big Data et IA, IPSSI Paris, en apprentissage
    2026 : Stage MJY Holding, de juillet à novembre
         : Alternance Ingénieur Logiciel et Solutions IA, agents, MCP, plateformes métier
```

<img src="assets/divider.svg" alt="" width="100%">

## 🎭 Centres d'intérêt

```bash
$ ls ~/hobbies
theatre/   lecture/   cinema/   dessin/   ecriture/   photographie/   gym/   nature/
```

Théâtre, lecture, cinéma, dessin, écriture et photographie nourrissent ma sensibilité visuelle et narrative (mes portfolios photo en sont la trace). Gym et nature font l'équilibre.

<img src="assets/divider.svg" alt="" width="100%">

## ✉️ Me contacter

Ouvert aux échanges sur l'IA appliquée, les agents et l'ingénierie logicielle.

[LinkedIn](https://www.linkedin.com/in/seer-mensah-assiakoley-542628198/) · [Portfolio](https://www.maashrees.com) · [Mail](mailto:seer.mensaha@maashrees.com)
