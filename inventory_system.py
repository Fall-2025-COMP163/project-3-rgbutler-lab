"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character["inventory"].append(item_id)
    return True



def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character["inventory"]


def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed = character["inventory"][:]
    character["inventory"].clear()
    return removed




# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Cannot use item that is not in inventory.")

    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Item is not consumable.")

    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)
    remove_item_from_inventory(character, item_id)
    char_name = character.get("name", "Unknown Character")
    item_name = item_data.get("name", item_id)
    return f"{char_name} used {item_name} (+{value} {stat})"



def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Weapon not found in inventory.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Cannot equip non-weapon item.")

    stat, value = parse_item_effect(item_data["effect"])

    # Unequip current weapon if present
    if character.get("equipped_weapon"):
        old_id = character["equipped_weapon"]
        old_stat, old_val = parse_item_effect(character["equipped_weapon_effect"])
        character[old_stat] -= old_val
        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Inventory full when unequipping old weapon.")
        character["inventory"].append(old_id)

    apply_stat_effect(character, stat, value)
    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item_data["effect"]
    remove_item_from_inventory(character, item_id)
    return f"{character['name']} equipped {item_data['name']} (+{value} {stat})"


def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Armor not in inventory.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    stat, value = parse_item_effect(item_data["effect"])

    if character.get("equipped_armor"):
        old_id = character["equipped_armor"]
        old_stat, old_val = parse_item_effect(character["equipped_armor_effect"])
        character[old_stat] -= old_val
        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Inventory full when unequipping old armor.")
        character["inventory"].append(old_id)

    apply_stat_effect(character, stat, value)
    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item_data["effect"]
    remove_item_from_inventory(character, item_id)


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    if not character.get("equipped_weapon"):
        return None

    weapon_id = character["equipped_weapon"]
    effect = character["equipped_weapon_effect"]
    stat, value = parse_item_effect(effect)
    character[stat] -= value

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot unequip — inventory full.")

    character["inventory"].append(weapon_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return weapon_id


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if not character.get("equipped_armor"):
        return None

    armor_id = character["equipped_armor"]
    effect = character["equipped_armor_effect"]
    stat, value = parse_item_effect(effect)
    character[stat] -= value

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot unequip — inventory full.")

    character["inventory"].append(armor_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return armor_id


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = item_data["cost"]
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold to purchase.")
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full.")
    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Cannot sell item not in inventory.")
    sell_price = item_data["cost"] // 2
    character["inventory"].remove(item_id)
    character["gold"] += sell_price
    return sell_price


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    try:
        stat, value = effect_string.split(":")
        return stat, int(value)
    except Exception:
        raise InvalidItemTypeError(f"Invalid effect format: {effect_string}")


def apply_stat_effect(character, stat_name, value):
    if stat_name not in character:
        raise InvalidItemTypeError(f"Invalid stat '{stat_name}'")
    character[stat_name] += value
    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]



def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    if stat_name not in ["health", "max_health", "strength", "magic"]:
        raise ValueError(f"Invalid stat name: {stat_name}")

    # Apply the modification
    try:
        character[stat_name] += value
    except KeyError:
        raise KeyError(f"Character missing stat: {stat_name}")

    # Special rule: health cannot exceed max_health
    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]



def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    inventory = character.get("inventory", [])

    if not inventory:
        print("\n--- Inventory is empty ---\n")
        return

    # Count item occurrences
    item_counts = {}
    for item_id in inventory:
        item_counts[item_id] = item_counts.get(item_id, 0) + 1

    print("\n--- Inventory ---")

    # Display items
    for item_id, quantity in item_counts.items():
        # Fetch item data safely
        item_info = item_data_dict.get(item_id)

        if item_info:
            name = item_info.get("name", "Unknown Item")
            type_ = item_info.get("type", "Unknown Type")
        else:
            name = "Unknown Item"
            type_ = "Unknown Type"

        print(f"{name} ({type_})  x{quantity}")

    print("--------------------\n")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    try:
        add_item_to_inventory(test_char, "health_potion")
        print(f"Inventory: {test_char['inventory']}")
    except InventoryFullError:
        print("Inventory is full!")
    
    # Test using items
    test_item = {
        'item_id': 'health_potion',
        'type': 'consumable',
        'effect': 'health:20'
    }
    
    try:
        result = use_item(test_char, "health_potion", test_item)
        print(result)
    except ItemNotFoundError:
        print("Item not found")

