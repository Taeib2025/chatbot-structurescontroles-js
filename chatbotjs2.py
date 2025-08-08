import gradio as gr
import random
from datetime import datetime
import threading
import os
import uuid
from typing import Dict, Any

# Dictionnaire pour stocker les états par session utilisateur
session_states = {}
session_lock = threading.Lock()

# Définir le dictionnaire des structures de contrôle JavaScript
structures_js = {
    "if": """Structure conditionnelle simple qui exécute un bloc de code si une condition est vraie.
Syntaxe: 
if (condition) {
    // code à exécuter si condition vraie
}

Exemple :
let age = 18;
if (age >= 18) {
    console.log("Vous êtes majeur");
}""",

    "if-else": """Structure conditionnelle qui exécute un bloc si condition vraie, un autre si fausse.
Syntaxe:
if (condition) {
    // code si condition vraie
} else {
    // code si condition fausse
}

Exemple :
let note = 12;
if (note >= 10) {
    console.log("Admis");
} else {
    console.log("Refué");
}""",

    "if-else-if": """Structure conditionnelle multiple pour tester plusieurs conditions.
Syntaxe:
if (condition1) {
    // code si condition1 vraie
} else if (condition2) {
    // code si condition2 vraie
} else {
    // code si toutes conditions fausses
}

Exemple :
let note = 15;
if (note >= 16) {
    console.log("Très bien");
} else if (note >= 14) {
    console.log("Bien");
} else if (note >= 10) {
    console.log("Passable");
} else {
    console.log("Insuffisant");
}""",

    "switch": """Structure de sélection multiple basée sur la valeur d'une expression.
Syntaxe:
switch (expression) {
    case valeur1:
        // code pour valeur1
        break;
    case valeur2:
        // code pour valeur2
        break;
    default:
        // code par défaut
}

Exemple :
let jour = 3;
switch (jour) {
    case 1:
        console.log("Lundi");
        break;
    case 2:
        console.log("Mardi");
        break;
    case 3:
        console.log("Mercredi");
        break;
    default:
        console.log("Autre jour");
}""",

    "for": """Boucle qui répète un bloc de code un nombre déterminé de fois.
Syntaxe:
for (initialisation; condition; incrémentation) {
    // code à répéter
}

Exemple :
for (let i = 0; i < 5; i++) {
    console.log("Itération " + i);
}
// Affiche: Itération 0, Itération 1, ..., Itération 4""",

    "while": """Boucle qui répète un bloc tant qu'une condition est vraie (test en début).
Syntaxe:
while (condition) {
    // code à répéter
    // modification de la condition
}

Exemple :
let i = 0;
while (i < 3) {
    console.log("Valeur de i: " + i);
    i++;
}
// Affiche: Valeur de i: 0, Valeur de i: 1, Valeur de i: 2""",

    "do-while": """Boucle qui répète un bloc au moins une fois, puis tant qu'une condition est vraie.
Syntaxe:
do {
    // code à répéter
    // modification de la condition
} while (condition);

Exemple :
let x = 0;
do {
    console.log("x vaut: " + x);
    x++;
} while (x < 2);
// Affiche: x vaut: 0, x vaut: 1"""
}

