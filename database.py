import pathlib, collections



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



system_locations  = {}
system_properties = {}

for mcu in dict.fromkeys( # TODO Cleaner way to determine the MCUs?
    item.stem
    for item in pathlib.Path(__file__).parent.joinpath('mcu').iterdir()
    if item.is_file()
    if item.stem.isidentifier()
):



    # Parse the database file.

    locationless_properties, location_tree = eval(
        pathlib.Path(__file__)
            .parent
            .joinpath(f'mcu/{mcu}.py')
            .read_text(),
        {
            'RealMinMax' : RealMinMax,
            'IntMinMax'  : IntMinMax,
        },
        {},
    )



    # Organize the entries' values and locations.

    properties = list(locationless_properties)
    locations  = []

    for peripheral, *register_tree in location_tree:

        for register, *field_tree in register_tree:

            for field, key, *value in field_tree:



                # If a value field is not explicitly given,
                # we assume it's a single-bit field.
                # e.g:
                # >
                # >    ('RCC',
                # >        ('CR',
                # >            ('HSION', 'HSI_ENABLE'),
                # >        ),
                # >    ),
                # >

                if value:
                    value, = value
                else:
                    value = (False, True)



                properties += [(key, value)]
                locations  += [(key, (peripheral, register, field))]



    # Sanity checks.

    if duplicate_keys := [
        key
        for key, count in collections.Counter(
            key for key, value in properties
        ).items()
        if count >= 2
    ]:

        duplicate_key, *_ = duplicate_keys

        raise ValueError(
            f'For {mcu}, there is already a database '
            f'entry with the key {repr(duplicate_key)}.'
        )

    system_properties[mcu] = dict(properties)
    system_locations [mcu] = dict(locations )



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
