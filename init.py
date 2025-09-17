from ..stpy.mcus             import MCUS, TBD
from ..stpy.parameterization import Parameterization
from ..stpy.configurize      import configurize
from ..pxd.utils             import justify



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



    # TODO.

    for interrupt in sorted(dict.fromkeys((
        'Reset',
        *target.interrupts_that_must_be_defined,
        *(name for name, niceness in target.interrupts)
    ))):

        Meta.line(f'''
            extern void INTERRUPT_{interrupt}(void);
            extern nullptr_t LINK_stack_addr[];
        ''')



    # TODO.

    with Meta.enter('''
        void (* const INTERRUPT_VECTOR_TABLE[])(void) __attribute__((used, section(".vector_table"))) =
    ''', '{', '};', indented = True):

        rows = [
            (f'(void*) &LINK_stack_addr', -16, 'Initial Stack Address'),
        ]

        for interrupt_i, interrupt_name in enumerate(MCUS[target.mcu]['INTERRUPTS'].value):

            interrupt_number = interrupt_i - 15

            word = None

            if interrupt_name is None:

                # No interrupt handler here.
                word = f'INTERRUPT_Default'

            elif target.use_freertos and interrupt_name in MCUS[target.mcu].freertos_interrupts:

                # This interrupt will be supplied by FreeRTOS.
                word = f'{MCUS[target.mcu].freertos_interrupts[interrupt_name]}'

            elif interrupt_name in (
                'Reset',
                *target.interrupts_that_must_be_defined,
                *(name for name, niceness in target.interrupts)
            ):

                # This interrupt must be defined somewhere.
                word = f'INTERRUPT_{interrupt_name}'

            else:

                # This interrupt isn't expected to be used by the target.
                word = f'INTERRUPT_Default'

            rows += [(
                word,
                interrupt_number,
                'Reserved' if interrupt_name is None else interrupt_name,
            )]



        # Output nice looking table.

        for word, interrupt_number, name in justify(
            (
                ('<' , word            ),
                ('>' , interrupt_number),
                (None, name            ),
            )
            for word, interrupt_number, name in rows
        ):
            Meta.line(f'{word}, // [{interrupt_number}] {name}')



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