# Questions pour le quiz
questions = [
    # Questions sur if
    {"type": "if", "question": "Quelle sera la sortie de ce code ?\nlet x = 5;\nif (x > 3) {\n    console.log('Grand');\n}", "reponse": "Grand"},
    {"type": "if", "question": "Que se passe-t-il si la condition d'un 'if' est false et qu'il n'y a pas de 'else' ?", "reponse": "rien"},
    
    # Questions sur if-else
    {"type": "if-else", "question": "Quelle sera la sortie ?\nlet age = 15;\nif (age >= 18) {\n    console.log('Majeur');\n} else {\n    console.log('Mineur');\n}", "reponse": "Mineur"},
    {"type": "if-else", "question": "Dans une structure if-else, combien de blocs peuvent être exécutés au maximum ?", "reponse": "1"},
    
    # Questions sur if-else-if
    {"type": "if-else-if", "question": "Quelle sera la sortie ?\nlet note = 12;\nif (note >= 16) console.log('A');\nelse if (note >= 12) console.log('B');\nelse console.log('C');", "reponse": "B"},
    {"type": "if-else-if", "question": "Dans if-else-if, que se passe-t-il quand une condition est vraie ?", "reponse": "les autres ne sont pas testées"},
    
    # Questions sur switch
    {"type": "switch", "question": "Quelle sera la sortie ?\nlet x = 2;\nswitch(x) {\n    case 1: console.log('Un'); break;\n    case 2: console.log('Deux'); break;\n    default: console.log('Autre');\n}", "reponse": "Deux"},
    {"type": "switch", "question": "Dans switch, quel mot-clé utilise-t-on pour le cas par défaut ?", "reponse": "default"},
    
    # Questions sur for
    {"type": "for", "question": "Combien de fois cette boucle s'exécute-t-elle ?\nfor (let i = 0; i < 4; i++) { ... }", "reponse": "4"},
    {"type": "for", "question": "Quelle est la valeur finale de i ?\nfor (let i = 1; i <= 3; i++) { }\nconsole.log(i);", "reponse": "erreur"},
    {"type": "for", "question": "Dans une boucle for, combien y a-t-il de parties entre parenthèses ?", "reponse": "3"},
    
    # Questions sur while
    {"type": "while", "question": "Combien de fois s'exécute cette boucle ?\nlet i = 0;\nwhile (i < 2) { i++; }", "reponse": "2"},
    {"type": "while", "question": "Que se passe-t-il si la condition d'un while est toujours vraie ?", "reponse": "boucle infinie"},
    {"type": "while", "question": "Dans while, quand la condition est-elle testée ?", "reponse": "avant chaque itération"},
    
    # Questions sur do-while
    {"type": "do-while", "question": "Combien de fois minimum s'exécute une boucle do-while ?", "reponse": "1"},
    {"type": "do-while", "question": "Dans do-while, quand la condition est-elle testée ?", "reponse": "après chaque itération"},
    
    
    # Questions mixtes
    {"type": "mixed", "question": "Quelle structure utiliser pour tester une variable contre plusieurs valeurs exactes ?", "reponse": "switch"},
    {"type": "mixed", "question": "Quelle boucle choisir quand on connaît le nombre d'itérations à l'avance ?", "reponse": "for"}
]

def get_session_id():
    """Génère un ID de session unique pour chaque utilisateur"""
    if not hasattr(get_session_id, 'session_id'):
        get_session_id.session_id = str(uuid.uuid4())
    return get_session_id.session_id

def get_session_state(session_id=None):
    """Obtient l'état de la session pour un utilisateur spécifique"""
    if session_id is None:
        session_id = get_session_id()
    
    with session_lock:
        if session_id not in session_states:
            session_states[session_id] = {
                "nom": None,
                "mode": "attente_nom",
                "question_en_cours": None,
                "score": 0,
                "reponses": [],
                "session_id": session_id
            }
        return session_states[session_id]

