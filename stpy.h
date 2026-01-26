#pragma once



////////////////////////////////////////////////////////////////////////////////
//
// Macros to control the NVIC interrupts.
//
// @/pg 626/tbl B3-8/`Armv7-M`.
// @/pg 1452/tbl D1.1.10/`Armv8-M`.
//



#define NVIC_ENABLE(NAME)        ((void) (NVIC->ISER[NVICInterrupt_##NAME / 32] = 1 << (NVICInterrupt_##NAME % 32)))
#define NVIC_DISABLE(NAME)       ((void) (NVIC->ICER[NVICInterrupt_##NAME / 32] = 1 << (NVICInterrupt_##NAME % 32)))
#define NVIC_SET_PENDING(NAME)   ((void) (NVIC->ISPR[NVICInterrupt_##NAME / 32] = 1 << (NVICInterrupt_##NAME % 32)))
#define NVIC_CLEAR_PENDING(NAME) ((void) (NVIC->ICPR[NVICInterrupt_##NAME / 32] = 1 << (NVICInterrupt_##NAME % 32)))



////////////////////////////////////////////////////////////////////////////////
//
// Macros to control GPIOs.
//



#define GPIO_ACTIVE(NAME)     ((void) (CONCAT(GPIO, _PORT_FOR_GPIO_WRITE(NAME))->BSRR  = CONCAT(_LOCATION_FOR_GPIO_ACTIVE  (NAME), _NUMBER_FOR_GPIO_WRITE(NAME))))
#define GPIO_INACTIVE(NAME)   ((void) (CONCAT(GPIO, _PORT_FOR_GPIO_WRITE(NAME))->BSRR  = CONCAT(_LOCATION_FOR_GPIO_INACTIVE(NAME), _NUMBER_FOR_GPIO_WRITE(NAME))))
#define GPIO_TOGGLE(NAME)     ((void) (CONCAT(GPIO, _PORT_FOR_GPIO_WRITE(NAME))->ODR  ^= CONCAT(GPIO_ODR_OD , _NUMBER_FOR_GPIO_WRITE(NAME))))
#define GPIO_SET(NAME, VALUE) ((void) ((VALUE) ? GPIO_ACTIVE(NAME) : GPIO_INACTIVE(NAME)))
#define GPIO_READ(NAME)       (_ACTIVE_FOR_GPIO_READ(NAME) (!!(CONCAT(GPIO, _PORT_FOR_GPIO_READ(NAME))->IDR & CONCAT(GPIO_IDR_ID, _NUMBER_FOR_GPIO_READ(NAME)))))



////////////////////////////////////////////////////////////////////////////////
//
// @/url:`https://github.com/PhucXDoan/phucxdoan.github.io/wiki/Macros-for-Reading-and-Writing-to-Memory%E2%80%90Mapped-Registers`.
//



#define _PARENTHESES                                 ()
#define _EXPAND_0(...)                               _EXPAND_1(_EXPAND_1(_EXPAND_1(__VA_ARGS__)))
#define _EXPAND_1(...)                               _EXPAND_2(_EXPAND_2(_EXPAND_2(__VA_ARGS__)))
#define _EXPAND_2(...)                               __VA_ARGS__
#define _MAP__(FUNCTION, SHARED, FIRST, SECOND, ...) FUNCTION(SHARED, FIRST, SECOND) __VA_OPT__(_MAP_ _PARENTHESES (FUNCTION, SHARED, __VA_ARGS__))
#define _MAP_()                                      _MAP__
#define _MAP(FUNCTION, PERIPHERAL_REGISTER, ...)     __VA_OPT__(_EXPAND_0(_MAP__(FUNCTION, PERIPHERAL_REGISTER, __VA_ARGS__)))

#define _GET_POS(PERIPHERAL_REGISTER, FIELD)         ((uint32_t) CONCAT(CONCAT(PERIPHERAL_REGISTER##_, FIELD##_), Pos))
#define _GET_MSK(PERIPHERAL_REGISTER, FIELD)         ((uint32_t) CONCAT(CONCAT(PERIPHERAL_REGISTER##_, FIELD##_), Msk))

