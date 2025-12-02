"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    
    Valid classes: Warrior, Mage, Rogue, Cleric
    
    Returns: Dictionary with character data including:
            - name, class, level, health, max_health, strength, magic
            - experience, gold, inventory, active_quests, completed_quests
    
    Raises: InvalidCharacterClassError if class is not valid
    """
    if character_class not in ["Warrior", "Mage", "Rogue", "Cleric"]:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    base_stats = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    stats = base_stats[character_class]

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character



def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    
    Filename format: {character_name}_save.txt
    
    File format:
    NAME: character_name
    CLASS: class_name
    LEVEL: 1
    HEALTH: 120
    MAX_HEALTH: 120
    STRENGTH: 15
    MAGIC: 5
    EXPERIENCE: 0
    GOLD: 100
    INVENTORY: item1,item2,item3
    ACTIVE_QUESTS: quest1,quest2
    COMPLETED_QUESTS: quest1,quest2
    
    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate or handle)
    """
    os.makedirs(save_directory, exist_ok=True)
    filename = f'{character["name"]}_save.txt'
    filepath = os.path.join(save_directory, filename)

    def list_to_csv(lst):
        return ",".join(lst) if lst else ""

    lines = [
        f"NAME: {character.get('name', '')}",
        f"CLASS: {character.get('class', '')}",
        f"LEVEL: {character.get('level', '')}",
        f"HEALTH: {character.get('health', '')}",
        f"MAX_HEALTH: {character.get('max_health', '')}",
        f"STRENGTH: {character.get('strength', '')}",
        f"MAGIC: {character.get('magic', '')}",
        f"EXPERIENCE: {character.get('experience', '')}",
        f"GOLD: {character.get('gold', '')}",
        f"INVENTORY: {list_to_csv(character.get('inventory', []))}",
        f"ACTIVE_QUESTS: {list_to_csv(character.get('active_quests', []))}",
        f"COMPLETED_QUESTS: {list_to_csv(character.get('completed_quests', []))}",
    ]
    with open(filepath, 'w') as file:
        file.write("\n".join(lines))
    
    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    
    Args:
        character_name: Name of character to load
        save_directory: Directory containing save files
    
    Returns: Character dictionary
    Raises: 
        CharacterNotFoundError if save file doesn't exist
        SaveFileCorruptedError if file exists but can't be read
        InvalidSaveDataError if data format is wrong
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Save for '{character_name}' not found at {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file '{filepath}': {e}")

    data = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip().upper()] = value.strip()

    required_keys = {
        "NAME": "name",
        "CLASS": "class",
        "LEVEL": "level",
        "HEALTH": "health",
        "MAX_HEALTH": "max_health",
        "STRENGTH": "strength",
        "MAGIC": "magic",
        "EXPERIENCE": "experience",
        "GOLD": "gold",
        "INVENTORY": "inventory",
        "ACTIVE_QUESTS": "active_quests",
        "COMPLETED_QUESTS": "completed_quests",
    }

    for file_key in required_keys.keys():
        if file_key not in data:
            raise InvalidSaveDataError(f"Missing key '{file_key}' in save file '{filepath}'")

    def csv_to_list(s):
        s = s.strip()
        if s == "":
            return []
        return [token for token in (part.strip() for part in s.split(",")) if token != ""]

    try:
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            "experience": int(data["EXPERIENCE"]),
            "gold": int(data["GOLD"]),
            "inventory": csv_to_list(data["INVENTORY"]),
            "active_quests": csv_to_list(data["ACTIVE_QUESTS"]),
            "completed_quests": csv_to_list(data["COMPLETED_QUESTS"]),
        }
    except ValueError as e:
        raise InvalidSaveDataError(f"Invalid numeric value in save file '{filepath}': {e}")

    validate_character_data(character)
    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    if not os.path.isdir(save_directory):
        return []

    names = []
    for fname in os.listdir(save_directory):
        if not fname.endswith("_save.txt"):
            continue
        base = fname[:-len("_save.txt")]
        if base:
            names.append(base)
    return names


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"No save found for '{character_name}'")

    os.remove(filepath)
    return True



# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    
    Level up formula: level_up_xp = current_level * 100
    Example when leveling up:
    - Increase level by 1
    - Increase max_health by 10
    - Increase strength by 2
    - Increase magic by 2
    - Restore health to max_health
    
    Raises: CharacterDeadError if character health is 0
    """
    if is_character_dead(character):
        raise CharacterDeadError("Character is dead.")

    try:
        xp_amount = int(xp_amount)
    except Exception:
        raise ValueError("xp_amount must be an integer-like value")

    if xp_amount < 0:
        character["experience"] = max(0, character.get("experience", 0) + xp_amount)
        return character["experience"]

    character["experience"] = character.get("experience", 0) + xp_amount

    while character["experience"] >= character["level"] * 100:
        required = character["level"] * 100
        character["experience"] -= required
        character["level"] += 1
        character["max_health"] = character.get("max_health", 0) + 10
        character["strength"] = character.get("strength", 0) + 2
        character["magic"] = character.get("magic", 0) + 2
        character["health"] = character["max_health"]

    return character["experience"]


def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    try:
        amount = int(amount)
    except Exception:
        raise ValueError("amount must be integer-like")

    current = int(character.get("gold", 0))
    new_total = current + amount
    if new_total < 0:
        raise ValueError("Insufficient gold: operation would result in negative gold")
    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    try:
        amount = int(amount)
    except Exception:
        raise ValueError("amount must be integer-like")

    max_h = int(character.get("max_health", 0))
    cur_h = int(character.get("health", 0))
    if cur_h >= max_h:
        return 0

    heal_amt = min(amount, max_h - cur_h)
    character["health"] = cur_h + heal_amt
    return heal_amt



def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    return int(character.get("health", 0)) <= 0



def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    if not is_character_dead(character):
        return False

    max_h = int(character.get("max_health", 0))
    restored = max(1, int(max_h * 0.5))
    character["health"] = restored
    return True



# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Required fields: name, class, level, health, max_health, 
                    strength, magic, experience, gold, inventory,
                    active_quests, completed_quests
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_keys = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    if not isinstance(character, dict):
        raise InvalidSaveDataError("Character must be a dictionary")

    for key in required_keys:
        if key not in character:
            raise InvalidSaveDataError(f"Missing required key '{key}'")

    if not isinstance(character["name"], str) or character["name"] == "":
        raise InvalidSaveDataError("Invalid 'name' value")

    if character["class"] not in ["Warrior", "Mage", "Rogue", "Cleric"]:
        raise InvalidSaveDataError(f"Invalid 'class' value: {character['class']}")

    int_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for k in int_fields:
        if not isinstance(character[k], int):
            raise InvalidSaveDataError(f"Field '{k}' must be an integer")

    list_fields = ["inventory", "active_quests", "completed_quests"]
    for k in list_fields:
        if not isinstance(character[k], list):
            raise InvalidSaveDataError(f"Field '{k}' must be a list")

    if character["health"] > character["max_health"]:
        raise InvalidSaveDataError("health cannot exceed max_health")

    if character["level"] < 1:
        raise InvalidSaveDataError("level must be >= 1")

    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    try:
        char = create_character("TestHero", "Warrior")
        print(f"Created: {char['name']} the {char['class']}")
        print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    except InvalidCharacterClassError as e:
        print(f"Invalid class: {e}")
    
    # Test saving
    try:
        save_character(char)
        print("Character saved successfully")
    except Exception as e:
        print(f"Save error: {e}")
    
    # Test loading
    try:
        loaded = load_character("TestHero")
        print(f"Loaded: {loaded['name']}")
    except CharacterNotFoundError:
        print("Character not found")
    except SaveFileCorruptedError:
        print("Save file corrupted")