def exporter_resultats(etat: Dict[str, Any]):
    """Exporte les résultats du quiz dans un fichier"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id_court = etat.get('session_id', 'unknown')[:8]
        filename = f"resultats_structures_{etat['nom']}_{session_id_court}_{timestamp}.txt"
        
        os.makedirs("resultats", exist_ok=True)
        filepath = os.path.join("resultats", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Résultats Quiz Structures de Contrôle JavaScript\n")
            f.write(f"Étudiant: {etat['nom']}\n")
            f.write(f"Session ID: {session_id_court}\n")
            f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Score final: {etat['score']}/{len(etat['reponses'])}\n")
            f.write(f"Pourcentage: {(etat['score']/len(etat['reponses'])*100):.1f}%\n\n")
            f.write("=" * 60 + "\n")
            f.write("Détail des réponses:\n")
            f.write("=" * 60 + "\n\n")
            
            for i, rep in enumerate(etat["reponses"], 1):
                f.write(f"Question {i}: {rep['question']}\n")
                f.write(f"Votre réponse: {rep['reponse_donnee']}\n")
                f.write(f"Réponse correcte: {rep['reponse_correcte']}\n")
                f.write(f"Type de structure: {rep['type']}\n")
                f.write(f"Résultat: {'✅ Correct' if rep['correct'] else '❌ Incorrect'}\n")
                f.write("-" * 40 + "\n\n")
        
        return filepath
    except Exception as e:
        print(f"Erreur lors de l'export: {e}")
        return None

def choisir_mode(choix, historique_actuel, session_id_state):
    """Gère le changement de mode"""
    if not session_id_state:
        session_id_state = str(uuid.uuid4())
    
    etat = get_session_state(session_id_state)
    
    if choix == "--Sélectionner un mode--":
        return historique_actuel, "Veuillez sélectionner un mode d'apprentissage", session_id_state
    
    if not etat["nom"]:
        return historique_actuel, "⚠️ Veuillez d'abord entrer votre prénom dans le chat", session_id_state
    
    if choix == "Structures":
        etat["mode"] = "structures"
        etat["question_en_cours"] = None
        message_bot = {
            "role": "assistant",
            "content": f"📚 **Mode Structures activé pour {etat['nom']} !**\n\nTapez le nom d'une structure pour voir son explication.\n\n💡 **Structures disponibles :**\n" + "\n".join([f"• `{struct}`" for struct in structures_js.keys()])
        }
        return historique_actuel + [message_bot], "📚 Mode Structures activé. Tapez le nom d'une structure pour voir son explication.", session_id_state
    
    elif choix == "Quiz":
        etat["mode"] = "quiz"
        etat["score"] = 0
        etat["reponses"] = []
        etat["question_en_cours"] = None
        
        premiere_question = demarrer_quiz_pour_session(session_id_state)
        message_bot = {
            "role": "assistant",
            "content": f"🎯 **Mode Quiz activé pour {etat['nom']} !**\n\n{premiere_question}"
        }
        return historique_actuel + [message_bot], "🎯 Mode Quiz activé. Quiz en cours...", session_id_state
    
    return historique_actuel, "Mode non reconnu", session_id_state

def demarrer_quiz_pour_session(session_id):
    """Démarre une nouvelle question du quiz pour une session spécifique"""
    etat = get_session_state(session_id)
    
    if etat["nom"] is None:
        return "⚠️ Veuillez d'abord entrer votre prénom"
    
    questions_utilisees = [r['question'] for r in etat["reponses"]]
    questions_dispos = [q for q in questions if q['question'] not in questions_utilisees]
    
    if not questions_dispos:
        pourcentage = (etat['score'] / len(etat['reponses']) * 100) if etat['reponses'] else 0
        fichier = exporter_resultats(etat)
        
        message_fin = f"""🎉 **Quiz terminé !** 🎉

📊 **Résultats finaux :**
- Score : {etat['score']}/{len(etat['reponses'])}
- Pourcentage : {pourcentage:.1f}%

