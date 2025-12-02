"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: Ryleigh Butler

AI Usage: Used AI to rework and fix issues

This module handles quest management, dependencies, and completion.
"""

import character_manager
from custom_exceptions import (
    InventoryFullError,
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)
from inventory_system import add_item_to_inventory

def accept_quest(character, quest_id, quest_data_dict):
    # Ensure quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")
    quest = quest_data_dict[quest_id]

     # Level requirement
    if character['level'] < quest['required_level']:
        raise InsufficientLevelError(f"Level too low for quest '{quest_id}'")
    
    # Prerequisite check
    prereq = quest['prerequisite']
    if prereq != "NONE" and prereq not in character['completed_quests']:
        raise QuestRequirementsNotMetError(f"Prerequisite '{prereq}' not done")
    
    # Quest already completed
    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed")
    
    # Quest already active
    if quest_id in character['active_quests']:
        raise QuestRequirementsNotMetError(f"Quest '{quest_id}' already active")

    # Add quest to active list
    character['active_quests'].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict, item_data_dict=None):
    # Ensure quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")
    # Must be in active quests
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")

    quest = quest_data_dict[quest_id]

    # Move quest from active to completed
    character['active_quests'].remove(quest_id)
    character['completed_quests'].append(quest_id)

    # Reward XP and gold
    character['experience'] += quest['reward_xp']
    character['gold'] += quest['reward_gold']

    # Reward items (optional)
    rewarded_items = []
    if item_data_dict and 'reward_items' in quest:
        for item_id in quest['reward_items']:
            try:
                add_item_to_inventory(character, item_id)
                rewarded_items.append(item_id)
            except InventoryFullError:
                print(f"Inventory full! Cannot add '{item_id}'")

    return {
        'reward_xp': quest['reward_xp'],
        'reward_gold': quest['reward_gold'],
        'reward_items': rewarded_items
    }

def abandon_quest(character, quest_id):
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")
    character['active_quests'].remove(quest_id)
    return True

# -------------------------
# QUEST DATA RETRIEVAL
# -------------------------

def get_active_quests(character, quest_data_dict):
    """Return a list of quest dictionaries for all active quests."""
    return [quest_data_dict[q] for q in character['active_quests'] if q in quest_data_dict]

def get_completed_quests(character, quest_data_dict):
    """Return a list of quest dictionaries for all completed quests."""
    return [quest_data_dict[q] for q in character['completed_quests'] if q in quest_data_dict]

def get_available_quests(character, quest_data_dict):
    """Return quests the character is eligible to accept."""
    return [q for qid, q in quest_data_dict.items() if can_accept_quest(character, qid, quest_data_dict)]

def is_quest_completed(character, quest_id):
    """Return True if quest is completed."""
    return quest_id in character['completed_quests']

def is_quest_active(character, quest_id):
    """Return True if quest is active."""
    return quest_id in character['active_quests']

def can_accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        return False
    quest = quest_data_dict[quest_id]
    prereq_done = quest['prerequisite'] == "NONE" or quest['prerequisite'] in character['completed_quests']
    not_taken = quest_id not in character['completed_quests'] and quest_id not in character['active_quests']
    return character['level'] >= quest['required_level'] and prereq_done and not_taken

# -------------------------
# QUEST STATISTICS
# -------------------------

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    return (len(character['completed_quests']) / total * 100) if total > 0 else 0.0

def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = sum(quest_data_dict[q]['reward_xp'] for q in character['completed_quests'] if q in quest_data_dict)
    total_gold = sum(quest_data_dict[q]['reward_gold'] for q in character['completed_quests'] if q in quest_data_dict)
    return {'total_xp': total_xp, 'total_gold': total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    return [q for q in quest_data_dict.values() if min_level <= q['required_level'] <= max_level]

def validate_quest_prerequisites(quest_data_dict):
    for qid, q in quest_data_dict.items():
        prereq = q['prerequisite']
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{qid}' has invalid prerequisite '{prereq}'")
    return True

# -------------------------
# MAIN TEST BLOCK
# -------------------------

if __name__ == "__main__":
    print("=== QUEST HANDLER MODULE TEST ===")

    # Example test character
    test_char = {
        'level': 1,
        'active_quests': [],
        'completed_quests': [],
        'experience': 0,
        'gold': 100,
        'inventory': []
    }

    # Sample item and quest data
    test_item_data = {'healing_potion': {'name': 'Healing Potion', 'type': 'consumable', 'effect': 'health:20'}}
    test_quests = {
        'first_quest': {
            'quest_id': 'first_quest',
            'title': 'First Steps',
            'description': 'Complete your first quest',
            'reward_xp': 50,
            'reward_gold': 25,
            'required_level': 1,
            'prerequisite': 'NONE',
            'reward_items': ['healing_potion']
        }
    }

    # Test accepting and completing a quest
    accept_quest(test_char, 'first_quest', test_quests)
    print("Quest accepted!")
    rewards = complete_quest(test_char, 'first_quest', test_quests, test_item_data)
    print(f"Quest completed! Rewards: {rewards}")
