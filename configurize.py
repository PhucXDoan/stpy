import difflib
from ..stpy.parameterization import TBD
from ..stpy.helpers          import get_helpers
from ..pxd.utils             import c_repr



################################################################################



# TODO Factor out.
# These interrupt routines
# will always be around even
# if the target didn't explcitly
# state their usage.

INTERRUPTS_THAT_MUST_BE_DEFINED = (
    'Default',
    'MemManage',
    'BusFault',
    'UsageFault'
)



################################################################################



def system_configurize(Meta, parameterization):



    target         = parameterization.target
    helpers        = get_helpers(Meta)
    CMSIS_SET      = helpers.CMSIS_SET
    CMSIS_WRITE    = helpers.CMSIS_WRITE
    CMSIS_SPINLOCK = helpers.CMSIS_SPINLOCK
    title_of       = lambda title: f'''



        //{f' {title} //'.center(80 - 4, '/')}



    '''



    def define_if_exist(key, *, undefined_ok = False):

        if undefined_ok:
            if (value := parameterization(key, TBD)) is not TBD:

                if parameterization.database[key].off_by_one:
                    formatting = '({} - 1)'
                else:
                    formatting = '{}'

                Meta.define(f'{key}_init', formatting.format(c_repr(value)))
        else:
            if (value := parameterization(key)) is not TBD:

                if parameterization.database[key].off_by_one:
                    formatting = '({} - 1)'
                else:
                    formatting = '{}'

                Meta.define(f'{key}_init', formatting.format(c_repr(value)))



    def tuplize(key, value = ..., *, tbd_ok = False):

        if value is ...:
            value = parameterization(key)

        if value is TBD:
            if tbd_ok:
                return None
            else:
                assert False, key


        if parameterization.database[key].off_by_one:
            formatting = '({} - 1)'
        else:
            formatting = '{}'

        value = formatting.format(c_repr(value))

        return (*parameterization.database[key].location, value)



    ################################################################################
    #
    # GPIOs.
    #



    with Meta.section(title_of('GPIOS')):  # @/`How GPIOs Are Made`:



        # Macros to make GPIOs easy to use.

        for gpio in parameterization.gpios:

            if gpio.pin is None:
                continue

            if gpio.mode in ('INPUT', 'ALTERNATE'):
                Meta.define('_PORT_FOR_GPIO_READ'  , ('NAME'), gpio.port  , NAME = gpio.name)
                Meta.define('_NUMBER_FOR_GPIO_READ', ('NAME'), gpio.number, NAME = gpio.name)

            if gpio.mode == 'OUTPUT':
                Meta.define('_PORT_FOR_GPIO_WRITE'  , ('NAME'), gpio.port  , NAME = gpio.name)
                Meta.define('_NUMBER_FOR_GPIO_WRITE', ('NAME'), gpio.number, NAME = gpio.name)



        # Enable GPIO ports that have defined pins.

        CMSIS_SET(
            (*parameterization.database[f'GPIO{port}_ENABLE'].location, True)
            for port in sorted(dict.fromkeys(
                gpio.port
                for gpio in parameterization.gpios
                if gpio.pin is not None
            ))
        )



        # Set output type (push-pull/open-drain).

        CMSIS_SET(
            (f'GPIO{gpio.port}', 'OTYPER', f'OT{gpio.number}', gpio.open_drain)
            for gpio in parameterization.gpios
            if gpio.pin        is not None
            if gpio.open_drain is not None
        )



        # Set initial output level.

        CMSIS_SET(
            tuplize(f'GPIO{gpio.port}{gpio.number}_OUTPUT', tbd_ok = True)
            for gpio in parameterization.gpios
        )



        # Set drive strength.

        CMSIS_SET(
            tuplize(f'GPIO{gpio.port}{gpio.number}_SPEED', tbd_ok = True)
            for gpio in parameterization.gpios
        )



        # Set pull configuration.

        CMSIS_SET(
            tuplize(f'GPIO{gpio.port}{gpio.number}_PULL', tbd_ok = True)
            for gpio in parameterization.gpios
        )



        # Set alternative function; must be done before setting pin mode
        # so that the alternate function pin will start off properly.

        CMSIS_WRITE(
            tuplize(f'GPIO{gpio.port}{gpio.number}_ALTERNATE_FUNCTION', tbd_ok = True)
            for gpio in parameterization.gpios
        )



        # Set pin mode.

        CMSIS_SET(
            tuplize(f'GPIO{gpio.port}{gpio.number}_MODE', tbd_ok = True)
            for gpio in parameterization.gpios
        )



    ################################################################################
    #
    # Interrupts.
    #



    # Check to make sure the interrupts
    # to be used by the target exists.

    for interrupt, niceness in target.interrupts:

        if interrupt not in parameterization('INTERRUPTS'):

            raise ValueError(
                f'For target {repr(target.name)}, '
                f'no such interrupt {repr(interrupt)} '
                f'exists on {repr(target.mcu)}; '
                f'did you mean any of the following? : '
                f'{difflib.get_close_matches(interrupt, parameterization('INTERRUPTS').keys(), n = 5, cutoff = 0)}'
            )



    with Meta.section(title_of('Interrupts')):



        # @/`Defining Interrupt Handlers`.

        for interrupt in dict.fromkeys((
            *INTERRUPTS_THAT_MUST_BE_DEFINED,
            *parameterization('INTERRUPTS'),
        )):



            # Skip reserved interrupts.

            if interrupt is None:
                continue



            # Skip unused interrupts.

            if interrupt not in (
                *INTERRUPTS_THAT_MUST_BE_DEFINED,
                *(name for name, niceness in target.interrupts)
            ):
                continue



            # The macro will ensure only the
            # expected ISRs can be defined.

            Meta.define(
                f'INTERRUPT_{interrupt}',
                f'extern void INTERRUPT_{interrupt}(void)'
            )



        # Configure the interrupt priorities.

        for interrupt, niceness in target.interrupts:



            # The amount of bits that can be used to specify
            # the priorities vary between implementations.
            # @/pg 526/sec B1.5.4/`Armv7-M`.
            # @/pg 86/sec B3.9/`Armv8-M`.

            Meta.line(f'''
                static_assert(0 <= {niceness} && {niceness} < (1 << __NVIC_PRIO_BITS));
            ''')



            # Set the Arm-specific interrupts' priorities.

            if parameterization('INTERRUPTS').index(interrupt) <= 14:

                assert interrupt in (
                    'MemoryManagement',
                    'BusFault',
                    'UsageFault',
                    'SVCall',
                    'DebugMonitor',
                    'PendSV',
                    'SysTick',
                )

                Meta.line(f'''
                    SCB->SHPR[{interrupt}_IRQn + 12] = {niceness} << __NVIC_PRIO_BITS;
                ''')



            # Set the MCU-specific interrupts' priorities within NVIC.

            else:

                Meta.line(f'''
                    NVIC->IPR[NVICInterrupt_{interrupt}] = {niceness} << __NVIC_PRIO_BITS;
                ''')



        # Enable Arm exceptions.

        CMSIS_SET(
            tuplize('BUS_FAULT_ENABLE'              , True),
            tuplize('MEMORY_MANAGEMENT_FAULT_ENABLE', True),
            tuplize('USAGE_FAULT_ENABLE'            , True),
        )



    ################################################################################
    #
    # Flash.
    #
    # We have to program a delay for reading the flash as it takes time
    # for the data stored in the flash memory to stablize for read operations;
    # this delay varies based on voltage and clock frequency.
    # @/pg 210/sec 5.3.7/`H7S3rm`.
    #



    with Meta.section(title_of('Flash')):



        # Set the wait-states.

        CMSIS_SET(
            tuplize('FLASH_LATENCY'          ),
            tuplize('FLASH_PROGRAMMING_DELAY'),
        )



        # Ensure the new number of wait-states is taken into account.

        CMSIS_SPINLOCK(
            tuplize('FLASH_LATENCY'          ),
            tuplize('FLASH_PROGRAMMING_DELAY'),
        )



    ################################################################################
    #
    # Power Supply.
    #
    # The way the power supply is configured can determine the
    # internal voltage level of the MCU, which can impact the maximum
    # clock speeds of peripherals for instance.
    #



    with Meta.section(title_of('Power Supply')):



        # The power supply setup must be configured first
        # before configuring VOS or the system clock frequency.
        # @/pg 323/sec 6.8.4/`H7S3rm`.

        match target.mcu:

            case 'STM32H7S3L8H6':
                CMSIS_SET(
                    tuplize('SMPS_OUTPUT_LEVEL'      , tbd_ok = True),
                    tuplize('SMPS_FORCED_ON'         , tbd_ok = True),
                    tuplize('SMPS_ENABLE'            , tbd_ok = True),
                    tuplize('LDO_ENABLE'             , tbd_ok = True),
                    tuplize('POWER_MANAGEMENT_BYPASS', tbd_ok = True),
                )

            case 'STM32H533RET6':
                CMSIS_SET(
                    tuplize('LDO_ENABLE'             , tbd_ok = True),
                    tuplize('POWER_MANAGEMENT_BYPASS', tbd_ok = True),
                )

            case _: raise NotImplementedError



        # A higher core voltage means higher power consumption,
        # but better performance in terms of max clock speed.

        CMSIS_SET(tuplize('INTERNAL_VOLTAGE_SCALING'))



        # Ensure the voltage scaling has been selected.

        CMSIS_SPINLOCK(
            tuplize('CURRENT_ACTIVE_VOS'      , parameterization('INTERNAL_VOLTAGE_SCALING')),
            tuplize('CURRENT_ACTIVE_VOS_READY', True),
        )



    ################################################################################
    #
    # HSI Oscillator.
    #



    with Meta.section(title_of('High-Speed-Internal (General)')):

        if parameterization('HSI_ENABLE'):
            pass # The HSI oscillator is enabled by default after reset.

        else:
            raise NotImplementedError # TODO.



    ################################################################################
    #
    # HSI48 Oscillator.
    #



    with Meta.section(title_of('High-Speed-Internal (48MHz)')):

        if parameterization('HSI48_ENABLE'):

            CMSIS_SET     (tuplize('HSI48_ENABLE', True))
            CMSIS_SPINLOCK(tuplize('HSI48_READY' , True))



    ################################################################################
    #
    # CSI Oscillator.
    #



    with Meta.section(title_of('Clock-Security-Internal')):

        if parameterization('CSI_ENABLE'):

            CMSIS_SET     (tuplize('CSI_ENABLE', True))
            CMSIS_SPINLOCK(tuplize('CSI_READY' , True))



    ################################################################################
    #
    # Peripheral Clock Option.
    #



    with Meta.section(title_of('Peripheral Clock Option')):

        CMSIS_SET(tuplize('PERIPHERAL_CLOCK_OPTION', tbd_ok = True))



    ################################################################################
    #
    # PLLs.
    #



    with Meta.section(title_of('PLLs')):



        enabled_plls = [
            (unit, channels)
            for unit, channels in parameterization('PLLS')
            if parameterization(f'PLL{unit}_ENABLE')
        ]

        sets = []



        # Set the clock source shared for all PLLs.

        match target.mcu:
            case 'STM32H7S3L8H6':
                sets += [tuplize('PLL_KERNEL_SOURCE')]



        # Configure each PLL.

        for unit, channels in enabled_plls:



            # Set the clock source for the specific PLL unit.

            match target.mcu:
                case 'STM32H533RET6':
                    sets += [tuplize(f'PLL{unit}_KERNEL_SOURCE')]



            # Configure the PLL unit.

            sets += [
                tuplize(f'PLL{unit}_PREDIVIDER' ),
                tuplize(f'PLL{unit}_INPUT_RANGE'),
                tuplize(f'PLL{unit}_MULTIPLIER' ),
            ]



            # Configure the PLL unit's channels.

            for channel in channels:

                if parameterization(f'PLL{unit}{channel}_DIVIDER') is TBD:
                    continue

                if parameterization(f'PLL{unit}{channel}_DIVIDER') is TBD:
                    continue

                sets += [
                    tuplize(f'PLL{unit}{channel}_DIVIDER'),
                    tuplize(f'PLL{unit}{channel}_ENABLE', True),
                ]



        CMSIS_SET(*sets)



        # Enable each PLL unit that are to be used
        # and ensure they become stablized.

        CMSIS_SET(
            tuplize(f'PLL{unit}_ENABLE')
            for unit, channels in enabled_plls
        )

        CMSIS_SPINLOCK(
            tuplize(f'PLL{unit}_READY', True)
            for unit, channels in enabled_plls
        )



    ################################################################################
    #
    # SCGU.
    #



    with Meta.section(title_of('System Clock Generation Unit')):



        # Configure the SCGU registers.

        match target.mcu:

            case 'STM32H7S3L8H6':

                CMSIS_SET(
                    tuplize('CPU_DIVIDER'),
                    tuplize('AXI_AHB_DIVIDER'),
                    *(
                        tuplize(f'APB{unit}_DIVIDER')
                        for unit in parameterization('APBS')
                    ),
                )



            case 'STM32H533RET6':

                CMSIS_SET(
                    tuplize('CPU_DIVIDER'),
                    *(
                        tuplize(f'APB{unit}_DIVIDER')
                        for unit in parameterization('APBS')
                    ),
                )



            case _: raise NotImplementedError



        # Now switch system clock to the desired source.

        CMSIS_SET(tuplize('SCGU_KERNEL_SOURCE'))



        # Wait until the desired source has been selected.

        CMSIS_SPINLOCK(
            tuplize('EFFECTIVE_SCGU_KERNEL_SOURCE', parameterization('SCGU_KERNEL_SOURCE'))
        )



    ################################################################################
    #
    # SysTick.
    #
    # @/pg 621/tbl B3-7/`Armv7-M`.
    # @/pg 1861/sec D1.2.239/`Armv8-M`.
    #



    with Meta.section(title_of('SysTick')):

        if parameterization('SYSTICK_ENABLE'):

            CMSIS_SET(
                tuplize('SYSTICK_RELOAD'                ),
                tuplize('SYSTICK_USE_CPU_CK'            ),
                tuplize('SYSTICK_COUNTER'         , 0   ),
                tuplize('SYSTICK_INTERRUPT_ENABLE', True),
                tuplize('SYSTICK_ENABLE'                ),
            )



    ################################################################################
    #
    # UXARTs.
    #



    for instances in parameterization('UXARTS', ()):

        with Meta.section(title_of(' / '.join(f'{peripheral}{unit}' for peripheral, unit in instances))):

            for peripheral, unit in instances:
                define_if_exist(f'{peripheral}{unit}_KERNEL_SOURCE')

            for peripheral, unit in instances:
                define_if_exist(f'{peripheral}{unit}_BAUD_DIVIDER')



    ################################################################################
    #
    # I2Cs.
    #



    for unit in parameterization('I2CS', ()):

        with Meta.section(title_of(f'I2C{unit}')):

            define_if_exist(f'I2C{unit}_KERNEL_SOURCE')
            define_if_exist(f'I2C{unit}_PRESC'        )
            define_if_exist(f'I2C{unit}_SCLH'         )
            define_if_exist(f'I2C{unit}_SCLL'         )



    ################################################################################
    #
    # Timers.
    #



    with Meta.section(title_of('Timers')):

        define_if_exist(f'GLOBAL_TIMER_PRESCALER', undefined_ok = True)

        for unit in parameterization('TIMERS', ()):

            define_if_exist(f'TIM{unit}_DIVIDER'   )
            define_if_exist(f'TIM{unit}_MODULATION')



    ################################################################################
