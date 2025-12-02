"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        raise CorruptedDataError(f"Unable to read {filename}")

    if not content:
        raise InvalidDataFormatError("Quest file is empty or improperly formatted.")

    raw_blocks = content.split("\n\n")
    quests = {}

    for block in raw_blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if len(lines) != 7:
            raise InvalidDataFormatError(f"Incomplete quest block:\n{block}")

        expected_fields = ["QUEST_ID:", "TITLE:", "DESCRIPTION:", "REWARD_XP:", "REWARD_GOLD:", "REQUIRED_LEVEL:", "PREREQUISITE:"]
        for line, field in zip(lines, expected_fields):
            if not line.startswith(field):
                raise InvalidDataFormatError(f"Expected '{field}' in line: '{line}'")

        try:
            quest_id = lines[0].replace("QUEST_ID:", "", 1).strip()
            title = lines[1].replace("TITLE:", "", 1).strip()
            description = lines[2].replace("DESCRIPTION:", "", 1).strip()
            reward_xp = int(lines[3].replace("REWARD_XP:", "", 1).strip())
            reward_gold = int(lines[4].replace("REWARD_GOLD:", "", 1).strip())
            required_level = int(lines[5].replace("REQUIRED_LEVEL:", "", 1).strip())
            prerequisite = lines[6].replace("PREREQUISITE:", "", 1).strip()
        except Exception:
            raise InvalidDataFormatError(f"Invalid values in quest block:\n{block}")

        quests[quest_id] = {
            "quest_id": quest_id,
            "title": title,
            "description": description,
            "reward_xp": reward_xp,
            "reward_gold": reward_gold,
            "required_level": required_level,
            "prerequisite": prerequisite
        }

    return quests




def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        raise CorruptedDataError(f"Unable to read {filename}")

    if not content:
        raise InvalidDataFormatError("Item file is empty or improperly formatted.")

    raw_blocks = content.split("\n\n")
    items = {}

    for block in raw_blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if len(lines) != 6:
            raise InvalidDataFormatError(f"Incomplete item block:\n{block}")

        expected = ["ITEM_ID:", "NAME:", "TYPE:", "EFFECT:", "COST:", "DESCRIPTION:"]
        for line, field in zip(lines, expected):
            if not line.startswith(field):
                raise InvalidDataFormatError(f"Expected '{field}' in line: '{line}'")

        try:
            item_id = lines[0].replace("ITEM_ID:", "", 1).strip()
            name = lines[1].replace("NAME:", "", 1).strip()
            typ = lines[2].replace("TYPE:", "", 1).strip().lower()
            effect = lines[3].replace("EFFECT:", "", 1).strip()
            cost = int(lines[4].replace("COST:", "", 1).strip())
            description = lines[5].replace("DESCRIPTION:", "", 1).strip()
        except Exception:
            raise InvalidDataFormatError(f"Invalid values in item block:\n{block}")

        items[item_id] = {
            "item_id": item_id,
            "name": name,
            "type": typ,
            "effect": effect,
            "cost": cost,
            "description": description
        }



def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    required = ["quest_id", "title", "description", "reward_xp", "reward_gold", "required_level", "prerequisite"]
    for k in required:
        if k not in quest_dict:
            raise InvalidDataFormatError(f"Missing field: {k}")
    if not isinstance(quest_dict["reward_xp"], int):
        raise InvalidDataFormatError("reward_xp must be integer")
    if not isinstance(quest_dict["reward_gold"], int):
        raise InvalidDataFormatError("reward_gold must be integer")
    if not isinstance(quest_dict["required_level"], int):
        raise InvalidDataFormatError("required_level must be integer")
    return True


def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required = ["item_id", "name", "type", "effect", "cost", "description"]
    for k in required:
        if k not in item_dict:
            raise InvalidDataFormatError(f"Missing field: {k}")
    if item_dict["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type")
    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("Item cost must be integer")
    if ":" not in item_dict["effect"]:
        raise InvalidDataFormatError("Item effect format invalid")
    return True


def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists("data/quests.txt"):
        try:
            with open("data/quests.txt", "w", encoding="utf-8") as f:
                f.write(
                    "QUEST_ID: intro_quest\n"
                    "TITLE: First Steps\n"
                    "DESCRIPTION: Your journey begins.\n"
                    "REWARD_XP: 50\n"
                    "REWARD_GOLD: 10\n"
                    "REQUIRED_LEVEL: 1\n"
                    "PREREQUISITE: NONE\n\n"
                )
        except Exception:
            raise CorruptedDataError("Unable to create quests.txt")

    if not os.path.exists("data/items.txt"):
        try:
            with open("data/items.txt", "w", encoding="utf-8") as f:
                f.write(
                    "ITEM_ID: basic_sword\n"
                    "NAME: Basic Sword\n"
                    "TYPE: weapon\n"
                    "EFFECT: strength:5\n"
                    "COST: 30\n"
                    "DESCRIPTION: A simple iron sword.\n\n"
                )
        except Exception:
            raise CorruptedDataError("Unable to create items.txt")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    quest_data = {}

    try:
        for line in lines:
            if not line.strip():
                continue  # ignore blank lines

            if ": " not in line:
                raise InvalidDataFormatError(f"Invalid quest line format: {line}")

            key, value = line.split(": ", 1)

            key = key.strip().upper()
            value = value.strip()

            # Convert numeric fields
            if key in ("REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL"):
                if not value.isdigit():
                    raise InvalidDataFormatError(f"Expected integer for {key}, got '{value}'")
                value = int(value)

            # Store normalized (lowercase keys)
            quest_data[key.lower()] = value

        # Required fields
        required_keys = [
            "quest_id",
            "title",
            "description",
            "reward_xp",
            "reward_gold",
            "required_level",
            "prerequisite"
        ]

        for k in required_keys:
            if k not in quest_data:
                raise InvalidDataFormatError(f"Missing required quest field: {k}")

        return quest_data

    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing quest block: {e}")


def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    item_data = {}

    try:
        for line in lines:
            if not line.strip():
                continue  # skip empty lines

            if ": " not in line:
                raise InvalidDataFormatError(f"Invalid item line format: {line}")

            key, value = line.split(": ", 1)

            key = key.strip().upper()
            value = value.strip()

            # Convert numerical fields
            # These are standard for most RPG item systems
            if key in ("VALUE", "POWER", "HEAL_AMOUNT", "DEFENSE"):
                if not value.isdigit():
                    raise InvalidDataFormatError(f"Expected integer for {key}, got '{value}'")
                value = int(value)

            item_data[key.lower()] = value

        # Required fields may vary based on your game structure
        # We use a general set that fits common RPG item systems
        required_keys = [
            "item_id",
            "name",
            "type",        # example: "weapon", "armor", "potion"
            "description",
            "value"
        ]

        for k in required_keys:
            if k not in item_data:
                raise InvalidDataFormatError(f"Missing required item field: {k}")

        return item_data

    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing item block: {e}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    try:
        quests = load_quests()
        print(f"Loaded {len(quests)} quests")
    except MissingDataFileError:
        print("Quest file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid quest format: {e}")
    
    # Test loading items
    try:
        items = load_items()
        print(f"Loaded {len(items)} items")
    except MissingDataFileError:
        print("Item file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid item format: {e}")