🏆 **Performance :**
"""
        if pourcentage >= 90:
            message_fin += "Excellent ! Vous maîtrisez parfaitement les structures de contrôle ! 🌟"
        elif pourcentage >= 75:
            message_fin += "Très bien ! Bonne compréhension des concepts ! 👏"
        elif pourcentage >= 60:
            message_fin += "Bien ! Continuez à pratiquer ! 👍"
        else:
            message_fin += "À améliorer ! Révisez les structures et recommencez ! 💪"
        
        if fichier:
            message_fin += f"\n\n📁 Résultats sauvegardés dans : `{fichier}`"
        
        etat["reponses"] = []
        etat["score"] = 0
        etat["question_en_cours"] = None
        
        return message_fin
    
    question = random.choice(questions_dispos)
    etat["question_en_cours"] = question
    
    return f"❓ **Question {len(etat['reponses']) + 1}/{len(questions)} :**\n{question['question']}"

def repondre(message, historique, session_id_state):
    """Gère les réponses de l'utilisateur"""
    if not message or not message.strip():
        return historique, "", session_id_state
    
    if not session_id_state:
        session_id_state = str(uuid.uuid4())
    
    etat = get_session_state(session_id_state)
    message = message.strip()
    
    nouveau_message_user = {"role": "user", "content": message}
    
    # Mode attente du nom
    if etat["mode"] == "attente_nom":
        etat["nom"] = message
        etat["mode"] = "selection_mode"
        reponse_bot = {
            "role": "assistant",
            "content": f"👋 Enchanté {etat['nom']} ! 😊\n\n🎯 Maintenant, choisissez un mode d'apprentissage dans le menu déroulant ci-dessus :\n- **Structures** : Pour explorer les structures de contrôle JavaScript\n- **Quiz** : Pour tester vos connaissances"
        }
        return historique + [nouveau_message_user, reponse_bot], "", session_id_state
    
    # Mode sélection
    elif etat["mode"] == "selection_mode":
        reponse_bot = {
            "role": "assistant",
            "content": "🎯 Veuillez sélectionner un mode d'apprentissage dans le menu déroulant ci-dessus :\n- **Structures** : Pour explorer les structures de contrôle JavaScript\n- **Quiz** : Pour tester vos connaissances"
        }
        return historique + [nouveau_message_user, reponse_bot], "", session_id_state
    
    # Mode quiz
    elif etat["mode"] == "quiz":
        if etat["question_en_cours"] is None:
            question_text = demarrer_quiz_pour_session(session_id_state)
            if "Quiz terminé" in question_text:
                reponse_bot = {"role": "assistant", "content": question_text}
                return historique + [nouveau_message_user, reponse_bot], "", session_id_state
            else:
                reponse_bot = {"role": "assistant", "content": question_text}
                return historique + [nouveau_message_user, reponse_bot], "", session_id_state
        
        bonne_reponse = etat["question_en_cours"]["reponse"]
        correct = message.lower().strip() == bonne_reponse.lower().strip()
        
        etat["reponses"].append({
            "type": etat["question_en_cours"]["type"],
            "question": etat["question_en_cours"]["question"],
            "reponse_donnee": message,
            "reponse_correcte": bonne_reponse,
            "correct": correct
        })
        
        if correct:
            etat["score"] += 1
            feedback = f"✅ **Excellent !** C'est la bonne réponse !\n\n📈 Score actuel : {etat['score']}/{len(etat['reponses'])}"
        else:
            feedback = f"❌ **Pas tout à fait...**\n\n💡 La bonne réponse était : **{bonne_reponse}**\n📈 Score actuel : {etat['score']}/{len(etat['reponses'])}"
        
        etat["question_en_cours"] = None
        prochaine_question = demarrer_quiz_pour_session(session_id_state)
        
        if "Quiz terminé" in prochaine_question:
            contenu_complet = f"{feedback}\n\n{'='*40}\n\n{prochaine_question}"
        else:
            contenu_complet = f"{feedback}\n\n{'='*30}\n\n{prochaine_question}"
        
        reponse_bot = {"role": "assistant", "content": contenu_complet}
        return historique + [nouveau_message_user, reponse_bot], "", session_id_state
    
    # Mode structures
    elif etat["mode"] == "structures":
        structure = message.lower().strip()
        
        structure_trouvee = None
        for struct_name, struct_desc in structures_js.items():
            if struct_name.lower() == structure:
                structure_trouvee = (struct_name, struct_desc)
                break
        
        if structure_trouvee:
            struct_name, struct_desc = structure_trouvee
            content = f"📖 **Structure JavaScript :** `{struct_name}`\n\n```javascript\n{struct_desc}\n```"
        else:
            structures_list = "\n".join([f"• `{struct}`" for struct in structures_js.keys()])
            content = f"❓ **Structure non trouvée !**\n\nStructures disponibles :\n{structures_list}\n\n💡 *Conseil : Tapez exactement le nom de la structure (ex: 'if', 'for', 'switch')*"
        
        reponse_bot = {"role": "assistant", "content": content}
        return historique + [nouveau_message_user, reponse_bot], "", session_id_state
    
    else:
        reponse_bot = {
            "role": "assistant", 
            "content": "⚠️ Mode non reconnu. Veuillez sélectionner un mode dans le menu déroulant."
        }
        return historique + [nouveau_message_user, reponse_bot], "", session_id_state

def reset_session(session_id_state):
    """Réinitialise la session"""
    if session_id_state:
        with session_lock:
            if session_id_state in session_states:
                del session_states[session_id_state]
    
    nouveau_session_id = str(uuid.uuid4())
    
    return (
        "",
        [{"role": "assistant", "content": "👋 **Session réinitialisée !**\n\nBonjour ! Quel est votre prénom ?"}],
        "--Sélectionner un mode--",
        "Session réinitialisée - En attente du prénom",
        nouveau_session_id
    )

