import pathlib, types, csv, difflib



################################################################################
#
# The `TBD` stands for "To-Be-Determined" which acts like a `None`
# in that it's a falsy singleton. It's mainly used by the database
# indicate that a particular entry hasn't been assigned a value yet;
# we could use `None` to indicate this, but sometimes `None` could
# actually mean something meaningful for a particular database entry,
# so we'll be clear and explicit by stating "To-Be-Determined" here.
#



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



################################################################################



class SystemDatabase:



    # The system database for an MCU is just a
    # dictionary with some nice helper methods.

    def __init__(self, mcu, dictionary):

        self.mcu         = mcu
        self.dictionary  = dictionary
        self.translation = {
            given_key : proper_key
            for proper_key, entry in self.dictionary.items()
            for given_key in (proper_key, *entry.pseudokeys)
        }



    def __getitem__(self, given_key):

        return self.dictionary[self.translate(given_key)]



    # It's convenient to have some database entries to go by multiple
    # keys, so we'll need to do some key mapping in order to do that.
    # It's just a simple dictionary look-up, but we also provide a nice
    # error message to make life easier.

    def translate(self, given_key):

        proper_key = self.translation.get(given_key, None)

        if proper_key is None:
            raise ValueError(
                f'Undefined key {repr(given_key)} for database of MCU {repr(self.mcu)}; '
                f'close matches: {
                    repr(difflib.get_close_matches(
                        str(given_key),
                        map(str, self.translation.keys()),
                        n      = 3,
                        cutoff = 0,
                    ))
                }.'
            )

        return proper_key



################################################################################
#
# Database entries can have a constraint on them to specify
# a certain set of values they can take on, if any.
#



class Constraint:
    pass



class RealMinMax(Constraint):

    def __init__(self, minimum, maximum):

        self.minimum = minimum
        self.maximum = maximum



    def check(self, value):

        if isinstance(value, str):
            value = float(value)

        return self.minimum <= value <= self.maximum



    def show(self):

        return f'{type(self).__name__}({self.minimum}, {self.maximum})'



class IntMinMax(Constraint):

    def __init__(self, minimum, maximum):

        self.minimum = minimum
        self.maximum = maximum



    def check(self, value):

        if isinstance(value, str):
            value = int(value, 0)

        return value.is_integer() and self.minimum <= value <= self.maximum



    def show(self):

        return f'{type(self).__name__}({self.minimum}, {self.maximum})'



    def iterate(self):

        return iter(range(self.minimum, self.maximum + 1))



class Choices(Constraint):

    def __init__(self, *values):
        self.values = tuple(values)

    def check(self, value):
        return value in self.values

    def iterate(self):
        return iter(self.values)

    def show(self):
        return f'({', '.join(map(repr, self.values))})'



class Mapping(Constraint):

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def check(self, value):
        return value in self.dictionary

    def iterate(self):
        return iter(self.dictionary)

    def show(self):
        return f'({', '.join(map(repr, self.dictionary.keys()))})'



################################################################################



def process_mcu(mcu):



    # Execute the database script.

    database_globals = {
        'TBD'        : TBD,
        'RealMinMax' : RealMinMax,
        'IntMinMax'  : IntMinMax,
        'Choices'    : Choices,
        'Mapping'    : Mapping,
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

    dictionary = {}

    for key, entry in database_globals['SCHEMA'].items():

        dictionary[key] = types.SimpleNamespace(
            category   = entry.pop('category'  , None),
            location   = entry.pop('location'  , None),
            off_by_one = entry.pop('off_by_one', None),
            pseudokeys = entry.pop('pseudokeys', ()  ),
        )



        # We can apply a weak but simple constraint
        # on the set of values that the entry can take,
        # if any.

        constraint = entry.pop('constraint', None)

        if constraint is not None and not isinstance(constraint, Constraint):
            raise ValueError(
                f'Database entry {repr(key)} for MCU {repr(mcu)} '
                f'has unknown constraint: {repr(constraint)}.'
            )

        dictionary[key].constraint = constraint



        # Some database entries can be assigned a
        # value during parameterization. Entries
        # can also be pinned to indicate that their
        # value shouldn't be modified. Some entries'
        # values can also be mapped to the actual
        # value to be used in the generated code.

        dictionary[key].can_hold_value = 'value' in entry
        dictionary[key].value          = entry.pop('value', None)
        dictionary[key].pinned         = dictionary[key].value is not TBD
        dictionary[key].mapped         = False



        # Ensure everything has been accounted for.

        if entry:
            raise ValueError(
                f'Leftover schema entry properties: {repr(entry)}.'
            )



    return SystemDatabase(mcu, dictionary)



# We automatically determine the supported MCUs.

MCUS = {
    mcu : process_mcu(mcu)
    for mcu in sorted(dict.fromkeys(
        item.stem
        for item in pathlib.Path(__file__).parent.joinpath('databases').iterdir()
        if item.is_file()
        if item.stem.isidentifier()
        if item.stem.startswith('STM32')
    ))
}



################################################################################
#
# STM32CubeMX can generate a CSV file that'll detail all of the MCU's GPIO's
# alternate functions; when working a particular MCU, we should have this file
# generated already.
#



GPIO_ALTERNATE_FUNCTION_CODES = {}

for mcu in MCUS:

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
