from ..stpy.database import system_database
from ..stpy.planner  import SystemPlanner, stringify_table, get_similars
from ..pxd.utils     import mk_dict
from ..pxd.log       import log, ANSI



################################################################################
#
# Helper class for keeping track of values calculated in the clock-tree.
#



class ClockTreeBook:

    def __init__(self, target):

        self.target     = target
        self.dictionary = {
            None : 0, # No clock source, zero frequency.
        }



    def __setitem__(self, key, value):

        # Prevent overwriting keys in the clock-tree book.

        if key in self.dictionary:
            raise RuntimeError(
                f'Key {repr(key)} is already defined in the '
                f'clock-tree book for target {repr(self.target.name)}.'
            )

        self.dictionary[key] = value

        return value



    def __getitem__(self, key):

        # Ensure the key into the clock-tree book exists.

        if key not in self.dictionary:
            raise RuntimeError(
                f'No key {repr(key)} '
                f'found in the clock-tree book '
                f'for target {repr(self.target.name)}; '
                f'closest matches are: '
                f'{get_similars(key, self.dictionary.keys())}.'
            )

        return self.dictionary[key]



    def __str__(self):
        return stringify_table(self.dictionary.items())



################################################################################
#
# Helper class for keeping track of constraints imposed on the clock-tree.
#



class ClockTreeSchemaWrapper:

    def __init__(self, target):
        self.target    = target
        self.used_keys = []



    def __getitem__(self, key):

        # We keep track of the clock-tree
        # options that have been used so far.

        if key not in self.target.clock_tree:
            raise RuntimeError(
                f'No key {repr(key)} '
                f'found in the clock-tree schema '
                f'for target {repr(self.target.name)}; '
                f'closest matches are: '
                f'{get_similars(key, self.target.clock_tree.keys())}.'
            )

        if key not in self.used_keys:
            self.used_keys += [key]

        return self.target.clock_tree[key]



    def done(self):

        # Verify that we didn't miss anything.

        if unused_keys := [
            key
            for key in self.target.clock_tree
            if key not in self.used_keys
        ]:
            log(ANSI(
                f'[WARNING] There are leftover {self.target.mcu} options: {unused_keys}.',
                'fg_yellow'
            ))



    def __str__(self):
        return stringify_table(self.target.clock_tree.items())



################################################################################



