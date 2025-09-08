import types, csv
from ..stpy.database import system_database
from ..pxd.utils     import root, mk_dict, OrderedSet, find_dupe

# We create a table to map GPIO pin and alternate
# function names to alternate function codes.
# e.g:
# >
# >    ('A', 0, 'UART4_TX')   ->   0b1000
# >

GPIO_AFSEL = {}

for mcu in system_database:

    GPIO_AFSEL[mcu] = []



    # Find the CSV file that STM32CubeMX can provide to
    # get all of the alternate functions for GPIOs.

    gpio_afsel_file_path = root(f'./deps/stpy/mcu/{mcu}.csv')



    # Process the CSV file.

    for entry in csv.DictReader(
        gpio_afsel_file_path.read_text().splitlines()
    ):

        match entry['Type']:



            # Most GPIOs we care about are the I/O ones.

            case 'I/O':

                # Some GPIO names are suffixed with
                # additional things, like for instance:
                #
                #     PC14-OSC32_IN(OSC32_IN)
                #     PH1-OSC_OUT(PH1)
                #     PA14(JTCK/SWCLK)
                #     PC2_C
                #
                # So we need to format it slightly so that
                # we just get the port letter and pin number.

                pin    = entry['Name']
                pin    = pin.split('-', 1)[0]
                pin    = pin.split('(', 1)[0]
                pin    = pin.split('_', 1)[0]
                port   = pin[1]
                number = int(pin[2:])

                assert pin.startswith('P') and ('A' <= port <= 'Z')



                # Gather all the alternate functions of the GPIO, if any.

                for afsel_code in range(16):



                    # Skip empty cells.

                    if not entry[f'AF{afsel_code}']:
                        continue



                    # Some have multiple names for the
                    # same AFSEL code (e.g. "I2S3_CK/SPI3_SCK").

                    GPIO_AFSEL[mcu] += [
                        ((port, number, afsel_name), afsel_code)
                        for afsel_name in entry[f'AF{afsel_code}'].split('/')
                    ]




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



    # Done processing the CSV file;
    # now we have a mapping of GPIO pin
    # and alternate function name to the
    # alternate function code.

    GPIO_AFSEL[mcu] = mk_dict(GPIO_AFSEL[mcu])



# The routine to create a single GPIO instance.

def mk_gpio(target, entry):

    name, pin, mode, properties = entry



    # The layout of a GPIO instance.

    gpio = types.SimpleNamespace(
        name       = name,
        pin        = pin,
        mode       = mode,
        port       = None,
        number     = None,
        speed      = None,
        pull       = None,
        open_drain = None,
        initlvl    = None,
        altfunc    = None,
        afsel      = None,
    )



    # If the pin of the GPIO is given, split it into
    # its port and number parts (e.g. 'A10' -> ('A', 10)).
    # The pin can be left unspecified as `None`, which is
    # useful for when we don't know where the pin will be
    # end up being at but we want to at least have it still
    # be in the table.

    if pin is not None:
        gpio.port   = pin[0]
        gpio.number = int(pin[1:])



    # Handle the GPIO mode.

    match mode:



        # A simple input GPIO to read digital voltage levels.

        case 'INPUT':



            # The pull-direction must be specified in order to
            # prevent accidentally defining a floating GPIO pin.

            gpio.pull = properties.pop('pull')



        # A simple output GPIO that can be driven low or high.

        case 'OUTPUT':



            # The initial voltage level must be specified
            # so the user remembers to take it into consideration.

            gpio.initlvl = properties.pop('initlvl')



            # Other optional properties.

            gpio.speed      = properties.pop('speed'     , None)
            gpio.open_drain = properties.pop('open_drain', None)




        # This GPIO would typically be used for some
        # peripheral functionality (e.g. SPI clock output).

        case 'ALTERNATE':



            # Alternate GPIOs are denoted by a string like "UART8_TX"
            # to indicate its alternate function.

            gpio.altfunc = properties.pop('altfunc')



            # Other optional properties.

            gpio.speed      = properties.pop('speed'     , None)
            gpio.pull       = properties.pop('pull'      , None)
            gpio.open_drain = properties.pop('open_drain', None)



        # An analog GPIO would have its Schmit trigger function
        # disabled; this obviously allows for ADC/DAC usage,
        # but it can also serve as a power-saving measure.

        case 'ANALOG':
            raise NotImplementedError



        # A GPIO that's marked as "RESERVED" is often useful
        # for marking a particular pin as something that
        # shouldn't be used because it has an important
        # functionality (e.g. JTAG debug).
        # We ignore any properties the reserved pin may have.

        case 'RESERVED':
            properties = {}



        # Unknown GPIO mode.

        case unknown:
            raise ValueError(
                f'GPIO "{name}" has unknown '
                f'mode: {repr(unknown)}.'
            )



    # Determine the GPIO's alternate function code.

    if gpio.pin is not None and gpio.altfunc is not None:

        gpio.afsel = GPIO_AFSEL[target.mcu].get(
            (gpio.port, gpio.number, gpio.altfunc),
            None
        )

        if gpio.afsel is None:
            raise ValueError(
                f'GPIO pin {repr(gpio.pin)} '
                f'for {target.mcu} ({target.name}) '
                f'has no alternate function {repr(gpio.altfunc)}.'
            )



    # Done processing this GPIO entry!

    if properties:
        raise ValueError(
            f'GPIO "{name}" has leftover properties: {properties}.'
        )

    return gpio



# The routine to ensure the list of GPIOs make sense for the target.

def PROCESS_GPIOS(target):

    gpios = tuple(
        mk_gpio(target, entry)
        for entry in target.gpios
    )

    if (name := find_dupe(
        gpio.name
        for gpio in gpios
    )) is not ...:
        raise ValueError(
            f'GPIO name {repr(name)} used more than once.'
        )

    if (pin := find_dupe(
        gpio.pin
        for gpio in gpios
        if gpio.pin is not None
    )) is not ...:
        raise ValueError(
            f'GPIO pin {repr(pin)} used more than once.'
        )

    return gpios
