import requests
from bs4 import BeautifulSoup
import re
import os
import time

# --- Configuration ---
# Define the Pokémon lists for Gen 4 and Gen 5
POKEMON_NAMES_GEN4 = [
    "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", # Gen 4 Start (#387)
    "Piplup", "Prinplup", "Empoleon", "Starly", "Staravia", "Staraptor",
    "Bidoof", "Bibarel", "Kricketot", "Kricketune", "Shinx", "Luxio", "Luxray",
    "Budew", "Roserade", "Cranidos", "Rampardos", "Shieldon", "Bastiodon",
    "Burmy", "Wormadam", "Mothim", "Combee", "Vespiquen", "Pachirisu", "Buizel",
    "Floatzel", "Cherubi", "Cherrim", "Shellos", "Gastrodon", "Ambipom",
    "Drifloon", "Drifblim", "Buneary", "Lopunny", "Mismagius", "Honchkrow",
    "Glameow", "Purugly", "Chingling", "Stunky", "Skuntank", "Bronzor",
    "Bronzong", "Bonsly", "Mime Jr.", "Happiny", "Chatot", "Spiritomb", "Gible",
    "Gabite", "Garchomp", "Munchlax", "Riolu", "Lucario", "Hippopotas",
    "Hippowdon", "Skorupi", "Drapion", "Croagunk", "Toxicroak", "Carnivine",
    "Finneon", "Lumineon", "Mantyke", "Snover", "Abomasnow", "Weavile",
    "Magnezone", "Lickilicky", "Rhyperior", "Tangrowth", "Electivire",
    "Magmortar", "Togekiss", "Yanmega", "Leafeon", "Glaceon", "Gliscor",
    "Mamoswine", "Porygon-Z", "Gallade", "Probopass", "Dusknoir", "Froslass",
    "Rotom", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran",
    "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai",
    "Shaymin", "Arceus" # Gen 4 End (#493)
]

POKEMON_NAMES_GEN5 = [
    "Victini", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", # Gen 5 Start (#494)
    "Oshawott", "Dewott", "Samurott", "Patrat", "Watchog", "Lillipup", "Herdier",
    "Stoutland", "Purrloin", "Liepard", "Pansage", "Simisage", "Pansear",
    "Simisear", "Panpour", "Simipour", "Munna", "Musharna", "Pidove",
    "Tranquill", "Unfezant", "Blitzle", "Zebstrika", "Roggenrola", "Boldore",
    "Gigalith", "Woobat", "Swoobat", "Drilbur", "Excadrill", "Audino", "Timburr",
    "Gurdurr", "Conkeldurr", "Tympole", "Palpitoad", "Seismitoad", "Throh",
    "Sawk", "Sewaddle", "Swadloon", "Leavanny", "Venipede", "Whirlipede",
    "Scolipede", "Cottonee", "Whimsicott", "Petilil", "Lilligant", "Basculin",
    "Sandile", "Krokorok", "Krookodile", "Darumaka", "Darmanitan", "Maractus",
    "Dwebble", "Crustle", "Scraggy", "Scrafty", "Sigilyph", "Yamask",
    "Cofagrigus", "Tirtouga", "Carracosta", "Archen", "Archeops", "Trubbish",
    "Garbodor", "Zorua", "Zoroark", "Minccino", "Cinccino", "Gothita",
    "Gothorita", "Gothitelle", "Solosis", "Duosion", "Reuniclus", "Ducklett",
    "Swanna", "Vanillite", "Vanillish", "Vanilluxe", "Deerling", "Sawsbuck",
    "Emolga", "Karrablast", "Escavalier", "Foongus", "Amoonguss", "Frillish",
    "Jellicent", "Alomomola", "Joltik", "Galvantula", "Ferroseed", "Ferrothorn",
    "Klink", "Klang", "Klinklang", "Tynamo", "Eelektrik", "Eelektross", "Elgyem",
    "Beheeyem", "Litwick", "Lampent", "Chandelure", "Axew", "Fraxure", "Haxorus",
    "Cubchoo", "Beartic", "Cryogonal", "Shelmet", "Accelgor", "Stunfisk",
    "Mienfoo", "Mienshao", "Druddigon", "Golett", "Golurk", "Pawniard",
    "Bisharp", "Bouffalant", "Rufflet", "Braviary", "Vullaby", "Mandibuzz",
    "Heatmor", "Durant", "Deino", "Zweilous", "Hydreigon", "Larvesta",
    "Volcarona", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus",
    "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta",
    "Genesect" # Gen 5 End (#649)
]

