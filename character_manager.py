"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Ryleigh Butler

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
    # Define which classes are valid
    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]

    # Raise error if the player picks a class that doesn't exist
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")
    
    # Assign stat values based on chosen class
    if character_class == "Warrior":
        health, strength, magic = 120, 15, 5
    elif character_class == "Mage":
        health, strength, magic = 80, 8, 20
    elif character_class == "Rogue":
        health, strength, magic = 90, 12, 10
    else:  # Cleric
        health, strength, magic = 100, 10, 15

    # Return structured character data as a dictionary
    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": health,
        "max_health": health,
        "strength": strength,
        "magic": magic,
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }


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
    import os

    # Create save directory if it doesn’t exist
    os.makedirs(save_directory, exist_ok=True)

    # Build the file path for the specific character
    file_path = os.path.join(save_directory, f"{character['name']}_save.txt")

    try:
        # Write each key-value pair into the save file
        with open(file_path, "w") as f:
            for key, value in character.items():
                f.write(f"{key}: {value}\n")
        return True

    except Exception as e:
        # Return False for any unexpected issue
        return False


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
    import os

    # Find the save file for this character
    file_path = os.path.join(save_directory, f"{character_name}_save.txt")

    # If missing, raise custom "not found" error
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Character '{character_name}' does not exist.")

    character = {}

    try:
        # Read all lines from the file
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Process each line individually
        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip blank lines

            # Ensure the line has a key/value structure
            if ": " not in line:
                raise SaveFileCorruptedError(f"Malformed line in save file: {line}")

            key, value = line.split(": ", 1)

            # Convert numeric strings back into integers
            if value.isdigit():
                value = int(value)

            # Convert list strings back into Python lists
            elif value.startswith("[") and value.endswith("]"):
                value = eval(value)

            character[key] = value

        return character

    except Exception as e:
        # Wrap any error into a "corrupted save file" exception
        raise SaveFileCorruptedError(
            f"Could not read save file for '{character_name}'"
        ) from e


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    if not os.path.exists(save_directory):
        return []

    result = []

    # Loop over all files and extract character names
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            result.append(filename[:-9])  # remove "_save.txt"

    return result



def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    # Build file path
    file_path = os.path.join(save_directory, f"{character_name}_save.txt")

    # If file doesn't exist, raise an error
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Character '{character_name}' does not exist.")

    # Delete the file and confirm success
    os.remove(file_path)
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
    if character['health'] <= 0:
        raise CharacterDeadError("Cannot gain experience: character is dead.")

    character['experience'] += xp_amount

    # Loop in case multiple level-ups happen at once
    while character['experience'] >= character['level'] * 100:
        character['experience'] -= character['level'] * 100
        character['level'] += 1

        # Increase stats each level
        character['max_health'] += 10
        character['strength'] += 2
        character['magic'] += 2

        # Restore full health on level up
        character['health'] = character['max_health']

def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    if character['gold'] + amount < 0:
        raise ValueError("Insufficient gold.")

    character['gold'] += amount
    return character['gold']



def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    # If already fully healed, return 0 healing done
    if character['health'] >= character['max_health']:
        return 0

    # Heal but do not exceed max health
    new_health = min(character['health'] + amount, character['max_health'])
    healed_amount = new_health - character['health']
    character['health'] = new_health

    return healed_amount



def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    # Return True if health is zero or less
    return character['health'] <= 0



def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    if character['health'] > 0:
        return False

    # Revive to half of max health
    character['health'] = character['max_health'] // 2
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
    # Ensure all required fields are present
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    # Ensure numeric fields are integers
    numeric_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]

    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field '{field}' must be an integer.")

    # Ensure list fields are actually lists
    list_fields = ["inventory", "active_quests", "completed_quests"]

    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field '{field}' must be a list.")

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