def system_parameterize(target):

    database = system_database[target.mcu]
    book     = ClockTreeBook(target)
    schema   = ClockTreeSchemaWrapper(target)
    planner  = SystemPlanner(target)



    ################################################################################
    #
    # Some clock frequencies are dictated by the schema,
    # so we can just immediately add them to the book.
    # We'll check later on to make sure that the
    # frequencies are actually solvable.
    #



    keys = [
        'CPU_CK',
        'SYSTICK_CK',
    ]



    match target.mcu:

        case 'STM32H7S3L8H6':
            keys += [
                'AXI_AHB_CK'
            ]

        case 'STM32H533RET6':
            keys += [
            ]

        case _: raise NotImplementedError



    keys += [
        f'APB{unit}_CK'
        for unit in database['APBS']
    ]



    keys += [
        f'PLL{unit}_{channel}_CK'
        for unit, channels in database['PLLS']
        for channel in channels
    ]



    for key in keys:
        book[key] = schema[key]



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

        case 'STM32H7S3L8H6':

            # @/pg 211/tbl 29/`H7S3rm`.
            planner['FLASH_LATENCY']           = '0x7'
            planner['FLASH_PROGRAMMING_DELAY'] = '0b11'

            # @/pg 327/sec 6.8.6/`H7S3rm`.
            planner['INTERNAL_VOLTAGE_SCALING'] = 'high'



        case 'STM32H533RET6':

            # @/pg 252/tbl 45/`H533rm`.
            planner['FLASH_LATENCY']           = 5
            planner['FLASH_PROGRAMMING_DELAY'] = '0b10'

            # @/pg 438/sec 10.11.4/`H533rm`.
            planner['INTERNAL_VOLTAGE_SCALING'] = 'VOS0'



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

            planner['SMPS_OUTPUT_LEVEL']       = None
            planner['SMPS_FORCED_ON']          = None
            planner['SMPS_ENABLE']             = False
            planner['LDO_ENABLE']              = True
            planner['POWER_MANAGEMENT_BYPASS'] = False



        # @/pg 407/fig 42/`H533rm`.
        # Note that the SMPS is not available. @/pg 402/sec 10.2/`H533rm`.
        case 'STM32H533RET6':

            planner['LDO_ENABLE']              = True
            planner['POWER_MANAGEMENT_BYPASS'] = False



        case _: raise NotImplementedError



    ################################################################################
    #
    # Built-in oscillators.
    #



    # TODO Put in database.

    hsi_default_frequency = {
        'STM32H7S3L8H6' : 64_000_000,
        'STM32H533RET6' : 32_000_000,
    }[target.mcu]



    # General high-speed-internal oscillator.
    # @/pg 361/sec 7.5.2/`H7S3rm`.
    # @/pg 458/sec 11.4.2/`H533rm`.
    # TODO Handle other frequencies.

    planner['HSI_ENABLE'] = schema['HSI_ENABLE']
    book['HSI_CK']        = 32_000_000 if planner['HSI_ENABLE'] else 0



    # High-speed-internal oscillator (48MHz).
    # @/pg 363/sec 7.5.2/`H7S3rm`.
    # @/pg 460/sec 11.4.4/`H533rm`.

    planner['HSI48_ENABLE'] = schema['HSI48_ENABLE']
    book['HSI48_CK']        = 48_000_000 if planner['HSI48_ENABLE'] else 0



    # "Clock Security System" oscillator (fixed at ~4MHz).
    # @/pg 362/sec 7.5.2/`H7S3rm`.
    # @/pg 459/sec 11.4.3/`H533rm`.

    planner['CSI_ENABLE'] = schema['CSI_ENABLE']
    book['CSI_CK']        = 4_000_000 if planner['CSI_ENABLE'] else 0



    # TODO Not implemented yet.

    book['HSE_CK'] = 0
    book['LSE_CK'] = 0



    ################################################################################
    #
    # Peripheral clock.
    # TODO Automate.
    #



    planner['PERIPHERAL_CLOCK_OPTION'] = schema['PERIPHERAL_CLOCK_OPTION']
    book['PER_CK']                     = book[schema['PERIPHERAL_CLOCK_OPTION']]



    ################################################################################
    #
    # PLLs.
    #
    # @/pg 371/fig 48/`H7S3rm`.
    # @/pg 354/fig 40/`H7S3rm`.
    # @/pg 461/fig 55/`H533rm`.
    # @/pg 456/fig 52/`H533rm`.
    #



    for unit, channels in database['PLLS']:

        for channel in channels:

            goal_frequency = schema[f'PLL{unit}_{channel}_CK']

            if goal_frequency is None:
                continue

            if goal_frequency not in database['PLL_CHANNEL_FREQ']:
                raise ValueError(
                    f'PLL{unit}_{channel}_CK frequency is '
                    f'out of range: {goal_frequency :_}Hz.'
                )



    #
    #
    #



    def each_vco_frequency(unit, kernel_frequency):

        for planner[f'PLL{unit}_PREDIVIDER'] in database[f'PLL{unit}_PREDIVIDER']:



            # Determine the range of the PLL input frequency.
            # TODO Simplify.

            reference_frequency = kernel_frequency / planner[f'PLL{unit}_PREDIVIDER']

            planner[f'PLL{unit}_INPUT_RANGE'] = next(( # TODO Make less weird.
                option
                for upper_frequency_range, option in database[f'PLL{unit}_INPUT_RANGE']
                if reference_frequency < upper_frequency_range
            ), None)

            if planner[f'PLL{unit}_INPUT_RANGE'] is None:
                continue



            # Try every available multiplier that the PLL can handle.

            for planner[f'PLL{unit}_MULTIPLIER'] in database[f'PLL{unit}_MULTIPLIER']:

                vco_frequency = reference_frequency * planner[f'PLL{unit}_MULTIPLIER']

                if vco_frequency not in database['PLL_VCO_FREQ']:
                    continue

                yield vco_frequency



    #
    #
    #



    def parameterize_channel(unit, vco_frequency, channel):

        goal_frequency = schema[f'PLL{unit}_{channel}_CK']



        # Channel even used?

        if goal_frequency is None:

            needed_divider = None



        # See what the channel divider would be.

        else:

            needed_divider = vco_frequency / goal_frequency

            if not needed_divider.is_integer():
                return False

            needed_divider = int(needed_divider)

            if needed_divider not in database[f'PLL{unit}{channel}_DIVIDER']:
                return False



        # Got the channel divider!

        planner[f'PLL{unit}_{channel}_DIVIDER'] = needed_divider

        return True



    #
    #
    #

    def parameterize_unit(unit, kernel_frequency):



        # TODO Unnecessary.

        planner[f'PLL{unit}_PREDIVIDER' ] = None
        planner[f'PLL{unit}_INPUT_RANGE'] = None
        planner[f'PLL{unit}_MULTIPLIER' ] = None
        for channel in mk_dict(database['PLLS'])[unit]:
            planner[f'PLL{unit}_{channel}_DIVIDER'] = None



        # See if the PLL unit is even used.

        planner[f'PLL{unit}_ENABLE'] = not all(
            schema[f'PLL{unit}_{channel}_CK'] is None
            for channel in mk_dict(database['PLLS'])[unit]
        )

        if not planner[f'PLL{unit}_ENABLE']:
            return True



        # Parameterize each channel.

        for vco_frequency in each_vco_frequency(unit, kernel_frequency):

            every_channel_satisfied = all(
                parameterize_channel(unit, vco_frequency, channel)
                for channel in mk_dict(database['PLLS'])[unit]
            )

            if every_channel_satisfied:
                return True



    #
    #
    #



    def parameterize_units():

        match target.mcu:



            # All of the PLL units share the same kernel clock source.

            case 'STM32H7S3L8H6':

                for planner['PLL_KERNEL_SOURCE'], _ in database['PLL_KERNEL_SOURCE']:

                    kernel_frequency     = book[planner['PLL_KERNEL_SOURCE']]
                    every_unit_satisfied = all(
                        parameterize_unit(units, kernel_frequency)
                        for units, channels in database['PLLS']
                    )

                    if every_unit_satisfied:
                        return True



            # Each PLL unit have their own clock source.

            case 'STM32H533RET6':

                every_unit_satisfied = all(
                    any(
                        parameterize_unit(unit, book[planner[f'PLL{unit}_KERNEL_SOURCE']])
                        for planner[f'PLL{unit}_KERNEL_SOURCE'], _ in database[f'PLL{unit}_KERNEL_SOURCE']
                    )
                    for unit, channels in database['PLLS']
                )

                return every_unit_satisfied



            case _: raise NotImplementedError



    #
    #
    #



    planner.brute(parameterize_units)



    ################################################################################
    #
    # System Clock Generation Unit.
    #
    # @/pg 378/fig 51/`H7S3rm`.
    #



    if book['CPU_CK'] not in database['CPU_FREQ']:
        raise ValueError(
            f'CPU_CK is out of range: '
            f'{book['CPU_CK'] :_}Hz.'
        )

    for unit in database['APBS']:
        if book[f'APB{unit}_CK'] not in database['APB_FREQ']:
            raise ValueError(
                f'APB{unit}_CK is out of range: '
                f'{book[f'APB{unit}_CK'] :_}Hz.'
            )

    match target.mcu:

        case 'STM32H7S3L8H6':

            if book['AXI_AHB_CK'] not in database['AXI_AHB_FREQ']:
                raise ValueError(
                    f'AXI_AHB_CK is out-of-range: '
                    f'{book['AXI_AHB_CK'] :_}Hz.'
                )



    #
    #
    #



    def parameterize_apb(unit):

        needed_divider                = book['AXI_AHB_CK'] / book[f'APB{unit}_CK']
        planner[f'APB{unit}_DIVIDER'] = mk_dict(database[f'APB{unit}_DIVIDER']).get(needed_divider, None)

        return planner[f'APB{unit}_DIVIDER'] is not None



    #
    #
    #



    def parameterize_scgu():

        for planner['SCGU_KERNEL_SOURCE'], _ in database['SCGU_KERNEL_SOURCE']:



            # CPU.

            needed_cpu_divider     = book[planner['SCGU_KERNEL_SOURCE']] / book['CPU_CK']
            planner['CPU_DIVIDER'] = mk_dict(database['CPU_DIVIDER']).get(needed_cpu_divider, None)

            if planner['CPU_DIVIDER'] is None:
                continue



            # AXI/AHB busses.

            match target.mcu:

                case 'STM32H7S3L8H6':

                    needed_axi_ahb_divider     = book['CPU_CK'] / book['AXI_AHB_CK']
                    planner['AXI_AHB_DIVIDER'] = mk_dict(database['AXI_AHB_DIVIDER']).get(needed_axi_ahb_divider, None)

                    if planner['AXI_AHB_DIVIDER'] is None:
                        continue



                case 'STM32H533RET6':

                    book['AXI_AHB_CK'] = book['CPU_CK']



                case _: raise NotImplementedError



            # Each APB bus.

            every_apb_satisfied = all(
                parameterize_apb(unit)
                for unit in database['APBS']
            )

            if not every_apb_satisfied:
                continue



            return True



    #
    #
    #



    planner.brute(parameterize_scgu)



    ################################################################################
    #
    # SysTick.
    #
    # @/pg 620/sec B3.3/`Armv7-M`.
    # @/pg 297/sec B11.1/`Armv8-M`.
    #



    if schema['SYSTICK_CK'] is not None and target.use_freertos:
        raise ValueError(
            f'FreeRTOS already uses SysTick for the time-base; '
            f'so for target {repr(target.name)}, '
            f'either remove "SYSTICK_CK" from the clock-tree '
            f'configuration or disable FreeRTOS.'
        )



    #
    #
    #



    def parameterize():



        # See if SysTick is even used.

        planner['SYSTICK_ENABLE'] = book['SYSTICK_CK'] is not None

        if not planner['SYSTICK_ENABLE']:
            return True



        # Try different clock sources.

        for planner['SYSTICK_USE_CPU_CK'] in database['SYSTICK_USE_CPU_CK']:



            # SysTick will use the CPU's frequency.
            # @/pg 621/sec B3.3.3/`Armv7-M`.
            # @/pg 1859/sec D1.2.238/`Armv8-M`.

            if planner['SYSTICK_USE_CPU_CK']:

                kernel_frequencies = [
                    book['CPU_CK']
                ]



            # SysTick will use an implementation-defined clock source.

            else:

                match target.mcu:

                    # @/pg 378/fig 51/`H7S3rm`.
                    case 'STM32H7S3L8H6':

                        kernel_frequencies = [
                            book['CPU_CK'] / 8
                        ]



                    # @/pg 456/fig 52/`H533rm`.
                    case 'STM32H533RET6':

                        kernel_frequencies = [
                            # TODO.
                        ]



                    case _: raise NotImplementedError



            # Try out the different kernel frequencies and see what sticks.

            for book['SYSTICK_KERNEL_FREQ'] in kernel_frequencies:

                planner['SYSTICK_RELOAD'] = book['SYSTICK_KERNEL_FREQ'] / book['SYSTICK_CK'] - 1

                if not planner['SYSTICK_RELOAD'].is_integer():
                    continue

                planner['SYSTICK_RELOAD'] = int(planner['SYSTICK_RELOAD'])

                if planner['SYSTICK_RELOAD'] not in database['SYSTICK_RELOAD']:
                    continue

                return True



    #
    #
    #



    planner.brute(parameterize)



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

    for instances in database.get('UXARTS', ()):



        #
        #
        #

        def parameterize_instance(kernel_frequency, instance):

            peripheral, unit = instance



            # See if this instance is even needed.

            needed_baud = schema[f'{peripheral}{unit}_BAUD']

            if needed_baud is None:
                return True



            # Check if the needed divider is valid.

            needed_divider = kernel_frequency / needed_baud

            if not needed_divider.is_integer():
                return False

            needed_divider = int(needed_divider)

            if needed_divider not in database['UXART_BAUD_DIVIDER']:
                return False



            # We found the desired divider!

            planner[f'{peripheral}{unit}_BAUD_DIVIDER'] = needed_divider

            return True



        #
        #
        #

        def parameterize_instances():



            # TODO Unnecessary.

            planner[f'UXART_{instances}_KERNEL_SOURCE'] = None
            for instance in instances:
                planner[f'{instance[0]}{instance[1]}_BAUD_DIVIDER'] = None



            # Check if an instance in this set is even used.

            using_instances = any(
                schema[f'{peripheral}{unit}_BAUD'] is not None
                for peripheral, unit in instances
            )

            if not using_instances:
                return True



            # Try every available clock source for this
            # set of instances and see what sticks.

            for planner[f'UXART_{instances}_KERNEL_SOURCE'], _ in database[f'UXART_{instances}_KERNEL_SOURCE']:

                kernel_frequency         = book[planner[f'UXART_{instances}_KERNEL_SOURCE']]
                every_instance_satisfied = all(
                    parameterize_instance(kernel_frequency, instance)
                    for instance in instances
                )

                if every_instance_satisfied:
                    return True



        #
        #
        #



        planner.brute(parameterize_instances)



    ################################################################################
    #
    # I2Cs.
    # TODO Consider maximum kernel frequency.
    #



    for unit in database.get('I2CS', ()):



        def parameterize():



            # See if the unit is even used.

            needed_baud = schema[f'I2C{unit}_BAUD']

            if needed_baud is None:

                planner[f'I2C{unit}_KERNEL_SOURCE'] = None

                return True



            # We can't get an exact baud-rate for I2C (since there's a lot
            # of factors involved anyways like clock-stretching), we'll have
            # to try every single possibility and find the one with the least
            # amount of error.

            best_baud_error = None

            for kernel_source, _ in database[f'I2C{unit}_KERNEL_SOURCE']:

                kernel_frequency = book[kernel_source] or 0

                for presc in database['I2C_PRESC']:



                    # Determine the SCL.

                    scl = round(kernel_frequency / (presc + 1) / needed_baud / 2)

                    if scl not in database['I2C_SCLH']:
                        continue

                    if scl not in database['I2C_SCLL']:
                        continue



                    # Determine the baud error.

                    actual_baud       = kernel_frequency / (scl * 2 * (presc + 1) + 1)
                    actual_baud_error = abs(1 - actual_baud / needed_baud)



                    # Keep the best so far.

                    if best_baud_error is None or actual_baud_error < best_baud_error:
                        best_baud_error                     = actual_baud_error
                        planner[f'I2C{unit}_KERNEL_SOURCE'] = kernel_source
                        planner[f'I2C{unit}_PRESC'        ] = presc
                        planner[f'I2C{unit}_SCL'          ] = scl



            # We are only successful if we are within tolerance.

            return best_baud_error is not None and best_baud_error <= 0.01 # TODO Ad-hoc tolerance.



        planner.brute(parameterize)



    ################################################################################
    #
    # Timers.
    #



    def parameterize_unit(unit):

        needed_rate = schema[f'TIM{unit}_RATE']



        # Determine the kernel frequency.

        match target.mcu:

            case 'STM32H533RET6':

                # TODO Not the best way to implement this.
                apb = {
                    2  : 1,
                    3  : 1,
                    4  : 1,
                    5  : 1,
                    6  : 1,
                    7  : 1,
                    12 : 1,
                    1  : 2,
                    8  : 2,
                    15 : 2,
                }[unit]

                # TODO Not the best way to implement this.
                # TODO Not entirely sure if correct.
                multiplier = {
                    (False, '0b000') : 1,
                    (False, '0b100') : 1,
                    (False, '0b101') : 1 / 2,
                    (False, '0b110') : 1 / 4,
                    (False, '0b111') : 1 / 8,
                    (True , '0b000') : 1,
                    (True , '0b100') : 1,
                    (True , '0b101') : 1 / 2,
                    (True , '0b110') : 1 / 2,
                    (True , '0b111') : 1 / 4,
                }[(
                    planner['GLOBAL_TIMER_PRESCALER'],
                    planner[f'APB{apb}_DIVIDER'])
                ]

                kernel_frequency = book[f'AXI_AHB_CK'] * multiplier



            case _: raise NotImplementedError



        # Find the pair of divider and modulation values to
        # get an output frequency that's within tolerance.

        for planner[f'TIM{unit}_DIVIDER'] in database[f'TIM{unit}_DIVIDER']:

            counter_frequency = kernel_frequency / planner[f'TIM{unit}_DIVIDER']



            # Determine the modulation value.
            # Note that zero will end up disabling
            # the counter. Since we're approximating
            # for the rate, anyways we might as well
            # round up to 1.

            planner[f'TIM{unit}_MODULATION'] = round(counter_frequency / needed_rate)

            if planner[f'TIM{unit}_MODULATION'] == 0:
                planner[f'TIM{unit}_MODULATION'] = 1

            if planner[f'TIM{unit}_MODULATION'] not in database[f'TIM{unit}_MODULATION']:
                continue



            # See if things are within tolerance.

            actual_rate  = counter_frequency / planner[f'TIM{unit}_MODULATION']
            actual_error = abs(1 - actual_rate / needed_rate)

            if actual_error <= 0.001: # TODO Ad-hoc.
                return True



    #
    #
    #



    def parameterize_units():



        units_to_be_parameterized = [
            unit
            for unit in database['TIMERS']
            if schema[f'TIM{unit}_RATE'] is not None
        ]



        if not units_to_be_parameterized:
            planner['GLOBAL_TIMER_PRESCALER'] = None
            return True



        for planner['GLOBAL_TIMER_PRESCALER'] in database['GLOBAL_TIMER_PRESCALER']:

            every_unit_satisfied = all(
                parameterize_unit(unit)
                for unit in units_to_be_parameterized
            )

            if every_unit_satisfied:
                return True



    #
    #
    #



    if 'TIMERS' in database:
        planner.brute(parameterize_units)



    ################################################################################
    #
    # Parameterization done!
    #



    schema.done()

    planner.done_parameterize()

    return planner, book.dictionary



