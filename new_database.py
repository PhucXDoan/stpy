import pathlib



class RealMinMax:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __contains__(self, value):
        return self.minimum <= value <= self.maximum



class IntMinMax:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __contains__(self, value):
        return value.is_integer() and self.minimum <= value <= self.maximum

    def __iter__(self):
        return iter(range(self.minimum, self.maximum + 1))



new_system_database = {}

for mcu in sorted(dict.fromkeys(
    item.stem
    for item in pathlib.Path(__file__).parent.joinpath('databases').iterdir()
    if item.is_file()
    if item.stem.isidentifier()
)):

    new_system_database[mcu] = {}

    # Parse the database file.

    globals = {
        'RealMinMax' : RealMinMax,
        'IntMinMax'  : IntMinMax,
    }

    original_keys = list(globals.keys())

    exec(
        pathlib.Path(__file__)
            .parent
            .joinpath(f'databases/{mcu}.py')
            .read_text(),
        globals,
        {},
    )

    for key in globals.keys():

        if key in ('__builtins__', 'SCHEMA', *original_keys):
            continue

        new_system_database[mcu][key] = {
            'category'   : 'constant',
            'location'   : None,
            'constraint' : None,
            'value'      : globals[key],
        }


    for key, value in globals['SCHEMA'].items():

        new_system_database[mcu][key] = {
            'category'   : value.pop('category'  , None),
            'location'   : value.pop('location'  , None),
            'constraint' : value.pop('constraint', None),
        }

        if 'value' in value:
            new_system_database[mcu][key]['value'] = value.pop('value')

        if 'pseudokeys' in value:

            pseudokeys = value.pop('pseudokeys')

            for pseudokey in pseudokeys:
                new_system_database[mcu][pseudokey] = new_system_database[mcu][key]

        if value:
            raise ValueError(f'Leftover schema entry properties: {repr(value)}.')
