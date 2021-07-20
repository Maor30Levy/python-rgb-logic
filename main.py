import random
from classes.game import Person, bcolors
from classes.magic import Spell
from classes.inventory import Item
import re

fire = Spell("Fire", 10, 100, "black")
thunder = Spell("Thunder", 10, 100, "black")
blizzard = Spell("Blizzard", 10, 100, "black")
meteor = Spell("Meteor", 20, 200, "black")
quake = Spell("Quake", 14, 140, "black")

cure = Spell("Cure", 12, 120, "white")
cura = Spell("Cura", 18, 200, "white")
curega = Spell("Curega", 50, 3000, "white")

potion = Item("Potion", "potion", "Heals 50 HP", 50)
hipotion = Item("Hi-Potion", "potion", "Heals 100 HP", 100)
superpotion = Item("Super-Potion", "potion", "Heals 500 HP", 500)
elixer = Item("Elixer", "elixer",
              "Fully restore HP/MP of one party members", 9999)
hielixer = Item("Mega-Elixer", "elixer",
                "Fully restore party's HP/MP", 9999)
grenade = Item("Grenade", "attack", "Deals 500 damage", 500)

player_spells = [fire, thunder, blizzard, meteor, cure, cura]
player1_items = [{"item": potion, "quantity": 15}, {"item": hipotion, "quantity": 5},
                 {"item": superpotion, "quantity": 5},
                 {"item": elixer, "quantity": 2},
                 {"item": hielixer, "quantity": 1}, {"item": grenade, "quantity": 2}]
player2_items = [{"item": potion, "quantity": 15}, {"item": hipotion, "quantity": 5},
                 {"item": superpotion, "quantity": 5},
                 {"item": elixer, "quantity": 2},
                 {"item": hielixer, "quantity": 1}, {"item": grenade, "quantity": 2}]
player3_items = [{"item": potion, "quantity": 15}, {"item": hipotion, "quantity": 5},
                 {"item": superpotion, "quantity": 5},
                 {"item": elixer, "quantity": 2},
                 {"item": hielixer, "quantity": 1}, {"item": grenade, "quantity": 2}]

enemy_spells = [fire, meteor, curega]

player1 = Person("Avi", 460, 65, 60,
                 34, player_spells, player1_items)
player2 = Person("Josh", 460, 65, 60, 34, player_spells, player2_items)
player3 = Person("Greg", 460, 65, 60, 34, player_spells, player3_items)
enemy1 = Person("Boss", 7000, 65, 60, 25, enemy_spells, [])
enemy2 = Person("Imp", 700, 40, 30, 25, enemy_spells, [])
enemy3 = Person("Imp", 700, 40, 30, 25, enemy_spells, [])

players = [player1, player2, player3]
enemies = [enemy1, enemy2, enemy3]
running = True


def player_play(player):
    player.choose_action()
    choice = input("Choose action:")
    if not validate_input(choice, 3, 0):
        return False
    index = int(choice) - 1
    if index == 0:
        player.choose_target(enemies)
        target_choice = input("Choose target:")
        if not validate_input(target_choice, len(enemies), 0):
            return False
        target_index = int(target_choice) - 1

        player_attack(player, target_index)
    elif index == 1:
        if player.get_mp() > 0:
            if not cast_spell_opt(player):
                return False
        else:
            print(bcolors.BOLD+"You don't have enough mp"+bcolors.ENDC)
            return False
    elif index == 2:
        if not use_item(player):
            return False
    return True


def player_attack(player, target_index):
    enemy = enemies[target_index]
    attack(player, enemy)
    if enemy.get_hp() == 0:
        remove_dead_target(enemies, target_index)


def cast_spell_opt(player):
    player.choose_magic()
    magicChoice = input("Choose magic:")
    if not validate_input(magicChoice, len(player.magic), -1):
        return False
    magicIndex = int(magicChoice) - 1
    if magicIndex == -1:
        return False
    spell = player.magic[magicIndex]
    if spell.cost > player.get_mp():
        print(bcolors.BOLD+"You don't have enough mp for casting ",
              spell.name+bcolors.ENDC)
        return False
    player_cast_spell(player, spell)
    return True