################################################################################



# TODO Stale.
# @/`About Parameterization`:
# This meta-directive figures out the register values needed
# to configure the MCU's clock-tree, but without necessarily
# worrying about the proper order that the register values
# should be written in.
#
# The latter is for `system_configurize` in <./electrical/system/configurize.py>
# to do, but here in `system_parameterize`, we essentially
# perform brute-forcing so that we have the CPU be clocked
# at the desired frequency, the SPI clock be clocking at the
# rate we want, and so forth.
#
# As it turns out, the algorithm to brute-force the clock-tree
# the very similar across all STM32 microcontrollers. Of course,
# there are some differences, but most of the logic is heavily
# overlapped. This is especially true when we have `system_database`
# to abstract over the details like the exact min/max frequencies
# allowed and what range is multipliers/dividers are permitted.
#
# While this meta-directive would have one of the most complicated jobs,
# what it exactly does is still pretty straight-forward and modular.
# It is divided into small, independent sections, so if you're looking
# into extending this meta-directive, look at how the existing logic
# work, copy-paste it, and adjust the logic through trial and error.
# Remember, the goal of this meta-directive is to figure out what the
# register values should be (which often mean you need to add new
# entries to the MCU's database); once you have that down, you can move
# onto `system_configurize` and generate the appropriate code.
#
# This process is more time-consuming than scary really.
# Obviously, before you do any of this, you should have existing
# code that proves the parameterization and configuration works
# (e.g. manually configuring I2C clock sources and dividers before
# using meta-directives to automate it).
#
# In an ideal world, there'd be a GUI to configure the clock-tree,
# rather than what is being done now with this Python code stuff.
# This is what STM32CubeMX does, actually, but it's incredibly slow
# and hostile towards the user, so I suggest we make something better
# than Cube. This side-mission, however, will take a lot of effort
# considering the design challenges. For instance, every microcontroller
# has really niche constraints; one example might be how a SDMMC
# divider can only be an even number (or 1) if a PLL divider is 1 (or
# something like that) because a 50% duty cycle is required. Really
# oddly specific stuff like that. So if we were to create a new and
# better GUI, it'd have to be extremely flexible with its logic, but
# in doing so, we must also ensure it's absurdly fast when it comes
# to brute-forcing. Like, so fast that we always do brute-forcing every
# time a build the project! One day. Dream big.
