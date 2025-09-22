global APBS
APBS = (
    1,
    2,
    3,
)



global PLLS
PLLS = (
    (1, ('P', 'Q', 'R')),
    (2, ('P', 'Q', 'R')),
    (3, ('P', 'Q', 'R')),
)



global GPIOS
GPIOS = tuple((port, tuple(range(0, 16))) for port in 'ABCDEFGHI')



global UXARTS
UXARTS = (
    (('USART', 1),),
    (('USART', 2),),
    (('USART', 3),),
    (('UART' , 4),),
    (('UART' , 5),),
    (('USART', 6),),
)



global I2CS
I2CS = (
    1,
    2,
    3,
)



global SPIS
SPIS = (
    1,
    2,
    3,
    4,
)



global TIMERS
TIMERS = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    12,
    15,
)


global INTERRUPTS
INTERRUPTS = (
    'Reset',
    'NonMaskableInt',
    'HardFault',
    'MemoryManagement',
    'BusFault',
    'UsageFault',
    'SecureFault',
    None,
    None,
    None,
    'SVCall',
    'DebugMonitor',
    None,
    'PendSV',
    'SysTick',
    'WWDG',
    'PVD_AVD',
    'RTC',
    'RTC_S',
    'TAMP',
    'RAMCFG',
    'FLASH',
    'FLASH_S',
    'GTZC',
    'RCC',
    'RCC_S',
    'EXTI0',
    'EXTI1',
    'EXTI2',
    'EXTI3',
    'EXTI4',
    'EXTI5',
    'EXTI6',
    'EXTI7',
    'EXTI8',
    'EXTI9',
    'EXTI10',
    'EXTI11',
    'EXTI12',
    'EXTI13',
    'EXTI14',
    'EXTI15',
    'GPDMA1_Channel0',
    'GPDMA1_Channel1',
    'GPDMA1_Channel2',
    'GPDMA1_Channel3',
    'GPDMA1_Channel4',
    'GPDMA1_Channel5',
    'GPDMA1_Channel6',
    'GPDMA1_Channel7',
    'IWDG',
    'SAES',
    'ADC1',
    'DAC1',
    'FDCAN1_IT0',
    'FDCAN1_IT1',
    'TIM1_BRK',
    'TIM1_UP',
    'TIM1_TRG_COM',
    'TIM1_CC',
    'TIM2',
    'TIM3',
    'TIM4',
    'TIM5',
    'TIM6',
    'TIM7',
    'I2C1_EV',
    'I2C1_ER',
    'I2C2_EV',
    'I2C2_ER',
    'SPI1',
    'SPI2',
    'SPI3',
    'USART1',
    'USART2',
    'USART3',
    'UART4',
    'UART5',
    'LPUART1',
    'LPTIM1',
    'TIM8_BRK',
    'TIM8_UP',
    'TIM8_TRG_COM',
    'TIM8_CC',
    'ADC2',
    'LPTIM2',
    'TIM15',
    None,
    None,
    'USB_DRD_FS',
    'CRS',
    'UCPD1',
    'FMC',
    'OCTOSPI1',
    'SDMMC1',
    'I2C3_EV',
    'I2C3_ER',
    'SPI4',
    None,
    None,
    'USART6',
    None,
    None,
    None,
    None,
    'GPDMA2_Channel0',
    'GPDMA2_Channel1',
    'GPDMA2_Channel2',
    'GPDMA2_Channel3',
    'GPDMA2_Channel4',
    'GPDMA2_Channel5',
    'GPDMA2_Channel6',
    'GPDMA2_Channel7',
    None,
    None,
    None,
    None,
    None,
    'FPU',
    'ICACHE',
    'DCACHE1',
    None,
    None,
    'DCMI_PSSI',
    'FDCAN2_IT0',
    'FDCAN2_IT1',
    None,
    None,
    'DTS',
    'RNG',
    'OTFDEC1',
    'AES',
    'HASH',
    'PKA',
    'CEC',
    'TIM12',
    None,
    None,
    'I3C1_EV',
    'I3C1_ER',
    None,
    None,
    None,
    None,
    None,
    None,
    'I3C2_EV',
    'I3C2_ER',
)



global PLL_CHANNEL_FREQ
PLL_CHANNEL_FREQ = RealMinMax(1_000_000, 250_000_000)



global CPU_FREQ
CPU_FREQ = RealMinMax(0, 250_000_000)



global AXI_AHB_FREQ
AXI_AHB_FREQ = RealMinMax(0, 250_000_000)



global APB_FREQ
APB_FREQ = RealMinMax(0, 250_000_000)