#define _CLEAR_BITS(PERIPHERAL_REGISTER, FIELD, VALUE) \
    & ~_GET_MSK(PERIPHERAL_REGISTER, FIELD)

#define _SET_BITS(PERIPHERAL_REGISTER, FIELD, VALUE)                  \
    | ((((uint32_t) (VALUE)) << _GET_POS(PERIPHERAL_REGISTER, FIELD)) \
                              & _GET_MSK(PERIPHERAL_REGISTER, FIELD))

#define CMSIS_READ(PERIPHERAL_REGISTER, VARIABLE, FIELD)              \
    ((uint32_t) (((VARIABLE) & _GET_MSK(PERIPHERAL_REGISTER, FIELD))  \
                            >> _GET_POS(PERIPHERAL_REGISTER, FIELD)))

#define CMSIS_WRITE(PERIPHERAL_REGISTER, VARIABLE, ...)                       \
    ((void) ((VARIABLE) =                                                     \
            ((VARIABLE) _MAP(_CLEAR_BITS, PERIPHERAL_REGISTER, __VA_ARGS__))  \
                        _MAP(_SET_BITS  , PERIPHERAL_REGISTER, __VA_ARGS__)))

#define CMSIS_SET(PERIPHERAL, REGISTER, ...)                  CMSIS_WRITE(CONCAT(PERIPHERAL##_, REGISTER), PERIPHERAL->REGISTER, __VA_ARGS__)
#define CMSIS_GET(PERIPHERAL, REGISTER, FIELD)                CMSIS_READ (CONCAT(PERIPHERAL##_, REGISTER), PERIPHERAL->REGISTER, FIELD      )
#define CMSIS_GET_FROM(VARIABLE, PERIPHERAL, REGISTER, FIELD) CMSIS_READ (CONCAT(PERIPHERAL##_, REGISTER), VARIABLE            , FIELD      )



////////////////////////////////////////////////////////////////////////////////
//
// Sometimes the register we're writing to cannot be
// known at compile-time, so we'll have to bundle up
// the peripheral-register-field tuple into a struct
// in order to do the RMW.
//



struct CMSISTuple
{
    volatile long unsigned int* address;
    int32_t                     position;
    uint32_t                    mask;
};



#define CMSIS_PUT(TUPLE, VALUE) CMSIS_PUT_((TUPLE), (uint32_t) (VALUE))
static mustinline void
CMSIS_PUT_(struct CMSISTuple tuple, uint32_t value)
{

    // Read.
    uint32_t temporary = *tuple.address;

    // Modify.
    temporary = (temporary & ~tuple.mask) | ((value << tuple.position) & tuple.mask);

    // Write.
    *tuple.address = temporary;

}



////////////////////////////////////////////////////////////////////////////////
//
// The CMSIS headers can contain mistakes or
// missing definitions, so we'll patch those here.
//



#if TARGET_MCU_IS_STM32H533RET6 || TARGET_MCU_IS_STM32H533VET6

    #define USART_BRR_BRR_Pos    0                             // For the full contiguous field.
    #define USART_BRR_BRR_Msk    (0xFFFF << USART_BRR_BRR_Pos) // "

    #define RCC_CCIPR5_CKPERSEL_ RCC_CCIPR5_CKERPSEL_         // Typo.
    #define USART_TDR_TDR_Pos    0                            // Position and mask not given.
    #define USART_TDR_TDR_Msk    (0x1FF << USART_TDR_TDR_Pos) // "
    #define USART_RDR_TDR_Pos    0                            // "
    #define USART_RDR_TDR_Msk    (0x1FF << USART_RDR_TDR_Pos) // "

    #define USART_RQR_ABRRQ_Pos  0                             // Missing position and masks.
    #define USART_RQR_ABRRQ_Msk  (0b1 << USART_RQR_ABRRQ_Pos)  // "
    #define USART_RQR_SBKRQ_Pos  1                             // "
    #define USART_RQR_SBKRQ_Msk  (0b1 << USART_RQR_SBKRQ_Pos)  // "
    #define USART_RQR_MMRQ_Pos   2                             // "
    #define USART_RQR_MMRQ_Msk   (0b1 << USART_RQR_MMRQ_Pos)   // "
    #define USART_RQR_RXFRQ_Pos  3                             // "
    #define USART_RQR_RXFRQ_Msk  (0b1 << USART_RQR_RXFRQ_Pos)  // "
    #define USART_RQR_TXFRQ_Pos  4                             // "
    #define USART_RQR_TXFRQ_Msk  (0b1 << USART_RQR_TXFRQ_Pos)  // "

