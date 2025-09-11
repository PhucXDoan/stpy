(
    (
        ################################################################################
        #
        # Peripheral counts.
        # @/pg 354/fig 40/`H7S3rm`.
        #

        ('APBS', (
            1,
            2,
            4,
            5,
        )),

        ('PLLS', (
            (1, ('P', 'Q',      'S',    )),
            (2, ('P', 'Q', 'R', 'S', 'T')),
            (3, ('P', 'Q', 'R', 'S',    )),
        )),

        ('UXARTS', (
            # TODO: (('USART', 1),),
            (('USART', 2), ('USART', 3), ('UART', 4), ('UART', 5), ('UART', 7), ('UART', 8)),
        )),

        ('INTERRUPTS', (
            'Reset',
            'NonMaskableInt',
            'HardFault',
            'MemoryManagement',
            'BusFault',
            'UsageFault',
            None,
            None,
            None,
            None,
            'SVCall',
            'DebugMonitor',
            None,
            'PendSV',
            'SysTick',
            'PVD_PVM',
            None,
            'DTS',
            'IWDG',
            'WWDG',
            'RCC',
            None,
            None,
            'FLASH',
            'RAMECC',
            'FPU',
            None,
            None,
            'TAMP',
            None,
            None,
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
            'RTC',
            'SAES',
            'CRYP',
            'PKA',
            'HASH',
            'RNG',
            'ADC1_2',
            'GPDMA1_Channel0',
            'GPDMA1_Channel1',
            'GPDMA1_Channel2',
            'GPDMA1_Channel3',
            'GPDMA1_Channel4',
            'GPDMA1_Channel5',
            'GPDMA1_Channel6',
            'GPDMA1_Channel7',
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
            'TIM9',
            'SPI1',
            'SPI2',
            'SPI3',
            'SPI4',
            'SPI5',
            'SPI6',
            'HPDMA1_Channel0',
            'HPDMA1_Channel1',
            'HPDMA1_Channel2',
            'HPDMA1_Channel3',
            'HPDMA1_Channel4',
            'HPDMA1_Channel5',
            'HPDMA1_Channel6',
            'HPDMA1_Channel7',
            'SAI1_A',
            'SAI1_B',
            'SAI2_A',
            'SAI2_B',
            'I2C1_EV',
            'I2C1_ER',
            'I2C2_EV',
            'I2C2_ER',
            'I2C3_EV',
            'I2C3_ER',
            'USART1',
            'USART2',
            'USART3',
            'UART4',
            'UART5',
            'UART7',
            'UART8',
            'I3C1_EV',
            'I3C1_ER',
            'OTG_HS',
            'ETH',
            'CORDIC',
            'GFXTIM',
            'DCMIPP',
            None,
            None,
            'DMA2D',
            'JPEG',
            'GFXMMU',
            'I3C1_WKUP',
            'MCE1',
            'MCE2',
            'MCE3',
            'XSPI1',
            'XSPI2',
            'FMC',
            'SDMMC1',
            'SDMMC2',
            None,
            None,
            'OTG_FS',
            'TIM12',
            'TIM13',
            'TIM14',
            'TIM15',
            'TIM16',
            'TIM17',
            'LPTIM1',
            'LPTIM2',
            'LPTIM3',
            'LPTIM4',
            'LPTIM5',
            'SPDIF_RX',
            'MDIOS',
            'ADF1_FLT0',
            'CRS',
            'UCPD1',
            'CEC',
            'PSSI',
            'LPUART1',
            'WAKEUP_PIN',
            'GPDMA1_Channel8',
            'GPDMA1_Channel9',
            'GPDMA1_Channel10',
            'GPDMA1_Channel11',
            'GPDMA1_Channel12',
            'GPDMA1_Channel13',
            'GPDMA1_Channel14',
            'GPDMA1_Channel15',
            'HPDMA1_Channel8',
            'HPDMA1_Channel9',
            'HPDMA1_Channel10',
            'HPDMA1_Channel11',
            'HPDMA1_Channel12',
            'HPDMA1_Channel13',
            'HPDMA1_Channel14',
            'HPDMA1_Channel15',
            None,
            None,
            None,
            'FDCAN1_IT0',
            'FDCAN1_IT1',
            'FDCAN2_IT0',
            'FDCAN2_IT1',
        )),

        ################################################################################
        #
        # Common values.
        #

        ('GPIO_MODE', (
            ('INPUT'    , '0b00'),
            ('OUTPUT'   , '0b01'),
            ('ALTERNATE', '0b10'),
            ('ANALOG'   , '0b11'),
        )),

        ('GPIO_SPEED', (
            ('LOW'      , '0b00'),
            ('MEDIUM'   , '0b01'),
            ('HIGH'     , '0b10'),
            ('VERY_HIGH', '0b11'),
        )),

        ('GPIO_PULL', (
            (None  , '0b00'),
            ('UP'  , '0b01'),
            ('DOWN', '0b10'),
        )),

        ################################################################################
        #
        # Frequency limits.
        # @/pg 39/tbl 6/`H7S3ds`.
        # TODO We're assuming a high internal voltage.
        # TODO Assuming wide frequency range.
        # TODO 600MHz only when ECC is disabled.
        #

        ('SDMMC_KERNEL_FREQ', 0          , 200_000_000),
        ('CPU_FREQ'         , 0          , 600_000_000),
        ('AXI_AHB_FREQ'     , 0          , 300_000_000),
        ('APB_FREQ'         , 0          , 150_000_000),
        ('PLL_CHANNEL_FREQ' , 1_500_000  , 600_000_000),
        ('PLL_VCO_FREQ'     , 192_000_000, 836_000_000),

    ),
    (

        ################################################################################

        ('SysTick',

            ('LOAD',
                ('RELOAD', 'SYSTICK_RELOAD', 1, (1 << 24) - 1),
            ),

            ('VAL',
                ('CURRENT', 'SYSTICK_COUNTER', 0, (1 << 32) - 1),
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
                    '0b11'
                )),
                ('LATENCY', 'FLASH_LATENCY', 0b0000, 0b1111),
            ),

        ),

        ################################################################################

        ('PWR',

            ('SR1',
                ('ACTVOS'   , 'CURRENT_ACTIVE_VOS'      ),
                ('ACTVOSRDY', 'CURRENT_ACTIVE_VOS_READY'),
            ),

            ('CSR2',
                ('SDHILEVEL', 'SMPS_OUTPUT_LEVEL'      ),
                ('SMPSEXTHP', 'SMPS_FORCED_ON'         ),
                ('SDEN'     , 'SMPS_ENABLE'            ),
                ('LDOEN'    , 'LDO_ENABLE'             ),
                ('BYPASS'   , 'POWER_MANAGEMENT_BYPASS'),
            ),

            ('CSR4',
                ('VOS', 'INTERNAL_VOLTAGE_SCALING', (
                    ('low' , 0),
                    ('high', 1),
                )),
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
            ),

            ('CFGR',
                *(
                    (field, tag, (
                        ('HSI_CK'   , '0b000'),
                        ('CSI_CK'   , '0b001'),
                        ('HSE_CK'   , '0b010'),
                        ('PLL1_P_CK', '0b011'),
                    ))
                    for field, tag in (
                        ('SWS', 'EFFECTIVE_SCGU_KERNEL_SOURCE'),
                        ('SW' , 'SCGU_KERNEL_SOURCE'          ),
                    )
                ),
            ),

            *(
                (register,
                    (field, tag, (
                        (1  , '0b0000'), # Low three bits are don't-care.
                        (2  , '0b1000'),
                        (4  , '0b1001'),
                        (8  , '0b1010'),
                        (16 , '0b1011'),
                        (64 , '0b1100'),
                        (128, '0b1101'),
                        (256, '0b1110'),
                        (512, '0b1111'),
                    ))
                )
                for register, field, tag in (
                    ('CDCFGR', 'CPRE' , 'CPU_DIVIDER'    ),
                    ('BMCFGR', 'BMPRE', 'AXI_AHB_DIVIDER'),
                )
            ),

            ('APBCFGR',
                *(
                    (f'PPRE{unit}', f'APB{unit}_DIVIDER', (
                        (1 , '0b000'),
                        (2 , '0b100'),
                        (4 , '0b101'),
                        (8 , '0b110'),
                        (16, '0b111'),
                    ))
                    for unit in (1, 2, 4, 5)
                ),
            ),

            ('AHB4ENR',
                *(
                    (f'GPIO{port}EN', f'GPIO{port}_ENABLE')
                    for port in 'ABCDEFGHI'
                ),
            ),

            ('APB1ENR1',
                ('USART3EN', 'USART3_ENABLE'),
            ),

            ('APB1RSTR1',
                ('USART3RST', 'USART3_RESET'),
                ('USART2RST', 'USART2_RESET'),
            ),

            ('PLLCFGR',
                *(
                    (f'PLL{unit}RGE', f'PLL{unit}_INPUT_RANGE', (
                        ( 1_000_000, None),
                        ( 2_000_000, None), # Can be '0b00', but only for medium VCO.
                        ( 4_000_000, 0b01),
                        ( 8_000_000, 0b10),
                        (16_000_000, 0b11),
                    ))
                    for unit in (1, 2, 3)
                ),
                *(
                    (f'PLL{unit}{channel}EN', f'PLL{unit}{channel}_ENABLE')
                    for unit, channels in (
                        (1, ('P', 'Q',      'S'     )),
                        (2, ('P', 'Q', 'R', 'S', 'T')),
                        (3, ('P', 'Q', 'R', 'S'     )),
                    )
                    for channel in channels
                ),
            ),

            ('PLLCKSELR',
                ('DIVM1' , 'PLL1_PREDIVIDER'  , 1, 63),
                ('DIVM2' , 'PLL2_PREDIVIDER'  , 1, 63),
                ('DIVM3' , 'PLL3_PREDIVIDER'  , 1, 63),
                ('PLLSRC', 'PLL_KERNEL_SOURCE', (
                    ('HSI_CK' , '0b00'),
                    ('CSI_CK' , '0b01'),
                    ('HSE_CK' , '0b10'),
                    (None     , '0b11'),
                )),
            ),

            *(
                (f'PLL{unit}DIVR1',
                    ('DIVN', f'PLL{unit}_MULTIPLIER', 12, 420),
                )
                for unit in (1, 2, 3)
            ),

            *(
                (f'PLL{unit}DIVR{2 if channel in ('S', 'T') else 1}',
                    (f'DIV{channel}', f'PLL{unit}{channel}_DIVIDER', 1, 128),
                )
                for unit, channels in (
                    (1, ('P', 'Q',      'S'     )),
                    (2, ('P', 'Q', 'R', 'S', 'T')),
                    (3, ('P', 'Q', 'R', 'S'     )),
                )
                for channel in channels
            ),

            ('CCIPR1',
                ('CKPERSEL', 'PERIPHERAL_CLOCK_OPTION', (
                    ('HSI_CK' , '0b00'),
                    ('CSI_CK' , '0b01'),
                    ('HSE_CK' , '0b10'),
                    (None     , '0b11'),
                )),
                ('SDMMC12SEL', 'SDMMC_KERNEL_SOURCE', (
                    ('PLL2_S_CK', '0b0'),
                    ('PLL2_T_CK', '0b1'),
                )),
            ),

            ('CCIPR2',
                ('UART234578SEL', f'UXART_{(('USART', 2), ('USART', 3), ('UART', 4), ('UART', 5), ('UART', 7), ('UART', 8))}_KERNEL_SOURCE', (
                    ('APB2_CK'  , '0b000'),
                    ('PLL2_Q_CK', '0b001'),
                    ('PLL3_Q_CK', '0b010'),
                    ('HSI_CK'   , '0b011'),
                    ('CSI_CK'   , '0b100'),
                    ('LSE_CK'   , '0b101'),
                )),
            ),

            ('CCIPR2', # TODO Should we allow for redundant locations?
                *(
                    ('UART234578SEL', f'{peripheral}{unit}_KERNEL_SOURCE', (
                        ('APB2_CK'  , '0b000'),
                        ('PLL2_Q_CK', '0b001'),
                        ('PLL3_Q_CK', '0b010'),
                        ('HSI_CK'   , '0b011'),
                        ('CSI_CK'   , '0b100'),
                        ('LSE_CK'   , '0b101'),
                    ))
                    for peripheral, unit in (('USART', 2), ('USART', 3), ('UART', 4), ('UART', 5), ('UART', 7), ('UART', 8))
                ),
            ),

        ),

        ################################################################################

        ('USART',
            ('BRR',
                ('BRR', 'UXART_BAUD_DIVIDER', 1, 1 << 16),
            ),
        ),

    ),
)
