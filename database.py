import types, pathlib, re, collections
from ..pxd.utils import mk_dict



################################################################################
#
# For database entries with a list of valid values given explicitly.
# e.g:
# >
# >    ('IWDG',
# >        ('KR',
# >            ('KEY', 'IWDG_KEY', (
# >                '0xAAAA',
# >                '0x5555',
# >                '0xCCCC',
# >            )),
# >        ),
# >    )
# >
#



class SystemDatabaseOptions(types.SimpleNamespace):



    # Allow for easy iteration over the possible options.

    def __iter__(self):
        return iter(self.options)



    # Index into the option table.

    def __getitem__(self, key):
        return mk_dict(self.options)[key] # TODO Stupid call to `mk_dict`.



################################################################################
#
# For database entries that have valid values within an interval.
# TODO Have integral and continuous range?
# e.g:
# >
# >    ('SysTick',
# >        ('LOAD',
# >            ('RELOAD', 'SYSTICK_RELOAD', 1, (1 << 24) - 1),
# >        ),
# >    )
# >
#



class SystemDatabaseMinMax(types.SimpleNamespace):



    # Allow for sweeping through the whole range of possible values.

    def __iter__(self):

        return iter(range(self.minimum, self.maximum + 1))



    # Determine if a value is within the minimum-maximum range.

    def __contains__(self, value):

        return self.minimum <= value <= self.maximum



################################################################################
#
# Parse each MCU's database expression.
#



system_database = {}

for mcu in dict.fromkeys(
    item.stem
    for item in pathlib.Path(__file__).parent.joinpath('mcu').iterdir()
    if item.is_file()
    if item.stem.isidentifier()
):



    # Load and evaluate the Python expression.

    database_file_path = pathlib.Path(__file__).parent.joinpath(f'mcu/{mcu}.py')


    constants, location_tree = eval(database_file_path.read_text(), {}, {})
    items                    = []



    # Parse the constants.

    for constant in constants:

        match constant:



            # The constant's value is directly given.
            # e.g:
            # >
            # >    ('APB_UNITS', (1, 2, 3))
            # >

            case (key, value):

                items += [(key, value)]



            # The constant's value is an inclusive min-max range.
            # e.g:
            # >
            # >    ('PLL_CHANNEL_FREQ', 1_000_000, 250_000_000)
            # >

            case (key, minimum, maximum):

                items += [(key, SystemDatabaseMinMax(
                    minimum = minimum,
                    maximum = maximum,
                ))]



            # Unsupported constant.

            case unknown:

                raise ValueError(
                    f'Database constant entry is '
                    f'in an unknown format: {repr(unknown)}.'
                )



    # Parse the locations.

    for peripheral, *register_tree in location_tree:

        for register, *field_tree in register_tree:

            for location in field_tree:

                match location:



                    # The location entry's value is assume to be 1 bit.
                    # e.g:
                    # >
                    # >    ('PWR',
                    # >        ('SR1',
                    # >            ('ACTVOS', 'CURRENT_ACTIVE_VOS'),
                    # >        ),
                    # >    )
                    # >

                    case (field, key):

                        items += [(key, SystemDatabaseOptions(
                            peripheral = peripheral,
                            register   = register,
                            field      = field,
                            options    = (False, True),
                        ))]



                    # The location entry's list of valid values are given.
                    # e.g:
                    # >
                    # >    ('IWDG',
                    # >        ('KR',
                    # >            ('KEY', 'IWDG_KEY', (
                    # >                '0xAAAA',
                    # >                '0x5555',
                    # >                '0xCCCC',
                    # >            )),
                    # >        ),
                    # >    )
                    # >

                    case (field, key, options):

                        items += [(key, SystemDatabaseOptions(
                            peripheral = peripheral,
                            register   = register,
                            field      = field,
                            options    = options,
                        ))]



                    # The location entry's value is an inclusive min-max range.
                    # e.g:
                    # >
                    # >    ('SysTick',
                    # >        ('LOAD',
                    # >            ('RELOAD', 'SYSTICK_RELOAD', 1, (1 << 24) - 1),
                    # >        ),
                    # >    )
                    # >

                    case (field, key, minimum, maximum):

                        items += [(key, SystemDatabaseMinMax(
                            peripheral  = peripheral,
                            register    = register,
                            field       = field,
                            minimum     = minimum,
                            maximum     = maximum,
                        ))]



                    # Unsupported location format.

                    case unknown:

                        raise ValueError(
                            f'Database location entry is '
                            f'in an unknown format: {repr(unknown)}.'
                        )



    # TODO Should we allow for redundant locations?

    if duplicate_keys := [
        key
        for key, count in collections.Counter(
            key for key, entry in items
        ).items()
        if count >= 2
    ]:

        duplicate_key, *_ = duplicate_keys

        raise ValueError(
            f'For {mcu}, there is already a database '
            f'entry with the key {repr(duplicate_key)}.'
        )



    system_database[mcu] = dict(items)



################################################################################



# TODO Stale?
# The microcontroller database contains information found in reference manuals
# and datasheets. The point of the database is to make it easy to port common
# code between multiple microcontrollers without having to worry about the exact
# naming conventions and specified values of each register / hardware properties.
#
# For instance, STM32 microcontrollers typically have a PLL unit to generate bus
# frequencies for other parts of the MCU to use. How many PLL units and channels,
# what the exact range of multipliers and dividers are, and so on would all be
# described in the database file (as found in <./deps/mcu/{MCU}_database.py>).
#
# This in turns makes the logic that needs to brute-force the PLL units for the
# clock-tree be overlapped with other microcontrollers. There will always be
# some slight differences that the database can't account for, like whether or
# not each PLL unit has its own clock source or they all share the same one,
# but this layer of abstraction helps a lot with reducing the code duplication.
#
# The database is just defined as a Python expression in a file that we then
# evaluate; we do a small amount of post-processing so it's more usable, but
# overall it's really not that complicated.
#
# The database is not at all comprehensive. When working with low-level system
# stuff and trying to automate things with meta-directives, you might find
# yourself seeing that there's missing entries in the database. This is expected;
# just add more registers and stuff to the database whenever needed. The syntax
# of the database expression should be pretty straight-forward to figure out.
