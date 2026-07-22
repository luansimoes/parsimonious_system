from app.composition import Composition
from app.utils import generate_sequence, save_json, load_json
from app.encoder import CompositionEncoder

from scamp._soundfont_host import get_soundfont_presets
from edopi import Scale

from app.interface import TkInterface #, PSGInterface

import json

PRESETS = sorted([p.name for p in get_soundfont_presets()])
PROGRAM_NAME = "Gerador de Fragmentos Timbrais"

composition = Composition(None, None)



# ------------------------------------------ GENERATION ----------------------------------------------------
def generate_piece(fields):
    """
    Generates a musical piece based on the provided parameters.
    Args:
        fields (dict): A dictionary containing the following keys:
            - 'edo_size' (str): Equal division of the octave size.
            - 'interval_struct' (str): Space-separated string of intervals.
            - 'tonic' (str): The tonic note.
            - 'beats' (str): Number of beats per measure.
            - 'base_octaves' (str): Space-separated string of base octaves.
            - 'inst_weights' (str): Space-separated string of instrument weights.
            - 'inst_names' (list): List of instrument names.
            - 'measures' (str): Number of measures.
            - 'k' (str): Parameter for sequence generation.
            - 'l' (str): Parameter for sequence generation.
            - 'n_timepoints' (str): Space-separated string of timepoints.
    Returns:
        Composition: An object representing the generated musical piece.
    """

    edo_size = int(fields['edo_size'])
    interval_struct = tuple(int(x) for x in fields['interval_struct'].split())
    tonic = int(fields['tonic'])

    scale = Scale(edo_size, interval_struct, tonic)
    beats = int(fields['beats'])
    base_octaves = [int(x) for x in fields['base_octaves'].split()]
    base_pitches = [(x*edo_size) + tonic for x in base_octaves]
    inst_weights = [float(x) for x in fields['inst_weights'].split()]

    inst_names = fields['inst_names']
    measures = int(fields['measures'])
    k = int(fields['k'])
    l = int(fields['l'])

    n_timepoints = [int(x) for x in fields['n_timepoints'].split()]

    n_tps = beats*n_timepoints[0] if len(n_timepoints) == 1 else sum(n_timepoints)

    chord_seq = generate_sequence(len(inst_names)+1, k, l, measures, inst_weights)
    rhythm_seq = generate_sequence(n_tps, k, l, measures)

    return Composition(chord_seq, 
                    rhythm_seq, 
                    scale = scale, 
                    beats = beats,
                    n_timepoints = n_timepoints,
                    inst_names = inst_names, 
                    base_pitches = base_pitches,
                    inst_weights = inst_weights,
                    pars = fields)

def generate(interface):
    """
    Generates a musical composition based on the provided interface.
    This function validates the fields of the interface, sets the state to generating,
    reads the current window values, and generates a musical piece if the fields are valid.
    Args:
        interface (Interface): An object that provides methods to validate fields,
                               set state, and read current values.
    Returns:
        None
    """
    global composition

    valid = interface.validate_fields()
    #print(valid)

    if valid:
        interface.set_state_to_generating()
        interface.read_window()
        composition = generate_piece(interface.cur_values)

def export_file(interface):
    """
    Exports the composition to a file.
    This function retrieves the filename from the provided interface, exports the composition score to that file,
    and then saves the composition data in JSON format using the same base filename.
    Args:
        interface: An object that provides the method `get_exporting_filename` to retrieve the filename for exporting.
    Returns:
        None
    """

    filename = interface.get_exporting_filename()
            
    composition.export_score(filename)
    save_json(f'{filename[:-4]}.json', composition, encoder = CompositionEncoder)

def save_pars(interface):
    """
    Save the current parameters of the interface to a JSON file.
    This function triggers the interface to set its state to saving parameters,
    retrieves the filename for saving, and then saves the current values of the
    interface to a JSON file.
    Args:
        interface (object): An object that has methods `set_state_to_saving_parameters`
                            and an attribute `cur_values` which holds the current values
                            to be saved.
    """

    filename = interface.set_state_to_saving_parameters()
    save_json(filename, interface.cur_values)

def load_pars(interface):
    """
    Loads parameters from a JSON file and updates the interface accordingly.
    This function sets the interface state to loading parameters, attempts to load
    the parameters from a JSON file, and updates the interface with the loaded parameters.
    If an error occurs during loading, an error popup is shown.
    Args:
        interface: An object that provides methods to interact with the user interface.
                   It should have the following methods:
                   - set_state_to_loading_parameters(): Sets the interface state to loading parameters and returns the filename.
                   - show_popup(message, title): Displays a popup with the given message and title.
                   - update_window(par_dict): Updates the interface window with the given parameters dictionary.
    Raises:
        Exception: If an error occurs during the loading of the JSON file, it is caught and printed,
                   and an error popup is shown to the user.
    """

    filename = interface.set_state_to_loading_parameters()

    try:
        par_dict = load_json(filename)    
    except Exception as e:
        print(e)
        interface.show_popup('Um erro inesperado ocorreu.', 'ERRO')
    else:
        interface.update_window(par_dict)
        interface.show_popup('Carregamento concluído com sucesso!', 'SUCESSO') 

def main():
    """
    Main function to initialize and run the TkInterface for the parsimonious system application.
    This function sets up the interface with the given program name and presets, binds various
    events to their corresponding handlers, and starts the main loop of the interface.
    Event bindings:
    - "<<GEN>>": Binds to the generate function.
    - "<<PLAY>>": Binds to the interface's play method and triggers the composition to play a piece.
    - "<<END_PLAY>>": Binds to set the interface state to ready.
    - "<<EXP_FILE>>": Binds to the export_file function.
    - "<<SAVE_PARS>>": Binds to the save_pars function.
    - "<<LOAD_PARS>>": Binds to the load_pars function.
    - "<<INST_NAMES>>": Binds to update the instrument names in the interface.
    Returns:
        None
    """

        
    interface = TkInterface(PROGRAM_NAME, PRESETS)

    interface.external_bind("<<GEN>>", generate, interface)
    interface.external_bind("<<PLAY>>", interface.play, lambda: composition.play_piece(100), "<<END_PLAY>>")
    interface.external_bind("<<END_PLAY>>", interface.set_state_to_ready)
    interface.external_bind("<<EXP_FILE>>", export_file, interface)
    interface.external_bind("<<SAVE_PARS>>", save_pars, interface)
    interface.external_bind("<<LOAD_PARS>>", load_pars, interface)
    interface.external_bind("<<INST_NAMES>>", interface.update_inst_names) 

    interface.run_mainloop()
