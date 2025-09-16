import collections, builtins, difflib
from ..stpy.parameterization import TBD
from ..stpy.gpio             import process_all_gpios
from ..stpy.helpers          import get_helpers
from ..pxd.utils             import OrderedSet, c_repr
from ..pxd.log               import log, ANSI



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

    target     = parameterization.target

    def put_title(title = None):

        if title is None:

            Meta.line(f'''

                {"/" * 128}

            ''')

        else:

            Meta.line(f'''

                {"/" * 64} {title} {"/" * 64}

            ''')

    helpers = get_helpers(Meta)

    CMSIS_SET      = helpers.CMSIS_SET
    CMSIS_WRITE    = helpers.CMSIS_WRITE
    CMSIS_SPINLOCK = helpers.CMSIS_SPINLOCK




    ################################################################################

    # TODO Placement?

    # Check to make sure the interrupts
    # to be used by the target eists.

    for interrupt, niceness in target.interrupts:
        if interrupt not in parameterization('INTERRUPTS'):

            raise ValueError(
                f'For target {repr(target.name)}, '
                f'no such interrupt {repr(interrupt)} '
                f'exists on {repr(target.mcu)}; '
                f'did you mean any of the following? : '
                f'{difflib.get_close_matches(interrupt, parameterization('INTERRUPTS').keys(), n = 5, cutoff = 0)}'
            )



    ################################################################################

    put_title('GPIOs') # @/`How GPIOs Are Made`:

    gpios = process_all_gpios(target)



    # Macros to make GPIOs easy to use.

    for gpio in gpios:

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
        for port in sorted(OrderedSet(
            gpio.port
            for gpio in gpios
            if gpio.pin is not None
        ))
    )



    # Set output type (push-pull/open-drain).

    CMSIS_SET(
        (f'GPIO{gpio.port}', 'OTYPER', f'OT{gpio.number}', gpio.open_drain)
        for gpio in gpios
        if gpio.pin        is not None
        if gpio.open_drain is not None
    )



    # Set initial output level.

    CMSIS_SET(
        (f'GPIO{gpio.port}', 'ODR', f'OD{gpio.number}', gpio.initlvl)
        for gpio in gpios
        if gpio.pin     is not None
        if gpio.initlvl is not None
    )



    # Set drive strength.

    CMSIS_SET(
        (
            f'GPIO{gpio.port}',
            'OSPEEDR',
            f'OSPEED{gpio.number}',
            parameterization('GPIO_SPEED')[gpio.speed]
        )
        for gpio in gpios
        if gpio.pin   is not None
        if gpio.speed is not None
    )



    # Set pull configuration.

    CMSIS_SET(
        (
            f'GPIO{gpio.port}',
            'PUPDR',
            f'PUPD{gpio.number}',
            parameterization('GPIO_PULL')[gpio.pull]
        )
        for gpio in gpios
        if gpio.pin  is not None
        if gpio.pull is not None
    )



    # Set alternative function; must be done before setting pin mode
    # so that the alternate function pin will start off properly.

    CMSIS_WRITE(
        (
            f'GPIO_AFR{('L', 'H')[gpio.number // 8]}',
            f'GPIO{gpio.port}->AFR[{gpio.number // 8}]',
            f'AFSEL{gpio.number}',
            gpio.afsel
        )
        for gpio in gpios
        if gpio.afsel is not None
    )



    # Set pin mode.

    CMSIS_SET(
        (
            f'GPIO{gpio.port}',
            'MODER',
            f'MODE{gpio.number}',
            parameterization('GPIO_MODE')[gpio.mode]
        )
        for gpio in gpios
        if gpio.pin  is not None
        if gpio.mode not in (None, 'RESERVED')
    )



    ################################################################################



    put_title('Interrupts')



    # @/`Defining Interrupt Handlers`.

    for routine in OrderedSet((
        *INTERRUPTS_THAT_MUST_BE_DEFINED,
        *parameterization('INTERRUPTS')
    )):



        # Skip reserved interrupts.

        if routine is None:
            continue



        # Skip unused interrupts.

        if routine not in (
            *INTERRUPTS_THAT_MUST_BE_DEFINED,
            *(name for name, niceness in target.interrupts)
        ):
            continue



        # The macro will ensure only the
        # expected ISRs can be defined.

        Meta.define(
            f'INTERRUPT_{routine}',
            f'extern void INTERRUPT_{routine}(void)'
        )



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



    ################################################################################



    TITLE = None

    def flush_title():
        nonlocal TITLE
        if TITLE is not None:
            put_title(TITLE)
            TITLE = None









    def define_if_exist(key, *, undefined_ok = False):

        if undefined_ok:
            if (value := parameterization(key, TBD)) is not TBD:

                flush_title()

                if parameterization.database[key].off_by_one:
                    formatting = '({} - 1)'
                else:
                    formatting = '{}'

                Meta.define(f'{key}_init', formatting.format(c_repr(value)))
        else:
            if (value := parameterization(key)) is not TBD:

                flush_title()

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



    def cmsis_set(*entries):
        entries = [entry for entry in entries if entry is not None]
        if entries:
            flush_title()
            CMSIS_SET(*entries)

    def cmsis_spinlock(*entries):
        entries = [entry for entry in entries if entry is not None]
        if entries:
            flush_title()
            CMSIS_SPINLOCK(*entries)




    ################################################################################
    #
    # Interrupts.
    #



    CMSIS_SET(
        ('SCB', 'SHCSR', 'BUSFAULTENA', True), # Enable the BusFault exception.
        ('SCB', 'SHCSR', 'MEMFAULTENA', True), # Enable the MemFault exception.
        ('SCB', 'SHCSR', 'USGFAULTENA', True), # Enable the UsageFault exception.
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



    TITLE = 'Flash'



    # Set the wait-states.

    cmsis_set(
        tuplize('FLASH_LATENCY'          ),
        tuplize('FLASH_PROGRAMMING_DELAY'),
    )



    # Ensure the new number of wait-states is taken into account.

    cmsis_spinlock(
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



    TITLE = 'Power Supply'



    # The power supply setup must be configured first
    # before configuring VOS or the system clock frequency.
    # @/pg 323/sec 6.8.4/`H7S3rm`.

    match target.mcu:

        case 'STM32H7S3L8H6':
            cmsis_set(
                tuplize('SMPS_OUTPUT_LEVEL'      , tbd_ok = True),
                tuplize('SMPS_FORCED_ON'         , tbd_ok = True),
                tuplize('SMPS_ENABLE'            , tbd_ok = True),
                tuplize('LDO_ENABLE'             , tbd_ok = True),
                tuplize('POWER_MANAGEMENT_BYPASS', tbd_ok = True),
            )

        case 'STM32H533RET6':
            cmsis_set(
                tuplize('LDO_ENABLE'             , tbd_ok = True),
                tuplize('POWER_MANAGEMENT_BYPASS', tbd_ok = True),
            )

        case _: raise NotImplementedError



    # A higher core voltage means higher power consumption,
    # but better performance in terms of max clock speed.

    cmsis_set(tuplize('INTERNAL_VOLTAGE_SCALING'))



    # Ensure the voltage scaling has been selected.

    cmsis_spinlock(
        tuplize('CURRENT_ACTIVE_VOS'      , parameterization('INTERNAL_VOLTAGE_SCALING')),
        tuplize('CURRENT_ACTIVE_VOS_READY', True),
    )



    ################################################################################
    #
    # HSI Oscillator.
    #



    TITLE = 'High-Speed-Internal (General)'

    if parameterization('HSI_ENABLE'):
        pass # The HSI oscillator is enabled by default after reset.

    else:
        raise NotImplementedError # TODO.



    ################################################################################
    #
    # HSI48 Oscillator.
    #



    TITLE = 'High-Speed-Internal (48MHz)'

    if parameterization('HSI48_ENABLE'):

        cmsis_set     (tuplize('HSI48_ENABLE', True))
        cmsis_spinlock(tuplize('HSI48_READY' , True))



    ################################################################################
    #
    # CSI Oscillator.
    #



    TITLE = 'Clock-Security-Internal'

    if parameterization('CSI_ENABLE'):

        cmsis_set     (tuplize('CSI_ENABLE', True))
        cmsis_spinlock(tuplize('CSI_READY' , True))



    ################################################################################
    #
    # Peripheral Clock Option.
    #



    TITLE = 'Peripheral Clock Option'

    cmsis_set(tuplize('PERIPHERAL_CLOCK_OPTION', tbd_ok = True))



    ################################################################################
    #
    # PLLs.
    #



    TITLE = 'PLLs'



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



    cmsis_set(*sets)



    # Enable each PLL unit that are to be used
    # and ensure they become stablized.

    cmsis_set(*(
        tuplize(f'PLL{unit}_ENABLE')
        for unit, channels in enabled_plls
    ))

    cmsis_spinlock(*(
        tuplize(f'PLL{unit}_READY', True)
        for unit, channels in enabled_plls
    ))



    ################################################################################
    #
    # SCGU.
    #



    TITLE = 'System Clock Generation Unit'



    # Configure the SCGU registers.

    match target.mcu:

        case 'STM32H7S3L8H6':

            cmsis_set(
                tuplize('CPU_DIVIDER'),
                tuplize('AXI_AHB_DIVIDER'),
                *(
                    tuplize(f'APB{unit}_DIVIDER')
                    for unit in parameterization('APBS')
                ),
            )



        case 'STM32H533RET6':

            cmsis_set(
                tuplize('CPU_DIVIDER'),
                *(
                    tuplize(f'APB{unit}_DIVIDER')
                    for unit in parameterization('APBS')
                ),
            )



        case _: raise NotImplementedError



    # Now switch system clock to the desired source.

    cmsis_set(tuplize('SCGU_KERNEL_SOURCE'))



    # Wait until the desired source has been selected.

    cmsis_spinlock(
        tuplize('EFFECTIVE_SCGU_KERNEL_SOURCE', parameterization('SCGU_KERNEL_SOURCE'))
    )



    ################################################################################
    #
    # SysTick.
    #
    # @/pg 621/tbl B3-7/`Armv7-M`.
    # @/pg 1861/sec D1.2.239/`Armv8-M`.
    #



    TITLE = 'SysTick'

    if parameterization('SYSTICK_ENABLE'):

        cmsis_set(
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

        TITLE = ' / '.join(f'{peripheral}{unit}' for peripheral, unit in instances)

        for peripheral, unit in instances:
            define_if_exist(f'{peripheral}{unit}_KERNEL_SOURCE')

        for peripheral, unit in instances:
            define_if_exist(f'{peripheral}{unit}_BAUD_DIVIDER')



    ################################################################################
    #
    # I2Cs.
    #



    for unit in parameterization('I2CS', ()):

        TITLE = f'I2C{unit}'

        define_if_exist(f'I2C{unit}_KERNEL_SOURCE')
        define_if_exist(f'I2C{unit}_PRESC'        )
        define_if_exist(f'I2C{unit}_SCLH'         )
        define_if_exist(f'I2C{unit}_SCLL'         )



    ################################################################################
    #
    # Timers.
    #



    TITLE = 'Timers'

    define_if_exist(f'GLOBAL_TIMER_PRESCALER', undefined_ok = True)

    for unit in parameterization('TIMERS', ()):

        define_if_exist(f'TIM{unit}_DIVIDER'   )
        define_if_exist(f'TIM{unit}_MODULATION')



    ################################################################################
