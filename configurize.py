import collections, builtins, difflib
from ..stpy.database import system_database
from ..stpy.gpio     import process_all_gpios
from ..stpy.helpers  import get_helpers
from ..pxd.utils     import mk_dict, OrderedSet
from ..pxd.log       import log, ANSI



################################################################################



def get_similars(given, options): # TODO Copy-pasta.

    import difflib

    return difflib.get_close_matches(
        given if given is not None else 'None',
        options,
        n      = 3,
        cutoff = 0
    )



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



def system_configurize(Meta, target, plan):

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
        if interrupt not in system_database[target.mcu]['INTERRUPTS']:

            raise ValueError(
                f'For target {repr(target.name)}, '
                f'no such interrupt {repr(interrupt)} '
                f'exists on {repr(target.mcu)}; '
                f'did you mean any of the following? : '
                f'{difflib.get_close_matches(interrupt, system_database[target.mcu]['INTERRUPTS'].keys(), n = 5, cutoff = 0)}'
            )


    ################################################################################



    # The database is how we will figure out which register to write and where.

    database = system_database[target.mcu]



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
        (
            system_database[target.mcu][f'GPIO{port}_ENABLE'].peripheral,
            system_database[target.mcu][f'GPIO{port}_ENABLE'].register,
            system_database[target.mcu][f'GPIO{port}_ENABLE'].field,
            True
        )
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
            mk_dict(system_database[target.mcu]['GPIO_SPEED'])[gpio.speed]
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
            mk_dict(system_database[target.mcu]['GPIO_PULL'])[gpio.pull]
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
            mk_dict(system_database[target.mcu]['GPIO_MODE'])[gpio.mode]
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
        *system_database[target.mcu]['INTERRUPTS']
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

        if system_database[target.mcu]['INTERRUPTS'].index(interrupt) <= 14:

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
        plan.tuple('FLASH_LATENCY'          ),
        plan.tuple('FLASH_PROGRAMMING_DELAY'),
    )



    # Ensure the new number of wait-states is taken into account.

    CMSIS_SPINLOCK(
        plan.tuple('FLASH_LATENCY'          ),
        plan.tuple('FLASH_PROGRAMMING_DELAY'),
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
        plan.tuple(field)
        for field in fields
        if plan[field] is not None
    )



    # A higher core voltage means higher power consumption,
    # but better performance in terms of max clock speed.

    CMSIS_SET(plan.tuple('INTERNAL_VOLTAGE_SCALING'))



    # Ensure the voltage scaling has been selected.

    CMSIS_SPINLOCK(
        plan.tuple('CURRENT_ACTIVE_VOS'      , plan['INTERNAL_VOLTAGE_SCALING']),
        plan.tuple('CURRENT_ACTIVE_VOS_READY', True                            ),
    )



    ################################################################################



    put_title('Built-in Oscillators')



    # High-speed-internal.

    if plan['HSI_ENABLE']:
        pass # The HSI oscillator is enabled by default after reset.
    else:
        raise NotImplementedError(
            f'Turning off HSI not implemented yet.'
        )



    # High-speed-internal (48MHz).

    if plan['HSI48_ENABLE']:
        CMSIS_SET     (plan.tuple('HSI48_ENABLE', True))
        CMSIS_SPINLOCK(plan.tuple('HSI48_READY' , True))



    # Clock-security-internal.

    if plan['CSI_ENABLE']:
        CMSIS_SET     (plan.tuple('CSI_ENABLE', True))
        CMSIS_SPINLOCK(plan.tuple('CSI_READY' , True))



    ################################################################################



    put_title('Peripheral Clock Source')



    # Set the clock source which will be
    # available for some peripheral to use.

    CMSIS_SET(plan.tuple('PERIPHERAL_CLOCK_OPTION'))



    ################################################################################



    put_title('PLLs')



    # Set up the PLL registers.

    with CMSIS_SET as sets:



        # Set the clock source shared for all PLLs.

        if target.mcu == 'STM32H7S3L8H6':
            sets += [plan.tuple('PLL_KERNEL_SOURCE')]



        # Configure each PLL.

        for unit, channels in database['PLLS']:



            # Set the clock source for this PLL unit.

            if target.mcu == 'STM32H533RET6':
                sets += [plan.tuple(f'PLL{unit}_KERNEL_SOURCE')]



            # Set the PLL's predividers.

            predivider = plan[f'PLL{unit}_PREDIVIDER']

            if predivider is not None:
                sets += [plan.tuple(f'PLL{unit}_PREDIVIDER')]



            # Set each PLL unit's expected input frequency range.

            input_range = plan[f'PLL{unit}_INPUT_RANGE']

            if input_range is not None:
                sets += [plan.tuple(f'PLL{unit}_INPUT_RANGE')]



            # Set each PLL unit's multipler.

            multiplier = plan[f'PLL{unit}_MULTIPLIER']

            if multiplier is not None:
                sets += [plan.tuple(f'PLL{unit}_MULTIPLIER', f'{multiplier} - 1')]



            # Set each PLL unit's output divider and enable the channel.

            for channel in channels:

                divider = plan[f'PLL{unit}_{channel}_DIVIDER']

                if divider is None:
                    continue

                sets += [
                    plan.tuple(f'PLL{unit}{channel}_DIVIDER', f'{divider} - 1'),
                    plan.tuple(f'PLL{unit}{channel}_ENABLE' , True            ),
                ]



    # Enable each PLL unit that is to be used.

    CMSIS_SET(
        plan.tuple(f'PLL{unit}_ENABLE')
        for unit, channels in database['PLLS']
    )



    # Ensure each enabled PLL unit has stabilized.

    for unit, channels in database['PLLS']:

        pllx_enable = plan[f'PLL{unit}_ENABLE']

        if pllx_enable:
            CMSIS_SPINLOCK(plan.tuple(f'PLL{unit}_READY', True))



    ################################################################################



    put_title('System Clock Generation Unit')



    # Configure the SCGU registers.

    match target.mcu:

        case 'STM32H7S3L8H6':
            CMSIS_SET(
                plan.tuple('CPU_DIVIDER'),
                plan.tuple('AXI_AHB_DIVIDER'),
                *(
                    plan.tuple(f'APB{unit}_DIVIDER')
                    for unit in database['APBS']
                ),
            )

        case 'STM32H533RET6':
            CMSIS_SET(
                plan.tuple('CPU_DIVIDER'),
                *(
                    plan.tuple(f'APB{unit}_DIVIDER')
                    for unit in database['APBS']
                ),
            )

        case _: raise NotImplementedError



    # Now switch system clock to the desired source.

    CMSIS_SET(plan.tuple('SCGU_KERNEL_SOURCE'))



    # Wait until the desired source has been selected.

    CMSIS_SPINLOCK(
        plan.tuple('EFFECTIVE_SCGU_KERNEL_SOURCE', plan['SCGU_KERNEL_SOURCE'])
    )



    ################################################################################



    if plan['SYSTICK_ENABLE']:

        put_title('SysTick')

        # @/pg 621/tbl B3-7/`Armv7-M`.
        # @/pg 1861/sec D1.2.239/`Armv8-M`.
        CMSIS_SET(
            plan.tuple('SYSTICK_RELOAD'          ), # Modulation of the counter.
            plan.tuple('SYSTICK_USE_CPU_CK'      ), # Use CPU clock or the vendor-provided one.
            plan.tuple('SYSTICK_COUNTER'         , 0   ), # SYST_CVR value is UNKNOWN on reset.
            plan.tuple('SYSTICK_INTERRUPT_ENABLE', True), # Enable SysTick interrupt, triggered at every overflow.
            plan.tuple('SYSTICK_ENABLE'          , True), # Enable SysTick counter.
        )



    ################################################################################



    for instances in database.get('UXARTS', ()):

        if plan[f'UXART_{instances}_KERNEL_SOURCE'] is None:
            continue

        put_title(' / '.join(f'{peripheral}{number}' for peripheral, number in instances))

        # TODO I honestly don't know how to feel about doing it this way.
        for peripheral, unit in instances:
            Meta.define(f'{peripheral}{unit}_KERNEL_SOURCE_init', plan[f'UXART_{instances}_KERNEL_SOURCE'])

        # TODO Deprecate...?
        Meta.define(
            f'UXART_{'_'.join(str(number) for peripheral, number in instances)}_KERNEL_SOURCE_init',
            plan[f'UXART_{instances}_KERNEL_SOURCE']
        )

        for peripheral, number in instances:

            baud_divider = plan[f'{peripheral}{number}_BAUD_DIVIDER']

            if baud_divider is None:
                continue

            # TODO More consistent naming?
            Meta.define(f'{peripheral}{number}_BRR_BRR_init', baud_divider)

        # TODO Deprecate.
        CMSIS_SET(plan.tuple(f'UXART_{instances}_KERNEL_SOURCE'))



    ################################################################################



    for unit in database.get('I2CS', ()):

        if plan[f'I2C{unit}_KERNEL_SOURCE'] is None:
            continue

        put_title(f'I2C{unit}')

        Meta.define(f'I2C{unit}_KERNEL_SOURCE_init', plan[f'I2C{unit}_KERNEL_SOURCE'])
        Meta.define(f'I2C{unit}_TIMINGR_PRESC_init', plan[f'I2C{unit}_PRESC'        ])
        Meta.define(f'I2C{unit}_TIMINGR_SCL_init'  , plan[f'I2C{unit}_SCL'          ])



    ################################################################################



    if plan.dictionary.get('GLOBAL_TIMER_PRESCALER', None) is not None:

        put_title('Timers')

        Meta.define(f'GLOBAL_TIMER_PRESCALER_init', plan['GLOBAL_TIMER_PRESCALER'])

        for unit in database.get('TIMERS', ()):

            if plan.dictionary.get(f'TIM{unit}_DIVIDER', None) is not None:
                Meta.define(f'TIM{unit}_DIVIDER_init', f'({plan[f'TIM{unit}_DIVIDER']} - 1)')

            if plan.dictionary.get(f'TIM{unit}_MODULATION', None) is not None:
                Meta.define(f'TIM{unit}_MODULATION_init', f'({plan[f'TIM{unit}_MODULATION']} - 1)')



    ################################################################################


    plan.done_configurize()



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
