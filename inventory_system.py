"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Ryleigh Butler

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from typing import Counter
from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)
from game_data import parse_item_block

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character['inventory'].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    character['inventory'].remove(item_id)
    return True

def has_item(character, item_id):
    return item_id in character['inventory']

def count_item(character, item_id):
    return character['inventory'].count(item_id)

def get_inventory_space_remaining(character):
    return MAX_INVENTORY_SIZE - len(character['inventory'])

def clear_inventory(character):
    removed_items = character['inventory'][:]
    character['inventory'].clear()
    return removed_items

# -------------------------
# ITEM USAGE
# -------------------------

def use_item(character, item_id, item_data):
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    if item_data['type'] != 'consumable':
        raise InvalidItemTypeError(f"Item '{item_id}' is not a consumable.")
    effects = parse_effect_string(item_data['effect'])
    for stat, value in effects.items():
        apply_stat_effect(character, stat, value)
    remove_item_from_inventory(character, item_id)
    item_name = item_data.get('name', item_id)
    return f"Used {item_name}. Effects applied: {effects}"

# -------------------------
# EQUIPMENT
# -------------------------

def equip_weapon(character, item_id, item_data):
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Weapon '{item_id}' not in inventory.")
    if item_data.get('type') != 'weapon':
        raise InvalidItemTypeError(f"Item '{item_id}' is not a weapon.")

    # Unequip old weapon
    old_weapon_id = character.get('equipped_weapon')
    if old_weapon_id:
        old_weapon_data = character['inventory_data'].get(old_weapon_id, {}) if 'inventory_data' in character else {}
        for stat, value in parse_effect_string(old_weapon_data.get('effect','')).items():
            apply_stat_effect(character, stat, -value)
        add_item_to_inventory(character, old_weapon_id)

    # Equip new weapon
    character['equipped_weapon'] = item_id
    for stat, value in parse_effect_string(item_data.get('effect','')).items():
        apply_stat_effect(character, stat, value)
    remove_item_from_inventory(character, item_id)
    return True

def equip_armor(character, item_id, item_data):
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Armor '{item_id}' not in inventory.")
    if item_data.get('type') != 'armor':
        raise InvalidItemTypeError(f"Item '{item_id}' is not armor.")

    # Unequip old armor
    old_armor_id = character.get('equipped_armor')
    if old_armor_id:
        old_armor_data = character['inventory_data'].get(old_armor_id, {}) if 'inventory_data' in character else {}
        for stat, value in parse_effect_string(old_armor_data.get('effect','')).items():
            apply_stat_effect(character, stat, -value)
        add_item_to_inventory(character, old_armor_id)

    # Equip new armor
    character['equipped_armor'] = item_id
    for stat, value in parse_effect_string(item_data.get('effect','')).items():
        apply_stat_effect(character, stat, value)
    remove_item_from_inventory(character, item_id)
    return True

def unequip_item(character, item_data, slot):
    """Unequip weapon or armor"""
    equipped_slot = f"equipped_{slot}"
    item_id = character.get(equipped_slot)
    if not item_id:
        return None
    for stat, value in parse_effect_string(item_data.get('effect','')).items():
        apply_stat_effect(character, stat, -value)
    add_item_to_inventory(character, item_id)
    character[equipped_slot] = None
    return item_id

# -------------------------
# SHOP SYSTEM
# -------------------------

def purchase_item(character, item_id, item_data):
    if character['gold'] < item_data['cost']:
        raise InsufficientResourcesError("Not enough gold to purchase item.")
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character['gold'] -= item_data['cost']
    character['inventory'].append(item_id)
    return True

def sell_item(character, item_id, item_data):
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    sell_price = item_data['cost'] // 2
    character['inventory'].remove(item_id)
    character['gold'] += sell_price
    return sell_price

# -------------------------
# HELPERS
# -------------------------

def parse_effect_string(effect_str):
    """Convert 'stat: value, stat2: value2' to dict"""
    effects = {}
    if not effect_str:
        return effects
    for pair in effect_str.split(','):
        if ':' in pair:
            stat, value = pair.split(':', 1)
            effects[stat.strip()] = int(value.strip())
    return effects

def apply_stat_effect(character, stat, value):
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    if stat == 'health':
        character['health'] = min(max(character['health'], 0), character.get('max_health', character['health']))

def display_inventory(character, item_data_dict):
    inventory_count = Counter(character['inventory'])
    print("Inventory:")
    for item_id, count in inventory_count.items():
        item_name = item_data_dict.get(item_id, {}).get('name', item_id)
        item_type = item_data_dict.get(item_id, {}).get('type', 'Unknown')
        print(f"- {item_name} (Type: {item_type}) x{count}")