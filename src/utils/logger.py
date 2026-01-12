import json
import os
import uuid
from datetime import datetime
from enum import Enum

# Chemin du fichier de logs
LOG_FILE = os.path.join("logs", "experiment_data.json")

class ActionType(str, Enum):
    """
    Énumération des types d'actions possibles pour standardiser l'analyse.
    """
    ANALYSIS = "CODE_ANALYSIS"  # Audit, lecture, recherche de bugs
    GENERATION = "CODE_GEN"     # Création de nouveau code/tests/docs
    DEBUG = "DEBUG"             # Analyse d'erreurs d'exécution
    FIX = "FIX"                 # Application de correctifs
    SYSTEM = "SYSTEM_INFO"      # ✅ ADDED: For system messages like startup

def log_experiment(agent_name: str, model_used: str, action: ActionType, details: dict, status: str):
    """
    Enregistre une interaction d'agent pour l'analyse scientifique.

    Args:
        agent_name (str): Nom de l'agent (ex: "Auditor", "Fixer").
        model_used (str): Modèle LLM utilisé (ex: "gemini-1.5-flash").
        action (ActionType): Le type d'action effectué (utiliser l'Enum ActionType).
        details (dict): Dictionnaire contenant les détails. DOIT contenir 'input_prompt' et 'output_response'.
        status (str): "SUCCESS" ou "FAILURE".

    Raises:
        ValueError: Si les champs obligatoires sont manquants dans 'details' ou si l'action est invalide.
    """
    
    # --- 1. VALIDATION DU TYPE D'ACTION ---
    # Permet d'accepter soit l'objet Enum, soit la chaîne de caractères correspondante
    valid_actions = [a.value for a in ActionType]
    
    # ✅ FIXED: Accept both Enum and string versions of valid actions
    if isinstance(action, ActionType):
        action_str = action.value
    elif isinstance(action, str) and action in valid_actions:
        action_str = action
    elif isinstance(action, str):
        # ✅ FIXED: Also accept the string name of the enum (e.g., "ANALYSIS" for ActionType.ANALYSIS)
        try:
            # Check if it's the enum name (not value)
            action_enum = ActionType[action]
            action_str = action_enum.value
        except KeyError:
            raise ValueError(
                f"❌ Action invalide : '{action}'. "
                f"Utilisez la classe ActionType (ex: ActionType.FIX) ou l'une de ces valeurs: {valid_actions}"
            )
    else:
        raise ValueError(
            f"❌ Action invalide : '{action}'. "
            f"Utilisez la classe ActionType (ex: ActionType.FIX) ou l'une de ces valeurs: {valid_actions}"
        )

    # --- 2. VALIDATION STRICTE DES DONNÉES (Prompts) ---
    # Pour l'analyse scientifique, nous avons absolument besoin du prompt et de la réponse
    # pour les actions impliquant une interaction majeure avec le code.
    
    # ✅ FIXED: Only require prompts for LLM interactions, not system messages
    if action_str in [ActionType.ANALYSIS.value, ActionType.GENERATION.value, 
                      ActionType.DEBUG.value, ActionType.FIX.value]:
        required_keys = ["input_prompt", "output_response"]
        missing_keys = [key for key in required_keys if key not in details]
        
        if missing_keys:
            raise ValueError(
                f"❌ Erreur de Logging (Agent: {agent_name}) : "
                f"Les champs {missing_keys} sont manquants dans le dictionnaire 'details'. "
                f"Ils sont OBLIGATOIRES pour les actions d'analyse/génération/débogage/correction."
            )
    
    # ✅ ADDED: For SYSTEM actions, we don't require prompts
    elif action_str == ActionType.SYSTEM.value:
        # System messages don't need prompts, but ensure details is a dict
        if not isinstance(details, dict):
            details = {"message": str(details)} if details else {}

    # --- 3. PRÉPARATION DE L'ENTRÉE ---
    # Création du dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    entry = {
        "id": str(uuid.uuid4()),  # ID unique pour éviter les doublons lors de la fusion des données
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "model": model_used,
        "action": action_str,
        "details": details,
        "status": status
    }

    # --- 4. LECTURE & ÉCRITURE ROBUSTE ---
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Vérifie que le fichier n'est pas juste vide
                    data = json.loads(content)
        except json.JSONDecodeError:
            # Si le fichier est corrompu, on repart à zéro (ou on pourrait sauvegarder un backup)
            print(f"⚠️ Attention : Le fichier de logs {LOG_FILE} était corrompu. Une nouvelle liste a été créée.")
            data = []

    data.append(entry)
    
    # Écriture
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ✅ ADDED: Helper function for backward compatibility
def log_system_message(message: str, status: str = "INFO", **extra_details):
    """
    Helper pour les messages système (comme le démarrage).
    Compatible avec l'ancien format du main.py du professeur.
    """
    details = {"message": message}
    details.update(extra_details)
    
    return log_experiment(
        agent_name="System",
        model_used="unknown",
        action=ActionType.SYSTEM,
        details=details,
        status=status
    )