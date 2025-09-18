from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize
from ..pxd.utils             import justify



def init(
    *,
    Meta,
    target,
    mcu,
    schema,
    gpios,
    interrupts,
):



    ################################################################################
    #
    # Parameterization.
    #



    # Figure out how to configure the target's
    # MCU based on the given parameterization.

    parameterization = Parameterization(
        target,
        mcu,
        schema,
        gpios,
        interrupts,
    )



    ################################################################################
    #
    # Interrupts.
    #



    # For interrupts used by the target that
    # are in NVIC, we create an enumeration so
    # that the user can only enable those specific
    # interrupts. Note that some interrupts, like
    # SysTick, are not a part of NVIC.

    Meta.enums(
        'NVICInterrupt',
        'u32',
        (
            (interrupt, f'{interrupt}_IRQn')
            for interrupt in parameterization.interrupts
            if MCUS[parameterization.mcu]['INTERRUPTS'].value.index(interrupt) >= 15
        )
    )



    # We forward-declare the prototype of
    # the interrupt service routines.

    for name in sorted((
        'INTERRUPT_Default',
        *(
            interrupt.symbol
            for interrupt in parameterization.interrupts.values()
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



        # Fill in the addresses of the interrupt routines
        # for the remainder of the interrupt vector table.

        for interrupt_i, interrupt in enumerate(MCUS[parameterization.mcu]['INTERRUPTS'].value):

            word = None

            if interrupt is None:

                # No interrupt handler here.
                word = f'INTERRUPT_Default'

            elif interrupt in parameterization.interrupts:

                # This interrupt will be defined by the user.
                word = parameterization.interrupts[interrupt].symbol

            else:

                # This interrupt isn't expected to be used by the target.
                word = f'INTERRUPT_Default'

            rows += [(
                word,
                interrupt_i - 15,
                'Reserved' if interrupt is None else interrupt,
            )]



        # Output a nice looking table.

        for word, number, name in justify(
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
        *parameterization.interrupts.keys()
    )):

        Meta.define(
            f'INTERRUPT_{interrupt}',
            f'extern void INTERRUPT_{interrupt}(void)'
        )



    ################################################################################
    #
    # Configurization.
    #



    with Meta.enter('''
        extern void
        STPY_init(void)
    '''):

        configurize(Meta, parameterization)



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
# >    INTERRUPT_I2C1_EB   <- Typo!
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
# >    INTERRUPT_I2C1_EB   <- Compile error!
# >    {
# >        ...
# >    }
# >
#
# Not only that, we can also prevent the user from trying to
# define an ISR that's not expected to be used by the target.
