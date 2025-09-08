from ..stpy.database     import system_database
from ..stpy.parameterize import system_parameterize
from ..stpy.configurize  import system_configurize
from ..pxd.utils         import justify



################################################################################



def do(Meta, target):



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
            for interrupt, niceness in target.interrupts
            if system_database[target.mcu]['INTERRUPTS'].index(interrupt) >= 15
        )
    )



    # Figure out how to configure the MCU
    # based on the target's constraints.

    plan, book = system_parameterize(target)



    # Generate the code to configure the MCU.

    with Meta.enter('''
        extern void
        SYSTEM_init(void)
    '''):

        system_configurize(Meta, target, plan)



    # Export the frequencies we found in the clock-tree.

    for macro, expansion in justify(
        (
            ('<', f'CLOCK_TREE_FREQUENCY_OF_{name}'),
            ('>', f'{frequency :,}'.replace(',', "'")),
        )
        for name, frequency in book.items()
        if name      is not None
        if frequency is not None
    ):
        Meta.define(macro, f'({expansion})')



################################################################################



# TODO Stale.
# @/`Defining Interrupt Handlers`:
#
# Most other applications use weak-symbols as a way to have
# the user be able to declare their interrupt routines, but
# also have a default routine if the user didn't do so.
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
# define an ISR that's not in the target's `interrupts`
# settings; this prevents the bug where the user declares
# an ISR that'll never be executed naturally.
