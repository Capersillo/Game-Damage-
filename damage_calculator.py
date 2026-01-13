import random
from enum import Enum
from dataclasses import dataclass

class DamageType(Enum):
    PHYSICAL = "physical"
    MAGICAL = "magical"
    TRUE = "true"
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"

@dataclass
class Attacker:
    name: str
    base_damage: float
    crit_chance: float = 0.0  # 0.0 to 1.0
    crit_multiplier: float = 2.0
    armor_penetration: float = 0.0  # 0.0 to 1.0

@dataclass
class Defender:
    name: str
    armor: float
    resistances: dict = None  # {DamageType: resistance_value}
    
    def __post_init__(self):
        if self.resistances is None:
            self.resistances = {}

class DamageCalculator:
    def __init__(self):
        self.damage_log = []
    
    def calculate_damage(self, attacker: Attacker, defender: Defender, 
                        damage_type: DamageType = DamageType.PHYSICAL,
                        skill_multiplier: float = 1.0) -> dict:
        """
        Calculate final damage with all modifiers.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
            damage_type: Type of damage being dealt
            skill_multiplier: Additional multiplier for skills/abilities
        
        Returns:
            Dictionary with damage breakdown
        """
        # Base damage
        base = attacker.base_damage * skill_multiplier
        
        # Critical hit check
        is_crit = random.random() < attacker.crit_chance
        crit_damage = base * attacker.crit_multiplier if is_crit else base
        
        # Armor/Resistance reduction
        if damage_type == DamageType.TRUE:
            # True damage ignores all defenses
            final_damage = crit_damage
            reduction = 0
        else:
            # Get resistance for this damage type
            resistance = defender.resistances.get(damage_type, 0)
            
            # For physical damage, use armor + resistance
            if damage_type == DamageType.PHYSICAL:
                effective_armor = defender.armor * (1 - attacker.armor_penetration)
                total_reduction = effective_armor + resistance
            else:
                total_reduction = resistance
            
            # Calculate damage reduction (diminishing returns formula)
            if total_reduction >= 0:
                reduction_percent = total_reduction / (total_reduction + 100)
            else:
                # Negative resistance increases damage
                reduction_percent = total_reduction / 100
            
            reduction = crit_damage * reduction_percent
            final_damage = max(0, crit_damage - reduction)
        
        result = {
            'attacker': attacker.name,
            'defender': defender.name,
            'base_damage': base,
            'is_critical': is_crit,
            'damage_after_crit': crit_damage,
            'damage_type': damage_type.value,
            'reduction': reduction,
            'final_damage': round(final_damage, 2)
        }
        
        self.damage_log.append(result)
        return result
    
    def calculate_dot(self, base_tick_damage: float, duration: float, 
                     tick_rate: float = 1.0) -> dict:
        """
        Calculate damage over time (DOT).
        
        Args:
            base_tick_damage: Damage per tick
            duration: Total duration in seconds
            tick_rate: Time between ticks in seconds
        
        Returns:
            Dictionary with DOT calculation
        """
        num_ticks = int(duration / tick_rate)
        total_damage = base_tick_damage * num_ticks
        
        return {
            'tick_damage': base_tick_damage,
            'num_ticks': num_ticks,
            'total_damage': total_damage,
            'duration': duration
        }
    
    def print_damage_report(self, result: dict):
        """Print a formatted damage report."""
        print(f"\n{'='*50}")
        print(f"{result['attacker']} attacks {result['defender']}")
        print(f"{'='*50}")
        print(f"Base Damage: {result['base_damage']:.2f}")
        if result['is_critical']:
            print(f"⚡ CRITICAL HIT! ⚡")
        print(f"Damage Type: {result['damage_type'].upper()}")
        print(f"Reduction: {result['reduction']:.2f}")
        print(f"Final Damage: {result['final_damage']:.2f}")
        print(f"{'='*50}\n")


# Example usage
if __name__ == "__main__":
    # ============================================
    # 🎮 CHANGE THESE NUMBERS TO GO CRAZY! 🎮
    # ============================================
    
    # ATTACKER STATS (Make these HUGE for crazy damage!)
    BASE_DAMAGE = 100           # Try: 1000, 5000, 10000!
    CRIT_CHANCE = 0.25          # 0.0 to 1.0 (1.0 = 100% crit!)
    CRIT_MULTIPLIER = 2.5       # Try: 5.0, 10.0, 100.0!
    ARMOR_PENETRATION = 0.2     # 0.0 to 1.0 (1.0 = ignore all armor!)
    
    # DEFENDER STATS
    DEFENDER_ARMOR = 50         # Try: 0, 100, 1000
    FIRE_RESISTANCE = 30        # Try: -100 (super weak), 200 (tank)
    ICE_RESISTANCE = -20        # Negative = weakness!
    
    # SKILL MULTIPLIERS (Apply to individual attacks)
    FIRE_SPELL_MULTIPLIER = 1.5    # Try: 3.0, 10.0, 50.0!
    ICE_SPELL_MULTIPLIER = 1.3     # Try: 5.0, 20.0!
    
    # ============================================
    
    # Create calculator
    calc = DamageCalculator()
    
    # Create attacker with YOUR settings
    warrior = Attacker(
        name="Warrior",
        base_damage=BASE_DAMAGE,
        crit_chance=CRIT_CHANCE,
        crit_multiplier=CRIT_MULTIPLIER,
        armor_penetration=ARMOR_PENETRATION
    )
    
    # Create defender with YOUR settings
    goblin = Defender(
        name="Goblin",
        armor=DEFENDER_ARMOR,
        resistances={
            DamageType.FIRE: FIRE_RESISTANCE,
            DamageType.ICE: ICE_RESISTANCE
        }
    )
    
    # Calculate different types of damage
    print("DAMAGE CALCULATIONS DEMO")
    
    # Normal physical attack
    result1 = calc.calculate_damage(warrior, goblin, DamageType.PHYSICAL)
    calc.print_damage_report(result1)
    
    # Fire spell (skill_multiplier for ability)
    result2 = calc.calculate_damage(
        warrior, goblin, 
        DamageType.FIRE, 
        skill_multiplier=FIRE_SPELL_MULTIPLIER
    )
    calc.print_damage_report(result2)
    
    # Ice spell (goblin is weak to ice)
    result3 = calc.calculate_damage(
        warrior, goblin, 
        DamageType.ICE,
        skill_multiplier=ICE_SPELL_MULTIPLIER
    )
    calc.print_damage_report(result3)
    
    # Poison DOT
    print("\nPOISON EFFECT (Damage Over Time)")
    print("="*50)
    dot = calc.calculate_dot(base_tick_damage=15, duration=10, tick_rate=2)
    print(f"Tick Damage: {dot['tick_damage']}")
    print(f"Number of Ticks: {dot['num_ticks']}")
    print(f"Total Damage: {dot['total_damage']}")
    print(f"Duration: {dot['duration']}s")
    print("="*50)
