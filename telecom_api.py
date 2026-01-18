import sqlite3
import json
from datetime import datetime, timedelta

class TelecomAPI:
    def __init__(self, db):
        self.db = db
    
    def recharge(self, msisdn, montant):
        """Effectue une recharge"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT solde FROM clients WHERE msisdn = ?', (msisdn,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'Client non trouvé'}
            
            nouveau_solde = result['solde'] + montant
            cursor.execute('UPDATE clients SET solde = ? WHERE msisdn = ?', (nouveau_solde, msisdn))
            
            # Enregistrer la transaction
            cursor.execute('''
                INSERT INTO transactions (msisdn, type, montant, description)
                VALUES (?, ?, ?, ?)
            ''', (msisdn, 'recharge', montant, f'Recharge de {montant} DH'))
            
            conn.commit()
            
            return {
                'success': True,
                'nouveau_solde': nouveau_solde,
                'montant': montant
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def activate_data_bundle(self, msisdn, bundle_id):
        """Active un pass internet"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Récupérer client et offre
            cursor.execute('SELECT * FROM clients WHERE msisdn = ?', (msisdn,))
            client = cursor.fetchone()
            
            cursor.execute('SELECT * FROM offres WHERE id = ?', (bundle_id,))
            offre = cursor.fetchone()
            
            if not client:
                return {'success': False, 'error': 'Client non trouvé'}
            
            if not offre:
                return {'success': False, 'error': 'Offre non trouvée'}
            
            if client['solde'] < offre['prix']:
                return {'success': False, 'error': 'Solde insuffisant'}
            
            # Mettre à jour le client
            nouveau_solde = client['solde'] - offre['prix']
            nouveau_data = client['data_restant'] + offre['data_go']
            expiration = (datetime.now() + timedelta(days=offre['duree_jours'])).isoformat()
            
            offres_actives = json.loads(client['offres_actives']) if client['offres_actives'] else []
            offres_actives.append({
                'id': offre['id'],
                'nom': offre['nom'],
                'expiration': expiration
            })
            
            cursor.execute('''
                UPDATE clients 
                SET solde = ?, data_restant = ?, data_expiration = ?, offres_actives = ?
                WHERE msisdn = ?
            ''', (nouveau_solde, nouveau_data, expiration, json.dumps(offres_actives), msisdn))
            
            # Transaction
            cursor.execute('''
                INSERT INTO transactions (msisdn, type, montant, description)
                VALUES (?, ?, ?, ?)
            ''', (msisdn, 'activation_bundle', -offre['prix'], f'Activation {offre["nom"]}'))
            
            conn.commit()
            
            return {
                'success': True,
                'offre': offre['nom'],
                'expiration': datetime.fromisoformat(expiration).strftime('%d/%m/%Y'),
                'nouveau_solde': nouveau_solde
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_balance(self, msisdn):
        """Récupère le solde"""
        client = self.db.get_client(msisdn)
        
        if not client:
            return {'success': False, 'error': 'Client non trouvé'}
        
        expiration = None
        if client['data_expiration']:
            expiration = datetime.fromisoformat(client['data_expiration']).strftime('%d/%m/%Y')
        
        return {
            'success': True,
            'solde': client['solde'],
            'data_restant': client['data_restant'],
            'data_expiration': expiration,
            'offres_actives': client['offres_actives']
        }
    
    def suspend_line(self, msisdn):
        """Suspend une ligne"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE clients SET statut = ? WHERE msisdn = ?', ('suspendue', msisdn))
            cursor.execute('''
                INSERT INTO transactions (msisdn, type, description)
                VALUES (?, ?, ?)
            ''', (msisdn, 'suspension', 'Suspension de ligne'))
            
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def cancel_bundle(self, msisdn, bundle_id):
        """Annule une offre"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT offres_actives FROM clients WHERE msisdn = ?', (msisdn,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'Client non trouvé'}
            
            offres_actives = json.loads(result['offres_actives']) if result['offres_actives'] else []
            offre_trouvee = None
            
            for i, offre in enumerate(offres_actives):
                if offre['id'] == bundle_id:
                    offre_trouvee = offres_actives.pop(i)
                    break
            
            if not offre_trouvee:
                return {'success': False, 'error': 'Offre non trouvée'}
            
            cursor.execute(
                'UPDATE clients SET offres_actives = ? WHERE msisdn = ?',
                (json.dumps(offres_actives), msisdn)
            )
            
            cursor.execute('''
                INSERT INTO transactions (msisdn, type, description)
                VALUES (?, ?, ?)
            ''', (msisdn, 'annulation_bundle', f'Annulation {offre_trouvee["nom"]}'))
            
            conn.commit()
            
            return {'success': True, 'offre_annulee': offre_trouvee['nom']}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()