def get_game_specific_keys():
    return {
        'click_left': 'z',
        'click_right': 'x',
        'smoke': 'c',
        'skip': 'space'
    }

def get_macro_presets():
    return [
        {
            'name': 'Быстрое кликание',
            'actions': [
                {'type': 'key_press', 'key': 'z', 'time': 0.05},
                {'type': 'key_press', 'key': 'x', 'time': 0.1},
                {'type': 'key_press', 'key': 'z', 'time': 0.15}
            ]
        }
    ]