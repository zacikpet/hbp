import re

from typing import List, Optional


# Returns luminosity in inverse femtobarns
def get_luminosity(text: str) -> List[float]:
    units = [
        ('pb', 0.001),
        ('fb', 1),
        ('pico', 0.001),
        ('femto', 1)
    ]

    multiplier = 1

    for unit, coefficient in units:
        if unit in text.lower():
            multiplier = coefficient
            break

    return [multiplier * float(x) for x in re.findall(r"[-+]?\d+\.*\d*", text) if x not in ['1', '-1']]


# Returns centre of mass energy in TeV
def get_energy(text: str) -> List[float]:
    units = [
        ('mev', 1_000_000),
        ('gev', 1_000),
        ('tev', 1)
    ]

    multiplier = 1

    for unit, coefficient in units:
        if unit in text.lower():
            multiplier = coefficient
            break

    energies = [multiplier * float(x) for x in re.findall(r"\d+\.*\d*", text)]

    return energies


# Returns collison type: 'pp' | 'pbpb' | 'ee'
def get_collision(text: str) -> Optional[str]:
    pp_keys = ['pp', 'proton', 'p-p', 'p--p']
    pb_keys = ['pb', 'lead']
    ee_keys = ['e+e', 'e^+', 'e^-', 'e+', 'e-', 'electron', 'positron']

    for pp_key in pp_keys:
        if pp_key in text.lower():
            return 'pp'

    for pb_key in pb_keys:
        if pb_key in text.lower():
            return 'pbpb'

    for ee_key in ee_keys:
        if ee_key in text.lower():
            return 'ee'

    return None


# Returns production mode: vbf, gf
def get_production(text: str) -> Optional[str]:
    vbf_keys = ['vector', 'vb']
    gf_keys = ['gluon', 'gf']

    for vbf_key in vbf_keys:
        if vbf_key in text:
            return 'vbf'

    for gf_key in gf_keys:
        if gf_key in text:
            return 'gf'

    return None
