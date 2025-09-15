import copy
from ..stpy.new_database import new_system_database

class new_Parameterization:


    def __setitem__(self, key, value):

        assert 'value' in self.database[key]

        self.database[key]['value'] = value


    def __setitem__(self, key, value):

        self.database[key]['value'] = value


    def __call__(self, key, *default):

        if key not in self.database:
            default, = default
            return default

        return self.database[key]['value']


    def __init__(self, target):

        self.target   = target
        self.database = copy.deepcopy(new_system_database[self.target.mcu])

        for key, value in target.clock_tree.items():

            if value is None:
                value = ...

            self[key] = value

        # Provide a way to perform brute-forcing conveniently.

        def brute(function):

            success = function()

            if not success:
                raise RuntimeError(
                    f'Failed to brute-force {repr(function.__name__)} '
                    f'for target {repr(target.name)}.'
                )

        def each(key):
            for self[key] in self.database[key]['constraint']:
                yield self(key)


        def satisfied(key, value):
            if value in self.database[key]['constraint']:
                self[key] = value
                return True
            else:
                return False



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



        match target.mcu:



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



        match target.mcu:



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
        # TODO Not implemented yet.
        #



        self['HSE_CK'] = 0
        self['LSE_CK'] = 0



        ################################################################################
        #
        # Peripheral Clock Source.
        # TODO Automate.
        #



        if self('PERIPHERAL_CLOCK_OPTION') is not ...:

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

                    if satisfied(
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
                if self(f'PLL{unit}{channel}_CK') is not ...
            ]

            if not used_channels:
                return True

            self[f'PLL{unit}_ENABLE'] = True

            for _ in each_vco_frequency(unit, kernel_frequency):

                every_channel_satisfied = all(
                    satisfied(
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



        @brute
        def parameterize_plls():

            match target.mcu:



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



        @brute
        def parameterize_scgu():

            for kernel_source in each('SCGU_KERNEL_SOURCE'):



                # CPU.

                if not satisfied(
                    'CPU_DIVIDER',
                    self(kernel_source) / self('CPU_CK')
                ):
                    continue



                # AXI/AHB busses.

                match target.mcu:



                    # There's a divider to configure.

                    case 'STM32H7S3L8H6':

                        if not satisfied(
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
                    satisfied(
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



        @brute
        def parameterize_systick():



            # See if SysTick is even used.

            self['SYSTICK_ENABLE'] = self('SYSTICK_CK') is not ...

            if not self('SYSTICK_ENABLE'):
                return True



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

                    match target.mcu:



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

                    if satisfied(
                        'SYSTICK_RELOAD',
                        self('SYSTICK_KERNEL_FREQ') / self('SYSTICK_CK') - 1
                    ):
                        return True



        ################################################################################
        #
        # UXARTs.
        # TODO Consider maximum kernel frequency.
        #



        for instances in self('UXARTS'):

            @brute
            def parameterize_uxarts():



                # Check if any of the instances are even used.

                used_instances = [
                    (peripheral, unit)
                    for peripheral, unit in instances
                    if self(f'{peripheral}{unit}_BAUD') is not ...
                ]

                if not used_instances:
                    return True



                # Try every available clock source for this
                # set of instances and see what sticks.

                for kernel_source in each(f'UXART_{instances}_KERNEL_SOURCE'):

                    every_instance_satisfied = all(
                        satisfied(
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



            @brute
            def parameterize():



                # See if the unit is even used.

                needed_baud = self(f'I2C{unit}_BAUD')

                if needed_baud is ...:
                    return True



                # We can't get an exact baud-rate for I2C (since there's a lot
                # of factors involved anyways like clock-stretching), we'll have
                # to try every single possibility and find the one with the least
                # amount of error.

                best_baud_error = None

                for kernel_source in each(f'I2C{unit}_KERNEL_SOURCE'):

                    kernel_frequency = self(kernel_source)

                    if kernel_frequency is ...:
                        continue

                    for presc in each(f'I2C{unit}_PRESC'):



                        # Determine the SCL.

                        scl = round(kernel_frequency / (presc + 1) / needed_baud / 2)

                        if scl not in self.database[f'I2C{unit}_SCLH']['constraint']:
                            continue

                        if scl not in self.database[f'I2C{unit}_SCLL']['constraint']:
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

            match target.mcu:



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

                if not satisfied(
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



        @brute
        def parameterize_timers():

            used_units = [
                unit
                for unit in self('TIMERS', ())
                if self(f'TIM{unit}_RATE') is not ...
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




        for key, value in self.database.items():

            if value.get('value', ...) is ...:
                continue

            if isinstance(self.database[key]['constraint'], dict) and 'remapped' not in value:
                value['remapped'] = True
                value['value'] = self.database[key]['constraint'][value['value']]

            if value.get('value', ...) is ...:
                continue

            print(f'{key :<40} | {str(value['category']) :<12} | {value.get('value', '')}')