def player_cast_spell(player, spell):
    player.choose_target(enemies)
    choice = input("Choose target:")
    if not validate_input(choice, len(enemies), 0):
        return False
    target_index = int(choice) - 1
    cast_spell(player, target_index, enemies, spell)


def use_item(player):
    player.choose_item()
    choice = input("Choose item:")
    if not validate_input(choice, len(player.items), -1):
        return False
    item_index = int(choice) - 1
    if item_index == -1:
        return False
    itemObj = player.items[item_index]
    item = itemObj["item"]
    if itemObj["quantity"] == 0:
        print(bcolors.BOLD+"You don't have enough",
              item.name+"s"+bcolors.ENDC)
        return False
    if item.type == "potion":
        player.heal(item.prop)
        print(bcolors.OKGREEN + bcolors.BOLD+"\n"+item.name,
              "heals for", str(item.prop), "HP."+bcolors.ENDC)
    elif item.type == "elixer":
        if item.name == "Elixer":
            player.hp = player.maxhp
            player.mp = player.maxmp
        elif item.name == "Mega-Elixer":
            for p in players:
                p.hp = p.maxhp
                p.mp = p.maxmp
        print(bcolors.OKGREEN + bcolors.BOLD+"\n"+item.name,
              "fully restores HP/MP."+bcolors.ENDC)
    elif item.type == "attack":
        player.choose_target(enemies)
        target_choice = input("Choose target:")
        if not validate_input(target_choice, len(enemies), 0):
            return False
        target_index = int(target_choice) - 1
        target = enemies[target_index]
        target.take_dmg(item.prop)
        print(bcolors.BOLD+player.name+"'s", item.name, "deals",
              item.prop, "points of damage to", target.name+bcolors.ENDC)
        if target.get_hp() == 0:
            remove_dead_target(enemies, target_index)
    player.reduce_quantity(item_index)
    return True


def enemy_play(enemy):
    target_index = random.randrange(0, len(players))
    action_index = random.randrange(0, 2)
    pct = enemy.get_hp()/enemy.get_max_hp()
    magicIndex = random.randrange(0, len(enemy.magic))
    cost = enemy.magic[magicIndex].cost
    if enemy.get_mp() > 50 and pct < 0.4:
        enemy_cast_spell(enemy, 2)
    elif enemy.get_mp() > cost and action_index == 1:
        enemy_cast_spell(enemy, magicIndex)
    else:
        enemy_attack(target_index, enemy)


def enemy_attack(target_index, enemey):
    target = players[target_index]
    attack(enemey, target)
    if target.get_hp() == 0:
        remove_dead_target(players, target_index)


def enemy_cast_spell(enemy, magicIndex):
    target_index = random.randrange(0, len(players))
    spell = enemy.magic[magicIndex]
    cast_spell(enemy, target_index, players, spell)


def validate_input(input, max_option, min_option):
    if not (re.match('[0-9]', input) and int(input) <= max_option and int(input) > min_option):
        print("Invalid input")
        return False
    return True


def attack(attacker, target):
    dmg = attacker.generate_damage()
    target.take_dmg(dmg)
    print(bcolors.BOLD + attacker.name, "attacked", target.name, "inflicting", dmg,
          "points of damage." + bcolors.ENDC)


def cast_spell(attacker, target_index, team, spell):
    target = team[target_index]
    dmg = spell.generate_damage()
    cost = spell.cost
    attacker.reduce_mp(cost)
    if spell.type == "white":
        attacker.heal(dmg)
        print(bcolors.OKBLUE+bcolors.BOLD + "\n"+spell.name +
              " heals for", str(dmg), "HP, with a cost of", cost, "mp's. "+bcolors.ENDC)
    elif spell.type == "black":
        target.take_dmg(dmg)
        print(bcolors.OKBLUE+bcolors.BOLD + attacker.name+"'s " + spell.name, "deals", dmg,
              "points of damage to", target.name, "with a cost of", cost, "mp's. " + bcolors.ENDC)
        if target.get_hp() == 0:
            remove_dead_target(team, target_index)


