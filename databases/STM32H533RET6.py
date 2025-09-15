def IntMinMax(minimum, maximum):
    pass

def RealMinMax(minimum, maximum):
    pass

APBS = (
    1,
    2,
    3,
)

PLLS = (
    (1, ('P', 'Q', 'R')),
    (2, ('P', 'Q', 'R')),
    (3, ('P', 'Q', 'R')),
)

GPIOS = (
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
)

UXARTS = (
    (('USART', 1),),
    (('USART', 2),),
    (('USART', 3),),
    (('UART' , 4),),
    (('UART' , 5),),
    (('USART', 6),),
)

I2CS = (
    1,
    2,
    3,
)

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



SCHEMA = {

    0 : {
        'type'  : 'frequency',
        'value' : 0,
    },

    **{
        key : {
            'type' : 'frequency',
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
        f'APB{unit}_CK' : {
            'type' : 'frequency',
        }
        for unit in APBS
    },

    **{
        f'PLL{unit}{channel}_CK' : {
            'type' : 'frequency',
        }
        for unit, channels in PLLS
        for channel in channels
    },

    **{
        f'{peripheral}{unit}_BAUD' : {
            'type' : 'rate',
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },





    ################################################################################



    'SYSTICK_COUNTER' : {
        'type'       : 'setting',
        'location'   : ('SysTick', 'VAL', 'CURRENT'),
        'constraint' : IntMinMax(0, (1 << 32) - 1),
    },


    'SYSTICK_USE_CPU_CK' : {
        'type'       : 'setting',
        'location'   : ('SysTick', 'CTRL', 'CLKSOURCE'),
        'constraint' : (False, True),
    },


    'SYSTICK_INTERRUPT_ENABLE' : {
        'type'       : 'setting',
        'location'   : ('SysTick', 'CTRL', 'TICKINT'),
        'constraint' : (False, True),
    },


    'SYSTICK_ENABLE' : {
        'type'       : 'setting',
        'location'   : ('SysTick', 'CTRL', 'ENABLE'),
        'constraint' : (False, True),
    },



    ################################################################################



    'FLASH_PROGRAMMING_DELAY' : {
        'type'       : 'setting',
        'location'   : ('FLASH', 'ACR', 'WRHIGHFREQ'),
        'constraint' : ('0b00', '0b01', '0b10'),
    },


    'FLASH_LATENCY' : {
        'type'       : 'setting',
        'location'   : ('FLASH', 'ACR', 'LATENCY'),
        'constraint' : IntMinMax(0b0000, 0b1111),
    },


    'INTERNAL_VOLTAGE_SCALING' : {
        'type'       : 'setting',
        'location'   : ('PWR', 'VOSCR', 'VOS'),
        'constraint' : {'VOS3': '0b00', 'VOS2': '0b01', 'VOS1': '0b10', 'VOS0': '0b11'},
    },


    'CURRENT_ACTIVE_VOS' : {
        'type'       : 'setting',
        'location'   : ('PWR', 'VOSSR', 'ACTVOS'),
        'constraint' : (False, True),
    },


    'CURRENT_ACTIVE_VOS_READY' : {
        'type'       : 'setting',
        'location'   : ('PWR', 'VOSSR', 'ACTVOSRDY'),
        'constraint' : (False, True),
    },


    'LDO_ENABLE' : {
        'type'       : 'setting',
        'location'   : ('PWR', 'SCCR', 'LDOEN'),
        'constraint' : (False, True),
    },


    'POWER_MANAGEMENT_BYPASS' : {
        'type'       : 'setting',
        'location'   : ('PWR', 'SCCR', 'BYPASS'),
        'constraint' : (False, True),
    },



    ################################################################################



    **{
        f'{source}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CR', f'{source}ON'),
            'constraint' : (False, True),
        }
        for source in (
            'HSI48',
            'CSI',
            'HSI',
        )
    },

    **{
        f'{source}_READY' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CR', f'{source}RDY'),
            'constraint' : (False, True),
        }
        for source in (
            'HSI48',
            'CSI',
            'HSI'
        )
    },



    ################################################################################



    'GLOBAL_TIMER_PRESCALER' : {
        'type'       : 'setting',
        'location'   : ('RCC', 'CFGR1', 'TIMPRE'),
        'constraint' : (False, True),
    },


    'EFFECTIVE_SCGU_KERNEL_SOURCE' : {
        'type'     : 'ablative',
        'location' : ('RCC', 'CFGR1', 'SWS'),
    },

    'SCGU_KERNEL_SOURCE' : {
        'type'       : 'setting',
        'location'   : ('RCC', 'CFGR1', 'SW'),
        'constraint' : {
            'HSI_CK'   : '0b000',
            'CSI_CK'   : '0b001',
            'HSE_CK'   : '0b010',
            'PLL1P_CK' : '0b011'
        },
    },

    **{
        f'APB{unit}_DIVIDER' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CFGR2', 'PPRE3'),
            'constraint' : {
                1   : '0b0000', # Low three bits are don't-care.
                2   : '0b1000',
                4   : '0b1001',
                8   : '0b1010',
                16  : '0b1011',
                64  : '0b1100',
                128 : '0b1101',
                256 : '0b1110',
                512 : '0b1111',
            },
        }
        for unit in APBS
    },

    'CPU_DIVIDER' : {
        'type'       : 'setting',
        'location'   : ('RCC', 'CFGR2', 'HPRE'),
        'constraint' : {
            1   : '0b0000', # Low three bits are don't-care.
            2   : '0b1000',
            4   : '0b1001',
            8   : '0b1010',
            16  : '0b1011',
            64  : '0b1100',
            128 : '0b1101',
            256 : '0b1110',
            512 : '0b1111',
        },
    },


    ################################################################################



    'PERIPHERAL_CLOCK_OPTION' : {
        'type'       : 'setting',
        'location'   : ('RCC', 'CCIPR5', 'CKPERSEL'),
        'constraint' : {
            'HSI_CK' : '0b00',
            'CSI_CK' : '0b01',
            'HSE_CK' : '0b10',
            0        : '0b11'
        },
    },



    ################################################################################
    #
    # PLLs.
    #



    **{
        f'PLL{unit}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CR', f'PLL{unit}ON'),
            'constraint' : (False, True),
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'PLL{unit}CFGR', 'PLL{unit}{channel}EN'),
            'constraint' : (False, True),
        }
        for unit, channels in PLLS
        for channel in channels
    },

    **{
        f'PLL{unit}_READY' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CR', f'PLL{unit}RDY'),
            'constraint' : (False, True),
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_KERNEL_SOURCE' : {
            'type'       : 'setting',
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}SRC'),
            'constraint' : {
                0        : '0b00',
                'HSI_CK' : '0b01',
                'CSI_CK' : '0b10',
                'HSE_CK' : '0b11',
            },
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_INPUT_RANGE' : {
            'type'       : 'setting',
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}RGE'),
            'constraint' : {
                (2_000_000,  4_000_000) : 1,
                (4_000_000,  8_000_000) : 2,
                (8_000_000, 16_000_000) : 3,
            },
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_PREDIVIDER' : {
            'type'       : 'setting',
            'location'   : ('RCC', f'PLL{unit}CFGR', f'PLL{unit}M'),
            'constraint' : IntMinMax(1, 63),
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_MULTIPLIER' : {
            'type'       : 'setting',
            'location'   : ('RCC', f'PLL{unit}DIVR', f'PLL{unit}N'),
            'constraint' : IntMinMax(4, 512),
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_DIVIDER' : {
            'type'       : 'setting',
            'location'   : ('RCC', f'PLL{unit}DIV{channel}', f'PLL{unit}{channel}'),
            'constraint' : IntMinMax(1, 128),
        }
        for unit, channels in PLLS
        for channel in channels
    },



    ################################################################################
    #
    # GPIOs.
    #



    **{
        f'GPIO{unit}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'AHB2ENR', f'GPIO{unit}EN'),
            'constraint' : (False, True),
        }
        for unit in GPIOS
    },



    ################################################################################
    #
    # UXARTs.
    #


    **{
        f'{peripheral}{unit}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'APB1LENR', '{peripheral}{unit}EN'),
            'constraint' : (False, True),
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_RESET' : {
            'type'     : 'ablative',
            'location' : ('RCC', 'APB1LRSTR', '{peripheral}{unit}RST'),
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_KERNEL_SOURCE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CCIPR1', field),
            'constraint' : kernel_source,
        }
        for field_instances, kernel_source in
        (
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
                {
                    'APB1_CK'  : '0b000',
                    'PLL2Q_CK' : '0b001',
                    'PLL3Q_CK' : '0b010',
                    'HSI_CK'   : '0b011',
                    'CSI_CK'   : '0b100',
                    'LSE_CK'   : '0b101',
                    0          : '0b110',
                },
            ),
            (
                (
                    ('USART1SEL', (('USART', 1),)),
                ),
                {
                    'RCC_PCLK2' : '0b000',
                    'PLL2Q_CK'  : '0b001',
                    'PLL3Q_CK'  : '0b010',
                    'HSI_CK'    : '0b011',
                    'CSI_CK'    : '0b100',
                    'LSE_CK'    : '0b101',
                    0           : '0b110',
                },
            ),
        )
        for field, instances in field_instances
        for peripheral, unit in instances
    },

    'UXART_BAUD_DIVIDER' : {
        'type'       : 'setting',
        'location'   : ('USART', 'BRR', 'BRR'),
        'constraint' : IntMinMax(1, 1 << 16),
    },



    ################################################################################
    #
    # I2Cs.
    #



    **{
        f'I2C{unit}_BAUD' : {
            'type' : 'rate',
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_KERNEL_SOURCE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'CCIPR4', f'I2C{unit}SEL'),
            'constraint' : constraint,
        }
        for units, constraint in(
            ((1, 2), {
                'APB1_CK'  : '0b00',
                'PLL3R_CK' : '0b01',
                'HSI_CK'   : '0b10',
                'CSI_CK'   : '0b11'
            }),
            ((3,), {
                'APB3_CK'  : '0b00',
                'PLL3R_CK' : '0b01',
                'HSI_CK'   : '0b10',
                'CSI_CK'   : '0b11',
            }),
        )
        for unit in units
    },

    **{
        f'I2C{unit}_RESET' : {
            'type'       : 'ablative',
            'location'   : ('RCC', 'APB1LRSTR', f'I2C{unit}RST'),
        }
        for unit in I2CS
    },

    **{
        f'I2C{unit}_ENABLE' : {
            'type'       : 'setting',
            'location'   : ('RCC', 'APB1LENR', f'I2C{unit}EN'),
            'constraint' : (False, True),
        }
        for unit in I2CS
    },

    'I2C_PRESC' : {
        'type'       : 'setting',
        'location'   : ('I2C', 'TIMINGR', 'PRESC'),
        'constraint' : IntMinMax(0, 15),
    },

    'I2C_SCLH' : {
        'type'       : 'setting',
        'location'   : ('I2C', 'TIMINGR', 'SCLH'),
        'constraint' : IntMinMax(0, 255),
    },

    'I2C_SCLL' : {
        'type'       : 'setting',
        'location'   : ('I2C', 'TIMINGR', 'SCLL'),
        'constraint' : IntMinMax(0, 255),
    },



    ################################################################################
    #
    # Timers.
    #



    **{
        f'TIM{unit}_RATE' : {
            'type' : 'rate',
        }
        for unit in TIMERS
    },

    **{
        f'TIM{unit}_DIVIDER' : {
            'type'       : 'setting',
            'location'   : (f'TIM{unit}', 'PSC', 'PSC'),
            'constraint' : IntMinMax(1, 1 << 16),
        }
        for unit in TIMERS
    },

    **{
        f'TIM{unit}_MODULATION' : {
            'type'       : 'setting',
            'location'   : (f'TIM{unit}', 'PSC', 'ARR'),
            'constraint' : IntMinMax(1, 1 << (32 if unit in (2, 5) else 16)),
        }
        for unit in TIMERS
    },



    ################################################################################

}
