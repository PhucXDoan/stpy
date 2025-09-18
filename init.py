import difflib
from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize
from ..pxd.utils             import justify



def init(Meta, target):



    ################################################################################



    # Check to make sure the interrupts
    # to be used by the target exists.

    for interrupt, niceness, properties in target.interrupts:

        if interrupt not in MCUS[target.mcu]['INTERRUPTS'].value:

            raise ValueError(
                f'For target {repr(target.name)}, '
                f'no such interrupt {repr(interrupt)} '
                f'exists on {repr(target.mcu)}; '
                f'did you mean any of the following? : '
                f'{difflib.get_close_matches(
                    str(interrupt),
                    map(str, MCUS[target.mcu]['INTERRUPTS'].value),
                    n      = 5,
                    cutoff = 0
                )}'
            )



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
            for interrupt, niceness, properties in target.interrupts
            if MCUS[target.mcu]['INTERRUPTS'].value.index(interrupt) >= 15
        )
    )



    # We forward-declare the prototype of
    # the interrupt service routines.

    for name in sorted((
        'INTERRUPT_Default',
        *(properties.get('symbol_name', f'INTERRUPT_{name}') for name, niceness, properties in target.interrupts)
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

        for interrupt_i, interrupt in enumerate(MCUS[target.mcu]['INTERRUPTS'].value):

            word = None

            if interrupt is None:

                # No interrupt handler here.
                word = f'INTERRUPT_Default'

            elif (symbol_name := {
                name : properties['symbol_name']
                for name, niceness, properties in target.interrupts
                if 'symbol_name' in properties
            }.get(interrupt, None)) is not None:

                # This interrupt will go by an alternative symbol name.
                word = symbol_name

            elif interrupt in (
                'Default',
                *(name for name, niceness, properties in target.interrupts)
            ):

                # This interrupt will be defined by the user.
                word = f'INTERRUPT_{interrupt}'

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
        *(name for name, niceness, properties in target.interrupts)
    )):

        Meta.define(
            f'INTERRUPT_{interrupt}',
            f'extern void INTERRUPT_{interrupt}(void)'
        )



    ################################################################################



    # Figure out how to configure the target's
    # MCU based on the given parameterization.

    parameterization = Parameterization(target)



    # Create the procedure that'll initialize
    # most of the target's MCU.

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
