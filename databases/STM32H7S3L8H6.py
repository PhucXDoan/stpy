global APBS
APBS = (
    1,
    2,
    4,
    5,
)



global PLLS
PLLS = (
    (1, ('P', 'Q',      'S',    )),
    (2, ('P', 'Q', 'R', 'S', 'T')),
    (3, ('P', 'Q', 'R', 'S',    )),
)



global GPIOS
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



global GPIO_MODE
GPIO_MODE = {
    'INPUT'     : '0b00',
    'OUTPUT'    : '0b01',
    'ALTERNATE' : '0b10',
    'ANALOG'    : '0b11',
}

global GPIO_SPEED
GPIO_SPEED = {
    'LOW'       : '0b00',
    'MEDIUM'    : '0b01',
    'HIGH'      : '0b10',
    'VERY_HIGH' : '0b11',
}

global GPIO_PULL
GPIO_PULL = {
    None   : '0b00',
    'UP'   : '0b01',
    'DOWN' : '0b10',
}



global UXARTS
UXARTS = ( # TODO Non-exhaustive.
    (('USART', 2), ('USART', 3), ('UART', 4), ('UART', 5), ('UART', 7), ('UART', 8)),
)



global INTERRUPTS
INTERRUPTS = (
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
)



global SDMMC_KERNEL_FREQ
SDMMC_KERNEL_FREQ = RealMinMax(0, 200_000_000)



global CPU_FREQ
CPU_FREQ = RealMinMax(0, 600_000_000)



global AXI_AHB_FREQ
AXI_AHB_FREQ = RealMinMax(0, 300_000_000)



global APB_FREQ
APB_FREQ = RealMinMax(0, 150_000_000)



global PLL_CHANNEL_FREQ
PLL_CHANNEL_FREQ = RealMinMax(1_500_000, 600_000_000)



global HSI_DEFAULT_FREQUENCY
HSI_DEFAULT_FREQUENCY = 64_000_000



UXART_KERNEL_SOURCE_TABLE = (
    (
        (
            ('UART234578SEL', (('USART', 2), ('USART', 3), ('UART', 4), ('UART', 5), ('UART', 7), ('UART', 8))),
        ),
        {
            'APB2_CK'  : '0b000',
            'PLL2Q_CK' : '0b001',
            'PLL3Q_CK' : '0b010',
            'HSI_CK'   : '0b011',
            'CSI_CK'   : '0b100',
            'LSE_CK'   : '0b101'
        }
    ),
)