global HSI_DEFAULT_FREQUENCY
HSI_DEFAULT_FREQUENCY = 32_000_000



global APB_PERIPHERALS
APB_PERIPHERALS = {
    'TIM2'  : 1,
    'TIM3'  : 1,
    'TIM4'  : 1,
    'TIM5'  : 1,
    'TIM6'  : 1,
    'TIM7'  : 1,
    'TIM12' : 1,
    'TIM1'  : 2,
    'TIM8'  : 2,
    'TIM15' : 2,
}



global GLOBAL_TIMER_PRESCALER_MULTIPLIER_TABLE
GLOBAL_TIMER_PRESCALER_MULTIPLIER_TABLE = {
    (False, 1 ) : 1,
    (False, 2 ) : 1,
    (False, 4 ) : 1 / 2,
    (False, 8 ) : 1 / 4,
    (False, 16) : 1 / 8,
    (True , 1 ) : 1,
    (True , 2 ) : 1,
    (True , 4 ) : 1 / 2,
    (True , 8 ) : 1 / 2,
    (True , 16) : 1 / 4,
}



UXART_KERNEL_SOURCE_TABLE = (
    (
        (
            ('USART10SEL', (('USART', 10),)),
            ('UART9SEL'  , (('UART' , 9 ),)),
            ('UART8SEL'  , (('UART' , 8 ),)),
            ('UART7SEL'  , (('UART' , 7 ),)),
            ('USART6SEL' , (('USART', 6 ),)),
            ('UART5SEL'  , (('UART' , 5 ),)),
            ('UART4SEL'  , (('UART' , 4 ),)),
            ('USART3SEL' , (('USART', 3 ),)),
            ('USART2SEL' , (('USART', 2 ),)),
        ),
        Mapping({
            'APB1_CK'  : '0b000',
            'PLL2Q_CK' : '0b001',
            'PLL3Q_CK' : '0b010',
            'HSI_CK'   : '0b011',
            'CSI_CK'   : '0b100',
            'LSE_CK'   : '0b101',
            0          : '0b110',
        }),
    ),
    (
        (
            ('USART1SEL', (('USART', 1),)),
        ),
        Mapping({
            'APB2_CK'  : '0b000',
            'PLL2Q_CK' : '0b001',
            'PLL3Q_CK' : '0b010',
            'HSI_CK'   : '0b011',
            'CSI_CK'   : '0b100',
            'LSE_CK'   : '0b101',
            0          : '0b110',
        }),
    ),
)



