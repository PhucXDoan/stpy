import pathlib, types



################################################################################



class RealMinMax:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def check(self, value):
        if isinstance(value, str): value = float(value)
        return self.minimum <= value <= self.maximum

    def show(self):
        return f'{type(self).__name__}({self.minimum}, {self.maximum})'



class IntMinMax:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def check(self, value):
        if isinstance(value, str): value = int(value, 0)
        return value.is_integer() and self.minimum <= value <= self.maximum

    def iterate(self):
        return iter(range(self.minimum, self.maximum + 1))

    def show(self):
        return f'{type(self).__name__}({self.minimum}, {self.maximum})'



class Choices(tuple):

    def check(self, value):
        return value in self

    def iterate(self):
        return iter(self)

    def show(self):
        return f'({', '.join(map(repr, self))})'



class Mapping(dict):

    def check(self, value):
        return value in self

    def iterate(self):
        return iter(self)

    def show(self):
        return f'({', '.join(map(repr, self.keys()))})'



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

        system_database[mcu][key] = types.SimpleNamespace(
            category   = entry.pop('category'  , None),
            location   = entry.pop('location'  , None),
        )



        # We can apply a weak but simple constraint
        # on the set of values that the entry can take,
        # if any.

        match constraint := entry.pop('constraint', None):
            case None         : pass
            case RealMinMax() : pass
            case IntMinMax()  : pass
            case tuple()      : constraint = Choices(constraint)
            case dict()       : constraint = Mapping(constraint)
            case unknown      : raise ValueError(unknown)

        system_database[mcu][key].constraint = constraint



        # Some database entries can be assigned a
        # value during parameterization. Entries
        # can also be pinned to indicate that their
        # value shouldn't be modified. Some entries'
        # values can also be mapped to the actual
        # value to be used in the generated code.

        system_database[mcu][key].can_hold_value = 'value' in entry
        system_database[mcu][key].value          = entry.pop('value', None)
        system_database[mcu][key].pinned         = system_database[mcu][key].value is not ...
        system_database[mcu][key].mapped         = False



        # It's useful to have the same entry go by multiple keys.

        for pseudokey in entry.pop('pseudokeys', ()):

            system_database[mcu][pseudokey] = system_database[mcu][key]



        # Ensure everything has been accounted for.

        if entry:
            raise ValueError(
                f'Leftover schema entry properties: {repr(entry)}.'
            )
