"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Ryleigh Butler

AI Usage: Used ChatGPT to help figure out how to get the main to run without error.

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice
    
    Options:
    1. New Game
    2. Load Game
    3. Exit
    
    Returns: Integer choice (1-3)
    """
    # How to start the game. Loop until one of the 3 option are chosen
    while True:
        print("\nMain Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Select an option (1-3): ").strip()

        # Validate menu choice
        if choice in ['1','2','3']:
            return int(choice)
        print("Invalid choice. Please select 1-3.")

def new_game():
    """
    Start a new game
    
    Prompts for:
    - Character name
    - Character class
    
    Creates character and starts game loop
    """
    # If you select new game, you choose character name and class
    global current_character

    while True:
        # Get character name
        name = input("Enter your character's name: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue

        # Choose class
        print("Select your character's class:")
        print("1. Warrior\n2. Mage\n3. Rogue")
        class_choice = input("Enter class number (1-3): ").strip()

        class_map = {'1': 'Warrior', '2': 'Mage', '3': 'Rogue'}

        # Validate class selection
        if class_choice in class_map:
            character_class = class_map[class_choice]
            try:
                # Create and save the character
                current_character = character_manager.create_character(name, character_class)
                character_manager.save_character(current_character)

                print(f"Character '{name}' the {character_class} created successfully!")
                game_loop()
                return

            except InvalidCharacterClassError as e:
                print(f"Error: {e}")

            except Exception as e:
                print(f"Unexpected error creating character: {e}")
                return

        else:
            print("Invalid class choice. Please select 1-3.")


def load_game():
    """
    Load an existing saved game
    
    Shows list of saved characters
    Prompts user to select one
    """
    # Loads previously saved game
    global current_character
    try:
        saved_characters = character_manager.list_saved_characters()
    except Exception:
        saved_characters = []

    # No characters saved
    if not saved_characters:
        print("No saved characters found.")
        return

    print("\nSaved Characters:")
    for idx, char_name in enumerate(saved_characters, start=1):
        print(f"{idx}. {char_name}")

    # Select character to load
    while True:
        choice = input(f"Select a character to load (1-{len(saved_characters)}): ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(saved_characters):
            selected_name = saved_characters[int(choice) - 1]
            try:
                current_character = character_manager.load_character(selected_name)
                print(f"Character '{selected_name}' loaded successfully!")
                game_loop()
                return

            except (CharacterNotFoundError, SaveFileCorruptedError) as e:
                print(f"Error: {e}")

            except Exception as e:
                print(f"Unexpected error loading character: {e}")
                return

        else:
            print(f"Invalid choice. Please select 1-{len(saved_characters)}.")


# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main game loop - shows game menu and processes actions
    """
    global game_running, current_character
    
    game_running = True

    while game_running:
        choice = game_menu()

        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            save_game()
            print("Exiting to main menu...")
            break