global SCHEMA
SCHEMA = {



    ################################################################################
    #
    # Interrupts.
    #



    'BUS_FAULT_ENABLE' : {
        'location' : ('SCB', 'SHCSR', 'BUSFAULTENA'),
    },

    'MEMORY_MANAGEMENT_FAULT_ENABLE' : {
        'location' : ('SCB', 'SHCSR', 'MEMFAULTENA'),
    },

    'USAGE_FAULT_ENABLE' : {
        'location' : ('SCB', 'SHCSR', 'USGFAULTENA'),
    },



    ################################################################################
    #
    # SysTick.
    #



    'SYSTICK_COUNTER' : {
        'location' : ('SysTick', 'VAL', 'CURRENT'),
    },

    'SYSTICK_USE_CPU_CK' : {
        'location'   : ('SysTick', 'CTRL', 'CLKSOURCE'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },

    'SYSTICK_INTERRUPT_ENABLE' : {
        'location'   : ('SysTick', 'CTRL', 'TICKINT'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },

    'SYSTICK_ENABLE' : {
        'location'   : ('SysTick', 'CTRL', 'ENABLE'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },



    ################################################################################
    #
    # GPIOs.
    #



    **{
        f'GPIO{port}_ENABLE' : {
            'location'   : ('RCC', 'AHB2ENR', f'GPIO{port}EN'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for port, numbers in GPIOS
    },

    **{
        f'GPIO{port}{number}_OPEN_DRAIN' : {
            'location'   : (f'GPIO{port}', 'OTYPER', f'OT{number}'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },

    **{
        f'GPIO{port}{number}_OUTPUT' : {
            'location'   : (f'GPIO{port}', 'ODR', f'OD{number}'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },

    **{
        f'GPIO{port}{number}_SPEED' : {
            'location'   : (f'GPIO{port}', 'OSPEEDR', f'OSPEED{number}'),
            'constraint' : Mapping({
                'LOW'       : '0b00',
                'MEDIUM'    : '0b01',
                'HIGH'      : '0b10',
                'VERY_HIGH' : '0b11',
            }),
            'value' : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },

    **{
        f'GPIO{port}{number}_PULL' : {
            'location'   : (f'GPIO{port}', 'PUPDR', f'PUPD{number}'),
            'constraint' : Mapping({
                None   : '0b00',
                'UP'   : '0b01',
                'DOWN' : '0b10',
            }),
            'value' : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },

    **{
        f'GPIO{port}{number}_ALTERNATE_FUNCTION' : {
            'location' : (f'GPIO_AFR{('L', 'H')[number // 8]}', f'GPIO{port}->AFR[{number // 8}]', f'AFSEL{number}'),
            'value'    : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },

    **{
        f'GPIO{port}{number}_MODE' : {
            'location'   : (f'GPIO{port}', 'MODER', f'MODE{number}'),
            'constraint' : Mapping({
                'INPUT'     : '0b00',
                'OUTPUT'    : '0b01',
                'ALTERNATE' : '0b10',
                'ANALOG'    : '0b11',
            }),
            'value' : TBD,
        }
        for port, numbers in GPIOS
        for number in numbers
    },



    ################################################################################
    #
    # Power.
    #



    'FLASH_PROGRAMMING_DELAY' : {
        'location'   : ('FLASH', 'ACR', 'WRHIGHFREQ'),
        'constraint' : Choices('0b00', '0b01', '0b10'),
        'value'      : TBD,
    },

    'FLASH_LATENCY' : {
        'location'   : ('FLASH', 'ACR', 'LATENCY'),
        'constraint' : IntMinMax(0b0000, 0b1111),
        'value'      : TBD,
    },

    'INTERNAL_VOLTAGE_SCALING' : {
        'location'   : ('PWR', 'VOSCR', 'VOS'),
        'constraint' : Mapping({
            'VOS3': '0b00',
            'VOS2': '0b01',
            'VOS1': '0b10',
            'VOS0': '0b11'
        }),
        'value' : TBD,
    },

    'CURRENT_ACTIVE_VOS' : {
        'location' : ('PWR', 'VOSSR', 'ACTVOS'),
    },

    'CURRENT_ACTIVE_VOS_READY' : {
        'location' : ('PWR', 'VOSSR', 'ACTVOSRDY'),
    },

    'LDO_ENABLE' : {
        'location'   : ('PWR', 'SCCR', 'LDOEN'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },

    'POWER_MANAGEMENT_BYPASS' : {
        'location'   : ('PWR', 'SCCR', 'BYPASS'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },



    ################################################################################
    #
    # Clock Sources.
    #



    0 : {
        'clocktree' : True,
        'value'     : 0,
    },

    **{
        key : {
            'clocktree' : True,
            'value'     : TBD,
        }
        for key in (
            'CPU_CK',
            'HSI_CK',
            'HSI48_CK',
            'CSI_CK',
            'HSE_CK',
            'LSE_CK',
            'PER_CK',
            'AXI_AHB_CK',
            'SYSTICK_CK',
        )
    },

    **{
        f'{source}_ENABLE' : {
            'location'   : ('RCC', 'CR', f'{source}ON'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for source in (
            'HSI',
            'HSI48',
            'CSI',
        )
    },

    **{
        f'{source}_READY' : {
            'location' : ('RCC', 'CR', f'{source}RDY'),
        }
        for source in (
            'HSI',
            'HSI48',
            'CSI',
        )
    },

    'PERIPHERAL_CLOCK_OPTION' : {
        'location'   : ('RCC', 'CCIPR5', 'CKPERSEL'),
        'constraint' : Mapping({
            'HSI_CK' : '0b00',
            'CSI_CK' : '0b01',
            'HSE_CK' : '0b10',
            0        : '0b11'
        }),
        'value' : TBD,
    },



    ################################################################################
    #
    # PLLs.
    #



    **{
        f'PLL{unit}{channel}_CK' : {
            'clocktree' : True,
            'value'     : TBD,
        }
        for unit, channels in PLLS
        for channel in channels
    },

    **{
        f'PLL{unit}_VCO_FREQ' : {
            'clocktree'  : True,
            'constraint' : RealMinMax(128_000_000, 560_000_000),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_ENABLE' : {
            'location'   : ('RCC', 'CR', f'PLL{unit}ON'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_ENABLE' : {
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}{channel}EN'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for unit, channels in PLLS
        for channel in channels
    },

    **{
        f'PLL{unit}_READY' : {
            'location' : ('RCC', 'CR', f'PLL{unit}RDY'),
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_KERNEL_SOURCE' : {
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}SRC'),
            'constraint' : Mapping({
                0        : '0b00',
                'HSI_CK' : '0b01',
                'CSI_CK' : '0b10',
                'HSE_CK' : '0b11',
            }),
            'value' : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_INPUT_RANGE' : {
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}RGE'),
            'constraint' : Mapping({
                (2_000_000,  4_000_000) : 1,
                (4_000_000,  8_000_000) : 2,
                (8_000_000, 16_000_000) : 3,
            }),
            'value' : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_PREDIVIDER' : {
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}M'),
            'constraint' : IntMinMax(1, 63),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_MULTIPLIER' : {
            'location'   : ('RCC', f'PLL{unit}DIVR', f'PLL{unit}N'),
            'constraint' : IntMinMax(4, 512),
            'value'      : TBD,
            'off_by_one' : True,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_DIVIDER' : {
            'location'   : ('RCC', f'PLL{unit}DIVR', f'PLL{unit}{channel}'),
            'constraint' : IntMinMax(1, 128),
            'value'      : TBD,
            'off_by_one' : True,
        }
        for unit, channels in PLLS
        for channel in channels
    },



    ################################################################################
    #
    # System Clock Generation Unit.
    #



    **{
        f'APB{unit}_CK' : {
            'clocktree' : True,
            'value'     : TBD,
        }
        for unit in APBS
    },


    'EFFECTIVE_SCGU_KERNEL_SOURCE' : {
        'location' : ('RCC', 'CFGR1', 'SWS'),
    },

    'SCGU_KERNEL_SOURCE' : {
        'location'   : ('RCC', 'CFGR1', 'SW'),
        'constraint' : Mapping({
            'HSI_CK'   : '0b000',
            'CSI_CK'   : '0b001',
            'HSE_CK'   : '0b010',
            'PLL1P_CK' : '0b011'
        }),
        'value' : TBD,
    },

    **{
        f'APB{unit}_DIVIDER' : {
            'location'   : ('RCC', 'CFGR2', f'PPRE{unit}'),
            'constraint' : Mapping({
                1  : '0b000',
                2  : '0b100',
                4  : '0b101',
                8  : '0b110',
                16 : '0b111',
            }),
            'value' : TBD,
        }
        for unit in APBS
    },

    'CPU_DIVIDER' : {
        'location'   : ('RCC', 'CFGR2', 'HPRE'),
        'constraint' : Mapping({
            1   : '0b0000', # Low three bits are don't-care.
            2   : '0b1000',
            4   : '0b1001',
            8   : '0b1010',
            16  : '0b1011',
            64  : '0b1100',
            128 : '0b1101',
            256 : '0b1110',
            512 : '0b1111',
        }),
        'value' : TBD,
    },



    ################################################################################
    #
    # UXARTs.
    #


    **{
        f'{peripheral}{unit}_BAUD' : {
            'value' : TBD,
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_ENABLE' : {
            'location'   : ('RCC', 'APB1LENR', f'{peripheral}{unit}EN'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_RESET' : {
            'location' : ('RCC', 'APB1LRSTR', f'{peripheral}{unit}RST'),
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'UXART_{instances}_KERNEL_SOURCE' : {
            'location'   : ('RCC', 'CCIPR1', field),
            'constraint' : kernel_source,
            'value'      : TBD,
            'pseudokeys' : [
                f'{peripheral}{unit}_KERNEL_SOURCE'
                for peripheral, unit in instances
            ],
        }
        for field_instances, kernel_source in UXART_KERNEL_SOURCE_TABLE
        for field, instances in field_instances
    },

    **{
        f'{peripheral}{unit}_BAUD_DIVIDER' : {
            'location'   : ('USART', 'BRR', 'BRR'),
            'constraint' : IntMinMax(1, 1 << 16),
            'value'      : TBD,
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },



    ################################################################################
    #
    # I2Cs.
    #



    **{
        f'I2C{unit}_BAUD' : {
            'value' : TBD,
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_KERNEL_SOURCE' : {
            'location'   : ('RCC', 'CCIPR4', f'I2C{unit}SEL'),
            'constraint' : constraint,
            'value'      : TBD,
        }
        for units, constraint in(
            ((1, 2), Mapping({
                'APB1_CK'  : '0b00',
                'PLL3R_CK' : '0b01',
                'HSI_CK'   : '0b10',
                'CSI_CK'   : '0b11'
            })),
            ((3,), Mapping({
                'APB3_CK'  : '0b00',
                'PLL3R_CK' : '0b01',
                'HSI_CK'   : '0b10',
                'CSI_CK'   : '0b11',
            })),
        )
        for unit in units
    },

    **{
        f'I2C{unit}_RESET' : {
            'location' : ('RCC', 'APB1LRSTR', f'I2C{unit}RST'),
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_ENABLE' : {
            'location'   : ('RCC', 'APB1LENR', f'I2C{unit}EN'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_PRESC' : {
            'location'   : ('I2C', 'TIMINGR', 'PRESC'),
            'constraint' : IntMinMax(0, 15),
            'value'      : TBD,
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_SCLH' : {
            'location'   : ('I2C', 'TIMINGR', 'SCLH'),
            'constraint' : IntMinMax(0, 255),
            'value'      : TBD,
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_SCLL' : {
            'location'   : ('I2C', 'TIMINGR', 'SCLL'),
            'constraint' : IntMinMax(0, 255),
            'value'      : TBD,
        }
        for unit in I2CS
    },



    ################################################################################
    #
    # Timers.
    #



    'GLOBAL_TIMER_PRESCALER' : {
        'location'   : ('RCC', 'CFGR1', 'TIMPRE'),
        'constraint' : Choices(False, True),
        'value'      : TBD,
    },

    **{
        f'TIM{unit}_COUNTER_RATE' : {
            'value' : TBD,
        }
        for unit in TIMERS
    },

    **{
        f'TIM{unit}_UPDATE_RATE' : {
            'value' : TBD,
        }
        for unit in TIMERS
    },

    **{
        f'TIM{unit}_DIVIDER' : {
            'location'   : (f'TIM{unit}', 'PSC', 'PSC'),
            'constraint' : IntMinMax(1, 1 << 16),
            'value'      : TBD,
            'off_by_one' : True,
        }
        for unit in TIMERS
    },

    **{
        f'TIM{unit}_MODULATION' : {
            'location'   : (f'TIM{unit}', 'PSC', 'ARR'),
            'constraint' : IntMinMax(1, 1 << (32 if unit in (2, 5) else 16)),
            'value'      : TBD,
            'off_by_one' : True,
        }
        for unit in TIMERS
    },



    ################################################################################
    #
    # SPIs.
    #



    **{
        f'SPI{unit}_BAUD' : {
            'value' : TBD,
        }
        for unit in SPIS
    },

    **{
        f'SPI{unit}_ENABLE' : {
            'location' : (
                'RCC',
                { # TODO Less redundancy.
                    1 : 'APB2ENR',
                    2 : 'APB1LENR',
                    3 : 'APB1LENR',
                    4 : 'APB2ENR',
                }[unit],
                f'SPI{unit}EN'
            ),
        }
        for unit in SPIS
    },

    **{
        f'SPI{unit}_RESET' : {
            'location' : (
                'RCC',
                { # TODO Less redundancy.
                    1 : 'APB2RSTR',
                    2 : 'APB1LRSTR',
                    3 : 'APB1LRSTR',
                    4 : 'APB2RSTR',
                }[unit],
                f'SPI{unit}RST'
            ),
        }
        for unit in SPIS
    },

    **{
        f'SPI{unit}_KERNEL_SOURCE' : {
            'location'   : ('RCC', 'CCIPR3', f'SPI{unit}SEL'),
            'constraint' : kernel_source,
            'value'      : TBD,
        }
        for units, kernel_source in (
            ((1, 2, 3), Mapping({
                'PLL1Q_CK' : '0b000',
                'PLL2P_CK' : '0b001',
                'PLL3P_CK' : '0b010',
                0          : '0b011', # TODO: 'AUDIOCLK'.
                'PER_CK'   : '0b100',
                0          : '0b101',
            })),
            ((4,), Mapping({
                'APB2_CK'  : '0b000',
                'PLL2Q_CK' : '0b001',
                'PLL3Q_CK' : '0b010',
                'HSI_CK'   : '0b011',
                'CSI_CK'   : '0b100',
                'HSE_CK'   : '0b101',
                0          : '0b110',
            })),
        )
        for unit in units
    },

    **{
        f'SPI{unit}_BYPASS_DIVIDER' : {
            'location'   : (f'SPI{unit}', 'CFG1', 'BPASS'),
            'constraint' : Choices(False, True),
            'value'      : TBD,
        }
        for unit in SPIS
    },

    **{
        f'SPI{unit}_DIVIDER' : {
            'location'   : (f'SPI{unit}', 'CFG1', 'MBR'),
            'constraint' : Mapping({
                2   : '0b000',
                4   : '0b001',
                8   : '0b010',
                16  : '0b011',
                32  : '0b100',
                64  : '0b101',
                128 : '0b110',
                256 : '0b111',
            }),
            'value' : TBD,
        }
        for unit in SPIS
    },



    ################################################################################

}