ALL_POKEMON_LISTS = {
    4: POKEMON_NAMES_GEN4,
    5: POKEMON_NAMES_GEN5
}
TARGET_GENERATIONS = [4, 5]

FILE_PATH = "level_up_learnsets.h"
INDENT = "    " # Use 4 standard spaces
REQUEST_DELAY = 0.5

# --- Define the Allowed Move Set Directly ---
ALLOWED_MOVES = {
    "MOVE_POUND", "MOVE_KARATE_CHOP", "MOVE_DOUBLE_SLAP", "MOVE_COMET_PUNCH",
    "MOVE_MEGA_PUNCH", "MOVE_PAY_DAY", "MOVE_FIRE_PUNCH", "MOVE_ICE_PUNCH",
    "MOVE_THUNDER_PUNCH", "MOVE_SCRATCH", "MOVE_VISE_GRIP", "MOVE_GUILLOTINE",
    "MOVE_RAZOR_WIND", "MOVE_SWORDS_DANCE", "MOVE_CUT", "MOVE_GUST",
    "MOVE_WING_ATTACK", "MOVE_WHIRLWIND", "MOVE_FLY", "MOVE_BIND", "MOVE_SLAM",
    "MOVE_VINE_WHIP", "MOVE_STOMP", "MOVE_DOUBLE_KICK", "MOVE_MEGA_KICK",
    "MOVE_JUMP_KICK", "MOVE_ROLLING_KICK", "MOVE_SAND_ATTACK", "MOVE_HEADBUTT",
    "MOVE_HORN_ATTACK", "MOVE_FURY_ATTACK", "MOVE_HORN_DRILL", "MOVE_TACKLE",
    "MOVE_BODY_SLAM", "MOVE_WRAP", "MOVE_TAKE_DOWN", "MOVE_THRASH",
    "MOVE_DOUBLE_EDGE", "MOVE_TAIL_WHIP", "MOVE_POISON_STING", "MOVE_TWINEEDLE",
    "MOVE_PIN_MISSILE", "MOVE_LEER", "MOVE_BITE", "MOVE_GROWL", "MOVE_ROAR",
    "MOVE_SING", "MOVE_SUPERSONIC", "MOVE_SONIC_BOOM", "MOVE_DISABLE", "MOVE_ACID",
    "MOVE_EMBER", "MOVE_FLAMETHROWER", "MOVE_MIST", "MOVE_WATER_GUN",
    "MOVE_HYDRO_PUMP", "MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_BLIZZARD",
    "MOVE_PSYBEAM", "MOVE_BUBBLE_BEAM", "MOVE_AURORA_BEAM", "MOVE_HYPER_BEAM",
    "MOVE_PECK", "MOVE_DRILL_PECK", "MOVE_SUBMISSION", "MOVE_LOW_KICK",
    "MOVE_COUNTER", "MOVE_SEISMIC_TOSS", "MOVE_STRENGTH", "MOVE_ABSORB",
    "MOVE_MEGA_DRAIN", "MOVE_LEECH_SEED", "MOVE_GROWTH", "MOVE_RAZOR_LEAF",
    "MOVE_SOLAR_BEAM", "MOVE_POISON_POWDER", "MOVE_STUN_SPORE", "MOVE_SLEEP_POWDER",
    "MOVE_PETAL_DANCE", "MOVE_STRING_SHOT", "MOVE_DRAGON_RAGE", "MOVE_FIRE_SPIN",
    "MOVE_THUNDER_SHOCK", "MOVE_THUNDERBOLT", "MOVE_THUNDER_WAVE", "MOVE_THUNDER",
    "MOVE_ROCK_THROW", "MOVE_EARTHQUAKE", "MOVE_FISSURE", "MOVE_DIG", "MOVE_TOXIC",
    "MOVE_CONFUSION", "MOVE_PSYCHIC", "MOVE_HYPNOSIS", "MOVE_MEDITATE",
    "MOVE_AGILITY", "MOVE_QUICK_ATTACK", "MOVE_RAGE", "MOVE_TELEPORT",
    "MOVE_NIGHT_SHADE", "MOVE_MIMIC", "MOVE_SCREECH", "MOVE_DOUBLE_TEAM",
    "MOVE_RECOVER", "MOVE_HARDEN", "MOVE_MINIMIZE", "MOVE_SMOKESCREEN",
    "MOVE_CONFUSE_RAY", "MOVE_WITHDRAW", "MOVE_DEFENSE_CURL", "MOVE_BARRIER",
    "MOVE_LIGHT_SCREEN", "MOVE_HAZE", "MOVE_REFLECT", "MOVE_FOCUS_ENERGY",
    "MOVE_BIDE", "MOVE_METRONOME", "MOVE_MIRROR_MOVE", "MOVE_SELF_DESTRUCT",
    "MOVE_EGG_BOMB", "MOVE_LICK", "MOVE_SMOG", "MOVE_SLUDGE", "MOVE_BONE_CLUB",
    "MOVE_FIRE_BLAST", "MOVE_WATERFALL", "MOVE_CLAMP", "MOVE_SWIFT",
    "MOVE_SKULL_BASH", "MOVE_SPIKE_CANNON", "MOVE_CONSTRICT", "MOVE_AMNESIA",
    "MOVE_KINESIS", "MOVE_SOFT_BOILED", "MOVE_HIGH_JUMP_KICK", "MOVE_GLARE",
    "MOVE_DREAM_EATER", "MOVE_POISON_GAS", "MOVE_BARRAGE", "MOVE_LEECH_LIFE",
    "MOVE_LOVELY_KISS", "MOVE_SKY_ATTACK", "MOVE_TRANSFORM", "MOVE_BUBBLE",
    "MOVE_DIZZY_PUNCH", "MOVE_SPORE", "MOVE_FLASH", "MOVE_PSYWAVE", "MOVE_SPLASH",
    "MOVE_ACID_ARMOR", "MOVE_CRABHAMMER", "MOVE_EXPLOSION", "MOVE_FURY_SWIPES",
    "MOVE_BONEMERANG", "MOVE_REST", "MOVE_ROCK_SLIDE", "MOVE_HYPER_FANG",
    "MOVE_SHARPEN", "MOVE_CONVERSION", "MOVE_TRI_ATTACK", "MOVE_SUPER_FANG",
    "MOVE_SLASH", "MOVE_SUBSTITUTE", "MOVE_STRUGGLE", "MOVE_SKETCH",
    "MOVE_TRIPLE_KICK", "MOVE_THIEF", "MOVE_SPIDER_WEB", "MOVE_MIND_READER",
    "MOVE_NIGHTMARE", "MOVE_FLAME_WHEEL", "MOVE_SNORE", "MOVE_CURSE", "MOVE_FLAIL",
    "MOVE_CONVERSION_2", "MOVE_AEROBLAST", "MOVE_COTTON_SPORE", "MOVE_REVERSAL",
    "MOVE_SPITE", "MOVE_POWDER_SNOW", "MOVE_PROTECT", "MOVE_MACH_PUNCH",
    "MOVE_SCARY_FACE", "MOVE_FEINT_ATTACK", "MOVE_SWEET_KISS", "MOVE_BELLY_DRUM",
    "MOVE_SLUDGE_BOMB", "MOVE_MUD_SLAP", "MOVE_OCTAZOOKA", "MOVE_SPIKES",
    "MOVE_ZAP_CANNON", "MOVE_FORESIGHT", "MOVE_DESTINY_BOND", "MOVE_PERISH_SONG",
    "MOVE_ICY_WIND", "MOVE_DETECT", "MOVE_BONE_RUSH", "MOVE_LOCK_ON", "MOVE_OUTRAGE",
    "MOVE_SANDSTORM", "MOVE_GIGA_DRAIN", "MOVE_ENDURE", "MOVE_CHARM",
    "MOVE_ROLLOUT", "MOVE_FALSE_SWIPE", "MOVE_SWAGGER", "MOVE_MILK_DRINK",
    "MOVE_SPARK", "MOVE_FURY_CUTTER", "MOVE_STEEL_WING", "MOVE_MEAN_LOOK",
    "MOVE_ATTRACT", "MOVE_SLEEP_TALK", "MOVE_HEAL_BELL", "MOVE_RETURN",
    "MOVE_PRESENT", "MOVE_FRUSTRATION", "MOVE_SAFEGUARD", "MOVE_PAIN_SPLIT",
    "MOVE_SACRED_FIRE", "MOVE_MAGNITUDE", "MOVE_DYNAMIC_PUNCH", "MOVE_MEGAHORN",
    "MOVE_DRAGON_BREATH", "MOVE_BATON_PASS", "MOVE_ENCORE", "MOVE_PURSUIT",
    "MOVE_RAPID_SPIN", "MOVE_SWEET_SCENT", "MOVE_IRON_TAIL", "MOVE_METAL_CLAW",
    "MOVE_VITAL_THROW", "MOVE_MORNING_SUN", "MOVE_SYNTHESIS", "MOVE_MOONLIGHT",
    "MOVE_HIDDEN_POWER", "MOVE_CROSS_CHOP", "MOVE_TWISTER", "MOVE_RAIN_DANCE",
    "MOVE_SUNNY_DAY", "MOVE_CRUNCH", "MOVE_MIRROR_COAT", "MOVE_PSYCH_UP",
    "MOVE_EXTREME_SPEED", "MOVE_ANCIENT_POWER", "MOVE_SHADOW_BALL",
    "MOVE_FUTURE_SIGHT", "MOVE_ROCK_SMASH", "MOVE_WHIRLPOOL", "MOVE_BEAT_UP",
    "MOVE_FAKE_OUT", "MOVE_UPROAR", "MOVE_STOCKPILE", "MOVE_SPIT_UP",
    "MOVE_SWALLOW", "MOVE_HEAT_WAVE", "MOVE_HAIL", "MOVE_TORMENT", "MOVE_FLATTER",
    "MOVE_WILL_O_WISP", "MOVE_MEMENTO", "MOVE_FACADE", "MOVE_FOCUS_PUNCH",
    "MOVE_SMELLING_SALTS", "MOVE_FOLLOW_ME", "MOVE_NATURE_POWER", "MOVE_CHARGE",
    "MOVE_TAUNT", "MOVE_HELPING_HAND", "MOVE_TRICK", "MOVE_ROLE_PLAY", "MOVE_WISH",
    "MOVE_ASSIST", "MOVE_INGRAIN", "MOVE_SUPERPOWER", "MOVE_MAGIC_COAT",
    "MOVE_RECYCLE", "MOVE_REVENGE", "MOVE_BRICK_BREAK", "MOVE_YAWN",
    "MOVE_KNOCK_OFF", "MOVE_ENDEAVOR", "MOVE_ERUPTION", "MOVE_SKILL_SWAP",
    "MOVE_IMPRISON", "MOVE_REFRESH", "MOVE_GRUDGE", "MOVE_SNATCH",
    "MOVE_SECRET_POWER", "MOVE_DIVE", "MOVE_ARM_THRUST", "MOVE_CAMOUFLAGE",
    "MOVE_TAIL_GLOW", "MOVE_LUSTER_PURGE", "MOVE_MIST_BALL", "MOVE_FEATHER_DANCE",
    "MOVE_TEETER_DANCE", "MOVE_BLAZE_KICK", "MOVE_MUD_SPORT", "MOVE_ICE_BALL",
    "MOVE_NEEDLE_ARM", "MOVE_SLACK_OFF", "MOVE_HYPER_VOICE", "MOVE_POISON_FANG",
    "MOVE_CRUSH_CLAW", "MOVE_BLAST_BURN", "MOVE_HYDRO_CANNON", "MOVE_METEOR_MASH",
    "MOVE_ASTONISH", "MOVE_WEATHER_BALL", "MOVE_AROMATHERAPY", "MOVE_FAKE_TEARS",
    "MOVE_AIR_CUTTER", "MOVE_OVERHEAT", "MOVE_ODOR_SLEUTH", "MOVE_ROCK_TOMB",
    "MOVE_SILVER_WIND", "MOVE_METAL_SOUND", "MOVE_GRASS_WHISTLE", "MOVE_TICKLE",
    "MOVE_COSMIC_POWER", "MOVE_WATER_SPOUT", "MOVE_SIGNAL_BEAM",
    "MOVE_SHADOW_PUNCH", "MOVE_EXTRASENSORY", "MOVE_SKY_UPPERCUT", "MOVE_SAND_TOMB",
    "MOVE_SHEER_COLD", "MOVE_MUDDY_WATER", "MOVE_BULLET_SEED", "MOVE_AERIAL_ACE",
    "MOVE_ICICLE_SPEAR", "MOVE_IRON_DEFENSE", "MOVE_BLOCK", "MOVE_HOWL",
    "MOVE_DRAGON_CLAW", "MOVE_FRENZY_PLANT", "MOVE_BULK_UP", "MOVE_BOUNCE",
    "MOVE_MUD_SHOT", "MOVE_POISON_TAIL", "MOVE_COVET", "MOVE_VOLT_TACKLE",
    "MOVE_MAGICAL_LEAF", "MOVE_WATER_SPORT", "MOVE_CALM_MIND", "MOVE_LEAF_BLADE",
    "MOVE_DRAGON_DANCE", "MOVE_ROCK_BLAST", "MOVE_SHOCK_WAVE", "MOVE_WATER_PULSE",
    "MOVE_DOOM_DESIRE", "MOVE_PSYCHO_BOOST"
}
print(f"Loaded {len(ALLOWED_MOVES)} allowed moves from Gen 1-3 move bank.")