#endif



////////////////////////////////////////////////////////////////////////////////
//
// @/`CMSIS Suffix Dropping`:
//
// We define macros to map things like `I2C1_` to `I2C_` so that the
// CMSIS_GET/CMSIS_SET macros can be used for macros like `I2C_CR1_PE_pos`
// which does not include the peripheral's suffix.
//



#define UART0_                     UART_
#define UART1_                     UART_
#define UART2_                     UART_
#define UART3_                     UART_
#define UART4_                     UART_
#define UART5_                     UART_
#define UART6_                     UART_
#define UART7_                     UART_
#define USART0_                    USART_
#define USART1_                    USART_
#define USART2_                    USART_
#define USART3_                    USART_
#define USART4_                    USART_
#define USART5_                    USART_
#define USART6_                    USART_
#define USART7_                    USART_
#define SPI0_                      SPI_
#define SPI1_                      SPI_
#define SPI2_                      SPI_
#define SPI3_                      SPI_
#define SPI4_                      SPI_
#define SPI5_                      SPI_
#define SPI6_                      SPI_
#define SPI7_                      SPI_
#define XSPI0_                     XSPI_
#define XSPI1_                     XSPI_
#define XSPI2_                     XSPI_
#define XSPI3_                     XSPI_
#define XSPI4_                     XSPI_
#define XSPI5_                     XSPI_
#define XSPI6_                     XSPI_
#define XSPI7_                     XSPI_
#define I2C0_                      I2C_
#define I2C1_                      I2C_
#define I2C2_                      I2C_
#define I2C3_                      I2C_
#define I2C4_                      I2C_
#define I2C5_                      I2C_
#define I2C6_                      I2C_
#define I2C7_                      I2C_
#define I3C0_                      I3C_
#define I3C1_                      I3C_
#define I3C2_                      I3C_
#define I3C3_                      I3C_
#define I3C4_                      I3C_
#define I3C5_                      I3C_
#define I3C6_                      I3C_
#define I3C7_                      I3C_
#define DMA0_                      DMA_
#define DMA1_                      DMA_
#define DMA2_                      DMA_
#define DMA3_                      DMA_
#define DMA4_                      DMA_
#define DMA5_                      DMA_
#define DMA6_                      DMA_
#define DMA7_                      DMA_
#define DMA0_Stream0_              DMA_
#define DMA0_Stream1_              DMA_
#define DMA0_Stream2_              DMA_
#define DMA0_Stream3_              DMA_
#define DMA0_Stream4_              DMA_
#define DMA0_Stream5_              DMA_
#define DMA0_Stream6_              DMA_
#define DMA0_Stream7_              DMA_
#define DMA1_Stream0_              DMA_
#define DMA1_Stream1_              DMA_
#define DMA1_Stream2_              DMA_
#define DMA1_Stream3_              DMA_
#define DMA1_Stream4_              DMA_
#define DMA1_Stream5_              DMA_
#define DMA1_Stream6_              DMA_
#define DMA1_Stream7_              DMA_
#define DMA2_Stream0_              DMA_
#define DMA2_Stream1_              DMA_
#define DMA2_Stream2_              DMA_
#define DMA2_Stream3_              DMA_
#define DMA2_Stream4_              DMA_
#define DMA2_Stream5_              DMA_
#define DMA2_Stream6_              DMA_
#define DMA2_Stream7_              DMA_
#define DMA3_Stream0_              DMA_
#define DMA3_Stream1_              DMA_
#define DMA3_Stream2_              DMA_
#define DMA3_Stream3_              DMA_
#define DMA3_Stream4_              DMA_
#define DMA3_Stream5_              DMA_
#define DMA3_Stream6_              DMA_
#define DMA3_Stream7_              DMA_
#define DMA4_Stream0_              DMA_
#define DMA4_Stream1_              DMA_
#define DMA4_Stream2_              DMA_
#define DMA4_Stream3_              DMA_
#define DMA4_Stream4_              DMA_
#define DMA4_Stream5_              DMA_
#define DMA4_Stream6_              DMA_
#define DMA4_Stream7_              DMA_
#define DMA5_Stream0_              DMA_
#define DMA5_Stream1_              DMA_
#define DMA5_Stream2_              DMA_
#define DMA5_Stream3_              DMA_
#define DMA5_Stream4_              DMA_
#define DMA5_Stream5_              DMA_
#define DMA5_Stream6_              DMA_
#define DMA5_Stream7_              DMA_
#define DMA6_Stream0_              DMA_
#define DMA6_Stream1_              DMA_
#define DMA6_Stream2_              DMA_
#define DMA6_Stream3_              DMA_
#define DMA6_Stream4_              DMA_
#define DMA6_Stream5_              DMA_
#define DMA6_Stream6_              DMA_
#define DMA6_Stream7_              DMA_
#define DMA7_Stream0_              DMA_
#define DMA7_Stream1_              DMA_
#define DMA7_Stream2_              DMA_
#define DMA7_Stream3_              DMA_
#define DMA7_Stream4_              DMA_
#define DMA7_Stream5_              DMA_
#define DMA7_Stream6_              DMA_
#define DMA7_Stream7_              DMA_
#define DMAMUX0_                   DMAMUX_
#define DMAMUX1_                   DMAMUX_
#define DMAMUX2_                   DMAMUX_
#define DMAMUX3_                   DMAMUX_
#define DMAMUX4_                   DMAMUX_
#define DMAMUX5_                   DMAMUX_
#define DMAMUX6_                   DMAMUX_
#define DMAMUX7_                   DMAMUX_
#define DMAMUX0_Channel0_          DMAMUX_
#define DMAMUX0_Channel1_          DMAMUX_
#define DMAMUX0_Channel2_          DMAMUX_
#define DMAMUX0_Channel3_          DMAMUX_
#define DMAMUX0_Channel4_          DMAMUX_
#define DMAMUX0_Channel5_          DMAMUX_
#define DMAMUX0_Channel6_          DMAMUX_
#define DMAMUX0_Channel7_          DMAMUX_
#define DMAMUX1_Channel0_          DMAMUX_
#define DMAMUX1_Channel1_          DMAMUX_
#define DMAMUX1_Channel2_          DMAMUX_
#define DMAMUX1_Channel3_          DMAMUX_
#define DMAMUX1_Channel4_          DMAMUX_
#define DMAMUX1_Channel5_          DMAMUX_
#define DMAMUX1_Channel6_          DMAMUX_
#define DMAMUX1_Channel7_          DMAMUX_
#define DMAMUX2_Channel0_          DMAMUX_
#define DMAMUX2_Channel1_          DMAMUX_
#define DMAMUX2_Channel2_          DMAMUX_
#define DMAMUX2_Channel3_          DMAMUX_
#define DMAMUX2_Channel4_          DMAMUX_
#define DMAMUX2_Channel5_          DMAMUX_
#define DMAMUX2_Channel6_          DMAMUX_
#define DMAMUX2_Channel7_          DMAMUX_
#define DMAMUX3_Channel0_          DMAMUX_
#define DMAMUX3_Channel1_          DMAMUX_
#define DMAMUX3_Channel2_          DMAMUX_
#define DMAMUX3_Channel3_          DMAMUX_
#define DMAMUX3_Channel4_          DMAMUX_
#define DMAMUX3_Channel5_          DMAMUX_
#define DMAMUX3_Channel6_          DMAMUX_
#define DMAMUX3_Channel7_          DMAMUX_
#define DMAMUX4_Channel0_          DMAMUX_
#define DMAMUX4_Channel1_          DMAMUX_
#define DMAMUX4_Channel2_          DMAMUX_
#define DMAMUX4_Channel3_          DMAMUX_
#define DMAMUX4_Channel4_          DMAMUX_
#define DMAMUX4_Channel5_          DMAMUX_
#define DMAMUX4_Channel6_          DMAMUX_
#define DMAMUX4_Channel7_          DMAMUX_
#define DMAMUX5_Channel0_          DMAMUX_
#define DMAMUX5_Channel1_          DMAMUX_
#define DMAMUX5_Channel2_          DMAMUX_
#define DMAMUX5_Channel3_          DMAMUX_
#define DMAMUX5_Channel4_          DMAMUX_
#define DMAMUX5_Channel5_          DMAMUX_
#define DMAMUX5_Channel6_          DMAMUX_
#define DMAMUX5_Channel7_          DMAMUX_
#define DMAMUX6_Channel0_          DMAMUX_
#define DMAMUX6_Channel1_          DMAMUX_
#define DMAMUX6_Channel2_          DMAMUX_
#define DMAMUX6_Channel3_          DMAMUX_
#define DMAMUX6_Channel4_          DMAMUX_
#define DMAMUX6_Channel5_          DMAMUX_
#define DMAMUX6_Channel6_          DMAMUX_
#define DMAMUX6_Channel7_          DMAMUX_
#define DMAMUX7_Channel0_          DMAMUX_
#define DMAMUX7_Channel1_          DMAMUX_
#define DMAMUX7_Channel2_          DMAMUX_
#define DMAMUX7_Channel3_          DMAMUX_
#define DMAMUX7_Channel4_          DMAMUX_
#define DMAMUX7_Channel5_          DMAMUX_
#define DMAMUX7_Channel6_          DMAMUX_
#define DMAMUX7_Channel7_          DMAMUX_
#define DMAMUX0_RequestGenerator0_ DMAMUX_
#define DMAMUX0_RequestGenerator1_ DMAMUX_
#define DMAMUX0_RequestGenerator2_ DMAMUX_
#define DMAMUX0_RequestGenerator3_ DMAMUX_
#define DMAMUX0_RequestGenerator4_ DMAMUX_
#define DMAMUX0_RequestGenerator5_ DMAMUX_
#define DMAMUX0_RequestGenerator6_ DMAMUX_
#define DMAMUX0_RequestGenerator7_ DMAMUX_
#define DMAMUX1_RequestGenerator0_ DMAMUX_
#define DMAMUX1_RequestGenerator1_ DMAMUX_
#define DMAMUX1_RequestGenerator2_ DMAMUX_
#define DMAMUX1_RequestGenerator3_ DMAMUX_
#define DMAMUX1_RequestGenerator4_ DMAMUX_
#define DMAMUX1_RequestGenerator5_ DMAMUX_
#define DMAMUX1_RequestGenerator6_ DMAMUX_
#define DMAMUX1_RequestGenerator7_ DMAMUX_
#define DMAMUX2_RequestGenerator0_ DMAMUX_
#define DMAMUX2_RequestGenerator1_ DMAMUX_
#define DMAMUX2_RequestGenerator2_ DMAMUX_
#define DMAMUX2_RequestGenerator3_ DMAMUX_
#define DMAMUX2_RequestGenerator4_ DMAMUX_
#define DMAMUX2_RequestGenerator5_ DMAMUX_
#define DMAMUX2_RequestGenerator6_ DMAMUX_
#define DMAMUX2_RequestGenerator7_ DMAMUX_
#define DMAMUX3_RequestGenerator0_ DMAMUX_
#define DMAMUX3_RequestGenerator1_ DMAMUX_
#define DMAMUX3_RequestGenerator2_ DMAMUX_
#define DMAMUX3_RequestGenerator3_ DMAMUX_
#define DMAMUX3_RequestGenerator4_ DMAMUX_
#define DMAMUX3_RequestGenerator5_ DMAMUX_
#define DMAMUX3_RequestGenerator6_ DMAMUX_
#define DMAMUX3_RequestGenerator7_ DMAMUX_
#define DMAMUX4_RequestGenerator0_ DMAMUX_
#define DMAMUX4_RequestGenerator1_ DMAMUX_
#define DMAMUX4_RequestGenerator2_ DMAMUX_
#define DMAMUX4_RequestGenerator3_ DMAMUX_
#define DMAMUX4_RequestGenerator4_ DMAMUX_
#define DMAMUX4_RequestGenerator5_ DMAMUX_
#define DMAMUX4_RequestGenerator6_ DMAMUX_
#define DMAMUX4_RequestGenerator7_ DMAMUX_
#define DMAMUX5_RequestGenerator0_ DMAMUX_
#define DMAMUX5_RequestGenerator1_ DMAMUX_
#define DMAMUX5_RequestGenerator2_ DMAMUX_
#define DMAMUX5_RequestGenerator3_ DMAMUX_
#define DMAMUX5_RequestGenerator4_ DMAMUX_
#define DMAMUX5_RequestGenerator5_ DMAMUX_
#define DMAMUX5_RequestGenerator6_ DMAMUX_
#define DMAMUX5_RequestGenerator7_ DMAMUX_
#define DMAMUX6_RequestGenerator0_ DMAMUX_
#define DMAMUX6_RequestGenerator1_ DMAMUX_
#define DMAMUX6_RequestGenerator2_ DMAMUX_
#define DMAMUX6_RequestGenerator3_ DMAMUX_
#define DMAMUX6_RequestGenerator4_ DMAMUX_
#define DMAMUX6_RequestGenerator5_ DMAMUX_
#define DMAMUX6_RequestGenerator6_ DMAMUX_
#define DMAMUX6_RequestGenerator7_ DMAMUX_
#define DMAMUX7_RequestGenerator0_ DMAMUX_
#define DMAMUX7_RequestGenerator1_ DMAMUX_
#define DMAMUX7_RequestGenerator2_ DMAMUX_
#define DMAMUX7_RequestGenerator3_ DMAMUX_
#define DMAMUX7_RequestGenerator4_ DMAMUX_
#define DMAMUX7_RequestGenerator5_ DMAMUX_
#define DMAMUX7_RequestGenerator6_ DMAMUX_
#define DMAMUX7_RequestGenerator7_ DMAMUX_
#define GPDMA0_                    DMA_
#define GPDMA1_                    DMA_
#define GPDMA2_                    DMA_
#define GPDMA3_                    DMA_
#define GPDMA4_                    DMA_
#define GPDMA5_                    DMA_
#define GPDMA6_                    DMA_
#define GPDMA7_                    DMA_
#define GPDMA0_Channel0_           DMA_
#define GPDMA0_Channel1_           DMA_
#define GPDMA0_Channel2_           DMA_
#define GPDMA0_Channel3_           DMA_
#define GPDMA0_Channel4_           DMA_
#define GPDMA0_Channel5_           DMA_
#define GPDMA0_Channel6_           DMA_
#define GPDMA0_Channel7_           DMA_
#define GPDMA1_Channel0_           DMA_
#define GPDMA1_Channel1_           DMA_
#define GPDMA1_Channel2_           DMA_
#define GPDMA1_Channel3_           DMA_
#define GPDMA1_Channel4_           DMA_
#define GPDMA1_Channel5_           DMA_
#define GPDMA1_Channel6_           DMA_
#define GPDMA1_Channel7_           DMA_
#define GPDMA2_Channel0_           DMA_
#define GPDMA2_Channel1_           DMA_
#define GPDMA2_Channel2_           DMA_
#define GPDMA2_Channel3_           DMA_
#define GPDMA2_Channel4_           DMA_
#define GPDMA2_Channel5_           DMA_
#define GPDMA2_Channel6_           DMA_
#define GPDMA2_Channel7_           DMA_
#define GPDMA3_Channel0_           DMA_
#define GPDMA3_Channel1_           DMA_
#define GPDMA3_Channel2_           DMA_
#define GPDMA3_Channel3_           DMA_
#define GPDMA3_Channel4_           DMA_
#define GPDMA3_Channel5_           DMA_
#define GPDMA3_Channel6_           DMA_
#define GPDMA3_Channel7_           DMA_
#define GPDMA4_Channel0_           DMA_
#define GPDMA4_Channel1_           DMA_
#define GPDMA4_Channel2_           DMA_
#define GPDMA4_Channel3_           DMA_
#define GPDMA4_Channel4_           DMA_
#define GPDMA4_Channel5_           DMA_
#define GPDMA4_Channel6_           DMA_
#define GPDMA4_Channel7_           DMA_
#define GPDMA5_Channel0_           DMA_
#define GPDMA5_Channel1_           DMA_
#define GPDMA5_Channel2_           DMA_
#define GPDMA5_Channel3_           DMA_
#define GPDMA5_Channel4_           DMA_
#define GPDMA5_Channel5_           DMA_
#define GPDMA5_Channel6_           DMA_
#define GPDMA5_Channel7_           DMA_
#define GPDMA6_Channel0_           DMA_
#define GPDMA6_Channel1_           DMA_
#define GPDMA6_Channel2_           DMA_
#define GPDMA6_Channel3_           DMA_
#define GPDMA6_Channel4_           DMA_
#define GPDMA6_Channel5_           DMA_
#define GPDMA6_Channel6_           DMA_
#define GPDMA6_Channel7_           DMA_
#define GPDMA7_Channel0_           DMA_
#define GPDMA7_Channel1_           DMA_
#define GPDMA7_Channel2_           DMA_
#define GPDMA7_Channel3_           DMA_
#define GPDMA7_Channel4_           DMA_
#define GPDMA7_Channel5_           DMA_
#define GPDMA7_Channel6_           DMA_
#define GPDMA7_Channel7_           DMA_
#define SDMMC0_                    SDMMC_
#define SDMMC1_                    SDMMC_
#define SDMMC2_                    SDMMC_
#define SDMMC3_                    SDMMC_
#define SDMMC4_                    SDMMC_
#define SDMMC5_                    SDMMC_
#define SDMMC6_                    SDMMC_
#define SDMMC7_                    SDMMC_
#define TIM0_                      TIM_
#define TIM1_                      TIM_
#define TIM2_                      TIM_
#define TIM3_                      TIM_
#define TIM4_                      TIM_
#define TIM5_                      TIM_
#define TIM6_                      TIM_
#define TIM7_                      TIM_
#define TIM8_                      TIM_
#define TIM9_                      TIM_
#define TIM10_                     TIM_
#define TIM11_                     TIM_
#define TIM12_                     TIM_
#define TIM13_                     TIM_
#define TIM14_                     TIM_
#define TIM15_                     TIM_
#define TIM16_                     TIM_
#define TIM17_                     TIM_
#define TIM18_                     TIM_
#define TIM19_                     TIM_
#define TIM20_                     TIM_
#define TIM21_                     TIM_
#define TIM22_                     TIM_
#define TIM23_                     TIM_
#define TIM24_                     TIM_
#define TIM25_                     TIM_
#define TIM26_                     TIM_
#define TIM27_                     TIM_
#define TIM28_                     TIM_
#define TIM29_                     TIM_
#define TIM30_                     TIM_
#define TIM31_                     TIM_
#define GPIOA_                     GPIO_
#define GPIOB_                     GPIO_
#define GPIOC_                     GPIO_
#define GPIOD_                     GPIO_
#define GPIOE_                     GPIO_
#define GPIOF_                     GPIO_
#define GPIOG_                     GPIO_
#define GPIOH_                     GPIO_
#define GPIOI_                     GPIO_
#define GPIOJ_                     GPIO_
#define GPIOK_                     GPIO_
#define GPIOL_                     GPIO_
#define GPIOM_                     GPIO_
#define GPION_                     GPIO_
#define GPIOO_                     GPIO_
#define GPIOP_                     GPIO_
#define GPIOQ_                     GPIO_
#define GPIOR_                     GPIO_
#define GPIOS_                     GPIO_
#define GPIOT_                     GPIO_
#define GPIOU_                     GPIO_
#define GPIOV_                     GPIO_
#define GPIOW_                     GPIO_
#define GPIOX_                     GPIO_
#define GPIOY_                     GPIO_
#define GPIOZ_                     GPIO_
#define ADC0_                      ADC_
#define ADC1_                      ADC_
#define ADC2_                      ADC_
#define ADC3_                      ADC_
#define ADC4_                      ADC_
#define ADC12_COMMON_              ADC_
