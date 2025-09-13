(
    (

        ################################################################################
        #
        # Peripheral counts.
        # @/pg 456/fig 52/`H533rm`.
        # @/pg 15/tbl 2/`H533ds`.
        #

        ('APBS', (
            1,
            2,
            3,
        )),

        ('PLLS', (
            (1, ('P', 'Q', 'R')),
            (2, ('P', 'Q', 'R')),
            (3, ('P', 'Q', 'R')),
        )),

        ('I2CS', (
            1,
            2,
            3,
        )),

        ('UXARTS', (
            (('USART', 1),),
            (('USART', 2),),
            (('USART', 3),),
            (('UART' , 4),),
            (('UART' , 5),),
            (('USART', 6),),
        )),

        ('TIMERS', (
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
        )),

        ('INTERRUPTS', (
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
        )),


        ################################################################################
        #
        # Common values.
        #

        ('GPIO_MODE', {
            'INPUT'     : '0b00',
            'OUTPUT'    : '0b01',
            'ALTERNATE' : '0b10',
            'ANALOG'    : '0b11',
        }),

        ('GPIO_SPEED', {
            'LOW'       : '0b00',
            'MEDIUM'    : '0b01',
            'HIGH'      : '0b10',
            'VERY_HIGH' : '0b11',
        }),

        ('GPIO_PULL', {
            None   : '0b00',
            'UP'   : '0b01',
            'DOWN' : '0b10',
        }),

        ################################################################################
        #
        # Frequency limits.
        # @/pg 124/tbl 47/`H533ds`.
        # TODO We're assuming a high internal voltage and wide range.
        #

        ('PLL_CHANNEL_FREQ', RealMinMax(  1_000_000, 250_000_000)),
        ('PLL_VCO_FREQ'    , RealMinMax(128_000_000, 560_000_000)),
        ('CPU_FREQ'        , RealMinMax(          0, 250_000_000)),
        ('AXI_AHB_FREQ'    , RealMinMax(          0, 250_000_000)),
        ('APB_FREQ'        , RealMinMax(          0, 250_000_000)),

    ),
    (

        ################################################################################

        ('SysTick',

            ('LOAD',
                ('RELOAD', 'SYSTICK_RELOAD', IntMinMax(1, (1 << 24) - 1)),
            ),

            ('VAL',
                ('CURRENT', 'SYSTICK_COUNTER', IntMinMax(0, (1 << 32) - 1)),
            ),

            ('CTRL',
                ('CLKSOURCE', 'SYSTICK_USE_CPU_CK'      ),
                ('TICKINT'  , 'SYSTICK_INTERRUPT_ENABLE'),
                ('ENABLE'   , 'SYSTICK_ENABLE'          ),
            ),

        ),

        ################################################################################

        ('FLASH',

            ('ACR',
                ('WRHIGHFREQ', 'FLASH_PROGRAMMING_DELAY', (
                    '0b00',
                    '0b01',
                    '0b10',
                )),
                ('LATENCY', 'FLASH_LATENCY', IntMinMax(0b0000, 0b1111)),
            ),

        ),

        ################################################################################

        ('PWR',

            ('VOSCR',
                ('VOS', 'INTERNAL_VOLTAGE_SCALING', {
                    'VOS3' : '0b00',
                    'VOS2' : '0b01',
                    'VOS1' : '0b10',
                    'VOS0' : '0b11',
                }),
            ),

            ('VOSSR',
                ('ACTVOS'   , 'CURRENT_ACTIVE_VOS'      ),
                ('ACTVOSRDY', 'CURRENT_ACTIVE_VOS_READY'),
            ),

            ('SCCR',
                ('LDOEN' , 'LDO_ENABLE'             ),
                ('BYPASS', 'POWER_MANAGEMENT_BYPASS'),
            ),

        ),

        ################################################################################

        ('RCC',

            ('CR',
                ('PLL3RDY' , 'PLL3_READY'  ),
                ('PLL3ON'  , 'PLL3_ENABLE' ),
                ('PLL2RDY' , 'PLL2_READY'  ),
                ('PLL2ON'  , 'PLL2_ENABLE' ),
                ('PLL1RDY' , 'PLL1_READY'  ),
                ('PLL1ON'  , 'PLL1_ENABLE' ),
                ('HSI48RDY', 'HSI48_READY' ),
                ('HSI48ON' , 'HSI48_ENABLE'),
                ('CSIRDY'  , 'CSI_READY'   ),
                ('CSION'   , 'CSI_ENABLE'  ),
                ('HSIRDY'  , 'HSI_READY'   ),
                ('HSION'   , 'HSI_ENABLE'  ),
            ),

            ('CFGR1',
                ('TIMPRE', 'GLOBAL_TIMER_PRESCALER'),
                *(
                    (field, tag, {
                        'HSI_CK'    : '0b000',
                        'CSI_CK'    : '0b001',
                        'HSE_CK'    : '0b010',
                        'PLL1_P_CK' : '0b011',
                    })
                    for field, tag in (
                        ('SWS', 'EFFECTIVE_SCGU_KERNEL_SOURCE'),
                        ('SW' , 'SCGU_KERNEL_SOURCE'          ),
                    )
                ),
            ),

            ('CFGR2',
                *(
                    (f'PPRE{unit}', f'APB{unit}_DIVIDER', {
                        1  : '0b000',
                        2  : '0b100',
                        4  : '0b101',
                        8  : '0b110',
                        16 : '0b111',
                    })
                    for unit in (1, 2, 3)
                ),
                ('HPRE', 'CPU_DIVIDER', {
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
            ),

            *(
                (f'PLL{unit}CFGR',
                    (f'PLL{unit}REN', f'PLL{unit}R_ENABLE'),
                    (f'PLL{unit}QEN', f'PLL{unit}Q_ENABLE'),
                    (f'PLL{unit}PEN', f'PLL{unit}P_ENABLE'),
                    (f'PLL{unit}M'  , f'PLL{unit}_PREDIVIDER', IntMinMax(1, 63)),
                    (f'PLL{unit}SRC', f'PLL{unit}_KERNEL_SOURCE', {
                        None     : '0b00',
                        'HSI_CK' : '0b01',
                        'CSI_CK' : '0b10',
                        'HSE_CK' : '0b11',
                    }),
                    (f'PLL{unit}RGE', f'PLL{unit}_INPUT_RANGE', {
                        # (1_000_000, 2_000_000 ) : None, # TODO Can be '0b00', but only for medium VCO. @/pg 124/tbl 47/`H533rm`.
                        (2_000_000, 4_000_000 ) : 0b01,
                        (4_000_000, 8_000_000 ) : 0b10,
                        (8_000_000, 16_000_000) : 0b11,
                    }),
                )
                for unit in (1, 2, 3)
            ),

            *(
                (f'PLL{unit}DIVR',
                    (f'PLL{unit}R', f'PLL{unit}R_DIVIDER'  , IntMinMax(1, 128)),
                    (f'PLL{unit}Q', f'PLL{unit}Q_DIVIDER'  , IntMinMax(1, 128)),
                    (f'PLL{unit}P', f'PLL{unit}P_DIVIDER'  , IntMinMax(1, 128)),
                    (f'PLL{unit}N', f'PLL{unit}_MULTIPLIER', IntMinMax(4, 512)),
                )
                for unit in (1, 2, 3)
            ),

            ('APB1LENR',
                ('USART2EN', 'USART2_ENABLE'),
                ('I2C1EN'  , 'I2C1_ENABLE'  ),
                ('I2C2EN'  , 'I2C2_ENABLE'  ),
            ),

            ('CCIPR1',
                *(
                    (field, f'UXART_{peripherals}_KERNEL_SOURCE', clock_source)
                    for field_peripherals, clock_source in
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
                                'APB1_CK'    : '0b000',
                                'PLL2_Q_CK'  : '0b001',
                                'PLL3_Q_CK'  : '0b010',
                                'HSI_CK'     : '0b011',
                                'CSI_CK'     : '0b100',
                                'LSE_CK'     : '0b101',
                                # TODO How to handle? None         : '0b110',
                            },
                        ),
                        (
                            (
                                ('USART1SEL', (('USART', 1),)),
                            ),
                            {
                                'RCC_PCLK2' : '0b000',
                                'PLL2_Q_CK' : '0b001',
                                'PLL3_Q_CK' : '0b010',
                                'HSI_CK'    : '0b011',
                                'CSI_CK'    : '0b100',
                                'LSE_CK'    : '0b101',
                                # TODO How to handle? None        : '0b110',
                            },
                        ),
                    )
                    for field, peripherals in field_peripherals
                ),
            ),

            ('CCIPR1', # TODO Redundancy.
                *(
                    (field, f'{peripheral}{unit}_KERNEL_SOURCE', clock_source)
                    for field_instances, clock_source in
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
                                'APB1_CK'    : '0b000',
                                'PLL2_Q_CK'  : '0b001',
                                'PLL3_Q_CK'  : '0b010',
                                'HSI_CK'     : '0b011',
                                'CSI_CK'     : '0b100',
                                'LSE_CK'     : '0b101',
                                # TODO How to handle? None         : '0b110',
                            },
                        ),
                        (
                            (
                                ('USART1SEL', (('USART', 1),)),
                            ),
                            {
                                'RCC_PCLK2'  : '0b000',
                                'PLL2_Q_CK'  : '0b001',
                                'PLL3_Q_CK'  : '0b010',
                                'HSI_CK'     : '0b011',
                                'CSI_CK'     : '0b100',
                                'LSE_CK'     : '0b101',
                                # TODO How to handle? None         : '0b110',
                            },
                        ),
                    )
                    for field, instances in field_instances
                    for peripheral, unit in instances
                ),
            ),

            ('CCIPR4',
                ('I2C3SEL', 'I2C3_KERNEL_SOURCE', {
                    'APB3_CK'   : '0b00',
                    'PLL3_R_CK' : '0b01',
                    'HSI_CK'    : '0b10',
                    'CSI_CK'    : '0b11',
                }),
                ('I2C2SEL', 'I2C2_KERNEL_SOURCE', {
                    'APB1_CK'   : '0b00',
                    'PLL3_R_CK' : '0b01',
                    'HSI_CK'    : '0b10',
                    'CSI_CK'    : '0b11',
                }),
                ('I2C1SEL', 'I2C1_KERNEL_SOURCE', {
                    'APB1_CK'   : '0b00',
                    'PLL3_R_CK' : '0b01',
                    'HSI_CK'    : '0b10',
                    'CSI_CK'    : '0b11',
                }),
            ),

            ('CCIPR5',
                ('CKPERSEL', 'PERIPHERAL_CLOCK_OPTION', {
                    'HSI_CK' : '0b00',
                    'CSI_CK' : '0b01',
                    'HSE_CK' : '0b10',
                    # TODO How to handle? None     : '0b11',
                }),
            ),

            ('AHB2ENR',
                *(
                    (f'GPIO{port}EN', f'GPIO{port}_ENABLE')
                    for port in 'ABCDEFGHI'
                ),
            ),

            ('APB1LRSTR',
                ('I2C1RST'  , 'I2C1_RESET'  ),
                ('I2C2RST'  , 'I2C2_RESET'  ),
                ('UART5RST' , 'UART5_RESET' ),
                ('UART4RST' , 'UART4_RESET' ),
                ('USART3RST', 'USART3_RESET'),
                ('USART2RST', 'USART2_RESET'),
            ),

        ),

        ################################################################################

        ('USART',
            ('BRR',
                ('BRR', 'UXART_BAUD_DIVIDER', IntMinMax(1, 1 << 16)),
            ),
        ),

        ################################################################################

        ('I2C',
            ('TIMINGR',
                ('PRESC', 'I2C_PRESC', IntMinMax(0, 15 )),
                ('SCLH' , 'I2C_SCLH' , IntMinMax(0, 255)),
                ('SCLL' , 'I2C_SCLL' , IntMinMax(0, 255)),
            ),
        ),


        ################################################################################

        *(
            (f'TIM{unit}',
                ('PSC',
                    ('PSC', f'TIM{unit}_DIVIDER'   , IntMinMax(1, 1 << 16)),
                    ('ARR', f'TIM{unit}_MODULATION', IntMinMax(1, 1 << (32 if unit in (2, 5) else 16))),
                ),
            )
            for unit in (1, 2, 3, 4, 5, 6, 7, 8, 12, 15)
        ),

    ),
)
