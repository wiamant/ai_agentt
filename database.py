import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_file='telecom.db'):
        self.db_file = db_file
        self.init_db()
    
    def get_connection(self):
        """Créer une connexion à la base de données"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialiser la base de données avec des tables et données de test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                msisdn TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                solde REAL DEFAULT 0,
                data_restant REAL DEFAULT 0,
                data_expiration TEXT,
                offres_actives TEXT,
                statut TEXT DEFAULT 'active'
            )
        ''')
        
        # Table offres
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                data_go REAL NOT NULL,
                prix REAL NOT NULL,
                duree_jours INTEGER NOT NULL
            )
        ''')
        
        # Table transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msisdn TEXT NOT NULL,
                type TEXT NOT NULL,
                montant REAL DEFAULT 0,
                description TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si des données existent déjà
        cursor.execute('SELECT COUNT(*) as count FROM clients')
        if cursor.fetchone()['count'] == 0:
            # Insérer des clients de test
            clients_test = [
                ('0612345678', 'Ahmed Bennani', 120.50, 5.2, None, '[]', 'active'),
                ('0698765432', 'Fatima Alami', 45.00, 0, None, '[]', 'active')
            ]
            
            cursor.executemany('''
                INSERT INTO clients (msisdn, nom, solde, data_restant, data_expiration, offres_actives, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', clients_test)
        
        # Vérifier si des offres existent
        cursor.execute('SELECT COUNT(*) as count FROM offres')
        if cursor.fetchone()['count'] == 0:
            # Insérer des offres
            offres_test = [
                ('Pass 1 Go', 1, 10, 7),
                ('Pass 5 Go', 5, 30, 30),
                ('Pass 10 Go', 10, 50, 30),
                ('Pass 20 Go', 20, 90, 30),
                ('Pass Illimité', 100, 150, 30)
            ]
            
            cursor.executemany('''
                INSERT INTO offres (nom, data_go, prix, duree_jours)
                VALUES (?, ?, ?, ?)
            ''', offres_test)
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée")
    
    def get_client(self, msisdn):
        """Récupérer un client par son numéro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clients WHERE msisdn = ?', (msisdn,))
        client = cursor.fetchone()
        
        conn.close()
        
        return dict(client) if client else None
    
    def get_offres(self):
        """Récupérer toutes les offres disponibles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM offres')
        offres = cursor.fetchall()
        
        conn.close()
        
        return [dict(offre) for offre in offres]
    
    def get_transactions(self, msisdn, limit=10):
        """Récupérer l'historique des transactions d'un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE msisdn = ? 
            ORDER BY date DESC 
            LIMIT ?
        ''', (msisdn, limit))
        
        transactions = cursor.fetchall()
        
        conn.close()
        
        return [dict(t) for t in transactions]