def remove_dead_target(team, target_index):
    target = team[target_index]
    del team[target_index]
    print(bcolors.FAIL+target.name+" has died."+bcolors.ENDC)


def print_stats():
    print("\n===============================================================================\n")
    print(bcolors.BOLD+"NAME:                      HP:                                    MP:"+bcolors.ENDC)
    for player in players:
        print_player_stats(player.name, player.get_hp(), player.get_max_hp(),
                           player.get_mp(), player.get_max_mp(), "")

    print("\n")

    for enemy in enemies:
        print_enemy_stats(enemy.name, enemy.get_hp(), enemy.get_max_hp())

    print("\n")


def print_player_stats(player_name, player_hp, player_max_hp, player_mp, player_max_mp, color):
    hp_string = str(player_hp)+"/"+str(player_max_hp)+bcolors.ENDC
    spaces_length = 25 - len(player_name)-1 - len(hp_string)
    hp_spaces = get_spaces(spaces_length)
    column1 = color+bcolors.BOLD+player_name + \
        ":" + hp_spaces+bcolors.OKGREEN+hp_string
    hp_bar = get_bars(round(player_hp*25/player_max_hp), 25)
    mp_string = bcolors.OKBLUE+bcolors.BOLD + \
        str(player_mp)+"/"+str(player_max_mp)
    mp_length = 10 - len(mp_string)
    mp_spaces = get_spaces(mp_length)
    mp_bar = get_bars(
        round(player_mp*10/player_max_mp), 10)
    column2 = bcolors.OKGREEN+"     |"+hp_bar + "|     "+bcolors.ENDC
    column3 = bcolors.OKBLUE+mp_spaces+mp_string+"  |"+mp_bar+"|"+bcolors.ENDC
    print("                       "+bcolors.OKGREEN+"    _________________________  " +
          bcolors.ENDC+"            "+bcolors.OKBLUE+"__________"+bcolors.ENDC)
    print(column1+column2+column3)


def print_enemy_stats(player_name, player_hp, player_max_hp):
    hp_string = str(player_hp)+"/"+str(player_max_hp)
    spaces_length = 25 - len(player_name)-1 - len(hp_string)
    hp_spaces = get_spaces(spaces_length)
    column1 = bcolors.FAIL+bcolors.BOLD+player_name + \
        ":" + hp_spaces+hp_string
    hp_bar = get_bars(round(player_hp*50/player_max_hp), 50)

    column2 = "   |"+hp_bar + "|"
    print(bcolors.FAIL+bcolors.BOLD +
          "                             __________________________________________________              " + bcolors.ENDC)
    print(column1+column2)


def get_bars(stat, max_stat):
    bar = ""
    i = 0
    while i < max_stat:
        if i < stat:
            bar += "█"
        else:
            bar += " "
        i += 1
    return bar


def get_spaces(spaces_length):
    i = 0
    spaces = ""
    while i < spaces_length:
        spaces += " "
        i += 1
    return spaces


def print_end_game_message():
    if not is_team_alive(enemies):
        print(bcolors.OKGREEN + bcolors.BOLD +
              "The enemy is dead. You win!" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + bcolors.BOLD +
              "Your team died. The enemy won!" + bcolors.ENDC)


def is_team_alive(team):
    one_alive = False
    for player in team:
        if player.get_hp() > 0:
            one_alive = True
            break
    return one_alive


print(bcolors.FAIL + bcolors.BOLD + "AN ENEMY ATTACKS!" + bcolors.ENDC)


while running:

    print_stats()
    for player in players:
        if is_team_alive(enemies):
            valid_action = False
            while not valid_action:
                valid_action = player_play(player)
    for enemy in enemies:
        if is_team_alive(players):
            enemy_play(enemy)
    running = is_team_alive(players) and is_team_alive(enemies)
    if not running:
        print_end_game_message()
