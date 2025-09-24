def get_game_specific_keys():
    return {
        'attack': 'a',
        'move': 's',
        'cast_q': 'q',
        'cast_w': 'w',
        'cast_e': 'e',
        'cast_r': 'r',
        'item_1': 'd',
        'item_2': 'f'
    }

def get_macro_presets():
    return [
        {
            'name': 'Combo QWE',
            'actions': [
                {'type': 'key_press', 'key': 'q', 'time': 0.1},
                {'type': 'key_press', 'key': 'w', 'time': 0.3},
                {'type': 'key_press', 'key': 'e', 'time': 0.5}
            ]
        }
    ]