import ollama

class LocalLLM:
    def __init__(self):
        self.system_prompt = (
            "Tu es un agent de service client télécom professionnel.\n"
            "Tu parles en français de manière claire et concise.\n"
            "Tu NE DONNES JAMAIS de code ou de blocs ```.\n"
            "Tu aides les clients pour : solde, recharge, internet, assistance.\n"
            "Réponds de façon naturelle et professionnelle.\n"
        )

    def generate(self, user_message: str, context: str = ""):
        """
        Génère une réponse avec le LLM local
        """
        # Construire le message avec le contexte si disponible
        full_message = f"{context}\n{user_message}" if context else user_message
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": full_message}
        ]

        try:
            response = ollama.chat(
                model="phi3:latest",
                messages=messages,
                options={
                    "temperature": 0.3,
                    "num_ctx": 2048
                }
            )
            
            return response["message"]["content"].strip()
        
        except Exception as e:
            print(f"❌ Erreur LLM: {e}")
            return "Désolé, je rencontre un problème technique. Pouvez-vous reformuler votre question ?"