def game_menu():
    """
    Display game menu and get player choice
    
    Options:
    1. View Character Stats
    2. View Inventory
    3. Quest Menu
    4. Explore (Find Battles)
    5. Shop
    6. Save and Quit
    
    Returns: Integer choice (1-6)
    """
    # Where the player chooses what to do in the game
    while True:
        print("\nGame Menu:")
        print("1. View Character Stats\n2. View Inventory\n3. Quest Menu")
        print("4. Explore (Find Battles)\n5. Shop\n6. Save and Quit")

        choice = input("Select an option (1-6): ").strip()

        # Validate input
        if choice in ['1', '2', '3', '4', '5', '6']:
            return int(choice)

        print("Invalid choice. Please select 1-6.")

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Display character information"""
    global current_character
    if not current_character:
        print("No character loaded.")
        return

    # Get character info safely
    name = current_character.get('name', 'Unknown')
    clazz = current_character.get('class', 'Unknown')
    level = current_character.get('level', 'Unknown')
    health = current_character.get('health', 0)
    max_health = current_character.get('max_health', 0)
    gold = current_character.get('gold', 0)
    stats = current_character.get('stats', {})

    print(f"\nCharacter Stats for {name}:")
    print(f"Class: {clazz}\nLevel: {level}\nHealth: {health}/{max_health}\nGold: {gold}")

    print("Stats:")
    for stat, value in stats.items():
        print(f"  {stat.capitalize()}: {value}")

    print("Active Quests:")

    try:
        active_quests = quest_handler.get_active_quests(current_character, all_quests)
    except Exception:
        active_quests = []

    # Display active quests
    if active_quests:
        for quest_id in active_quests:
            quest = all_quests.get(quest_id, {})
            print(f"  - {quest.get('title', quest_id)}: {quest.get('description', '')}")
    else:
        print("  None")

def view_inventory():
    """Display and manage inventory"""
    global current_character, all_items
    if not current_character:
        print("No character loaded.")
        return

    from inventory_system import use_item, equip_weapon, equip_armor, display_inventory

    while True:
        print("\nInventory:")
        display_inventory(current_character, all_items)

        # Inventory actions
        action = input("\nActions: Use (u), Equip Weapon (w), Equip Armor (a), Back (b): ").lower()

        if action == 'u':
            item_id = input("Enter item ID to use: ").strip()
            if item_id in all_items:
                try:
                    print(use_item(current_character, item_id, all_items[item_id]))
                except Exception as e:
                    print(f"Cannot use item: {e}")
            else:
                print("Invalid item ID.")

        elif action == 'w':
            item_id = input("Enter weapon ID to equip: ").strip()
            if item_id in all_items:
                try:
                    equip_weapon(current_character, item_id, all_items)
                    print(f"Equipped weapon: {all_items[item_id]['name']}")
                except Exception as e:
                    print(f"Cannot equip weapon: {e}")
            else:
                print("Invalid item ID.")

        elif action == 'a':
            item_id = input("Enter armor ID to equip: ").strip()
            if item_id in all_items:
                try:
                    equip_armor(current_character, item_id, all_items)
                    print(f"Equipped armor: {all_items[item_id]['name']}")
                except Exception as e:
                    print(f"Cannot equip armor: {e}")
            else:
                print("Invalid item ID.")

        elif action == 'b':
            break  # Exit inventory

        else:
            print("Invalid action. Enter u, w, a, or b.")
 


def quest_menu():
    """Quest management menu"""
    global current_character, all_quests
    from quest_handler import QuestNotFoundError, QuestAlreadyAcceptedError, QuestNotAcceptedError

    while True:
        print("\nQuest Menu:")
        print("1. View Active Quests\n2. View Available Quests\n3. View Completed Quests")
        print("4. Accept Quest\n5. Abandon Quest\n6. Complete Quest (Testing)\n7. Back")

        choice = input("Select an option (1-7): ").strip()

        if choice == '1':
            try:
                active_quests = quest_handler.get_active_quests(current_character, all_quests)
            except Exception:
                active_quests = []

            print("\nActive Quests:")
            if active_quests:
                for qid in active_quests:
                    quest = all_quests.get(qid, {})
                    print(f"  - {quest.get('title', qid)}: {quest.get('description', '')}")
            else:
                print("  None")

        elif choice == '2':
            try:
                available_quests = quest_handler.get_available_quests(current_character, all_quests)
            except Exception:
                available_quests = []

            print("\nAvailable Quests:")
            if available_quests:
                for qid in available_quests:
                    quest = all_quests.get(qid, {})
                    print(f"  - {quest.get('title', qid)}: {quest.get('description', '')}")
            else:
                print("  None")

        elif choice == '3':
            try:
                completed_quests = quest_handler.get_completed_quests(current_character, all_quests)
            except Exception:
                completed_quests = []

            print("\nCompleted Quests:")
            if completed_quests:
                for qid in completed_quests:
                    quest = all_quests.get(qid, {})
                    print(f"  - {quest.get('title', qid)}: {quest.get('description', '')}")
            else:
                print("  None")

        elif choice == '4':
            quest_id = input("Enter Quest ID to accept: ").strip()
            try:
                quest_handler.accept_quest(current_character, quest_id, all_quests)
                print(f"Quest '{quest_id}' accepted!")
            except (QuestNotFoundError, QuestAlreadyAcceptedError) as e:
                print(f"Error: {e}")

        elif choice == '5':
            quest_id = input("Enter Quest ID to abandon: ").strip()
            try:
                quest_handler.abandon_quest(current_character, quest_id)
                print(f"Quest '{quest_id}' abandoned.")
            except QuestNotAcceptedError as e:
                print(f"Error: {e}")

        elif choice == '6':
            quest_id = input("Enter Quest ID to complete (testing): ").strip()
            try:
                quest_handler.complete_quest(current_character, quest_id, all_quests)
                print(f"Quest '{quest_id}' completed!")
            except QuestNotAcceptedError as e:
                print(f"Error: {e}")

        elif choice == '7':
            break  # Exit quest menu

        else:
            print("Invalid choice. Please select 1-7.")


def explore():
    """Find and fight random enemies"""
    global current_character
    import random
    from combat_system import SimpleBattle, CharacterDeadError

    if not current_character:
        print("No character loaded.")
        return

    # Enemy level is equal or slightly higher than player level
    level = current_character.get('level', 1)
    enemy_level = random.choice([level, level + 1])

    # Generate enemy
    try:
        enemy = combat_system.generate_random_enemy(enemy_level)
    except AttributeError:
        # Fallback enemy if system fails
        enemy = combat_system.create_enemy("goblin")
        enemy['level'] = enemy_level

    print(f"\nA wild {enemy.get('name', 'Enemy')} (Level {enemy.get('level', '?')}) appears!")

    battle = SimpleBattle(current_character, enemy)

    try:
        result = battle.start_battle()
        winner = result.get('winner') if isinstance(result, dict) else result

        if winner in ('player', 'victory'):
            xp = enemy.get('xp_reward', 0)
            gold = enemy.get('gold_reward', 0)

            # Give rewards
            try:
                character_manager.gain_experience(current_character, xp)
            except Exception:
                current_character['experience'] = current_character.get('experience', 0) + xp

            current_character['gold'] = current_character.get('gold', 0) + gold
            print(f"You defeated the {enemy.get('name')}! Gained {xp} XP and {gold} gold.")

        else:
            handle_character_death()

    except CharacterDeadError:
        handle_character_death()

def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    from inventory_system import purchase_item, sell_item
    from inventory_system import InsufficientResourcesError, ItemNotFoundError, InventoryFullError

    while True:
        print("\nShop Menu:\n1. Buy Item\n2. Sell Item\n3. Back")

        choice = input("Select an option (1-3): ").strip()

        if choice == '1':
            print("\nItems for Sale:")
            for item_id, item in all_items.items():
                print(f"  - {item.get('name')} (ID: {item_id}) - Cost: {item.get('cost', 0)} gold")

            item_id = input("Enter Item ID to buy: ").strip()

            if item_id in all_items:
                try:
                    purchase_item(current_character, item_id, all_items[item_id])
                    print(f"Purchased '{all_items[item_id]['name']}'!")
                except (InsufficientResourcesError, InventoryFullError) as e:
                    print(f"Error: {e}")
            else:
                print("Invalid Item ID.")

        elif choice == '2':
            inventory = current_character.get('inventory', [])

            if inventory:
                print("\nYour Inventory:")
                for item_id in inventory:
                    print(f"  - {all_items.get(item_id, {'name': 'Unknown'})['name']} (ID: {item_id})")

                item_id = input("Enter Item ID to sell: ").strip()

                if item_id in all_items:
                    try:
                        gold = sell_item(current_character, item_id, all_items[item_id])
                        print(f"Sold '{all_items[item_id]['name']}' for {gold} gold!")
                    except ItemNotFoundError as e:
                        print(f"Error: {e}")

                else:
                    print("Invalid Item ID.")
            else:
                print("Inventory is empty.")

        elif choice == '3':
            break  # Exit shop

        else:
            print("Invalid choice. Enter 1-3.")
# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save current game state"""
    global current_character
    try:
        character_manager.save_character(current_character)
        print("Game saved successfully!")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game_data():
    """Load all quest and item data from files"""
    global all_quests, all_items

    try:
        all_quests = game_data.load_quests()
    except Exception:
        all_quests = {}

    try:
        all_items = game_data.load_items()
    except Exception:
        all_items = {}


def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    if not current_character:
        return

    print(f"\n{current_character.get('name', 'Your character')} has fallen in battle!")

    while True:
        choice = input("Revive (R) or Quit (Q)? ").strip().upper()

        if choice == 'R':
            try:
                character_manager.revive_character(current_character)
                print(f"{current_character.get('name')} has been revived!")
                return
            except Exception:
                # Fallback revival system
                cost = 10
                if current_character.get('gold', 0) >= cost:
                    current_character['gold'] -= cost
                    current_character['health'] = current_character.get('max_health', 100)
                    print("You paid the revive fee and were revived.")
                    return
                else:
                    print("Not enough gold to revive!")

        elif choice == 'Q':
            game_running = False
            print("Thanks for playing Quest Chronicles!")
            return



def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()

