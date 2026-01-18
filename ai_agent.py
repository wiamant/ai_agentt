from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json, re, numpy as np
from llm import LocalLLM

class AIAgent:
    def __init__(self, db=None, telecom=None):
        print("🔄 Chargement des modèles...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.llm = LocalLLM()
        self.db = db  # NOUVEAU : accès à la base de données
        self.telecom = telecom  # NOUVEAU : accès aux fonctions télécom
        self.load_knowledge_base()
        print("✅ Agent AI prêt")

    def load_knowledge_base(self):
        with open('knowledge_base.json', encoding='utf-8') as f:
            self.kb = json.load(f)

        self.texts = [f"{x['question']} {x['reponse']}" for x in self.kb]
        self.embeddings = self.model.encode(self.texts)

    def rag_search(self, query):
        q_emb = self.model.encode([query])
        sims = cosine_similarity(q_emb, self.embeddings)[0]
        idx = np.argmax(sims)
        return self.kb[idx]['reponse'] if sims[idx] > 0.4 else None

    def detect_intent(self, msg):
        msg = msg.lower()
        if re.search(r'\b(recharge|credit)\b', msg):
            m = re.search(r'\d+', msg)
            return {'type': 'recharge', 'montant': int(m.group()) if m else None}
        if re.search(r'\b(solde|reste|combien)\b', msg):
            return {'type': 'get_balance'}
        if re.search(r'\b(pass|internet|go|data)\b', msg):
            return {'type': 'activate_bundle'}
        if re.search(r'\b(annul|desactiv|stop)\b', msg):
            return {'type': 'cancel_bundle'}
        if re.search(r'\b(vol|perdu|suspend)\b', msg):
            return {'type': 'suspend_line'}
        return {'type': 'question'}

    def llm_answer(self, user_msg, rag=None):
        context = f"Info : {rag}\n" if rag else ""
        return self.llm.generate(f"{context}Question : {user_msg}")

    def process(self, message, msisdn=None):
        """
        Traite le message de l'utilisateur
        msisdn : numéro de téléphone de l'utilisateur connecté
        """
        intent = self.detect_intent(message)
        response = {'action': None, 'message': '', 'data': {}}

        # ========================================
        # CONSULTER LE SOLDE
        # ========================================
        if intent['type'] == 'get_balance':
            if not msisdn:
                response['message'] = "Erreur : utilisateur non connecté"
                return response

            balance_info = self.telecom.get_balance(msisdn)
            
            if balance_info['success']:
                msg = f"💰 **Votre solde :**\n"
                msg += f"• Crédit : {balance_info['solde']:.2f} DH\n"
                msg += f"• Data restant : {balance_info['data_restant']:.2f} Go\n"
                
                if balance_info['data_expiration']:
                    msg += f"• Expire le : {balance_info['data_expiration']}\n"
                
                # Afficher les offres actives
                offres = json.loads(balance_info['offres_actives']) if balance_info['offres_actives'] else []
                if offres:
                    msg += f"\n📦 Offres actives : {len(offres)}"
                    response['action'] = 'show_active_bundles'
                    response['data'] = {'offres_actives': offres}
                else:
                    msg += "\n📦 Aucune offre active"
                
                response['message'] = msg
            else:
                response['message'] = f"❌ Erreur : {balance_info['error']}"

        # ========================================
        # RECHARGE
        # ========================================
        elif intent['type'] == 'recharge':
            if not intent['montant']:
                response['message'] = "Quel montant souhaitez-vous recharger ? (ex: 50 DH)"
            else:
                if not msisdn:
                    response['message'] = "Erreur : utilisateur non connecté"
                    return response

                result = self.telecom.recharge(msisdn, intent['montant'])
                
                if result['success']:
                    response['message'] = (
                        f"✅ Recharge de {result['montant']} DH effectuée avec succès !\n"
                        f"💰 Nouveau solde : {result['nouveau_solde']:.2f} DH"
                    )
                else:
                    response['message'] = f"❌ Erreur : {result['error']}"

        # ========================================
        # ACTIVER UN PASS INTERNET
        # ========================================
        elif intent['type'] == 'activate_bundle':
            if not self.db:
                response['message'] = "Service indisponible"
                return response

            # Récupérer toutes les offres disponibles
            offres = self.db.get_offres()
            
            response['action'] = 'show_bundles'
            response['data'] = {'offres': offres}
            response['message'] = "🌐 Voici les offres internet disponibles :"

        # ========================================
        # ANNULER UNE OFFRE
        # ========================================
        elif intent['type'] == 'cancel_bundle':
            if not msisdn:
                response['message'] = "Erreur : utilisateur non connecté"
                return response

            balance_info = self.telecom.get_balance(msisdn)
            offres = json.loads(balance_info['offres_actives']) if balance_info['offres_actives'] else []
            
            if not offres:
                response['message'] = "Vous n'avez aucune offre active à annuler."
            else:
                response['action'] = 'show_active_bundles'
                response['data'] = {'offres_actives': offres}
                response['message'] = "Quelle offre souhaitez-vous annuler ?"

        # ========================================
        # SUSPENDRE LA LIGNE
        # ========================================
        elif intent['type'] == 'suspend_line':
            response['action'] = 'confirm_suspend'
            response['message'] = "⚠️ Voulez-vous vraiment suspendre votre ligne ? Cette action empêchera tout appel et SMS."

        # ========================================
        # QUESTION GÉNÉRALE
        # ========================================
        else:
            rag = self.rag_search(message)
            response['message'] = self.llm_answer(message, rag)

        return response