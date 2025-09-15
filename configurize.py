import collections, builtins, difflib
from ..stpy.database import system_properties, system_locations
from ..stpy.gpio     import process_all_gpios
from ..stpy.helpers  import get_helpers
from ..stpy.planner  import SystemPlanner
from ..pxd.utils     import OrderedSet
from ..pxd.log       import log, ANSI



################################################################################



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

    target = parameterization.target
    planner = SystemPlanner(target)

    planner.dictionary = {
        key : value
        for key, (kind, value) in parameterization.dictionary.items()
    }

    properties = system_properties[target.mcu]

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
        if interrupt not in properties['INTERRUPTS']:

            raise ValueError(
                f'For target {repr(target.name)}, '
                f'no such interrupt {repr(interrupt)} '
                f'exists on {repr(target.mcu)}; '
                f'did you mean any of the following? : '
                f'{difflib.get_close_matches(interrupt, properties['INTERRUPTS'].keys(), n = 5, cutoff = 0)}'
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
        (*system_locations[target.mcu][f'GPIO{port}_ENABLE'], True)
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
            properties['GPIO_SPEED'][gpio.speed]
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
            properties['GPIO_PULL'][gpio.pull]
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
            properties['GPIO_MODE'][gpio.mode]
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
        *properties['INTERRUPTS']
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

        if properties['INTERRUPTS'].index(interrupt) <= 14:

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



    CMSIS_SET(
        ('SCB', 'SHCSR', 'BUSFAULTENA', True), # Enable the BusFault exception.
        ('SCB', 'SHCSR', 'MEMFAULTENA', True), # Enable the MemFault exception.
        ('SCB', 'SHCSR', 'USGFAULTENA', True), # Enable the UsageFault exception.
    )



    ################################################################################

    # We have to program a delay for reading the flash as it takes time
    # for the data stored in the flash memory to stablize for read operations;
    # this delay varies based on voltage and clock frequency.
    # @/pg 210/sec 5.3.7/`H7S3rm`.

    put_title('Flash')



    # Set the wait-states.

    CMSIS_SET(
        planner.tuple('FLASH_LATENCY'          ),
        planner.tuple('FLASH_PROGRAMMING_DELAY'),
    )



    # Ensure the new number of wait-states is taken into account.

    CMSIS_SPINLOCK(
        planner.tuple('FLASH_LATENCY'          ),
        planner.tuple('FLASH_PROGRAMMING_DELAY'),
    )



    ################################################################################



    # The way the power supply is configured can determine the
    # internal voltage level of the MCU, which can impact the maximum
    # clock speeds of peripherals for instance.

    put_title('Power Supply')



    # The power supply setup must be configured first
    # before configuring VOS or the system clock frequency.
    # @/pg 323/sec 6.8.4/`H7S3rm`.

    match target.mcu:

        case 'STM32H7S3L8H6':
            fields = (
                'SMPS_OUTPUT_LEVEL',
                'SMPS_FORCED_ON',
                'SMPS_ENABLE',
                'LDO_ENABLE',
                'POWER_MANAGEMENT_BYPASS',
            )

        case 'STM32H533RET6':
            fields = (
                'LDO_ENABLE',
                'POWER_MANAGEMENT_BYPASS',
            )

        case _: raise NotImplementedError

    CMSIS_SET(
        planner.tuple(field)
        for field in fields
        if planner[field] is not None
    )



    # A higher core voltage means higher power consumption,
    # but better performance in terms of max clock speed.

    CMSIS_SET(planner.tuple('INTERNAL_VOLTAGE_SCALING'))



    # Ensure the voltage scaling has been selected.

    CMSIS_SPINLOCK(
        planner.tuple('CURRENT_ACTIVE_VOS'      , planner['INTERNAL_VOLTAGE_SCALING']),
        planner.tuple('CURRENT_ACTIVE_VOS_READY', True                            ),
    )



    ################################################################################



    put_title('Built-in Oscillators')



    # High-speed-internal.

    if planner['HSI_ENABLE']:
        pass # The HSI oscillator is enabled by default after reset.
    else:
        raise NotImplementedError(
            f'Turning off HSI not implemented yet.'
        )



    # High-speed-internal (48MHz).

    if planner['HSI48_ENABLE']:
        CMSIS_SET     (planner.tuple('HSI48_ENABLE', True))
        CMSIS_SPINLOCK(planner.tuple('HSI48_READY' , True))



    # Clock-security-internal.

    if planner['CSI_ENABLE']:
        CMSIS_SET     (planner.tuple('CSI_ENABLE', True))
        CMSIS_SPINLOCK(planner.tuple('CSI_READY' , True))



    ################################################################################



    # Set the clock source which will be
    # available for some peripheral to use.

    if 'PERIPHERAL_CLOCK_OPTION' in planner.dictionary and planner['PERIPHERAL_CLOCK_OPTION'] is not None:

        put_title('Peripheral Clock Source')

        CMSIS_SET(planner.tuple('PERIPHERAL_CLOCK_OPTION'))



    ################################################################################



    put_title('PLLs')



    # Set up the PLL registers.

    with CMSIS_SET as sets:



        # Set the clock source shared for all PLLs.

        if target.mcu == 'STM32H7S3L8H6':
            sets += [planner.tuple('PLL_KERNEL_SOURCE')]



        # Configure each PLL.

        for unit, channels in properties['PLLS']:



            # Set the clock source for this PLL unit.

            if target.mcu == 'STM32H533RET6':
                sets += [planner.tuple(f'PLL{unit}_KERNEL_SOURCE')]



            # Set the PLL's predividers.

            predivider = planner[f'PLL{unit}_PREDIVIDER']

            if predivider is not None:
                sets += [planner.tuple(f'PLL{unit}_PREDIVIDER')]



            # Set each PLL unit's expected input frequency range.

            input_range = planner[f'PLL{unit}_INPUT_RANGE']

            if input_range is not None:
                sets += [planner.tuple(f'PLL{unit}_INPUT_RANGE')]



            # Set each PLL unit's multipler.

            multiplier = planner[f'PLL{unit}_MULTIPLIER']

            if multiplier is not None:
                sets += [planner.tuple(f'PLL{unit}_MULTIPLIER', f'{multiplier} - 1')]



            # Set each PLL unit's output divider and enable the channel.

            for channel in channels:

                divider = planner[f'PLL{unit}{channel}_DIVIDER']

                if divider is None:
                    continue

                sets += [
                    planner.tuple(f'PLL{unit}{channel}_DIVIDER', f'{divider} - 1'),
                    planner.tuple(f'PLL{unit}{channel}_ENABLE' , True            ),
                ]



    # Enable each PLL unit that is to be used.

    CMSIS_SET(
        planner.tuple(f'PLL{unit}_ENABLE')
        for unit, channels in properties['PLLS']
    )



    # Ensure each enabled PLL unit has stabilized.

    for unit, channels in properties['PLLS']:

        pllx_enable = planner[f'PLL{unit}_ENABLE']

        if pllx_enable:
            CMSIS_SPINLOCK(planner.tuple(f'PLL{unit}_READY', True))



    ################################################################################



    put_title('System Clock Generation Unit')



    # Configure the SCGU registers.

    match target.mcu:

        case 'STM32H7S3L8H6':
            CMSIS_SET(
                planner.tuple('CPU_DIVIDER'),
                planner.tuple('AXI_AHB_DIVIDER'),
                *(
                    planner.tuple(f'APB{unit}_DIVIDER')
                    for unit in properties['APBS']
                ),
            )

        case 'STM32H533RET6':
            CMSIS_SET(
                planner.tuple('CPU_DIVIDER'),
                *(
                    planner.tuple(f'APB{unit}_DIVIDER')
                    for unit in properties['APBS']
                ),
            )

        case _: raise NotImplementedError



    # Now switch system clock to the desired source.

    CMSIS_SET(planner.tuple('SCGU_KERNEL_SOURCE'))



    # Wait until the desired source has been selected.

    CMSIS_SPINLOCK(
        planner.tuple('EFFECTIVE_SCGU_KERNEL_SOURCE', planner['SCGU_KERNEL_SOURCE'])
    )



    ################################################################################



    TITLE = None

    def flush_title():
        nonlocal TITLE
        if TITLE is not None:
            put_title(TITLE)
            TITLE = None

    def define(key, formatter = lambda value: value, *, name = ...):

        if name is ...:
            name = f'{key}_init'

        if (value := parameterization(key, None)) is not None:
            flush_title()
            Meta.define(name, formatter(value))

    def mk_tuple(key, value = ...):

        if value is ...:
            value = parameterization(key, None)
            if value is None:
                return None

        return (*system_locations[target.mcu][key], value)


    def cmsis_set(*entries):
        entries = [entry for entry in entries if entry is not None]
        if entries:
            flush_title()
            CMSIS_SET(*entries)


    ################################################################################


    # @/pg 621/tbl B3-7/`Armv7-M`.
    # @/pg 1861/sec D1.2.239/`Armv8-M`.

    title = 'SysTick'

    if planner['SYSTICK_ENABLE']:

        cmsis_set(
            mk_tuple('SYSTICK_RELOAD'                ), # Modulation of the counter.
            mk_tuple('SYSTICK_USE_CPU_CK'            ), # Use CPU clock or the vendor-provided one.
            mk_tuple('SYSTICK_COUNTER'         , 0   ), # SYST_CVR value is UNKNOWN on reset.
            mk_tuple('SYSTICK_INTERRUPT_ENABLE', True), # Enable SysTick interrupt, triggered at every overflow.
            mk_tuple('SYSTICK_ENABLE'                ), # Enable SysTick counter.
        )



    ################################################################################



    for instances in properties.get('UXARTS', ()):

        TITLE = ' / '.join(f'{peripheral}{number}' for peripheral, number in instances)

        for peripheral, unit in instances:
            define(f'UXART_{instances}_KERNEL_SOURCE', name = f'{peripheral}{unit}_KERNEL_SOURCE_init')

        for peripheral, unit in instances:
            define(f'{peripheral}{unit}_BAUD_DIVIDER')



    ################################################################################



    for unit in properties.get('I2CS', ()):

        TITLE = f'I2C{unit}'

        define(f'I2C{unit}_KERNEL_SOURCE')
        define(f'I2C{unit}_PRESC')
        define(f'I2C{unit}_SCL')



    ################################################################################



    TITLE = 'Timers'

    define(f'GLOBAL_TIMER_PRESCALER')

    for unit in properties.get('TIMERS', ()):

        define(f'TIM{unit}_DIVIDER'   , lambda value: f'({value} - 1)')
        define(f'TIM{unit}_MODULATION', lambda value: f'({value} - 1)')



    ################################################################################


    planner.done_configurize()



################################################################################



# TODO Stale.
# In this meta-directive, we take the configuration
# values from `system_parameterize` and generate
# code to set the registers in the right order.
#
# Order matters because some clock sources depend
# on other clock sources, so we have to respect that.
#
# More details at @/`About Parameterization`.
