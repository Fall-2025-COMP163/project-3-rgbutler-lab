"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

from random import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()

    if enemy_type == "goblin":
        return {
            "name": "Goblin",
            "type": "goblin",
            "health": 50,
            "max_health": 50,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10
        }

    elif enemy_type == "orc":
        return {
            "name": "Orc",
            "type": "orc",
            "health": 80,
            "max_health": 80,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25
        }

    elif enemy_type == "dragon":
        return {
            "name": "Dragon",
            "type": "dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }

    else:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")



def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn = 0
        # TODO: Implement initialization
        # Store character and enemy
        # Set combat_active flag
        # Initialize turn counter
        pass
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        
        Raises: CharacterDeadError if character is already dead
        """
        if self.character["health"] <= 0:
            raise CharacterDeadError("Character cannot fight when dead.")

        display_battle_log("Battle begins!")
        display_combat_stats(self.character, self.enemy)

        while self.combat_active:
            self.turn += 1

            winner = self.player_turn()
            if winner:
                return winner

            winner = self.enemy_turn()
            if winner:
                return winner
    
    def player_turn(self):
        """
        Handle player's turn
        
        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError()

        print("\nChoose an action:")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Run")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            dmg = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, dmg)
            display_battle_log(f"You deal {dmg} damage!")
            display_combat_stats(self.character, self.enemy)

        elif choice == "2":
            try:
                result = use_special_ability(self.character, self.enemy)
                display_battle_log(result)
                display_combat_stats(self.character, self.enemy)
            except AbilityOnCooldownError:
                display_battle_log("Ability on cooldown! You lose your turn.")

        elif choice == "3":
            escaped = self.attempt_escape()
            if escaped:
                display_battle_log("You escaped successfully!")
                return {"winner": "escaped", "xp_gained": 0, "gold_gained": 0}
            else:
                display_battle_log("You failed to escape!")

        winner = self.check_battle_end()
        if winner:
            rewards = get_victory_rewards(self.enemy) if winner == "player" else {"xp": 0, "gold": 0}
            return {"winner": winner, "xp_gained": rewards["xp"], "gold_gained": rewards["gold"]}

        return None

    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError()

        dmg = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, dmg)
        display_battle_log(f"{self.enemy['name']} deals {dmg} damage to you!")
        display_combat_stats(self.character, self.enemy)

        winner = self.check_battle_end()
        if winner:
            rewards = get_victory_rewards(self.enemy) if winner == "player" else {"xp": 0, "gold": 0}
            return {"winner": winner, "xp_gained": rewards["xp"], "gold_gained": rewards["gold"]}

        return None

    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        
        Returns: Integer damage amount
        """
        dmg = attacker["strength"] - (defender["strength"] // 4)
        if dmg < 1:
            dmg = 1
        return dmg

    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
        target["health"] -= damage
        if target["health"] < 0:
            target["health"] = 0

    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy["health"] <= 0:
            self.combat_active = False
            return "player"
        if self.character["health"] <= 0:
            self.combat_active = False
            return "enemy"
        return None
        # TODO: Implement battle end check
        pass
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        
        Returns: True if escaped, False if failed
        """
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success



# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    
    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)
    
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    cls = character["class"]

    if cls == "Warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "Mage":
        return mage_fireball(character, enemy)
    elif cls == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "Cleric":
        return cleric_heal(character)
    else:
        raise InvalidTargetError("Character class not recognized.")


def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    dmg = character["strength"] * 2
    enemy["health"] -= dmg
    if enemy["health"] < 0:
        enemy["health"] = 0
    return f"Warrior Power Strike deals {dmg} damage!"



def mage_fireball(character, enemy):
    """Mage special ability"""
    dmg = character["magic"] * 2
    enemy["health"] -= dmg
    if enemy["health"] < 0:
        enemy["health"] = 0
    return f"Mage Fireball hits for {dmg} damage!"



def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    if random.random() < 0.5:
        dmg = character["strength"] * 3
        enemy["health"] -= dmg
        if enemy["health"] < 0:
            enemy["health"] = 0
        return f"Critical Strike succeeds! {dmg} damage!"
    else:
        return "Critical Strike failed! No damage."


def cleric_heal(character):
    """Cleric special ability"""
    heal_amt = 30
    character["health"] += heal_amt
    if character["health"] > character["max_health"]:
        character["health"] = character["max_health"]
    return f"Cleric heals for {heal_amt} HP!"

    
# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle
    """


def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {
        "xp": enemy["xp_reward"],
        "gold": enemy["gold_reward"]
    }


def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """


    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    """
    Display a formatted battle message
    """

    print(f">>> {message}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    try:
        goblin = create_enemy("goblin")
        print(f"Created {goblin['name']}")
    except InvalidTargetError as e:
        print(f"Invalid enemy: {e}")
    
    # Test battle
    test_char = {
        'name': 'Hero',
        'class': 'Warrior',
        'health': 120,
        'max_health': 120,
        'strength': 15,
        'magic': 5
    }
    
    battle = SimpleBattle(test_char, goblin)
    try:
        result = battle.start_battle()
        print(f"Battle result: {result}")
    except CharacterDeadError:
        print("Character is dead!")