# --- Move Name Correction Map ---
MOVE_NAME_CORRECTIONS = {
    "MOVE_ANCIENTPOWER": "MOVE_ANCIENT_POWER",
    "MOVE_BUBBLEBEAM": "MOVE_BUBBLE_BEAM",
    "MOVE_DOUBLESLAP": "MOVE_DOUBLE_SLAP",
    "MOVE_DRAGONBREATH": "MOVE_DRAGON_BREATH",
    "MOVE_DYNAMICPUNCH": "MOVE_DYNAMIC_PUNCH",
    "MOVE_EXTREMESPEED": "MOVE_EXTREME_SPEED",
    "MOVE_FEATHERDANCE": "MOVE_FEATHER_DANCE",
    "MOVE_GRASSWHISTLE": "MOVE_GRASS_WHISTLE",
    "MOVE_POISONPOWDER": "MOVE_POISON_POWDER",
    "MOVE_SELFDESTRUCT": "MOVE_SELF_DESTRUCT",
    "MOVE_SOLARBEAM": "MOVE_SOLAR_BEAM",
    "MOVE_SONICBOOM": "MOVE_SONIC_BOOM",
    "MOVE_THUNDERPUNCH": "MOVE_THUNDER_PUNCH",
    "MOVE_THUNDERSHOCK": "MOVE_THUNDER_SHOCK",
    "MOVE_SOFTBOILED": "MOVE_SOFT_BOILED",
}
# --- End Configuration ---


