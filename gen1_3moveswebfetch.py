import requests
from bs4 import BeautifulSoup
import re
import os
import time # Import time for delay

# --- Configuration ---
# List of Pokémon names from Generation 1, 2, and 3 (#1 to #386)
POKEMON_NAMES_GEN1_3 = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata",
    "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu",
    "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂",
    "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
    "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume",
    "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth",
    "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine",
    "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke",
    "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
    "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter",
    "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb",
    "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee",
    "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon",
    "Chansey", "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking",
    "Staryu", "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar",
    "Pinsir", "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee",
    "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto",
    "Kabutops", "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres",
    "Dratini", "Dragonair", "Dragonite", "Mewtwo", "Mew",
    "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", # Gen 2 Start
    "Totodile", "Croconaw", "Feraligatr", "Sentret", "Furret", "Hoothoot",
    "Noctowl", "Ledyba", "Ledian", "Spinarak", "Ariados", "Crobat", "Chinchou",
    "Lanturn", "Pichu", "Cleffa", "Igglybuff", "Togepi", "Togetic", "Natu",
    "Xatu", "Mareep", "Flaaffy", "Ampharos", "Bellossom", "Marill", "Azumarill",
    "Sudowoodo", "Politoed", "Hoppip", "Skiploom", "Jumpluff", "Aipom", "Sunkern",
    "Sunflora", "Yanma", "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow",
    "Slowking", "Misdreavus", "Unown", "Wobbuffet", "Girafarig", "Pineco",
    "Forretress", "Dunsparce", "Gligar", "Steelix", "Snubbull", "Granbull",
    "Qwilfish", "Scizor", "Shuckle", "Heracross", "Sneasel", "Teddiursa",
    "Ursaring", "Slugma", "Magcargo", "Swinub", "Piloswine", "Corsola",
    "Remoraid", "Octillery", "Delibird", "Mantine", "Skarmory", "Houndour",
    "Houndoom", "Kingdra", "Phanpy", "Donphan", "Porygon2", "Stantler", "Smeargle",
    "Tyrogue", "Hitmontop", "Smoochum", "Elekid", "Magby", "Miltank", "Blissey",
    "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar", "Tyranitar", "Lugia",
    "Ho-Oh", "Celebi",
    "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", # Gen 3 Start
    "Mudkip", "Marshtomp", "Swampert", "Poochyena", "Mightyena", "Zigzagoon",
    "Linoone", "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox", "Lotad",
    "Lombre", "Ludicolo", "Seedot", "Nuzleaf", "Shiftry", "Taillow", "Swellow",
    "Wingull", "Pelipper", "Ralts", "Kirlia", "Gardevoir", "Surskit", "Masquerain",
    "Shroomish", "Breloom", "Slakoth", "Vigoroth", "Slaking", "Nincada", "Ninjask",
    "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita", "Hariyama", "Azurill",
    "Nosepass", "Skitty", "Delcatty", "Sableye", "Mawile", "Aron", "Lairon",
    "Aggron", "Meditite", "Medicham", "Electrike", "Manectric", "Plusle", "Minun",
    "Volbeat", "Illumise", "Roselia", "Gulpin", "Swalot", "Carvanha", "Sharpedo",
    "Wailmer", "Wailord", "Numel", "Camerupt", "Torkoal", "Spoink", "Grumpig",
    "Spinda", "Trapinch", "Vibrava", "Flygon", "Cacnea", "Cacturne", "Swablu",
    "Altaria", "Zangoose", "Seviper", "Lunatone", "Solrock", "Barboach",
    "Whiscash", "Corphish", "Crawdaunt", "Baltoy", "Claydol", "Lileep", "Cradily",
    "Anorith", "Armaldo", "Feebas", "Milotic", "Castform", "Kecleon", "Shuppet",
    "Banette", "Duskull", "Dusclops", "Tropius", "Chimecho", "Absol", "Wynaut",
    "Snorunt", "Glalie", "Spheal", "Sealeo", "Walrein", "Clamperl", "Huntail",
    "Gorebyss", "Relicanth", "Luvdisc", "Bagon", "Shelgon", "Salamence", "Beldum",
    "Metang", "Metagross", "Regirock", "Regice", "Registeel", "Latias", "Latios",
    "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys" # Gen 3 End (#386)
]

FILE_PATH = "level_up_learnsets.h" # Path to your header file
URL_TEMPLATE = "https://pokemondb.net/pokedex/{pokemon}/moves/3" # Gen 3 moves
# Using the exact indentation string from your original code
INDENT = "    " # NOTE: This might contain non-breaking spaces depending on how you copied it. A standard indent is usually 4 regular spaces.
REQUEST_DELAY = 0.5 # Seconds delay between requests
# --- End Configuration ---

