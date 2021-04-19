import re

from typing import List, Optional


# Returns luminosity in inverse picobarns
def get_luminosity(text: str) -> List[float]:
    units = [
        ('pb', 1),
        ('fb', 1_000),
        ('pico', 1),
        ('femto', 1_000)
    ]

    for unit, coefficient in units:
        if unit in text.lower():
            multiplier = coefficient
            break
    else:
        multiplier = 1_000

    return [multiplier * float(x) for x in re.findall(r"[-+]?\d+\.*\d*", text) if x not in ['1', '-1']]


# Returns centre of mass energy in MeV
def get_energy(text: str) -> List[float]:
    units = [
        ('mev', 1),
        ('gev', 1_000),
        ('tev', 1_000_000)
    ]

    for unit, coefficient in units:
        if unit in text.lower():
            multiplier = coefficient
            break
    else:
        multiplier = 1_000_000

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


def get_production(text: str) -> Optional[str]:
    text = text.lower()

    # associated production
    if 'assoc' in text or 'wh' in text or 'zh' in text:

        if 'top' in text or 'quark' in text:
            return 'tth'

        if 'vector' in text or 'boson' in text or 'wh' in text or 'zh' in text:
            return 'whzh'

    if 'fusion' in text or 'f' in text:
        if 'gluon' in text or 'gg' in text or 'gf' in text:
            return 'ggf'

        if 'vector' in text or 'boson' in text or 'vbf' in text:
            return 'vbf'

    return None


def get_associated_production(text: str) -> Optional[str]:

    text = text.lower()

    if 'boson' in text or 'w' in text or 'z' in text or 'vector' in text or 'weak' in text:
        return 'whzh'

    if 'top' in text or 'quark' in text or 'tth' in text:
        return 'tth'


def get_particles(text: str) -> List[str]:
    words = [word.lower() for word in text.split(' ') if word != '']
    joined = ' '.join(words)

    options = {
        # Bosons
        'boson': ['boson'],
        'higgs': ['h boson', 'higgs'],
        'photon': ['photon', 'γ', 'gamma'],
        'gluon': ['gluon'],
        'w_boson': ['w boson', 'ww'],
        'z_boson': ['z boson', 'zz'],

        # Quarks
        'quark': ['quark'],
        'top': ['top quark', 't quark', 't-quark', 'top', 'top-quark', 'tt'],
        'bottom': ['bottom quark', 'b quark', 'b-quark', 'bottom', 'bottom-quark', 'beauty', 'bb'],
        'up': ['up quark', 'u quark', 'u-quark', 'up-quark'],
        'down': ['down quark', 'd quark', 'd-quark', 'down', 'down-quark'],
        'charm': ['charm quark', 'c quark', 'c-quark', 'charm', 'charm-quark'],
        'strange': ['strange quark', 's quark', 's-quark', 'strange', 'strange-quark'],

        # 1st gen leptons
        'lepton': ['lepton', 'ℓ'],
        'electron': ['electron', 'ee'],
        'muon': ['muon', 'μ', 'mu'],
        'tau': ['tau', 'τ'],

        # Neutrinos
        'neutrino': ['neutrino', 'ν'],
        'e_neutrino': ['e neutrino', 'electron neutrino', 'eν'],
        'm_neutrino': ['m neutrino', 'muon neutrino', 'μν'],
        't_neutrino': ['t neutrino', 'electron neutrino', 'τν'],

        # Other
        'invisible': ['invisible'],
        'jets': ['jets'],
        'new': ['new'],
        'gravitino': ['gravitino'],
        'dark': ['dark', 'dark matter'],
        'lsp': ['lsp']
    }

    result = []

    exclusion = {
        'top': {
            'tt': 'bottom'
        }
    }

    for particle in options.keys():
        for option in options[particle]:

            if particle in exclusion and option in exclusion[particle]:
                if exclusion[particle][option] in joined:
                    continue

            if option in joined:
                result.append(particle)
                break

    return list(set(result))