# --- Functions ---
def format_c_move_name(move_name):
    """
    Converts a fetched move name to the correct C constant format,
    applying known corrections for spelling, abbreviations, and formatting.
    """
    processed_name = move_name.upper()
    processed_name = re.sub(r'[\s\-]', '_', processed_name)
    processed_name = re.sub(r'[^\w_]', '', processed_name)

    if processed_name == "HI_JUMP_KICK": processed_name = "HIGH_JUMP_KICK"
    if processed_name == "VICEGRIP": processed_name = "VISE_GRIP"
    if processed_name == "SMELLINGSALT": processed_name = "SMELLING_SALTS"
    if processed_name == "FAINT_ATTACK": processed_name = "FEINT_ATTACK" # Standardize

    c_name = f"MOVE_{processed_name}"
    corrected_name = MOVE_NAME_CORRECTIONS.get(c_name, c_name)
    return corrected_name

def fetch_pokemon_moves(pokemon_name, generation):
    """Fetches level-up moves for a given Pokémon and Generation from PokemonDB."""
    pokemon_url_name = pokemon_name.lower()
    if pokemon_name == "Mime Jr.": pokemon_url_name = "mime-jr"
    if pokemon_name == "Porygon-Z": pokemon_url_name = "porygon-z"

    url = f"https://pokemondb.net/pokedex/{pokemon_url_name}/moves/{generation}"
    print(f"Fetching Gen {generation} moves for {pokemon_name} (URL: '{url}')... ", end='')
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")
        return None
    print("Parsing... ", end='')
    soup = BeautifulSoup(response.content, 'html.parser')
    level_up_heading = soup.find('h2', string=re.compile(r'Moves learnt by level up', re.IGNORECASE))
    if not level_up_heading:
        print(f"Failed: Could not find 'Moves learnt by level up' heading.")
        data_table = soup.find('table', class_='data-table')
        if not data_table: print("Fallback failed: No data table found."); return None
        print("Warning: Using fallback table search... ", end='')
    else:
        data_table = level_up_heading.find_next_sibling('table', class_='data-table')
        if not data_table: print(f"Failed: Found heading but no table after it."); return None
    tbody = data_table.find('tbody')
    if not tbody:
        print("Failed: Could not find table body (tbody).")
        if data_table.find('thead'): return None
        else: print("Note: Table appears empty."); return []
    moves = []
    rows = tbody.find_all('tr')
    if not rows: print("Note: Table body is empty."); return []
    for row in rows:
        level_cell = row.find('td', class_='cell-num')
        move_cell = row.find('td', class_='cell-name')
        if level_cell and move_cell:
            level_text = level_cell.get_text(strip=True)
            move_name_tag = move_cell.find('a', class_='ent-name')
            if move_name_tag:
                move_name = move_name_tag.get_text(strip=True)
                try: level = int(level_text)
                except ValueError: level = 1 if level_text=='1' or level_text.lower()=='evo.' or level_text=='—' else -1
                if level != -1: moves.append({'level': level, 'move': move_name})
    if not moves and len(rows) > 0: print("Warning: Found table rows but couldn't extract valid moves.")
    elif not moves: print("Note: No moves extracted.")
    if moves: print(f"OK ({len(moves)} moves).")
    return moves