global SCHEMA
SCHEMA = {

    ################################################################################
    #
    # GPIOs.
    #



    **{
        f'GPIO{unit}_ENABLE' : {
            'location'   : ('RCC', 'AHB4ENR', f'GPIO{unit}EN'),
            'constraint' : (False, True),
            'value'      : TBD,
        }
        for unit in GPIOS
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
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'SYSTICK_INTERRUPT_ENABLE' : {
        'location'   : ('SysTick', 'CTRL', 'TICKINT'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'SYSTICK_ENABLE' : {
        'location'   : ('SysTick', 'CTRL', 'ENABLE'),
        'constraint' : (False, True),
        'value'      : TBD,
    },



    ################################################################################
    #
    # Power.
    #



    'FLASH_PROGRAMMING_DELAY' : {
        'location'   : ('FLASH', 'ACR', 'WRHIGHFREQ'),
        'constraint' : (
            '0b00',
            '0b11',
        ),
        'value' : TBD,
    },

    'FLASH_LATENCY' : {
        'location'   : ('FLASH', 'ACR', 'LATENCY'),
        'constraint' : IntMinMax(0, 15),
        'value'      : TBD,
    },

    'CURRENT_ACTIVE_VOS' : {
        'location' : ('PWR', 'SR1', 'ACTVOS'),
    },

    'CURRENT_ACTIVE_VOS_READY' : {
        'location' : ('PWR', 'SR1', 'ACTVOSRDY'),
    },

    'SMPS_OUTPUT_LEVEL' : {
        'location'   : ('PWR', 'CSR2', 'SDHILEVEL'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'SMPS_FORCED_ON' : {
        'location'   : ('PWR', 'CSR2', 'SMPSEXTHP'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'SMPS_ENABLE' : {
        'location'   : ('PWR', 'CSR2', 'SDEN'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'LDO_ENABLE' : {
        'location'   : ('PWR', 'CSR2', 'LDOEN'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'POWER_MANAGEMENT_BYPASS' : {
        'location'   : ('PWR', 'CSR2', 'BYPASS'),
        'constraint' : (False, True),
        'value'      : TBD,
    },

    'INTERNAL_VOLTAGE_SCALING' : {
        'location'   : ('PWR', 'CSR4', 'VOS'),
        'constraint' : {
            'low'  : 0,
            'high' : 1
        },
        'value' : TBD,
    },



    ################################################################################
    #
    # Clock Sources.
    #



    0 : {
        'category' : 'frequency',
        'value'    : 0,
    },

    **{
        key : {
            'category' : 'frequency',
            'value'    : TBD,
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
            'constraint' : (False, True),
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
        'location'   : ('RCC', 'CCIPR1', 'CKPERSEL'),
        'constraint' : {
            'HSI_CK' : '0b00',
            'CSI_CK' : '0b01',
            'HSE_CK' : '0b10',
            0        : '0b11'
        },
        'value' : TBD,
    },



    ################################################################################
    #
    # PLLs.
    #



    **{
        f'PLL{unit}{channel}_CK' : {
            'category' : 'frequency',
            'value'    : TBD,
        }
        for unit, channels in PLLS
        for channel in channels
    },

    **{
        f'PLL{unit}_VCO_FREQ' : {
            'category'   : 'frequency',
            'constraint' : RealMinMax(192_000_000, 836_000_000),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_ENABLE' : {
            'location'   : ('RCC', 'CR', f'PLL{unit}ON'),
            'constraint' : (False, True),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_ENABLE' : {
            'location'   : ('RCC', 'PLLCFGR', f'PLL{unit}{channel}EN'),
            'constraint' : (False, True),
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
        f'PLL{unit}_INPUT_RANGE' : {
            'location'   : ('RCC', 'PLLCFGR', f'PLL{unit}RGE'),
            'constraint' : {
                (2_000_000, 4_000_000 ) : 0b01,
                (4_000_000, 8_000_000 ) : 0b10,
                (8_000_000, 16_000_000) : 0b11,
            },
            'value' : TBD,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}_PREDIVIDER' : {
            'location'   : ('RCC', f'PLLCKSELR', f'DIVM{unit}'),
            'constraint' : IntMinMax(1, 63),
            'value'      : TBD,
        }
        for unit, channels in PLLS
    },

    'PLL_KERNEL_SOURCE' : {
        'location'   : ('RCC', 'PLLCKSELR', 'PLLSRC'),
        'constraint' : {
            'HSI_CK' : '0b00',
            'CSI_CK' : '0b01',
            'HSE_CK' : '0b10',
            0        : '0b11'
        },
        'value' : TBD,
    },

    **{
        f'PLL{unit}_MULTIPLIER' : {
            'location'   : ('RCC', f'PLL{unit}DIVR1', 'DIVN'),
            'constraint' : IntMinMax(12, 420),
            'value'      : TBD,
            'off_by_one' : True,
        }
        for unit, channels in PLLS
    },

    **{
        f'PLL{unit}{channel}_DIVIDER' : {
            'location'   : ('RCC', f'PLL{unit}DIVR{2 if channel in ('S', 'T') else 1}', f'DIV{channel}'),
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
            'category' : 'frequency',
            'value'    : TBD,
        }
        for unit in APBS
    },

    'EFFECTIVE_SCGU_KERNEL_SOURCE' : {
        'location'   : ('RCC', 'CFGR', 'SWS'),
        'constraint' : {
            'HSI_CK'   : '0b000',
            'CSI_CK'   : '0b001',
            'HSE_CK'   : '0b010',
            'PLL1P_CK' : '0b011'
        },
        'value' : TBD,
    },

    'SCGU_KERNEL_SOURCE' : {
        'location'   : ('RCC', 'CFGR', 'SW'),
        'constraint' : {
            'HSI_CK'   : '0b000',
            'CSI_CK'   : '0b001',
            'HSE_CK'   : '0b010',
            'PLL1P_CK' : '0b011'
        },
        'value' : TBD,
    },

    **{
        f'APB{unit}_DIVIDER' : {
            'location'   : ('RCC', 'APBCFGR', f'PPRE{unit}'),
            'constraint' : {
                1  : '0b000',
                2  : '0b100',
                4  : '0b101',
                8  : '0b110',
                16 : '0b111',
            },
            'value' : TBD,
        }
        for unit in APBS
    },

    'CPU_DIVIDER' : {
        'location'   : ('RCC', 'CDCFGR', 'CPRE'),
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
        'value' : TBD,
    },

    'AXI_AHB_DIVIDER' : {
        'location'   : ('RCC', 'BMCFGR', 'BMPRE'),
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
        'value' : TBD,
    },



    ################################################################################
    #
    # UXARTs.
    #



    **{
        f'{peripheral}{unit}_BAUD' : {
            'category' : 'rate',
            'value'    : TBD,
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_ENABLE' : {
            'location'   : ('RCC', 'APB1ENR1', f'{peripheral}{unit}EN'),
            'constraint' : (False, True),
            'value'      : TBD,
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'{peripheral}{unit}_RESET' : {
            'location' : ('RCC', 'APB1RSTR1', f'{peripheral}{unit}RST'),
        }
        for instances in UXARTS
        for peripheral, unit in instances
    },

    **{
        f'UXART_{instances}_KERNEL_SOURCE' : {
            'location'   : ('RCC', 'CCIPR2', field),
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

}
