import collections, difflib
from ..stpy.database import system_properties



class Parameterization:



    ################################################################################
    #
    # We'll keep track of values that'll be calculated and
    # configurations determined during the parameterization process.
    #



    def __init__(self, target):

        self.target     = target
        self.dictionary = {
            key : ('clock-tree-unused', value)
            for key, value in target.clock_tree.items()
        }

        self.parameterize()



    ################################################################################
    #
    # Keys can be inserted with an associated category.
    #



    def __setitem__(self, category_key, value):
        category, key        = category_key
        self.dictionary[key] = (category, value)



    ################################################################################
    #
    # Indexing can be done with just the key. Thus, the
    # categories' set of keys are disjoint with each other.
    #



    def __call__(self, key):

        if key not in self.dictionary:
            raise RuntimeError(
                f'While parameterizing, no key {repr(key)} was '
                f'found for target {repr(self.target.name)}; '
                f'closest matches are: {
                    difflib.get_close_matches(
                        str(key),
                        map(str, self.dictionary.keys()),
                        n      = 3,
                        cutoff = 0
                    )
                }.'
            )

        category, value = self.dictionary[key]

        if category == 'clock-tree-unused':
            self.dictionary[key] = ('clock-tree-used', value)

        return value



    ################################################################################
    #
    # Allows for easy print-debugging.
    # TODO Improve.
    #



    def __str__(self):

        from ..pxd.utils import justify

        return '\n' + '\n'.join(
            '| {} | {} | {} |'.format(*justs)
            for justs in justify(
                (
                    ('<', key),
                    ('<', category),
                    ('>', value),
                )
                for key, (category, value) in self.dictionary.items()
            )
        ) + '\n'



    ################################################################################
    #
    # Provide a way to perform brute-forcing conveniently.
    #



    def brute(self, function):

        success = function()

        if not success:
            raise RuntimeError(
                f'Failed to brute-force {repr(function.__name__)} '
                f'for target {repr(self.target.name)}.'
            )



    ################################################################################
    #
    # Some stuff to be done after parameterization.
    #



    def done(self):



        # See if any clock-tree options were left unused.

        if unused_keys := [
            key
            for key, (category, value) in self.dictionary.items()
            if category == 'clock-tree-unused'
        ]:

            # TODO Remove?
            from ..pxd.log import log, ANSI

            log(ANSI(
                f'[WARNING] There are unused clock-tree options '
                f'for target {repr(self.target.name)}: {unused_keys}.',
                'fg_yellow'
            ))



        # TODO.

        properties = system_properties[self.target.mcu]

        for key, (category, value) in self.dictionary.items():
            if key in properties and isinstance(properties[key], dict):
                if value in properties[key]:
                    self.dictionary[key] = (category, properties[key][value])

        for key, (category, value) in self.dictionary.items():
            if isinstance(value, float) and value.is_integer():
                self.dictionary[key] = (category, int(value))



    ################################################################################
    #
    # The algorithm to brute-force the MCU's clock-tree.
    #



    def parameterize(self):



        properties = system_properties[self.target.mcu]



        self['frequency', None] = 0 # No clock source, no frequency.



        ################################################################################
        #
        # Flash and internal voltage.
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
                self['settings', 'FLASH_LATENCY'           ] = '0x7'
                self['settings', 'FLASH_PROGRAMMING_DELAY' ] = '0b11'
                self['settings', 'INTERNAL_VOLTAGE_SCALING'] = 'high'



            # @/pg 252/tbl 45/`H533rm`.
            # @/pg 438/sec 10.11.4/`H533rm`.

            case 'STM32H533RET6':
                self['settings', 'FLASH_LATENCY'           ] = 5
                self['settings', 'FLASH_PROGRAMMING_DELAY' ] = '0b10'
                self['settings', 'INTERNAL_VOLTAGE_SCALING'] = 'VOS0'



            case _: raise NotImplementedError



        ################################################################################
        #
        # Power-supply setup.
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
                self['settings', 'SMPS_OUTPUT_LEVEL'      ] = None
                self['settings', 'SMPS_FORCED_ON'         ] = None
                self['settings', 'SMPS_ENABLE'            ] = False
                self['settings', 'LDO_ENABLE'             ] = True
                self['settings', 'POWER_MANAGEMENT_BYPASS'] = False



            # @/pg 407/fig 42/`H533rm`.
            # Note that the SMPS is not available. @/pg 402/sec 10.2/`H533rm`.

            case 'STM32H533RET6':
                self['settings', 'LDO_ENABLE'             ] = True
                self['settings', 'POWER_MANAGEMENT_BYPASS'] = False



            case _: raise NotImplementedError



        ################################################################################
        #
        # General high-speed-internal oscillator.
        # @/pg 361/sec 7.5.2/`H7S3rm`.
        # @/pg 458/sec 11.4.2/`H533rm`.
        # TODO Handle other frequencies.
        #



        self['frequency', 'HSI_CK'] = (
            properties['HSI_DEFAULT_FREQUENCY']
            if self('HSI_ENABLE')
            else 0
        )



        ################################################################################
        #
        # High-speed-internal oscillator (48MHz).
        # @/pg 363/sec 7.5.2/`H7S3rm`.
        # @/pg 460/sec 11.4.4/`H533rm`.
        #



        self['frequency', 'HSI48_CK'] = (
            48_000_000
            if self('HSI48_ENABLE')
            else 0
        )



        ################################################################################
        #
        # "Clock Security System" oscillator (fixed at ~4MHz).
        # @/pg 362/sec 7.5.2/`H7S3rm`.
        # @/pg 459/sec 11.4.3/`H533rm`.
        #



        self['frequency', 'CSI_CK'] = (
            4_000_000
            if self('CSI_ENABLE')
            else 0
        )



        ################################################################################
        #
        # TODO Not implemented yet.
        #



        self['frequency', 'HSE_CK'] = 0
        self['frequency', 'LSE_CK'] = 0



        ################################################################################
        #
        # Peripheral clock.
        # TODO Automate.
        #



        self['frequency', 'PER_CK'] = self(self('PERIPHERAL_CLOCK_OPTION'))



        ################################################################################
        #
        # PLLs.
        #
        # @/pg 371/fig 48/`H7S3rm`.
        # @/pg 354/fig 40/`H7S3rm`.
        # @/pg 461/fig 55/`H533rm`.
        # @/pg 456/fig 52/`H533rm`.
        #



        # TODO Better way to do asserts?

        for unit, channels in properties['PLLS']:

            for channel in channels:

                goal_frequency = self(f'PLL{unit}_{channel}_CK')

                if goal_frequency is None:
                    continue

                if goal_frequency not in properties['PLL_CHANNEL_FREQ']:
                    raise ValueError(
                        f'PLL{unit}_{channel}_CK frequency is '
                        f'out of range: {goal_frequency :_}Hz.'
                    )



        #
        #
        #



        def each_vco_frequency(unit, kernel_frequency):

            for self['settings', f'PLL{unit}_PREDIVIDER'] in properties[f'PLL{unit}_PREDIVIDER']:



                # Determine the range of the PLL input frequency.

                reference_frequency = kernel_frequency / self(f'PLL{unit}_PREDIVIDER')

                for lower, upper in properties[f'PLL{unit}_INPUT_RANGE']:
                    if lower <= reference_frequency < upper:
                        break
                else:
                    continue

                self['settings', f'PLL{unit}_INPUT_RANGE'] = (lower, upper)



                # Try every available multiplier that the PLL can handle.

                for self['settings', f'PLL{unit}_MULTIPLIER'] in properties[f'PLL{unit}_MULTIPLIER']:

                    vco_frequency = reference_frequency * self(f'PLL{unit}_MULTIPLIER')

                    if vco_frequency not in properties['PLL_VCO_FREQ']:
                        continue

                    yield vco_frequency



        #
        #
        #



        def parameterize_channel(unit, vco_frequency, channel):



            # See if the PLL channel is even used.

            goal_frequency = self(f'PLL{unit}_{channel}_CK')

            if goal_frequency is None:
                return True



            # Find the channel divider.

            needed_divider = vco_frequency / goal_frequency

            if needed_divider not in properties[f'PLL{unit}{channel}_DIVIDER']:
                return False

            self['settings', f'PLL{unit}_{channel}_DIVIDER'] = needed_divider

            return True



        #
        #
        #



        def parameterize_pll(unit, kernel_frequency):

            channels = dict(properties['PLLS'])[unit]



            # TODO Unnecessary.

            self['settings', f'PLL{unit}_PREDIVIDER' ] = None
            self['settings', f'PLL{unit}_INPUT_RANGE'] = None
            self['settings', f'PLL{unit}_MULTIPLIER' ] = None
            for channel in dict(properties['PLLS'])[unit]:
                self['settings', f'PLL{unit}_{channel}_DIVIDER'] = None



            # See if the PLL unit is even used.

            self['settings', f'PLL{unit}_ENABLE'] = any(
                self(f'PLL{unit}_{channel}_CK') is not None
                for channel in channels
            )

            if not self(f'PLL{unit}_ENABLE'):
                return True



            # Parameterize each channel.

            for vco_frequency in each_vco_frequency(unit, kernel_frequency):

                every_channel_satisfied = all(
                    parameterize_channel(unit, vco_frequency, channel)
                    for channel in channels
                )

                if every_channel_satisfied:
                    return True



        #
        #
        #



        @self.brute
        def parameterize_plls():

            match self.target.mcu:



                # All of the PLL units share the same kernel clock source.

                case 'STM32H7S3L8H6':

                    return any(
                        all(
                            parameterize_pll(unit, self(self('PLL_KERNEL_SOURCE')))
                            for unit, channels in properties['PLLS']
                        )
                        for self['settings', 'PLL_KERNEL_SOURCE'] in properties['PLL_KERNEL_SOURCE']
                    )



                # Each PLL unit have their own clock source.

                case 'STM32H533RET6':

                    return all(
                        any(
                            parameterize_pll(unit, self(self(f'PLL{unit}_KERNEL_SOURCE')))
                            for self['settings', f'PLL{unit}_KERNEL_SOURCE'] in properties[f'PLL{unit}_KERNEL_SOURCE']
                        )
                        for unit, channels in properties['PLLS']
                    )



                case _: raise NotImplementedError



        ################################################################################
        #
        # System Clock Generation Unit.
        #
        # @/pg 378/fig 51/`H7S3rm`.
        #



        # TODO Better way to do asserts?

        if self('CPU_CK') not in properties['CPU_FREQ']:
            raise ValueError(
                f'CPU_CK is out of range: '
                f'{self('CPU_CK') :_}Hz.'
            )

        for unit in properties['APBS']:
            if self(f'APB{unit}_CK') not in properties['APB_FREQ']:
                raise ValueError(
                    f'APB{unit}_CK is out of range: '
                    f'{self(f'APB{unit}_CK') :_}Hz.'
                )

        match self.target.mcu:

            case 'STM32H7S3L8H6':

                if self('AXI_AHB_CK') not in properties['AXI_AHB_FREQ']:
                    raise ValueError(
                        f'AXI_AHB_CK is out-of-range: '
                        f'{self('AXI_AHB_CK') :_}Hz.'
                    )



        #
        #
        #



        @self.brute
        def parameterize_scgu():

            for self['settings', 'SCGU_KERNEL_SOURCE'] in properties['SCGU_KERNEL_SOURCE']:



                # CPU.

                self['settings', 'CPU_DIVIDER'] = self(self('SCGU_KERNEL_SOURCE')) / self('CPU_CK')

                if self('CPU_DIVIDER') not in properties['CPU_DIVIDER']:
                    continue



                # AXI/AHB busses.

                match self.target.mcu:



                    # There's a divider to configure.

                    case 'STM32H7S3L8H6':

                        self['settings', 'AXI_AHB_DIVIDER'] = self('CPU_CK') / self('AXI_AHB_CK')

                        if self('AXI_AHB_DIVIDER') not in properties['AXI_AHB_DIVIDER']:
                            continue



                    # The CPU and AXI/AHB bus are directly connected.

                    case 'STM32H533RET6':

                        self['frequency', 'AXI_AHB_CK'] = self('CPU_CK')



                    case _: raise NotImplementedError



                # Each APB bus.

                def parameterize_apb(unit):
                    self['settings', f'APB{unit}_DIVIDER'] = self('AXI_AHB_CK') / self(f'APB{unit}_CK')
                    return self(f'APB{unit}_DIVIDER') in properties[f'APB{unit}_DIVIDER']

                every_apb_satisfied = all(
                    parameterize_apb(unit)
                    for unit in properties['APBS']
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



        # TODO Better way to do asserts?

        if self('SYSTICK_CK') is not None and self.target.use_freertos:
            raise ValueError(
                f'FreeRTOS already uses SysTick for the time-base; '
                f'so for target {repr(self.target.name)}, '
                f'either remove "SYSTICK_CK" from the clock-tree '
                f'configuration or disable FreeRTOS.'
            )



        #
        #
        #



        @self.brute
        def parameterize_systick():



            # See if SysTick is even used.

            self['settings', 'SYSTICK_ENABLE'] = self('SYSTICK_CK') is not None

            if not self('SYSTICK_ENABLE'):
                return True



            # Try different clock sources.

            for self['settings', 'SYSTICK_USE_CPU_CK'] in properties['SYSTICK_USE_CPU_CK']:



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

                for self['frequency', 'SYSTICK_KERNEL_FREQ'] in kernel_frequencies:

                    self['settings', 'SYSTICK_RELOAD'] = self('SYSTICK_KERNEL_FREQ') / self('SYSTICK_CK') - 1

                    if self('SYSTICK_RELOAD') in properties['SYSTICK_RELOAD']:
                        return True



        ################################################################################
        #
        # UXARTs.
        # TODO Consider maximum kernel frequency.
        #



        # Some UXART peripherals are tied together in hardware where
        # they would all share the same clock source. Each can still
        # have a different baud rate by changing their respective
        # baud-rate divider, but nonetheless, we must process each set
        # of connected UXART peripherals as a whole.

        for instances in properties.get('UXARTS', ()):



            #
            #
            #



            def parameterize_uxart(instance, kernel_frequency):

                peripheral, unit = instance



                # See if this instance is even needed.

                needed_baud = self(f'{peripheral}{unit}_BAUD')

                if needed_baud is None:
                    return True



                # Check if the needed divider is valid.

                needed_divider = kernel_frequency / needed_baud

                if not needed_divider.is_integer():
                    return False

                needed_divider = int(needed_divider)

                if needed_divider not in properties['UXART_BAUD_DIVIDER']:
                    return False



                # We found the desired divider!

                self['settings', f'{peripheral}{unit}_BAUD_DIVIDER'] = needed_divider

                return True



            #
            #
            #



            @self.brute
            def parameterize_uxarts():



                # TODO Unnecessary.

                self['settings', f'UXART_{instances}_KERNEL_SOURCE'] = None
                for instance in instances:
                    self['settings', f'{instance[0]}{instance[1]}_BAUD_DIVIDER'] = None



                # Check if any of the instances are even used.

                using_instances = any(
                    self(f'{peripheral}{unit}_BAUD') is not None
                    for peripheral, unit in instances
                )

                if not using_instances:
                    return True



                # Try every available clock source for this
                # set of instances and see what sticks.

                for self['settings', f'UXART_{instances}_KERNEL_SOURCE'] in properties[f'UXART_{instances}_KERNEL_SOURCE']:

                    every_instance_satisfied = all(
                        parameterize_uxart(instance, self(self(f'UXART_{instances}_KERNEL_SOURCE')))
                        for instance in instances
                    )

                    if every_instance_satisfied:
                        return True



        ################################################################################
        #
        # I2Cs.
        # TODO Consider maximum kernel frequency.
        #



        for unit in properties.get('I2CS', ()):



            @self.brute
            def parameterize():



                # TODO Unnecessary.

                self['settings', f'I2C{unit}_KERNEL_SOURCE'] = None



                # See if the unit is even used.

                needed_baud = self(f'I2C{unit}_BAUD')

                if needed_baud is None:
                    return True



                # We can't get an exact baud-rate for I2C (since there's a lot
                # of factors involved anyways like clock-stretching), we'll have
                # to try every single possibility and find the one with the least
                # amount of error.

                best_baud_error = None

                for kernel_source in properties[f'I2C{unit}_KERNEL_SOURCE']:

                    kernel_frequency = self(kernel_source) or 0

                    for presc in properties['I2C_PRESC']:



                        # Determine the SCL.

                        scl = round(kernel_frequency / (presc + 1) / needed_baud / 2)

                        if scl not in properties['I2C_SCLH']:
                            continue

                        if scl not in properties['I2C_SCLL']:
                            continue



                        # Determine the baud error.

                        actual_baud       = kernel_frequency / (scl * 2 * (presc + 1) + 1)
                        actual_baud_error = abs(1 - actual_baud / needed_baud)



                        # Keep the best so far.

                        if best_baud_error is None or actual_baud_error < best_baud_error:

                            best_baud_error                                = actual_baud_error
                            self['settings', f'I2C{unit}_KERNEL_SOURCE'] = kernel_source
                            self['settings', f'I2C{unit}_PRESC'        ] = presc
                            self['settings', f'I2C{unit}_SCL'          ] = scl



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

                    apb         = properties['APB_PERIPHERALS'][f'TIM{unit}']
                    apb_divider = self(f'APB{apb}_DIVIDER')
                    multiplier  = properties['GLOBAL_TIMER_PRESCALER_MULTIPLIER_TABLE'][(self('GLOBAL_TIMER_PRESCALER'), apb_divider)]

                    kernel_frequency = self(f'AXI_AHB_CK') * multiplier



                case _: raise NotImplementedError



            # Find the pair of divider and modulation values to
            # get an output frequency that's within tolerance.

            for self['settings', f'TIM{unit}_DIVIDER'] in properties[f'TIM{unit}_DIVIDER']:

                counter_frequency = kernel_frequency / self(f'TIM{unit}_DIVIDER')



                # Determine the modulation value.

                self['settings', f'TIM{unit}_MODULATION'] = (
                    min(
                        max(
                            round(counter_frequency / needed_rate),
                            properties[f'TIM{unit}_MODULATION'].minimum
                        ),
                        properties[f'TIM{unit}_MODULATION'].maximum
                    )
                )



                # See if things are within tolerance.

                actual_rate  = counter_frequency / self(f'TIM{unit}_MODULATION')
                actual_error = abs(1 - actual_rate / needed_rate)

                if actual_error <= 0.001: # TODO Ad-hoc.
                    return True



        #
        #
        #



        @self.brute
        def parameterize_timers():

            used_units = [
                unit
                for unit in properties.get('TIMERS', ())
                if self(f'TIM{unit}_RATE') is not None
            ]

            if not used_units:
                return True

            for self['settings', 'GLOBAL_TIMER_PRESCALER'] in properties['GLOBAL_TIMER_PRESCALER']:

                every_unit_satisfied = all(
                    parameterize_timer(unit)
                    for unit in used_units
                )

                if every_unit_satisfied:
                    return True



        ################################################################################



        self.done()