# --- Functions exactly as provided previously ---
def format_c_move_name(move_name):
    """Converts a move name like 'Fire Fang' to 'MOVE_FIRE_FANG'."""
    # Handle special cases if any arise, e.g., "Double-Edge" -> "DOUBLE_EDGE"
    processed_name = move_name.upper()
    processed_name = re.sub(r'[\s\-]', '_', processed_name) # Replace space and hyphen with underscore
    processed_name = re.sub(r'[^\w_]', '', processed_name) # Remove other non-alphanumeric characters (except underscore)
    return f"MOVE_{processed_name}"

def fetch_pokemon_moves(pokemon_name):
    """Fetches level-up moves for a given Pokémon from PokemonDB."""
    pokemon_url_name = pokemon_name.lower() # Simple lowercasing for URL
    url = URL_TEMPLATE.format(pokemon=pokemon_url_name)
    print(f"Fetching moves for {pokemon_name} (URL name: '{pokemon_url_name}')... ", end='') # Added URL name for clarity

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")
        return None # Signal failure

    print("Parsing... ", end='') # Progress update
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the specific table for level-up moves.
    # PokemonDB usually has a heading like "Moves learnt by level up"
    # then the table follows. We look for the first table after such a heading.
    level_up_heading = soup.find('h2', string=re.compile(r'Moves learnt by level up', re.IGNORECASE))

    if not level_up_heading:
        print(f"Failed: Could not find the 'Moves learnt by level up' section heading on the page.")
        # Fallback: try finding the first data table directly (less reliable)
        data_table = soup.find('table', class_='data-table')
        if not data_table:
            print("Fallback failed: Could not find any data table.")
            return None # Signal failure
        print("Warning: Using fallback table search... ", end='') # Progress update
    else:
         # Find the first table immediately following the heading
        data_table = level_up_heading.find_next_sibling('table', class_='data-table')
        if not data_table:
             print(f"Failed: Found heading but could not find the data table immediately after it.")
             return None # Signal failure


    tbody = data_table.find('tbody')
    if not tbody:
        print("Failed: Could not find the table body (tbody).")
        return None # Signal failure

    moves = []
    rows = tbody.find_all('tr') # Get rows to check if tbody is empty
    if not rows:
        print("Note: Table body is empty.")
        return [] # Return empty list, not None, as fetch/parse technically worked

    for row in rows:
        level_cell = row.find('td', class_='cell-num')
        move_cell = row.find('td', class_='cell-name')

        if level_cell and move_cell:
            level_text = level_cell.get_text(strip=True)
            move_name_tag = move_cell.find('a', class_='ent-name')

            if move_name_tag:
                move_name = move_name_tag.get_text(strip=True)
                # Try converting level to int, handle 'Evo.' or other non-numeric cases
                try:
                    level = int(level_text)
                    moves.append({'level': level, 'move': move_name})
                except ValueError:
                    # Handle cases like 'Evo.' - often implies level 1 for starting movesets
                    # Or starting moves sometimes marked differently. Assume 1 for simplicity here.
                    if level_text == '1' or level_text.lower() == 'evo.' or level_text == '—':
                         moves.append({'level': 1, 'move': move_name})
                         # print(f"Note: Treating level '{level_text}' for move '{move_name}' as level 1.") # Optional note
                    # else: # No warning for skipped rows in original code
                         # print(f"Warning: Skipping row with non-numeric level '{level_text}' for move '{move_name}'.")
                         pass # Silently ignore other non-numeric levels

    # Check if moves were actually extracted even if rows existed
    if not moves and len(rows) > 0:
         print("Warning: Found table rows but couldn't extract valid moves.")
         return [] # Return empty list to indicate parsing happened but yielded nothing usable
    elif not moves: # No rows found initially, or moves is still empty
        print("Note: No moves extracted.")
        return [] # Return empty list

    print(f"OK ({len(moves)} moves).") # Progress update
    return moves # Return list of moves (can be empty)

