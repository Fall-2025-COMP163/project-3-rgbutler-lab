"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Ryleigh Butler

AI Usage: Used ChatGPT to help figure out how to get the main to run without error. Used it to load the game before each game loop.

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
        print("\n=== MAIN MENU ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()
        if choice in {"1", "2", "3"}:
            return int(choice)
        print("Invalid input. Enter 1, 2, or 3.")


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
    print("\n=== NEW GAME ===")
    name = input("Enter your character name: ").strip()
    print("Choose a class:")
    print("1. Warrior")
    print("2. Mage")
    print("3. Rogue")
    print("4. Cleric")
    class_map = {"1": "Warrior", "2": "Mage", "3": "Rogue", "4": "Cleric"}

    while True:
        class_choice = input("Enter class number: ").strip()
        if class_choice in class_map:
            chosen_class = class_map[class_choice]
            break
        print("Invalid class. Choose 1–4.")

    try:
        current_character = character_manager.create_character(name, chosen_class)
        print(f"\nCharacter '{name}' the {chosen_class} created successfully!")
    except InvalidCharacterClassError as e:
        print("Error: Invalid character class.", e)
        return

    # Make sure data is loaded before game loop (defensive)
    load_game_data()

    game_loop()

def load_game():
    """
    Load an existing saved game
    
    Shows list of saved characters
    Prompts user to select one
    """
    # Loads previously saved game
    global current_character
    print("\n=== LOAD GAME ===")
    saves = character_manager.list_saved_characters()
    if not saves:
        print("No save files found.")
        return
    print("\nSaved Characters:")
    for i, save in enumerate(saves, start=1):
        print(f"{i}. {save}")

    while True:
        try:
            choice = int(input("Choose a character to load: ").strip())
            if 1 <= choice <= len(saves):
                filename = saves[choice - 1]
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Enter a valid number.")

    try:
        current_character = character_manager.load_character(filename)
        print(f"\nLoaded character: {current_character['name']}")
    except CharacterNotFoundError:
        print("Error: Character not found.")
        return
    except SaveFileCorruptedError:
        print("Error: Save file corrupted.")
        return
    except InvalidSaveDataError as e:
        print("Invalid save data:", e)
        return

    # Ensure game data is loaded before entering loop
    load_game_data()
    game_loop()
    


# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main game loop - shows game menu and processes actions
    """
    global game_running, current_character
    
    if current_character is None:
        print("No active character. Returning to main menu.")
        return

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
            print("\nSaving game...")
            save_game()
            print("Goodbye!")
            game_running = False



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
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")
    while True:
        choice = input("Choose (1-6): ").strip()
        if choice in {"1","2","3","4","5","6"}:
            return int(choice)
        print("Invalid option.")


# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Display character information"""
    global current_character
    if current_character is None:
        print("No character loaded.")
        return
    # Had to use ChatGPT to help me figure out how to get this to run without error. I needed to add .get.
    print("\n=== CHARACTER STATS ===")
    print(f"Name: {current_character.get('name','UNKNOWN')}")
    print(f"Class: {current_character.get('class','UNKNOWN')}")
    print(f"Level: {current_character.get('level',0)}")
    print(f"HP: {current_character.get('health',0)}/{current_character.get('max_health',0)}")
    print(f"STR: {current_character.get('strength',0)}, MAG: {current_character.get('magic',0)}")
    print(f"XP: {current_character.get('experience',0)}, Gold: {current_character.get('gold',0)}")
    print("Active Quests:", current_character.get("active_quests", []))
    print("Completed Quests:", current_character.get("completed_quests", []))
    quest_handler.display_character_quest_progress(current_character, all_quests)

def view_inventory():
    """Display and manage inventory"""
    global current_character, all_items
    if current_character is None:
        print("No character loaded.")
        return
    # Also needed help from ChatGPT to get this to run without error.
    print("\n=== INVENTORY ===")
    inventory_system.display_inventory(current_character, all_items)
    print("\n1. Use Item")
    print("2. Equip Weapon")
    print("3. Equip Armor")
    print("4. Drop Item")
    print("5. Back")
    choice = input("Choose an option: ").strip()
    if choice == "1":
        item_id = input("Enter item ID to use: ").strip()
        if item_id not in all_items:
            print("Invalid item ID.")
            return
        try:
            result = inventory_system.use_item(current_character, item_id, all_items[item_id])
            print(result)
        except Exception as e:
            print("Error:", e)
    elif choice == "2":
        item_id = input("Weapon item ID: ").strip()
        if item_id not in all_items:
            print("Invalid item.")
            return
        try:
            print(inventory_system.equip_weapon(current_character, item_id, all_items[item_id]))
        except Exception as e:
            print("Error:", e)
    elif choice == "3":
        item_id = input("Armor item ID: ").strip()
        if item_id not in all_items:
            print("Invalid item.")
            return
        try:
            print(inventory_system.equip_armor(current_character, item_id, all_items[item_id]))
        except Exception as e:
            print("Error:", e)
    elif choice == "4":
        item_id = input("Enter item to drop: ").strip()
        try:
            inventory_system.remove_item_from_inventory(current_character, item_id)
            print("Item dropped.")
        except ItemNotFoundError:
            print("Item not found.")
   


def quest_menu():
    """Quest management menu"""
    global current_character, all_quests
    if current_character is None:
        print("No character loaded.")
        return

    print("\n=== QUEST MENU ===")
    print("1. View Active Quests")
    print("2. View Available Quests")
    print("3. View Completed Quests")
    print("4. Accept Quest")
    print("5. Abandon Quest")
    print("6. Complete Quest (for testing)")
    print("7. Back")
    choice = input("Choose (1-7): ").strip()
    if choice == "1":
        quest_handler.display_quest_list(quest_handler.get_active_quests(current_character, all_quests))
    elif choice == "2":
        quest_handler.display_quest_list(quest_handler.get_available_quests(current_character, all_quests))
    elif choice == "3":
        quest_handler.display_quest_list(quest_handler.get_completed_quests(current_character, all_quests))
    elif choice == "4":
        qid = input("Enter quest ID: ").strip()
        try:
            quest_handler.accept_quest(current_character, qid, all_quests)
            print("Quest accepted!")
        except Exception as e:
            print("Error:", e)
    elif choice == "5":
        qid = input("Quest ID to abandon: ").strip()
        try:
            quest_handler.abandon_quest(current_character, qid)
            print("Quest abandoned.")
        except Exception as e:
            print("Error:", e)
    elif choice == "6":
        qid = input("Quest ID to complete: ").strip()
        try:
            rewards = quest_handler.complete_quest(current_character, qid, all_quests)
            print(f"Quest completed: +{rewards['xp']} XP, +{rewards['gold']} gold")
        except Exception as e:
            print("Error:", e)
  


def explore():
    """Find and fight random enemies"""
    global current_character
    print("\n=== EXPLORATION ===")
    if current_character is None:
        print("No character loaded.")
        return
    # Used ChatGPT to see I needed to add .get to avoid errors.
    enemy = combat_system.get_random_enemy_for_level(current_character.get("level",1))
    print(f"You encounter a {enemy['name']}!")
    battle = combat_system.SimpleBattle(current_character, enemy)
    try:
        result = battle.start_battle()
        if result and result.get("winner") == "player":
            xp = result.get("xp_gained", 0)
            gold = result.get("gold_gained", 0)
            print(f"You defeated the {enemy['name']}! +{xp} XP, +{gold} gold")
            try:
                character_manager.add_gold(current_character, gold)
                character_manager.gain_experience(current_character, xp)
            except Exception as e:
                print("Error applying rewards:", e)
        elif result and result.get("winner") == "enemy":
            print("You have been defeated...")
            handle_character_death()
        elif result and result.get("winner") == "escaped":
            print("You escaped.")
    except CharacterDeadError:
        print("\nYou have died!")
        handle_character_death()


def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    if current_character is None:
        print("No character loaded.")
        return

    # Ensure items are loaded (did not work without this)
    if not isinstance(all_items, dict) or not all_items:
        print("Shop currently unavailable (item data not loaded). Attempting to load default data...")
        try:
            game_data.create_default_data_files()
            # try reload once
            load_game_data()
        except Exception as e:
            print("Failed to initialize shop data:", e)
            return

        if not isinstance(all_items, dict) or not all_items:
            print("Shop is still unavailable. Try again later.")
            return

    print("\n=== SHOP ===")
    print(f"Gold: {current_character.get('gold',0)}")
    print("\nAvailable Items:")
    for item_id, data in all_items.items():
        item_name = data.get("name", item_id)
        item_cost = data.get("cost", "N/A")
        print(f"{item_id}: {item_name} - {item_cost} gold")

    print("\n1. Buy Item")
    print("2. Sell Item")
    print("3. Back")
    choice = input("Select: ").strip()
    if choice == "1":
        item_id = input("Item ID to buy: ").strip()
        if item_id not in all_items:
            print("Invalid item.")
            return
        try:
            inventory_system.purchase_item(current_character, item_id, all_items[item_id])
            print("Purchase successful!")
        except Exception as e:
            print("Error:", e)
    elif choice == "2":
        item_id = input("Item ID to sell: ").strip()
        if item_id not in all_items:
            print("Invalid item.")
            return
        try:
            gold = inventory_system.sell_item(current_character, item_id, all_items[item_id])
            print(f"Sold for {gold} gold.")
        except Exception as e:
            print("Error:", e)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save current game state"""
    global current_character
    if current_character is None:
        print("No character to save.")
        return
    try:
        character_manager.save_character(current_character)
        print("Game saved.")
    except Exception as e:
        print("Error saving game:", e)


def load_game_data():
    """Load all quest and item data from files"""
    try:
        q = game_data.load_quests()
        i = game_data.load_items()
        # Ensure we got dictionaries (not None)
        if not isinstance(q, dict) or not isinstance(i, dict):
            raise Exception("Loaded data not in expected format.")
        all_quests = q
        all_items = i
        return
    except (MissingDataFileError, InvalidDataFormatError, CorruptedDataError, Exception) as e:
        # Last-resort: create defaults and try once more
        try:
            print("Game data missing or invalid. Creating default data files...")
            game_data.create_default_data_files()
            all_quests = game_data.load_quests()
            all_items = game_data.load_items()
            if not isinstance(all_quests, dict) or not isinstance(all_items, dict):
                # If still invalid, fallback to empty dicts to avoid None
                all_quests = {}
                all_items = {}
        except Exception as e2:
            print("Failed to create or load default data:", e2)
            all_quests = {}
            all_items = {}


def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    print("\n=== YOU DIED ===")
    print("1. Revive (costs 50 gold)")
    print("2. Quit")
    choice = input("Choose: ").strip()
    if choice == "1":
        revived = character_manager.revive_character(current_character)
        if revived:
            try:
                character_manager.add_gold(current_character, -50)
                print("You have been revived for 50 gold!")
            except Exception:
                print("Not enough gold to pay revival. You are revived anyway in this implementation.")
        else:
            print("Could not revive.")
    else:
        print("Game over.")
        game_running = False


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

