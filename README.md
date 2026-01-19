# AI Agent
## Description 
Ce projet consiste à concevoir et implémenter un agent intelligent basé sur l’IA destiné pour les opérateurs. L’agent a pour objectif d’assister les clients des opérateurs réseau .

---


##  Fonctionnalités principales
*  Agent conversationnel pour requêtes techniques
*  Authentification-Chat IA-Détection d’intentions-LLM local

## Architecture générale

[ Frontend HTML/CSS/JS ]
|
v
[ Flask API Backend ]
|
+--> [ AIAgent ]
| |
| +--> Intent Detection
| +--> RAG Search
| +--> LLM Answer
|
+--> [ LocalLLM ] 

##  Technologies utilisées

* Backend
* Python 3
* Flask
* Sentence-Transformers
* Ollama (client Python)
IA
* Embeddings MiniLM
* RAG
* LLaMA Phi(local)
Frontend
* HTML5
* CSS3
* JavaScript


## Installation

```bash
# Cloner le dépôt
git clone https://github.com/wiamant/ai_agentt.git

# Accéder au projet
cd ai_agentt

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate     # sous Windows

# Installer les dépendances
pip install -r requirements.txt


##  Exécution

```bash
python app.py
```


## Structure du projet

Nouveau dossier/
│
├── app.py # Serveur Flask
├── ai_agent.py # Logique de l’agent IA
├── llm.py # Interface LLM (Ollama)
├── database.py # Base de données (optionnelle)
│
├── templates/
│ └── index.html # Interface web
│
├── static/
│ ├── style.css # Styles UI
│ └── script.js # Logique frontend
│
└── venv/ # Environnement virtuel Python
