import collections, types
from ..stpy.mcus import MCUS
from ..pxd.utils import coalesce, c_repr, justify



def get_helpers(Meta):



    ################################################################################



    # @/url:`github.com/PhucXDoan/phucxdoan.github.io/wiki/Macros-for-Reading-and-Writing-to-Memory%E2%80%90Mapped-Registers`.

    class CMSIS_MODIFY:



        # This class is just a support to define CMSIS_SET
        # and CMSIS_WRITE in the meta-preprocessor;
        # the only difference in the output is which
        # CMSIS_SET/WRITE macro is being used.

        def __init__(self, macro):
            self.macro = macro



        # The most common usage of CMSIS_SET/WRITE in
        # the meta-preprocessor is to mimic how the
        # CMSIS_SET/WRITE macros would be called in C code.

        def __call__(self, *modifies):



            # e.g:
            # >
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DCTRL', 'DTEN', True),
            # >    )
            # >

            if len(modifies) == 1:
                modifies, = modifies



            # e.g:
            # >
            # >    CMSIS_SET(x for x in xs)
            # >

            if modifies is None:
                modifies = ()
            else:
                modifies = tuple(modifies)



            # e.g:
            # >
            # >    CMSIS_SET(())
            # >

            modifies = [
                modify
                for modify in modifies
                if modify is not None
            ]

            if len(modifies) == 0:
                return



            # If multiple fields of the same register are to be modified,
            # the caller can format it to look like a table.
            #
            # Before:
            # >
            # >    CMSIS_SET(
            # >        'SDMMC' , 'DCTRL',
            # >        'DTEN'  , True   ,
            # >        'DTDIR' , False  ,
            # >        'DTMODE', 0b10   ,
            # >    )
            # >
            #
            # After:
            # >
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DCTRL', 'DTEN'  , True ),
            # >        ('SDMMC', 'DCTRL', 'DTDIR' , False),
            # >        ('SDMMC', 'DCTRL', 'DTMODE', 0b10 ),
            # >    )
            # >

            if not isinstance(modifies[0], tuple):
                modifies = tuple(
                    (modifies[0], modifies[1], modifies[i], modifies[i + 1])
                    for i in range(2, len(modifies), 2)
                )



            # Multiple RMWs to different registers can be done
            # within a single CMSIS_SET/WRITE macro. This is mostly
            # for convenience and only should be done when the
            # effects of the registers are independent of each other.
            #
            # Before:
            # >
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DCTRL' , 'DTEN'    , True  ),
            # >        ('SDMMC', 'DTIMER', 'DATATIME', 1234  ),
            # >        ('I2C'  , 'CR1'   , 'DNF'     , 0b1001),
            # >        ('SDMMC', 'DCTRL' , 'DTDIR'   , False ),
            # >    )
            # >
            #
            # After:
            # >
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DCTRL', 'DTEN' , True ),
            # >        ('SDMMC', 'DCTRL', 'DTDIR', False),
            # >    )
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DTIMER', 'DATATIME', 1234),
            # >    )
            # >    CMSIS_SET(
            # >        ('I2C', 'CR1', 'DNF', 0b1001),
            # >    )
            # >

            modifies = dict(coalesce(
                ((peripheral, register), (field, c_repr(value)))
                for peripheral, register, field, value in modifies
            ))



            # Find any field that'd be modified more than once.
            # e.g:
            # >
            # >    CMSIS_SET(
            # >        ('SDMMC', 'DCTRL' , 'DTEN'    , True  ),
            # >        ('SDMMC', 'DTIMER', 'DATATIME', 1234  ),
            # >        ('I2C'  , 'CR1'   , 'DNF'     , 0b1001),
            # >        ('SDMMC', 'DCTRL' , 'DTDIR'   , False ),
            # >        ('I2C'  , 'CR1'   , 'DNF'     , 0b0110), <- Duplicate!
            # >    )
            # >

            for (peripheral, register), field_values in modifies.items():

                if duplicate_fields := [
                    field
                    for field, count in collections.Counter(
                        field for field, value in field_values
                    ).items()
                    if count >= 2
                ]:

                    duplicate_field, *_ = duplicate_fields

                    raise ValueError(
                        f'Modifying field {repr(duplicate_field)} more than once.'
                    )



            # Output the proper call to the CMSIS_SET/WRITE macro.

            for (peripheral, register), field_values in modifies.items():

                match field_values:



                    # Single-lined output.
                    # e.g:
                    # >
                    # >    CMSIS_SET(a, b, c, d)
                    # >

                    case [(field, value)]:

                        Meta.line(f'''
                            {self.macro}({peripheral}, {register}, {field}, {value});
                        ''')



                    # Multi-lined output.
                    # e.g:
                    # >
                    # >    CMSIS_SET(
                    # >        a, b,
                    # >        c, d,
                    # >        e, f,
                    # >        g, h,
                    # >    )
                    # >

                    case _:

                        with Meta.enter(self.macro, '(', ');'):

                            for lhs, rhs in justify(
                                (
                                    ('<', lhs),
                                    ('<', rhs),
                                )
                                for lhs, rhs in (
                                    (peripheral, register),
                                    *field_values
                                )
                            ):
                                Meta.line(f'{lhs}, {rhs},')



        # The CMSIS_SET/WRITE functions in the meta-preprocessor
        # can also be used as a context manager.
        #
        # For example:
        # >
        # >    with CMSIS_SET as sets:
        # >        sets += [('SDMMC', 'DCTRL' , 'DTEN'    , True  )]
        # >        sets += [('SDMMC', 'DTIMER', 'DATATIME', 1234  )]
        # >        sets += [('I2C'  , 'CR1'   , 'DNF'     , 0b1001)]
        # >        sets += [('SDMMC', 'DCTRL' , 'DTDIR'   , False )]
        # >
        #
        # The above is equivalent to:
        # >
        # >    CMSIS_SET(
        # >        ('SDMMC', 'DCTRL' , 'DTEN'    , True  ),
        # >        ('SDMMC', 'DTIMER', 'DATATIME', 1234  ),
        # >        ('I2C'  , 'CR1'   , 'DNF'     , 0b1001),
        # >        ('SDMMC', 'DCTRL' , 'DTDIR'   , False ),
        # >   )
        # >
        #
        # The benefit of this syntax is that the logic
        # can be arbitrarily complicated in determining
        # what fields of what registers need to be modified.
        #
        # TODO Somehow enforce no code can be generated
        #      until the context manager is exited?

        def __enter__(self):
            self.modifies = []
            return self.modifies

        def __exit__(self, *exception_info):
            self(self.modifies)



    ################################################################################



    def CMSIS_SPINLOCK(*spinlocks):



        if len(spinlocks) == 1:
            spinlocks, = spinlocks



        # Spinlocking on multiple fields.
        # e.g:
        # >
        # >    CMSIS_SPINLOCK(
        # >        ('IWDG' , 'SR' , 'WVU'    , False ),
        # >        ('IWDG' , 'SR' , 'RVU'    , True  ),
        # >        ('FLASH', 'ACR', 'LATENCY', 0b1111),
        # >    )
        # >

        if all(isinstance(spinlock, tuple) for spinlock in spinlocks):
            pass



        # Spinlocking on just a single field.
        # e.g:
        # >
        # >    CMSIS_SPINLOCK('IWDG', 'SR', 'WVU', False)
        # >

        else:
            spinlocks = [spinlocks]



        # Output the code to spinlock on the fields until they match the expected value.
        #
        # Before:
        # >
        # >    CMSIS_SPINLOCK('FLASH', 'ACR', 'LATENCY', 0b1111)
        # >
        #
        # After:
        # >
        # >    while (CMSIS_GET(FLASH, ACR, LATENCY) != 0b1111);
        # >

        spinlocks = [
            spinlock
            for spinlock in spinlocks
            if spinlock is not None
        ]

        for peripheral, register, field, value in spinlocks:

            value = c_repr(value)

            match value:
                case 'true'  : Meta.line(f'while (!CMSIS_GET({peripheral}, {register}, {field}));')
                case 'false' : Meta.line(f'while (CMSIS_GET({peripheral}, {register}, {field}));')
                case _       : Meta.line(f'while (CMSIS_GET({peripheral}, {register}, {field}) != {value});')



    ################################################################################



    def CMSIS_TUPLE(mcu, key): # TODO How useful is this?

        peripheral, register, field = MCUS[mcu][key].location

        return '(struct CMSISTuple) {{ {}, {}, {} }}'.format(
            f'&{peripheral}->{register}',
            f'{peripheral}_{register}_{field}_Pos',
            f'{peripheral}_{register}_{field}_Msk',
        )



    ################################################################################



    return types.SimpleNamespace(
        CMSIS_SET      = CMSIS_MODIFY('CMSIS_SET'),
        CMSIS_WRITE    = CMSIS_MODIFY('CMSIS_WRITE'),
        CMSIS_SPINLOCK = CMSIS_SPINLOCK,
        CMSIS_TUPLE    = CMSIS_TUPLE,
    )