def update_learnset_in_file(file_path, pokemon_name, moves_data):
    """Updates the learnset for a specific Pokémon in the .h file."""
    c_pokemon_name = pokemon_name.capitalize()
    if pokemon_name == "Mime Jr.": c_pokemon_name = "MimeJr"
    if pokemon_name == "Porygon-Z": c_pokemon_name = "PorygonZ"

    start_marker = f"static const struct LevelUpMove s{c_pokemon_name}LevelUpLearnset[] = {{"
    end_marker_text = "LEVEL_UP_END"
    end_marker_line_exact = f"{INDENT}{end_marker_text}"
    closing_brace_text = "};"

    if not os.path.exists(file_path):
         print(f"      Error: File not found at {file_path}. Cannot update.")
         return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
    except Exception as e: print(f"      Error reading file {file_path}: {e}"); return False

    start_index, end_index, brace_index = -1, -1, -1
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if start_index == -1 and start_marker.strip() in stripped_line:
             if stripped_line.startswith(start_marker.strip()): start_index = i
        elif start_index != -1 and end_index == -1:
            if stripped_line == end_marker_text and line.startswith(INDENT): end_index = i
        elif end_index != -1 and stripped_line == closing_brace_text: brace_index = i; break

    if start_index == -1: print(f"      Update Failed: Start marker for '{c_pokemon_name}' not found."); print(f"      Searched for line starting with: '{start_marker.strip()}'"); return False
    if end_index == -1: print(f"      Update Failed: Correctly indented '{end_marker_text}' marker for '{c_pokemon_name}' not found after line {start_index + 1}."); return False
    if brace_index == -1: print(f"      Update Failed: Closing brace '{closing_brace_text}' for '{c_pokemon_name}' not found after line {end_index + 1}."); return False

    new_move_lines = []
    processed_c_names = set()
    moves_data.sort(key=lambda x: x['level'])

    for move_info in moves_data:
        level = move_info['level']
        c_move_name = format_c_move_name(move_info['move'])
        # Only add unique moves per Pokemon
        if c_move_name not in processed_c_names:
            if c_move_name in ALLOWED_MOVES:
                 new_move_lines.append(f"{INDENT}LEVEL_UP_MOVE({level:>2}, {c_move_name}),\n")
                 processed_c_names.add(c_move_name)
            else:
                print(f"      INTERNAL WARNING: Move '{move_info['move']}' ({c_move_name}) was processed but is not in ALLOWED_MOVES.")

    new_lines = lines[:start_index + 1] + new_move_lines + [f"{end_marker_line_exact}\n", lines[brace_index]] + lines[brace_index + 1:]

    try:
        if lines == new_lines:
            print(f"      Learnset for {c_pokemon_name} already up-to-date (with mapped Gen 1-3 moves).")
        else:
            with open(file_path, 'w', encoding='utf-8') as f: f.writelines(new_lines)
            print(f"      Successfully updated {c_pokemon_name}'s learnset in {file_path} (with mapped Gen 1-3 moves).")
        return True
    except Exception as e: print(f"      Error writing updated file {file_path}: {e}"); return False
