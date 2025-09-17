from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize



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
