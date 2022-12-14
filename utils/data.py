import string
from collections import Counter

import numpy as np
import pandas as pd
from global_land_mask import globe

from utils.colors import map_colors, COLOR_LIST

country_indicators = pd.read_csv("data/country_indicators.csv")

# country_indicators.year = country_indicators.year.apply(lambda x: int(x) if x else 'N/A')
# country_indicators.population = country_indicators.population.apply(lambda x: int(x) if x else 'N/A')
# country_indicators.population = country_indicators.population.apply(lambda x: int(x) if x else 'N/A')

pirate_attacks = pd.read_csv("data/pirate_attacks.csv")

# Add ID
pirate_attacks['reference_id'] = pirate_attacks.index.values

# Filter points on land
pirate_attacks["is_ocean"] = pirate_attacks.apply(lambda row: globe.is_ocean(row.latitude, row.longitude), axis=1)
pirate_attacks = pirate_attacks[pirate_attacks["is_ocean"]].copy()

# Year
pirate_attacks['date_year'] = pirate_attacks.date.apply(lambda x: int(x.split('-')[0]))

# Attack Type "Boarding" -> "Boarded"
pirate_attacks['attack_type'] = pirate_attacks['attack_type'].apply(
    lambda at: 'Boarded' if at == 'Boarding' else str(at)).copy()

# Map attack types to colors
colors = Counter(pirate_attacks.attack_type).keys()
c_map = map_colors(colors, COLOR_LIST)
pirate_attacks['color'] = pirate_attacks.attack_type.apply(str).map(c_map).copy()
pirate_attacks['shaded_color'] = pirate_attacks['color'].copy()

# Vessel Status "steaming" -> "Steaming"
pirate_attacks['vessel_status'] = pirate_attacks['vessel_status'].apply(
    lambda vs: 'Steaming' if vs == 'steaming' else str(vs)).copy()

# Vessel Status "Underway" -> "Steaming"
pirate_attacks['vessel_status'] = pirate_attacks['vessel_status'].apply(
    lambda vs: 'Steaming' if vs == 'Underway' else str(vs)).copy()

# Vessel Status "Moored" -> "Berthed"
pirate_attacks['vessel_status'] = pirate_attacks['vessel_status'].apply(
    lambda vs: 'Berthed' if vs == 'Moored' else str(vs)).copy()


def break_lines(s: str, max_len: int = 30) -> str:
    # Split the string into words.
    words = s.split()

    # Initialize the result string and the current line.
    result = ""
    line = ""

    # Loop over the words.
    for word in words:
        # If the current line plus the current word is longer than the maximum line length,
        # add the current line to the result and reset the current line.
        if len(line) + len(word) > max_len:
            result += line + "<br>"
            line = ""

        # Add the current word to the current line, followed by a space.
        line += word + " "

    # Add the remaining line to the result.
    result += line

    return result


def get_custom_data(data: pd.DataFrame):
    def remove_nans(col):
        return col.apply(lambda s: s if (s is not None and str(s) != 'nan') else 'N/A')

    vessel_names = remove_nans(data['vessel_name'])
    loc_desc = remove_nans(data['location_description'])
    loc_desc = loc_desc.apply(break_lines)

    attack_desc = remove_nans(data['attack_description'])
    attack_desc = attack_desc.apply(break_lines)

    nearest_country = data['nearest_country']
    year = data['date_year']

    ref_id = data['reference_id']

    custom_data = np.stack([vessel_names, loc_desc, attack_desc, nearest_country, year, ref_id], axis=-1)
    return custom_data


def format_colname(plot_type):
    plot_type = plot_type.replace("_", " ")
    plot_type = string.capwords(plot_type)
    return plot_type.replace('Eez', 'EEZ')


def filter_data(df: pd.DataFrame,
                range: list = None,
                attack_types: list = None,
                selected_data: dict = None):
    data_mask = np.ones(df.shape[0], dtype=bool)

    if range:
        data_mask = data_mask & (df.date_year >= range[0])
        data_mask = data_mask & (df.date_year <= range[1])

    if attack_types:
        data_mask = data_mask & (df.attack_type.apply(lambda at: at in attack_types))

    if selected_data:
        ref_idx = [p['customdata'][-1] for p in selected_data['points']]
        data_mask = data_mask & (df.reference_id.apply(lambda ref_id: ref_id in ref_idx))

    filtered_data = df[data_mask].copy()

    return filtered_data