# --- End of Functions ---


# --- Main Execution ---
if __name__ == "__main__":
    print(f"--- Starting Pokémon Learnset Update (Generations {TARGET_GENERATIONS}) ---")
    print(f"--- Applying Gen 1-3 Move Filter ({len(ALLOWED_MOVES)} moves allowed) using Mapping ---")
    print(f"Target file: {FILE_PATH}")
    print(f"Data source: PokemonDB")
    print(f"Delay between requests: {REQUEST_DELAY} seconds")
    print("\nIMPORTANT: Make sure you have a backup of your .h file!")

    fetch_failures = []
    update_failures = []
    processed_count = 0
    total_pokemon_to_process = sum(len(ALL_POKEMON_LISTS.get(gen, [])) for gen in TARGET_GENERATIONS)
    corrections_applied_log = [] # Log when corrections are applied

    for gen in TARGET_GENERATIONS:
        print(f"\n--- Processing Generation {gen} ---")
        pokemon_list = ALL_POKEMON_LISTS.get(gen, [])
        if not pokemon_list:
            print(f"Warning: No Pokémon list found for Generation {gen}.")
            continue

        for pokemon_name in pokemon_list:
            processed_count += 1
            print(f"\n[{processed_count}/{total_pokemon_to_process} | Gen {gen}] Processing: {pokemon_name}")

            fetched_moves = fetch_pokemon_moves(pokemon_name, gen)

            if fetched_moves is None:
                fetch_failures.append((pokemon_name, gen))
                print(f"      -> Added {pokemon_name} (Gen {gen}) to fetch failure list.")
            else:
                if not fetched_moves:
                     print("      Note: No moves were fetched.")
                     filtered_moves = []
                     total_fetched = 0
                else:
                    total_fetched = len(fetched_moves)

                    # Filter moves using the enhanced formatter and check against allowed set
                    filtered_moves = []
                    disallowed_moves_details = []

                    for move_info in fetched_moves:
                        # Get the potentially corrected C name
                        c_move_name = format_c_move_name(move_info['move'])
                        # Check if this final C name is in the allowed set
                        if c_move_name in ALLOWED_MOVES:
                            filtered_moves.append(move_info) # Add original info

                            # --- FIX: Calculate raw_formatted outside f-string ---
                            temp_sub1 = re.sub(r'[\s\-]', '_', move_info['move'].upper())
                            basic_formatted_name_part = re.sub(r'[^\w_]', '', temp_sub1)
                            raw_formatted = f"MOVE_{basic_formatted_name_part}"
                            # --- End FIX ---

                            # Log if a correction was applied by the map or specific logic
                            if c_move_name != raw_formatted:
                                corrections_applied_log.append(f"{pokemon_name}({gen}): Fetched '{move_info['move']}' -> Corrected to {c_move_name} (Raw basic format: {raw_formatted})")
                        else:
                            disallowed_moves_details.append(f"{move_info['move']} ({c_move_name})")

                    print(f"      Filtered Moves: Kept {len(filtered_moves)} out of {total_fetched} fetched moves (based on Gen 1-3 bank + mapping).")
                    if disallowed_moves_details:
                        print(f"      Disallowed moves (Gen 4/5 or not in bank/map): {', '.join(disallowed_moves_details)}")


                # Attempt to update the file with the filtered moves
                update_successful = update_learnset_in_file(FILE_PATH, pokemon_name, filtered_moves)
                if not update_successful:
                     update_failures.append((pokemon_name, gen))
                     print(f"      -> Added {pokemon_name} (Gen {gen}) to update failure list.")

            time.sleep(REQUEST_DELAY)

    # --- Final Summary ---
    print("\n--- Update Process Finished ---")
    print(f"Total Pokémon processed: {processed_count}")

    if fetch_failures:
        print(f"\n--- Fetch/Parse Failures ({len(fetch_failures)}) ---")
        print("Check URL name/format or page structure for these Pokémon/Generations:")
        print(", ".join([f"{name} (Gen {g})" for name, g in fetch_failures]))
    else:
        print("\nNo fetch/parse failures encountered.")

    if update_failures:
         print(f"\n--- File Update Failures ({len(update_failures)}) ---")
         print("Check C variable name/format in file or write permissions for:")
         print(", ".join([f"{name} (Gen {g})" for name, g in update_failures]))
    else:
         print("\nNo file update failures encountered.")

    # Optional: Print summary of corrections applied
    if corrections_applied_log:
         print(f"\n--- Name Corrections Applied Summary ({len(corrections_applied_log)} instances) ---")
         # Use set for unique corrections if desired, but log shows all instances
         unique_corrections = sorted(list(set(corrections_applied_log)))
         print("\n".join(unique_corrections)) # Print unique corrections applied
         # print("\n".join(corrections_applied_log)) # Print all instances if preferred