def update_learnset_in_file(file_path, pokemon_name, moves_data):
    """Updates the learnset for a specific Pokémon in the .h file."""
    # Format the Pokémon name as it appears in the C variable (e.g., "Charmeleon")
    c_pokemon_name = pokemon_name.capitalize() # Simple capitalization for C Var Name
    start_marker = f"static const struct LevelUpMove s{c_pokemon_name}LevelUpLearnset[] = {{"
    end_marker = f"{INDENT}LEVEL_UP_END" # Includes exact indentation from config

    if not os.path.exists(file_path):
        print(f"      Error: File not found at {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"      Error reading file {file_path}: {e}")
        return False

    start_index = -1
    end_index = -1
    brace_index = -1 # Keep track of closing brace index

    # Find the start and end lines of the existing learnset
    for i, line in enumerate(lines):
        # Find start marker
        if start_index == -1 and start_marker in line: # Check only if not already found
            start_index = i
        # Find the *first* LEVEL_UP_END after the start marker
        elif start_index != -1 and end_index == -1: # Check only if start found and end not yet found
            # Check if the line *exactly* matches the end marker line (including indent)
            # Using strip() comparison first is safer for potential trailing whitespace issues
            if line.strip() == 'LEVEL_UP_END' and line.startswith(INDENT):
                 end_index = i
                 # Don't break yet, find the closing brace too for accuracy
        # Find the closing brace '};' after the end marker is found
        elif end_index != -1 and line.strip() == '};':
            brace_index = i
            break # Found start, end, and brace

    if start_index == -1:
        print(f"      Update Failed: Could not find the start marker for {c_pokemon_name}.")
        print(f"      Searched for line containing: '{start_marker}'")
        return False # Indicate failure
    if end_index == -1:
        print(f"      Update Failed: Could not find the correctly indented 'LEVEL_UP_END' marker for {c_pokemon_name} after line {start_index + 1}.")
        # print(f"      Searched for line starting with '{INDENT}' and containing 'LEVEL_UP_END'") # Debug info
        return False # Indicate failure
    if brace_index == -1:
         print(f"      Update Failed: Closing brace '}};' for '{c_pokemon_name}' not found after line {end_index + 1}.")
         return False # Indicate failure

    # print(f"      Found learnset for {c_pokemon_name} between lines {start_index + 1} and {brace_index + 1}.") # Optional debug

    # Prepare the new move lines
    new_move_lines = []
    for move_info in moves_data:
        level = move_info['level']
        c_move_name = format_c_move_name(move_info['move'])
        new_move_lines.append(f"{INDENT}LEVEL_UP_MOVE({level:>2}, {c_move_name}),\n") # {:>2} formats level with padding

    # Construct the new file content
    new_lines = lines[:start_index + 1] # Keep lines up to and including the start marker
    new_lines.extend(new_move_lines)     # Add the new move lines
    new_lines.append(f"{end_marker}\n")  # Add the end marker line (exactly as defined)
    new_lines.append(lines[brace_index]) # Add the original closing brace line
    new_lines.extend(lines[brace_index + 1:]) # Keep lines after the closing brace

    # Write the updated content back to the file
    try:
        # Avoid writing if no changes were made
        if lines == new_lines:
            print(f"      Learnset for {c_pokemon_name} already up-to-date.")
            return True
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"      Successfully updated {c_pokemon_name}'s learnset in {file_path}.")
            return True
    except Exception as e:
        print(f"      Error writing updated file {file_path}: {e}")
        return False # Indicate failure
# --- End of original functions ---


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Pokémon Learnset Update (Gen 1-3) ---")
    print(f"Processing {len(POKEMON_NAMES_GEN1_3)} Pokémon.")
    print(f"Target file: {FILE_PATH}")
    print(f"Data source: PokemonDB (Gen 3 moves)")
    print(f"Delay between requests: {REQUEST_DELAY} seconds")
    print("\nIMPORTANT: Make sure you have a backup of your .h file!")

    fetch_failures = [] # List to store names of Pokémon that failed fetch/parse
    update_failures = [] # List to store names where file update failed (marker not found, write error)
    processed_count = 0

    for pokemon_name in POKEMON_NAMES_GEN1_3:
        processed_count += 1
        print(f"\n[{processed_count}/{len(POKEMON_NAMES_GEN1_3)}] Processing: {pokemon_name}")

        # Call the original fetch function
        fetched_moves = fetch_pokemon_moves(pokemon_name)

        # Check if fetch failed (returned None)
        if fetched_moves is None:
            fetch_failures.append(pokemon_name)
            print(f"      -> Added {pokemon_name} to fetch failure list.")
        else:
            # Fetch succeeded (returned a list, possibly empty)
            # Sort moves primarily by level, then alphabetically by name for consistency
            fetched_moves.sort(key=lambda x: (x['level'], x['move']))
            # Attempt to update the file using the original update function
            update_successful = update_learnset_in_file(FILE_PATH, pokemon_name, fetched_moves)
            if not update_successful:
                 update_failures.append(pokemon_name)
                 print(f"      -> Added {pokemon_name} to update failure list.")

        # Wait before the next request
        time.sleep(REQUEST_DELAY)

    print("\n--- Update Process Finished ---")
    print(f"Total Pokémon processed: {processed_count}")

    if fetch_failures:
        print(f"\n--- Fetch/Parse Failures ({len(fetch_failures)}) ---")
        print("These Pokémon likely failed due to network errors, 404 (check URL name - needs manual formatting?), or page parsing issues:")
        # Print list comma-separated for easier reading
        print(", ".join(fetch_failures))
    else:
        print("\nNo fetch/parse failures encountered.")

    if update_failures:
         print(f"\n--- File Update Failures ({len(update_failures)}) ---")
         print("Could not update the file for these Pokémon (likely marker not found - check C variable name - or write error):")
         # Print list comma-separated
         print(", ".join(update_failures))
    else:
         print("\nNo file update failures encountered (updates attempted successfully or learnsets were already current).")