# Interface Gradio
with gr.Blocks(title="🤖 Quiz Structures de Contrôle JavaScript", theme=gr.themes.Soft()) as app:
    
    session_id_state = gr.State(value=str(uuid.uuid4()))
    
    # En-tête
    gr.Markdown("""
    # 🤖 Apprentissage des Structures de Contrôle JavaScript
    ### 📚 École d'été 2025 - Formation Interactive
    ### 🏫 Lycée Privé ABC Senior - Kairouan
    
    ---
    """)
    
    # Informations du professeur
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("""
            **🎯 Bienvenue dans cet outil d'apprentissage interactif !**
            
            Cet outil vous permettra d'apprendre et de tester vos connaissances 
            sur les structures conditionnelles (if, else, switch) et les structures 
            itératives (for, while, do-while) en JavaScript.
            
            **🔒 Session privée :** Votre progression est indépendante des autres utilisateurs.
            """)
        with gr.Column(scale=2):
            gr.Markdown("""
            **👨‍🏫 Professeur :** Mr. Guizani Taieb  
            *Professeur Principal Émérite Classe Exceptionnelle*  
            📧 guizanitaeib@gmail.com  
            📞 +216 96 785 177
            """)
    
    gr.Markdown("---")
    
    # Interface principale
    with gr.Row():
        with gr.Column(scale=2):
            mode = gr.Dropdown(
                choices=["--Sélectionner un mode--", "Structures", "Quiz"],
                label="🎮 Choisissez votre mode d'apprentissage",
                value="--Sélectionner un mode--",
                info="Sélectionnez 'Structures' pour explorer ou 'Quiz' pour vous tester"
            )
        with gr.Column(scale=3):
            mode_output = gr.Textbox(
                label="📊 Statut du mode", 
                interactive=False,
                value="En attente de sélection du mode..."
            )
    
    # Chat interface
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                label="💬 Assistant d'apprentissage",
                value=[{"role": "assistant", "content": "👋 **Bonjour et bienvenue !**\n\nJe suis votre assistant pour apprendre les structures de contrôle JavaScript.\n\n🔹 **Pour commencer, dites-moi votre prénom s'il vous plaît.**\n\n✨ *Votre session est privée et indépendante des autres utilisateurs.*"}],
                height=450,
                type="messages",
                avatar_images=None
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="✍️ Votre message",
                    placeholder="Tapez votre message ici...",
                    lines=1,
                    scale=4
                )
                reset_btn = gr.Button("🔄 Réinitialiser", scale=1, variant="secondary")
    
    # Exemples de structures
    gr.Examples(
        examples=list(structures_js.keys()),
        inputs=msg,
        label="💡 Exemples de structures à explorer (cliquez pour tester)"
    )
    
    # Aide
    with gr.Accordion("ℹ️ Guide d'utilisation", open=False):
        gr.Markdown("""
        ### 📖 Comment utiliser cet outil :
        
        1. **Entrez votre prénom** dans le chat pour commencer
        2. **Choisissez un mode** dans le menu déroulant :
           - **Mode Structures** : Tapez le nom d'une structure pour voir son explication et des exemples
           - **Mode Quiz** : Répondez aux questions pour tester vos connaissances
        3. **Interagissez** avec l'assistant selon le mode choisi
        4. **Utilisez le bouton Réinitialiser** pour recommencer à zéro
        
        ### 🎯 Structures disponibles :
        
        **Structures conditionnelles :**
        - `if` : Condition simple
        - `if-else` : Condition avec alternative
        - `if-else-if` : Conditions multiples
        - `switch` : Sélection multiple
        
        **Structures itératives :**
        - `for` : Boucle avec compteur
        - `while` : Boucle avec condition en début
        - `do-while` : Boucle avec condition en fin
        
        ### 🔒 Confidentialité :
        - Chaque utilisateur a sa propre session privée
        - Vos réponses n'affectent pas les autres utilisateurs
        - Vos résultats sont sauvegardés individuellement
        """)
    
    # Événements
    msg.submit(
        fn=repondre,
        inputs=[msg, chatbot, session_id_state],
        outputs=[chatbot, msg, session_id_state]
    )
    
    mode.change(
        fn=choisir_mode,
        inputs=[mode, chatbot, session_id_state],
        outputs=[chatbot, mode_output, session_id_state]
    )
    
    reset_btn.click(
        fn=reset_session,
        inputs=[session_id_state],
        outputs=[msg, chatbot, mode, mode_output, session_id_state]
    )

# Lancement de l'application
# Lancement de l'application
if __name__ == "__main__":
    print("🚀 Lancement de l'application Quiz Structures de Contrôle JavaScript...")
    print("📁 Les résultats seront sauvegardés dans le dossier 'resultats/'")
    print("👥 Sessions multiples supportées - Chaque utilisateur aura sa propre session")
    
    import os
    
    # Configuration pour Railway
    port = int(os.environ.get("PORT", 7860))
    
    try:
        print(f"🔄 Lancement sur le port {port}...")
        app.launch(
            server_name="127.0.0.1",  # Important pour Railway !
            server_port=port,
            share=True,  # Pas besoin de share en production
            show_error=True,
            quiet=False
        )
        print(f"✅ Application lancée avec succès sur le port {port}")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        # Fallback pour le développement local
        app.launch(share=True, server_port=7860)