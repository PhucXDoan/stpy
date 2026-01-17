import deps.stpy.pxd.pxd as pxd
from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize



def init(
    *,
    Meta,
    target,
    mcu,
    schema,
    gpios,
    interrupts,
):



    # Figure out how to configure the target's
    # MCU based on the given parameterization.

    parameterization = Parameterization(
        target,
        mcu,
        schema,
        gpios,
        interrupts,
    )



    # When the schema is None, the parameterization
    # process just verifies the correctness of the
    # other parameters like GPIOs without focusing
    # on the code generation.

    if parameterization.schema is None:
        return



    # For interrupts used by the target that
    # are in NVIC, we create an enumeration so
    # that the user can only enable those specific
    # interrupts. Note that some interrupts, like
    # SysTick, are not a part of NVIC.

    Meta.enums(
        'NVICInterrupt',
        'u32',
        (
            (interrupt.name, f'{interrupt.name}_IRQn')
            for interrupt in parameterization.interrupts
            if interrupt.number >= 0
        )
    )



    # We forward-declare the prototype of
    # the interrupt service routines.

    for name in sorted((
        'INTERRUPT_Default',
        *(
            interrupt.symbol
            for interrupt in parameterization.interrupts
        )
    )):

        Meta.line(f'''
            extern void {name}(void);
        ''')



    # We create the interrupt vector table.

    with Meta.enter('''
        void (* const INTERRUPT_VECTOR_TABLE[])(void) __attribute__((used, section(".INTERRUPT_VECTOR_TABLE"))) =
    ''', '{', '};', indented = True):



        # The first entry in the Arm IVT is actually the
        # initial value of $SP after a reset of the CPU.

        rows = [
            (f'(void*) INITIAL_STACK_ADDRESS', -16, 'Initial Stack Address'),
        ]



        # For interrupts that the target will be using,
        # we put those interrupts into their corresponding
        # slots in the interrupt vector table; everything
        # else will be to the default interrupt handler.

        for table_interrupt_i, table_interrupt in enumerate(MCUS[parameterization.mcu]['INTERRUPTS'].value):

            rows += [(
                next(
                    (
                        target_interrupt.symbol
                        for target_interrupt in parameterization.interrupts
                        if target_interrupt.name == table_interrupt
                    ),
                    f'INTERRUPT_Default'
                ),
                table_interrupt_i - 15,
                'Reserved' if table_interrupt is None else table_interrupt,
            )]



        # Output a nice looking table.

        for word, number, name in pxd.justify(
            (
                ('<' , word  ),
                ('>' , number),
                (None, name  ),
            )
            for word, number, name in rows
        ):
            Meta.line(f'{word}, // [{number}] {name}')



    # @/`Defining Interrupt Handlers`.

    for interrupt in sorted((
        'Default',
        *(
            interrupt.name
            for interrupt in parameterization.interrupts
        )
    )):

        Meta.define(
            f'INTERRUPT_{interrupt}',
            ('...'),
            f'extern void INTERRUPT_{interrupt}(__VA_ARGS__)'
        )



    # Forward-declare the interrupt callback for GPIOs with EXTI.

    for gpio in parameterization.gpios:

        if gpio.interrupt is None:
            continue

        Meta.line(f'''
            static void
            INTERRUPT_EXTIx_{gpio.name}(void);
        ''')



    # When the EXTI interrupt is called,
    # we invoke the callback of the GPIOs associated with it
    # if their interrupt flag is pending.

    for exti_number, gpios in pxd.coalesce(
        (gpio.number, gpio)
        for gpio in parameterization.gpios
        if gpio.interrupt is not None
    ):

        with Meta.enter(f'INTERRUPT_EXTI{exti_number}(void)'):

            for gpio in gpios:

                peripheral, register, field = ( # TODO Dumbest way to do this.
                    MCUS
                        [parameterization.mcu]
                        [f'EXTI{exti_number}_PENDING_{gpio.interrupt}_INTERRUPT']
                ).location

                Meta.line(f'''
                    if (CMSIS_GET({peripheral}, {register}, {field}))
                    {{
                        CMSIS_SET({peripheral}, {register}, {field}, true);
                        INTERRUPT_EXTIx_{gpio.name}();
                    }}
                ''')



    # Make the EXTI interrupt callback macro to ensure
    # no extraneous declarations are made.

    for gpio in parameterization.gpios:

        if gpio.interrupt is None:
            continue

        Meta.define(
            f'INTERRUPT_EXTIx_{gpio.name}',
            ('...'),
            f'static void INTERRUPT_EXTIx_{gpio.name}(__VA_ARGS__)'
        )



    # Configurization.

    with Meta.enter('''
        extern void
        STPY_init(void)
    '''):

        configurize(Meta, parameterization)



    Meta.line('#undef STPY_IMPLEMENTATION')



    # Clock-tree frequencies.

    for macro, expansion in pxd.justify(
        (
            ('<', f'STPY_{key}'),
            ('>', f'{value :,}'.replace(',', "'")),
        )
        for key, value in parameterization.determined.items()
        if value is not TBD
        if MCUS[parameterization.mcu].database[key].clocktree
    ):
        Meta.define(macro, f'({expansion})')



################################################################################



# @/`Defining Interrupt Handlers`:
#
# Most other applications use weak-symbols as a way to have
# the user be able to declare their interrupt routines, but
# also have a default routine to fallback on if the user didn't
# do so.
#
# However, this leaves for a potential bug where the user makes
# a typo and ends up declaring a useless function that the
# linker then ignores and the intended ISR will still be
# referring to the default interrupt handler.
#
# e.g:
# >
# >    extern void
# >    INTERRUPT_I2C1_EB(void)   <- Typo!
# >    {
# >        ...
# >    }
# >
#
# To address this, macros will be made specifically for only
# expected ISRs to be defined by the target. If the macro
# doesn't exist, then this ends up being a compilation error,
# but otherwise the macro expands to the expected function
# prototype.
#
# e.g:
# >
# >    INTERRUPT_I2C1_EB(void)   <- Compile error!
# >    {
# >        ...
# >    }
# >
#
# Not only that, we can also prevent the user from trying to
# define an ISR that's not expected to be used by the target.
