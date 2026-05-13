// ARM64 hot loop, single-table, one 64-bit load per 8 bigrams.
//
// void histogram_hot_loop_asm_single(const uint8_t *data, size_t pairs,
//                                    uint32_t *counts);
//
// Each iteration reads 9 bytes (one uint64 + one trailing byte) and
// derives the 8 overlapping unaligned uint16 bigrams via UBFX bitfield
// extracts. This replaces 8 ldrh load µops with 2 loads + 8 cheap ALU
// ops; the RMW on counts[bin] is still strict per-bigram because two
// bigrams in the same chunk can alias to the same bin.

#if defined(__APPLE__)
# define SYM(name) _##name
#else
# define SYM(name) name
#endif

    .text
    .globl SYM(histogram_hot_loop_asm_single)
    .p2align 2

SYM(histogram_hot_loop_asm_single):
    // Need 9 bytes per chunk (8 bigrams need byte 0..8). To safely read
    // the trailing byte we require pairs >= 8 AND there are >= 9 bytes
    // remaining; since the caller passes pairs == n - 1 and the mmap is
    // n bytes long, byte at q+8 exists whenever pairs >= 8.
    cmp     x1, #8
    b.lo    Ltail2

Lmain2:
    ldr     x5, [x0]           // bytes 0..7 (LE in x5)
    ldrb    w6, [x0, #8]       // byte 8 (high half of bigram 7)

    // x5 holds bytes 0..7 in LE order. To form bigram k = byte k |
    // (byte k+1 << 8) we extract bits [k*8 + 15 : k*8] of x5 for k=0..6,
    // and combine x5's top byte with the freshly loaded byte 8 for k=7.
    ubfx    x3, x5, #0,  #16    // bigram 0
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #8,  #16    // bigram 1
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #16, #16    // bigram 2
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #24, #16    // bigram 3
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #32, #16    // bigram 4
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #40, #16    // bigram 5
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    ubfx    x3, x5, #48, #16    // bigram 6
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    // bigram 7 = (byte 8 << 8) | byte 7 = (w6 << 8) | (x5 >> 56)
    lsr     x3, x5, #56
    orr     x3, x3, x6, lsl #8
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]

    add     x0, x0, #8
    sub     x1, x1, #8
    cmp     x1, #8
    b.hs    Lmain2

Ltail2:
    cbz     x1, Ldone2
Ltail2_loop:
    ldrh    w3, [x0]
    add     x3, x2, x3, lsl #2
    ldr     w4, [x3]
    add     w4, w4, #1
    str     w4, [x3]
    add     x0, x0, #1
    subs    x1, x1, #1
    b.ne    Ltail2_loop

Ldone2:
    ret
