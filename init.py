from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize



################################################################################



def init(Meta, target):



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
            if MCUS[target.mcu]['INTERRUPTS'].value.index(interrupt) >= 15
        )
    )



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
