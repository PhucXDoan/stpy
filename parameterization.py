import copy, types, collections
from ..stpy.database import system_database, TBD, Mapping, GPIO_ALTERNATE_FUNCTION_CODES



def get_similars(given, options): # TODO Copy-pasta.

    import difflib

    return difflib.get_close_matches(
        str(given),
        [str(option) for option in options],
        n      = 3,
        cutoff = 0
    )



class Parameterization:



    ################################################################################
    #
    # For easy print-debugging.
    # TODO Improve.
    #



    def __str__(self):
        output = '\n'
        for key, entry in self.database.items():
            output += f'{key :<40} | {str(entry.category) :<12} | {entry.value if entry.can_hold_value else ''}\n'
        output += '\n'
        return output



    ################################################################################
    #
    # Shorthand to allow for updating values in the target's database.
    #



    def __setitem__(self, key, value):



        # Ensure the key exists.

        if key not in self.database:

            raise RuntimeError(
                f'No key {repr(key)} exists in the database for target '
                f'{repr(self.target.name)} ({repr(self.target.mcu)}); '
                f'close matches: {repr(get_similars(key, self.database.keys()))}.'
            )



        # Ensure the key is meant to be parameterized.

        if not self.database[key].can_hold_value:

            raise RuntimeError(
                f'Attempting to write to unparameterizable '
                f'key {repr(key)} for target '
                f'{repr(self.target.name)} ({repr(self.target.mcu)}).'
            )



        # Ensure the key's value can be changed.

        if self.database[key].pinned:

            raise RuntimeError(
                f'Attempting to write to pinned '
                f'key {repr(key)} for target '
                f'{repr(self.target.name)} ({repr(self.target.mcu)}).'
            )



        # Ensure the new value fits the entry's constraint.

        if (
            self.database[key].constraint is not None and
            not self.database[key].constraint.check(value)
        ):
            raise RuntimeError(
                f'For target {repr(self.target.name)} ({repr(self.target.mcu)}), '
                f'the key {repr(key)} was written with value {repr(value)}, '
                f'but this does not satisfy the constraint: '
                f'{self.database[key].constraint.show()}.'
            )



        # Alright, update the value!

        self.database[key].value = value



    ################################################################################
    #
    # Shorthand to index for the value of a datbase entry.
    # We are not using `__getitem__` here because there can
    # be a default, and this also has the additional benefit
    # of being easier to search for whenever we need to find
    # where accesses to the database is done.
    #



    def __call__(self, key, *default):



        # Get the database entry.

        if key in self.database:

            if not self.database[key].can_hold_value:

                raise RuntimeError(
                    f'Attempting to read key {repr(key)} which '
                    f'is not associated with a value for target '
                    f'{repr(self.target.name)} ({repr(self.target.mcu)}).'
                )

            return self.database[key].value



        # Fallback to a default value.

        elif default:

            default, = default
            return default



        # Missing database entry!

        else:
            raise RuntimeError(
                f'No key {repr(key)} exists in the database for target '
                f'{repr(self.target.name)} ({repr(self.target.mcu)}); '
                f'close matches: {repr(get_similars(key, self.database.keys()))}.'
            )



    ################################################################################
    #
    # Algorithm to brute-force the parameterization of the target.
    #



    def __init__(self, target):

        self.target   = target
        self.database = copy.deepcopy(system_database[self.target.mcu])



        # The target specifies part of the parameterization
        # that we then figure out the rest automatically.

        for key, value in self.target.clock_tree.items():

            self[key]                 = value
            self.database[key].pinned = True



        # Routine to ensure the parameterization is not in a conflicting state.

        def sanity_check():

            for key, entry in self.database.items():

                if entry.constraint is None:
                    continue

                if entry.value is TBD:
                    continue

                if not entry.constraint.check(entry.value):
                    raise RuntimeError(
                        f'For target {repr(self.target.name)} ({repr(self.target.mcu)}), '
                        f'key {repr(key)} has value {repr(entry.value)} '
                        f'which does not satisfy the constraint: {entry.constraint.show()}.'
                    )

        sanity_check()



        # Decorater to indicate the entry-point
        # to when we are starting to brute-force.

        def bruteforce(function):

            success = function()

            if not success:
                raise RuntimeError(
                    f'Failed to brute-force {repr(function.__name__)} '
                    f'for target {repr(self.target.name)}.'
                )



        # Shorthand to update the value of a database entry
        # by iterating over all the possible valid values
        # it can be.

        def each(key):

            for self[key] in self.database[key].constraint.iterate():

                yield self(key)



        # Shorthand to update the value of a database
        # entry if it satisfies the constraint.
        # As of now, the constraint is something
        # simple that we can check the membership of;
        # things like tuples, dictionaries, or ranges.

        def checkout(key, value):

            ok = self.database[key].constraint.check(value)

            if ok:
                self[key] = value

            return ok



        ################################################################################
        #
        # Flash and Internal Voltage.
        #
        # TODO The settings should be dependent upon the AXI frequency,
        #      but for simplicity right now, we're using the max flash
        #      delay and highest voltage scaling. This means flash will
        #      probably be slower than needed and more power might be
        #      used unnecessarily.
        #



        match self.target.mcu:



            # @/pg 211/tbl 29/`H7S3rm`.
            # @/pg 327/sec 6.8.6/`H7S3rm`.

            case 'STM32H7S3L8H6':
                self['FLASH_LATENCY'           ] = '0x7'
                self['FLASH_PROGRAMMING_DELAY' ] = '0b11'
                self['INTERNAL_VOLTAGE_SCALING'] = 'high'



            # @/pg 252/tbl 45/`H533rm`.
            # @/pg 438/sec 10.11.4/`H533rm`.

            case 'STM32H533RET6':
                self['FLASH_LATENCY'           ] = 5
                self['FLASH_PROGRAMMING_DELAY' ] = '0b10'
                self['INTERNAL_VOLTAGE_SCALING'] = 'VOS0'



            case _: raise NotImplementedError



        ################################################################################
        #
        # Power-Supply Setup.
        #
        # TODO We currently only support a system power supply
        #      configuration of LDO. This isn't as power-efficient
        #      as compared to using the SMPS, for instance, but
        #      it's the simplest.
        #



        match self.target.mcu:



            # @/pg 285/fig 21/`H7S3rm`.
            # @/pg 286/tbl 44/`H7S3rm`.

            case 'STM32H7S3L8H6':
                self['SMPS_ENABLE'            ] = False
                self['LDO_ENABLE'             ] = True
                self['POWER_MANAGEMENT_BYPASS'] = False



            # @/pg 407/fig 42/`H533rm`.
            # Note that the SMPS is not available. @/pg 402/sec 10.2/`H533rm`.

            case 'STM32H533RET6':
                self['LDO_ENABLE'             ] = True
                self['POWER_MANAGEMENT_BYPASS'] = False



            case _: raise NotImplementedError



        ################################################################################
        #
        # General High-Speed-Internal Oscillator.
        # @/pg 361/sec 7.5.2/`H7S3rm`.
        # @/pg 458/sec 11.4.2/`H533rm`.
        # TODO Handle other frequencies.
        #



        self['HSI_CK'] = (
            self('HSI_DEFAULT_FREQUENCY')
            if self('HSI_ENABLE')
            else 0
        )



        ################################################################################
        #
        # High-Speed-Internal Oscillator (48MHz).
        # @/pg 363/sec 7.5.2/`H7S3rm`.
        # @/pg 460/sec 11.4.4/`H533rm`.
        #



        self['HSI48_CK'] = (
            48_000_000
            if self('HSI48_ENABLE')
            else 0
        )



        ################################################################################
        #
        # "Clock Security System" Oscillator (fixed at ~4MHz).
        # @/pg 362/sec 7.5.2/`H7S3rm`.
        # @/pg 459/sec 11.4.3/`H533rm`.
        #



        self['CSI_CK'] = (
            4_000_000
            if self('CSI_ENABLE')
            else 0
        )



        ################################################################################
        #
        # Peripheral Clock Source.
        # TODO Automate.
        #



        if self('PERIPHERAL_CLOCK_OPTION') is not TBD:

            self['PER_CK'] = self(self('PERIPHERAL_CLOCK_OPTION'))



        ################################################################################
        #
        # PLLs.
        #
        # @/pg 371/fig 48/`H7S3rm`.
        # @/pg 354/fig 40/`H7S3rm`.
        # @/pg 461/fig 55/`H533rm`.
        # @/pg 456/fig 52/`H533rm`.
        #



        def each_vco_frequency(unit, kernel_frequency):

            for predivider in each(f'PLL{unit}_PREDIVIDER'):

                input_frequency = kernel_frequency / predivider



                # Determine the range of the PLL input frequency.

                for lower, upper in each(f'PLL{unit}_INPUT_RANGE'):
                    if lower <= input_frequency < upper:
                        break
                else:
                    continue



                # Try every available multiplier that the PLL can handle.

                for multiplier in each(f'PLL{unit}_MULTIPLIER'):

                    if checkout(
                        f'PLL{unit}_VCO_FREQ',
                        input_frequency * multiplier
                    ):
                        yield



        #
        #
        #



        def parameterize_pll(unit, channels, kernel_frequency):



            used_channels = [
                channel
                for channel in channels
                if self(f'PLL{unit}{channel}_CK') is not TBD
            ]

            if not used_channels:
                return True



            self[f'PLL{unit}_ENABLE'] = True

            for _ in each_vco_frequency(unit, kernel_frequency):

                every_channel_satisfied = all(
                    checkout(
                        f'PLL{unit}{channel}_DIVIDER',
                        self(f'PLL{unit}_VCO_FREQ') / self(f'PLL{unit}{channel}_CK')
                    )
                    for channel in used_channels
                )

                if every_channel_satisfied:
                    return True



        #
        #
        #



        @bruteforce
        def parameterize_plls():

            match self.target.mcu:



                # All of the PLL units share the same kernel clock source.

                case 'STM32H7S3L8H6':

                    return any(
                        all(
                            parameterize_pll(unit, channels, self(kernel_source))
                            for unit, channels in self('PLLS')
                        )
                        for kernel_source in each('PLL_KERNEL_SOURCE')
                    )



                # Each PLL unit have their own clock source.

                case 'STM32H533RET6':

                    return all(
                        any(
                            parameterize_pll(unit, channels, self(kernel_source))
                            for kernel_source in each(f'PLL{unit}_KERNEL_SOURCE')
                        )
                        for unit, channels in self('PLLS')
                    )



                case _: raise NotImplementedError



        ################################################################################
        #
        # System Clock Generation Unit.
        #
        # @/pg 378/fig 51/`H7S3rm`.
        #



        @bruteforce
        def parameterize_scgu():

            for kernel_source in each('SCGU_KERNEL_SOURCE'):

                kernel_frequency = self(kernel_source)

                if kernel_frequency is TBD:
                    continue


                # CPU.

                if not checkout(
                    'CPU_DIVIDER',
                     kernel_frequency / self('CPU_CK')
                ):
                    continue



                # AXI/AHB busses.

                match self.target.mcu:



                    # There's a divider to configure.

                    case 'STM32H7S3L8H6':

                        if not checkout(
                            'AXI_AHB_DIVIDER',
                            self('CPU_CK') / self('AXI_AHB_CK')
                        ):
                            continue



                    # The CPU and AXI/AHB bus are directly connected.

                    case 'STM32H533RET6':

                        self['AXI_AHB_CK'] = self('CPU_CK')



                    case _: raise NotImplementedError



                # APB busses.

                every_apb_satisfied = all(
                    checkout(
                        f'APB{unit}_DIVIDER',
                        self('AXI_AHB_CK') / self(f'APB{unit}_CK')
                    )
                    for unit in self('APBS')
                )

                if not every_apb_satisfied:
                    continue



                return True



        ################################################################################
        #
        # SysTick.
        #
        # @/pg 620/sec B3.3/`Armv7-M`.
        # @/pg 297/sec B11.1/`Armv8-M`.
        #



        @bruteforce
        def parameterize_systick():



            # See if SysTick is even used.

            if self('SYSTICK_CK') is TBD:
                return True

            self['SYSTICK_ENABLE'] = True



            # Try different clock sources.

            for _ in each('SYSTICK_USE_CPU_CK'):



                # SysTick will use the CPU's frequency.
                # @/pg 621/sec B3.3.3/`Armv7-M`.
                # @/pg 1859/sec D1.2.238/`Armv8-M`.

                if self('SYSTICK_USE_CPU_CK'):

                    kernel_frequencies = [
                        self('CPU_CK')
                    ]



                # SysTick will use an implementation-defined clock source.

                else:

                    match self.target.mcu:



                        # @/pg 378/fig 51/`H7S3rm`.

                        case 'STM32H7S3L8H6':

                            kernel_frequencies = [
                                self('CPU_CK') / 8
                            ]



                        # @/pg 456/fig 52/`H533rm`.

                        case 'STM32H533RET6':

                            kernel_frequencies = [
                                # TODO.
                            ]



                        case _: raise NotImplementedError



                # Try out the different kernel frequencies and see what sticks.

                for self['SYSTICK_KERNEL_FREQ'] in kernel_frequencies:

                    if checkout(
                        'SYSTICK_RELOAD',
                        self('SYSTICK_KERNEL_FREQ') / self('SYSTICK_CK') - 1
                    ):
                        return True



        ################################################################################
        #
        # UXARTs.
        # TODO Consider maximum kernel frequency.
        #



        for instances in self('UXARTS', ()):

            @bruteforce
            def parameterize_uxarts():



                # Check if any of the instances are even used.

                used_instances = [
                    (peripheral, unit)
                    for peripheral, unit in instances
                    if self(f'{peripheral}{unit}_BAUD') is not TBD
                ]

                if not used_instances:
                    return True



                # Try every available clock source for this
                # set of instances and see what sticks.

                for kernel_source in each(f'UXART_{instances}_KERNEL_SOURCE'):

                    every_instance_satisfied = all(
                        checkout(
                            f'{peripheral}{unit}_BAUD_DIVIDER',
                            self(kernel_source) / self(f'{peripheral}{unit}_BAUD')
                        )
                        for peripheral, unit in used_instances
                    )

                    if every_instance_satisfied:
                        return True



        ################################################################################
        #
        # I2Cs.
        # TODO Consider maximum kernel frequency.
        #



        for unit in self('I2CS', ()):



            @bruteforce
            def parameterize():



                # See if the unit is even used.

                needed_baud = self(f'I2C{unit}_BAUD')

                if needed_baud is TBD:
                    return True



                # We can't get an exact baud-rate for I2C (since there's a lot
                # of factors involved anyways like clock-stretching), we'll have
                # to try every single possibility and find the one with the least
                # amount of error.

                best_baud_error = None

                for kernel_source in each(f'I2C{unit}_KERNEL_SOURCE'):

                    kernel_frequency = self(kernel_source)

                    if kernel_frequency is TBD:
                        continue

                    for presc in each(f'I2C{unit}_PRESC'):



                        # Determine the SCL.

                        scl = round(kernel_frequency / (presc + 1) / needed_baud / 2)

                        if not self.database[f'I2C{unit}_SCLH'].constraint.check(scl):
                            continue

                        if not self.database[f'I2C{unit}_SCLL'].constraint.check(scl):
                            continue



                        # Determine the baud error.

                        actual_baud       = kernel_frequency / (scl * 2 * (presc + 1) + 1)
                        actual_baud_error = abs(1 - actual_baud / needed_baud)



                        # Keep the best so far.

                        if best_baud_error is None or actual_baud_error < best_baud_error:

                            best_baud_error                  = actual_baud_error
                            self[f'I2C{unit}_KERNEL_SOURCE'] = kernel_source
                            self[f'I2C{unit}_PRESC'        ] = presc
                            self[f'I2C{unit}_SCLH'         ] = scl
                            self[f'I2C{unit}_SCLL'         ] = scl



                # We are only successful if we are within tolerance.

                return best_baud_error is not None and best_baud_error <= 0.01 # TODO Ad-hoc tolerance.



        ################################################################################
        #
        # Timers.
        #



        def parameterize_timer(unit):

            needed_rate = self(f'TIM{unit}_RATE')



            # Determine the kernel frequency.

            match self.target.mcu:



                case 'STM32H533RET6':

                    apb              = self('APB_PERIPHERALS')[f'TIM{unit}']
                    apb_divider      = self(f'APB{apb}_DIVIDER')
                    multiplier       = self('GLOBAL_TIMER_PRESCALER_MULTIPLIER_TABLE')[(self('GLOBAL_TIMER_PRESCALER'), apb_divider)]
                    kernel_frequency = self(f'AXI_AHB_CK') * multiplier



                case _: raise NotImplementedError



            # Find the pair of divider and modulation values to
            # get an output frequency that's within tolerance.

            for divider in each(f'TIM{unit}_DIVIDER'):

                counter_frequency = kernel_frequency / divider



                # Determine the modulation value.

                if not checkout(
                    f'TIM{unit}_MODULATION',
                    round(counter_frequency / needed_rate)
                ):
                    continue



                # See if things are within tolerance.

                actual_rate  = counter_frequency / self(f'TIM{unit}_MODULATION')
                actual_error = abs(1 - actual_rate / needed_rate)

                if actual_error <= 0.001: # TODO Ad-hoc.
                    return True



        #
        #
        #



        @bruteforce
        def parameterize_timers():

            used_units = [
                unit
                for unit in self('TIMERS', ())
                if self(f'TIM{unit}_RATE') is not TBD
            ]

            if not used_units:
                return True

            for _ in each('GLOBAL_TIMER_PRESCALER'):

                every_unit_satisfied = all(
                    parameterize_timer(unit)
                    for unit in used_units
                )

                if every_unit_satisfied:
                    return True



        ################################################################################
        #
        # GPIOs.
        #



        def process_single_gpio(target, entry):

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



                    # Alternate GPIOs are denoted by a string like
                    # "UART8_TX" to indicate its alternate function.

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
                        f'GPIO {repr(name)} has unknown '
                        f'mode: {repr(unknown)}.'
                    )



            # Determine the GPIO's alternate function code.

            if gpio.pin is not None and gpio.altfunc is not None:

                gpio.afsel = GPIO_ALTERNATE_FUNCTION_CODES[target.mcu].get(
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
                    f'GPIO {repr(name)} has leftover properties: {properties}.'
                )

            return gpio



        self.gpios = tuple(
            process_single_gpio(target, gpio)
            for gpio in target.gpios
        )



        if duplicate_names := [
            name
            for name, count in collections.Counter(
                gpio.name for gpio in self.gpios
            ).items()
            if count >= 2
        ]:

            duplicate_name, *_ = duplicate_names

            raise ValueError(
                f'GPIO name {repr(duplicate_name)} used more than once.'
            )



        if duplicate_pins := [
            pin
            for pin, count in collections.Counter(
                gpio.pin for gpio in self.gpios
            ).items()
            if count >= 2
        ]:

            duplicate_pin, *_ = duplicate_pins

            raise ValueError(
                f'GPIO pin {repr(duplicate_pin)} used more than once.'
            )



        for port in sorted(dict.fromkeys(
            gpio.port
            for gpio in self.gpios
            if gpio.pin is not None
        )):
            self[f'GPIO{port}_ENABLE'] = True


        for gpio in self.gpios:

            if gpio.pin is None:
                continue

            if gpio.open_drain is None:
                continue

            self[f'GPIO{gpio.port}{gpio.number}_OPEN_DRAIN'] = gpio.open_drain


        for gpio in self.gpios:

            if gpio.pin is None:
                continue

            if gpio.initlvl is None:
                continue

            self[f'GPIO{gpio.port}{gpio.number}_OUTPUT'] = gpio.initlvl



        for gpio in self.gpios:

            if gpio.pin is None:
                continue

            if gpio.speed is None:
                continue

            self[f'GPIO{gpio.port}{gpio.number}_SPEED'] = gpio.speed



        for gpio in self.gpios:

            if gpio.pin is None:
                continue

            if gpio.pull is None:
                continue

            self[f'GPIO{gpio.port}{gpio.number}_PULL'] = gpio.pull



        for gpio in self.gpios:

            if gpio.afsel is None:
                continue

            self[f'GPIO{gpio.port}{gpio.number}_ALTERNATE_FUNCTION'] = gpio.afsel



        for gpio in self.gpios:

            if gpio.pin is None:
                continue

            if gpio.mode in (None, 'RESERVED'):
                continue

            self[f'GPIO{gpio.port}{gpio.number}_MODE'] = gpio.mode



        ################################################################################



        sanity_check()



        # Mapping constraints are a table of sematic names
        # to the actual underlying value to be used in the
        # generated code (e.g. the binary code).

        for key, entry in self.database.items():

            if self.database[key].mapped:
                continue

            if self.database[key].value is TBD:
                continue

            if isinstance(self.database[key].constraint, Mapping):

                entry.value  = self.database[key].constraint[entry.value]
                entry.mapped = True
