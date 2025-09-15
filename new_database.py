import pathlib, types



################################################################################



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



################################################################################



MCUS = sorted(dict.fromkeys(
    item.stem
    for item in pathlib.Path(__file__).parent.joinpath('databases').iterdir()
    if item.is_file()
    if item.stem.isidentifier()
    if item.stem.startswith('STM32')
))



################################################################################



system_database = {
    mcu : {}
    for mcu in MCUS
}

for mcu in MCUS:



    # Execute the database script.

    database_globals = {
        'RealMinMax' : RealMinMax,
        'IntMinMax'  : IntMinMax,
    }

    initial_globals = list(database_globals.keys())

    exec(
        pathlib.Path(__file__)
            .parent
            .joinpath(f'databases/{mcu}.py')
            .read_text(),
        database_globals,
        {},
    )



    # Any newly declared globals will be added to the schema as a constant.

    for key in database_globals.keys():

        if key in ('__builtins__', 'SCHEMA', *initial_globals):
            continue

        database_globals['SCHEMA'][key] = {
            'category' : 'constant',
            'value'    : database_globals[key],
        }



    # Process each entry of the database schema.

    for key, entry in database_globals['SCHEMA'].items():



        # Common fields all database entries have.

        system_database[mcu][key] = types.SimpleNamespace(
            category   = entry.pop('category'  , None),
            location   = entry.pop('location'  , None),
            constraint = entry.pop('constraint', None),
        )



        # Some database entries can be assigned a value for parameterization.

        if 'value' in entry:
            system_database[mcu][key].value = entry.pop('value')



        # It's useful to have the same entry go by multiple keys.

        for pseudokey in entry.pop('pseudokeys', ()):

            system_database[mcu][pseudokey] = system_database[mcu][key]



        # Ensure everything has been accounted for.

        if entry:
            raise ValueError(
                f'Leftover schema entry properties: {repr(entry)}.'
            )
