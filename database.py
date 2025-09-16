import pathlib, types, csv



################################################################################



def get_similars(given, options): # TODO Copy-pasta.

    import difflib

    return difflib.get_close_matches(
        str(given),
        [str(option) for option in options],
        n      = 3,
        cutoff = 0
    )



class TBD:

    def __bool__(self):
        return False

    def __repr__(self):
        return '<TBD>'

    def __str__(self):
        return '<TBD>'

    def __deepcopy__(self, memo):
        return self

TBD = TBD()



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
        'TBD'        : TBD,
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
            off_by_one = entry.pop('off_by_one', None),
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
        system_database[mcu][key].pinned         = system_database[mcu][key].value is not TBD
        system_database[mcu][key].mapped         = False



        # It's useful to have the same entry go by multiple keys.

        for pseudokey in entry.pop('pseudokeys', ()):

            system_database[mcu][pseudokey] = system_database[mcu][key]



        # Ensure everything has been accounted for.

        if entry:
            raise ValueError(
                f'Leftover schema entry properties: {repr(entry)}.'
            )



################################################################################
#
# STM32CubeMX can generate a CSV file that'll detail all of the MCU's GPIO's
# alternate functions; when working a particular MCU, we should have this file
# generated already.
#



GPIO_ALTERNATE_FUNCTION_CODES = {}

for mcu in system_database:

    GPIO_ALTERNATE_FUNCTION_CODES[mcu] = {}

    for entry in csv.DictReader(
        pathlib.Path(__file__)
            .parent
            .joinpath(f'databases/{mcu}.csv')
            .read_text()
            .splitlines()
    ):

        match entry['Type']:



            # Most GPIOs we care about are the I/O ones.

            case 'I/O':



                # Some GPIO names are suffixed with additional things,
                # so we need to format it slightly so that we just get
                # the port letter and pin number.
                # e.g:
                # >
                # >     PC14-OSC32_IN(OSC32_IN) -> PC14
                # >     PH1-OSC_OUT(PH1)        -> PH1
                # >     PA14(JTCK/SWCLK)        -> PA14
                # >     PC2_C                   -> PC2
                # >

                pin    = entry['Name']
                pin    = pin.split('-', 1)[0]
                pin    = pin.split('(', 1)[0]
                pin    = pin.split('_', 1)[0]
                port   = pin[1]
                number = int(pin[2:])

                assert pin.startswith('P') and ('A' <= port <= 'Z')



                # Gather all the alternate functions of the GPIO, if any.

                for code in range(16):



                    # Skip empty cells.

                    if not entry[f'AF{code}']:
                        continue



                    # Some have multiple names for the
                    # same AFSEL code (e.g. "I2S3_CK/SPI3_SCK").

                    for alternate_function in entry[f'AF{code}'].split('/'):

                        key = (port, number, alternate_function)

                        assert key not in GPIO_ALTERNATE_FUNCTION_CODES[mcu]

                        GPIO_ALTERNATE_FUNCTION_CODES[mcu][key] = code



            # TODO Maybe use this information to ensure
            #      the PCB footprint is correct?

            case 'Power' | 'Reset' | 'Boot':
                pass



            # TODO I have no idea what this is.

            case 'MonoIO':
                pass



            # Unknown GPIO type in the CSV;
            # doesn't neccessarily mean an error though.

            case _:
                pass # TODO Warn.
