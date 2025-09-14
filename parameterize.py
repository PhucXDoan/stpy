import collections, difflib
from ..stpy.database import system_properties



################################################################################



class Blueprint:



    # The blueprint will keep track of values that'll be calculated
    # and determined during the parameterization process.

    def __init__(self, target):

        self.target     = target
        self.dictionary = {
            key : ('clock-tree-unused', value)
            for key, value in target.clock_tree.items()
        }



    # Keys can be added to the blueprint with an associated category.

    def __setitem__(self, category_key, value):
        category, key        = category_key
        self.dictionary[key] = (category, value)



    # Indexing into the blueprint can be done just with the key.
    # Thus, the categories' set of keys are disjoint with each other.

    def __call__(self, key):

        if key not in self.dictionary:
            raise RuntimeError(
                f'No key {repr(key)} in blueprint '
                f'for target {repr(self.target.name)}; '
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



    # Allows for easy print-debugging.
    # TODO Improve.

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



    # Provide a way to perform brute-forcing conveniently.

    def brute(self, function):

        success = function()

        if not success:
            raise RuntimeError(
                f'Failed to brute-force {repr(function.__name__)} '
                f'for target {repr(self.target.name)}.'
            )



    # Provide diagnostics.

    def done(self):

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



################################################################################



def system_parameterize(target):

    properties = system_properties[target.mcu]
    blueprint  = Blueprint(target)



    blueprint['frequency', None] = 0 # No clock source, no frequency.



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



    match target.mcu:



        # @/pg 211/tbl 29/`H7S3rm`.
        # @/pg 327/sec 6.8.6/`H7S3rm`.

        case 'STM32H7S3L8H6':
            blueprint['settings', 'FLASH_LATENCY'           ] = '0x7'
            blueprint['settings', 'FLASH_PROGRAMMING_DELAY' ] = '0b11'
            blueprint['settings', 'INTERNAL_VOLTAGE_SCALING'] = 'high'



        # @/pg 252/tbl 45/`H533rm`.
        # @/pg 438/sec 10.11.4/`H533rm`.

        case 'STM32H533RET6':
            blueprint['settings', 'FLASH_LATENCY'           ] = 5
            blueprint['settings', 'FLASH_PROGRAMMING_DELAY' ] = '0b10'
            blueprint['settings', 'INTERNAL_VOLTAGE_SCALING'] = 'VOS0'



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



    match target.mcu:



        # @/pg 285/fig 21/`H7S3rm`.
        # @/pg 286/tbl 44/`H7S3rm`.

        case 'STM32H7S3L8H6':
            blueprint['settings', 'SMPS_OUTPUT_LEVEL'      ] = None
            blueprint['settings', 'SMPS_FORCED_ON'         ] = None
            blueprint['settings', 'SMPS_ENABLE'            ] = False
            blueprint['settings', 'LDO_ENABLE'             ] = True
            blueprint['settings', 'POWER_MANAGEMENT_BYPASS'] = False



        # @/pg 407/fig 42/`H533rm`.
        # Note that the SMPS is not available. @/pg 402/sec 10.2/`H533rm`.

        case 'STM32H533RET6':
            blueprint['settings', 'LDO_ENABLE'             ] = True
            blueprint['settings', 'POWER_MANAGEMENT_BYPASS'] = False



        case _: raise NotImplementedError



    ################################################################################
    #
    # General high-speed-internal oscillator.
    # @/pg 361/sec 7.5.2/`H7S3rm`.
    # @/pg 458/sec 11.4.2/`H533rm`.
    # TODO Handle other frequencies.
    #



    blueprint['frequency', 'HSI_CK'] = (
        properties['HSI_DEFAULT_FREQUENCY']
        if blueprint('HSI_ENABLE')
        else 0
    )



    ################################################################################
    #
    # High-speed-internal oscillator (48MHz).
    # @/pg 363/sec 7.5.2/`H7S3rm`.
    # @/pg 460/sec 11.4.4/`H533rm`.
    #



    blueprint['frequency', 'HSI48_CK'] = (
        48_000_000
        if blueprint('HSI48_ENABLE')
        else 0
    )



    ################################################################################
    #
    # "Clock Security System" oscillator (fixed at ~4MHz).
    # @/pg 362/sec 7.5.2/`H7S3rm`.
    # @/pg 459/sec 11.4.3/`H533rm`.
    #



    blueprint['frequency', 'CSI_CK'] = (
        4_000_000
        if blueprint('CSI_ENABLE')
        else 0
    )



    ################################################################################
    #
    # TODO Not implemented yet.
    #



    blueprint['frequency', 'HSE_CK'] = 0
    blueprint['frequency', 'LSE_CK'] = 0



    ################################################################################
    #
    # Peripheral clock.
    # TODO Automate.
    #



    blueprint['frequency', 'PER_CK'] = blueprint(blueprint('PERIPHERAL_CLOCK_OPTION'))



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

            goal_frequency = blueprint(f'PLL{unit}_{channel}_CK')

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

        for blueprint['settings', f'PLL{unit}_PREDIVIDER'] in properties[f'PLL{unit}_PREDIVIDER']:



            # Determine the range of the PLL input frequency.

            reference_frequency = kernel_frequency / blueprint(f'PLL{unit}_PREDIVIDER')

            for lower, upper in properties[f'PLL{unit}_INPUT_RANGE']:
                if lower <= reference_frequency < upper:
                    break
            else:
                continue

            blueprint['settings', f'PLL{unit}_INPUT_RANGE'] = (lower, upper)



            # Try every available multiplier that the PLL can handle.

            for blueprint['settings', f'PLL{unit}_MULTIPLIER'] in properties[f'PLL{unit}_MULTIPLIER']:

                vco_frequency = reference_frequency * blueprint(f'PLL{unit}_MULTIPLIER')

                if vco_frequency not in properties['PLL_VCO_FREQ']:
                    continue

                yield vco_frequency



    #
    #
    #



    def parameterize_channel(unit, vco_frequency, channel):



        # See if the PLL channel is even used.

        goal_frequency = blueprint(f'PLL{unit}_{channel}_CK')

        if goal_frequency is None:
            return True



        # Find the channel divider.

        needed_divider = vco_frequency / goal_frequency

        if needed_divider not in properties[f'PLL{unit}{channel}_DIVIDER']:
            return False

        blueprint['settings', f'PLL{unit}_{channel}_DIVIDER'] = needed_divider

        return True



    #
    #
    #



    def parameterize_pll(unit, kernel_frequency):

        channels = dict(properties['PLLS'])[unit]



        # TODO Unnecessary.

        blueprint['settings', f'PLL{unit}_PREDIVIDER' ] = None
        blueprint['settings', f'PLL{unit}_INPUT_RANGE'] = None
        blueprint['settings', f'PLL{unit}_MULTIPLIER' ] = None
        for channel in dict(properties['PLLS'])[unit]:
            blueprint['settings', f'PLL{unit}_{channel}_DIVIDER'] = None



        # See if the PLL unit is even used.

        blueprint['settings', f'PLL{unit}_ENABLE'] = any(
            blueprint(f'PLL{unit}_{channel}_CK') is not None
            for channel in channels
        )

        if not blueprint(f'PLL{unit}_ENABLE'):
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



    @blueprint.brute
    def parameterize_plls():

        match target.mcu:



            # All of the PLL units share the same kernel clock source.

            case 'STM32H7S3L8H6':

                return any(
                    all(
                        parameterize_pll(unit, blueprint(blueprint('PLL_KERNEL_SOURCE')))
                        for unit, channels in properties['PLLS']
                    )
                    for blueprint['settings', 'PLL_KERNEL_SOURCE'] in properties['PLL_KERNEL_SOURCE']
                )



            # Each PLL unit have their own clock source.

            case 'STM32H533RET6':

                return all(
                    any(
                        parameterize_pll(unit, blueprint(blueprint(f'PLL{unit}_KERNEL_SOURCE')))
                        for blueprint['settings', f'PLL{unit}_KERNEL_SOURCE'] in properties[f'PLL{unit}_KERNEL_SOURCE']
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

    if blueprint('CPU_CK') not in properties['CPU_FREQ']:
        raise ValueError(
            f'CPU_CK is out of range: '
            f'{blueprint('CPU_CK') :_}Hz.'
        )

    for unit in properties['APBS']:
        if blueprint(f'APB{unit}_CK') not in properties['APB_FREQ']:
            raise ValueError(
                f'APB{unit}_CK is out of range: '
                f'{blueprint(f'APB{unit}_CK') :_}Hz.'
            )

    match target.mcu:

        case 'STM32H7S3L8H6':

            if blueprint('AXI_AHB_CK') not in properties['AXI_AHB_FREQ']:
                raise ValueError(
                    f'AXI_AHB_CK is out-of-range: '
                    f'{blueprint('AXI_AHB_CK') :_}Hz.'
                )



    #
    #
    #



    @blueprint.brute
    def parameterize_scgu():

        for blueprint['settings', 'SCGU_KERNEL_SOURCE'] in properties['SCGU_KERNEL_SOURCE']:



            # CPU.

            blueprint['settings', 'CPU_DIVIDER'] = blueprint(blueprint('SCGU_KERNEL_SOURCE')) / blueprint('CPU_CK')

            if blueprint('CPU_DIVIDER') not in properties['CPU_DIVIDER']:
                continue



            # AXI/AHB busses.

            match target.mcu:



                # There's a divider to configure.

                case 'STM32H7S3L8H6':

                    blueprint['settings', 'AXI_AHB_DIVIDER'] = blueprint('CPU_CK') / blueprint('AXI_AHB_CK')

                    if blueprint('AXI_AHB_DIVIDER') not in properties['AXI_AHB_DIVIDER']:
                        continue



                # The CPU and AXI/AHB bus are directly connected.

                case 'STM32H533RET6':

                    blueprint['frequency', 'AXI_AHB_CK'] = blueprint('CPU_CK')



                case _: raise NotImplementedError



            # Each APB bus.

            def parameterize_apb(unit):
                blueprint['settings', f'APB{unit}_DIVIDER'] = blueprint('AXI_AHB_CK') / blueprint(f'APB{unit}_CK')
                return blueprint(f'APB{unit}_DIVIDER') in properties[f'APB{unit}_DIVIDER']

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

    if blueprint('SYSTICK_CK') is not None and target.use_freertos:
        raise ValueError(
            f'FreeRTOS already uses SysTick for the time-base; '
            f'so for target {repr(target.name)}, '
            f'either remove "SYSTICK_CK" from the clock-tree '
            f'configuration or disable FreeRTOS.'
        )



    #
    #
    #



    @blueprint.brute
    def parameterize_systick():



        # See if SysTick is even used.

        blueprint['settings', 'SYSTICK_ENABLE'] = blueprint('SYSTICK_CK') is not None

        if not blueprint('SYSTICK_ENABLE'):
            return True



        # Try different clock sources.

        for blueprint['settings', 'SYSTICK_USE_CPU_CK'] in properties['SYSTICK_USE_CPU_CK']:



            # SysTick will use the CPU's frequency.
            # @/pg 621/sec B3.3.3/`Armv7-M`.
            # @/pg 1859/sec D1.2.238/`Armv8-M`.

            if blueprint('SYSTICK_USE_CPU_CK'):

                kernel_frequencies = [
                    blueprint('CPU_CK')
                ]



            # SysTick will use an implementation-defined clock source.

            else:

                match target.mcu:



                    # @/pg 378/fig 51/`H7S3rm`.

                    case 'STM32H7S3L8H6':

                        kernel_frequencies = [
                            blueprint('CPU_CK') / 8
                        ]



                    # @/pg 456/fig 52/`H533rm`.

                    case 'STM32H533RET6':

                        kernel_frequencies = [
                            # TODO.
                        ]



                    case _: raise NotImplementedError



            # Try out the different kernel frequencies and see what sticks.

            for blueprint['frequency', 'SYSTICK_KERNEL_FREQ'] in kernel_frequencies:

                blueprint['settings', 'SYSTICK_RELOAD'] = blueprint('SYSTICK_KERNEL_FREQ') / blueprint('SYSTICK_CK') - 1

                if blueprint('SYSTICK_RELOAD') in properties['SYSTICK_RELOAD']:
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

            needed_baud = blueprint(f'{peripheral}{unit}_BAUD')

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

            blueprint['settings', f'{peripheral}{unit}_BAUD_DIVIDER'] = needed_divider

            return True



        #
        #
        #



        @blueprint.brute
        def parameterize_uxarts():



            # TODO Unnecessary.

            blueprint['settings', f'UXART_{instances}_KERNEL_SOURCE'] = None
            for instance in instances:
                blueprint['settings', f'{instance[0]}{instance[1]}_BAUD_DIVIDER'] = None



            # Check if any of the instances are even used.

            using_instances = any(
                blueprint(f'{peripheral}{unit}_BAUD') is not None
                for peripheral, unit in instances
            )

            if not using_instances:
                return True



            # Try every available clock source for this
            # set of instances and see what sticks.

            for blueprint['settings', f'UXART_{instances}_KERNEL_SOURCE'] in properties[f'UXART_{instances}_KERNEL_SOURCE']:

                every_instance_satisfied = all(
                    parameterize_uxart(instance, blueprint(blueprint(f'UXART_{instances}_KERNEL_SOURCE')))
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



        @blueprint.brute
        def parameterize():



            # TODO Unnecessary.

            blueprint['settings', f'I2C{unit}_KERNEL_SOURCE'] = None



            # See if the unit is even used.

            needed_baud = blueprint(f'I2C{unit}_BAUD')

            if needed_baud is None:
                return True



            # We can't get an exact baud-rate for I2C (since there's a lot
            # of factors involved anyways like clock-stretching), we'll have
            # to try every single possibility and find the one with the least
            # amount of error.

            best_baud_error = None

            for kernel_source in properties[f'I2C{unit}_KERNEL_SOURCE']:

                kernel_frequency = blueprint(kernel_source) or 0

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
                        blueprint['settings', f'I2C{unit}_KERNEL_SOURCE'] = kernel_source
                        blueprint['settings', f'I2C{unit}_PRESC'        ] = presc
                        blueprint['settings', f'I2C{unit}_SCL'          ] = scl



            # We are only successful if we are within tolerance.

            return best_baud_error is not None and best_baud_error <= 0.01 # TODO Ad-hoc tolerance.



    ################################################################################
    #
    # Timers.
    #



    def parameterize_timer(unit):

        needed_rate = blueprint(f'TIM{unit}_RATE')



        # Determine the kernel frequency.

        match target.mcu:



            case 'STM32H533RET6':

                apb         = properties['APB_PERIPHERALS'][f'TIM{unit}']
                apb_divider = blueprint(f'APB{apb}_DIVIDER')
                multiplier  = properties['GLOBAL_TIMER_PRESCALER_MULTIPLIER_TABLE'][(blueprint('GLOBAL_TIMER_PRESCALER'), apb_divider)]

                kernel_frequency = blueprint(f'AXI_AHB_CK') * multiplier



            case _: raise NotImplementedError



        # Find the pair of divider and modulation values to
        # get an output frequency that's within tolerance.

        for blueprint['settings', f'TIM{unit}_DIVIDER'] in properties[f'TIM{unit}_DIVIDER']:

            counter_frequency = kernel_frequency / blueprint(f'TIM{unit}_DIVIDER')



            # Determine the modulation value.

            blueprint['settings', f'TIM{unit}_MODULATION'] = (
                min(
                    max(
                        round(counter_frequency / needed_rate),
                        properties[f'TIM{unit}_MODULATION'].minimum
                    ),
                    properties[f'TIM{unit}_MODULATION'].maximum
                )
            )



            # See if things are within tolerance.

            actual_rate  = counter_frequency / blueprint(f'TIM{unit}_MODULATION')
            actual_error = abs(1 - actual_rate / needed_rate)

            if actual_error <= 0.001: # TODO Ad-hoc.
                return True



    #
    #
    #



    @blueprint.brute
    def parameterize_timers():

        used_units = [
            unit
            for unit in properties.get('TIMERS', ())
            if blueprint(f'TIM{unit}_RATE') is not None
        ]

        if not used_units:
            return True

        for blueprint['settings', 'GLOBAL_TIMER_PRESCALER'] in properties['GLOBAL_TIMER_PRESCALER']:

            every_unit_satisfied = all(
                parameterize_timer(unit)
                for unit in used_units
            )

            if every_unit_satisfied:
                return True



    ################################################################################



    for key, (category, value) in blueprint.dictionary.items():
        if key in properties and isinstance(properties[key], dict):
            if value in properties[key]:
                blueprint.dictionary[key] = (category, properties[key][value])

    for key, (category, value) in blueprint.dictionary.items():
        if isinstance(value, float) and value.is_integer():
            blueprint.dictionary[key] = (category, int(value))



    ################################################################################
    #
    # Parameterization done!
    #



    blueprint.done()

    return blueprint
