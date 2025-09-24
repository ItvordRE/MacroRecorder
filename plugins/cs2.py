def get_game_specific_keys():
    return {
        'shoot': 'left_click',
        'reload': 'r',
        'jump': 'space',
        'crouch': 'ctrl',
        'sprint': 'shift',
        'knife': '1',
        'pistol': '2',
        'primary': '3',
        'use': 'e',
        'inspect': 'f'
    }

def get_default_coords():
    return {
        'buy_menu': (960, 540),
        'defuse_kit': (100, 100),
        'map_center': (960, 540),
        'radar': (1750, 150)
    }

def get_macro_presets():
    return [
        {
            'name': 'Быстрая покупка AK47',
            'actions': [
                {'type': 'key_press', 'key': 'b', 'time': 0.1},
                {'type': 'click', 'x': 800, 'y': 400, 'button': 'left', 'time': 0.2},
                {'type': 'click', 'x': 900, 'y': 300, 'button': 'left', 'time': 0.3}
            ]
        }
    ]