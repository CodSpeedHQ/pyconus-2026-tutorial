/* Native byte-pair histogram counter.
 *
 * Strategy:
 *   - mmap the file (skip the fread buffer copy and any chunk-boundary logic).
 *   - madvise(SEQUENTIAL) so the kernel prefetches aggressively.
 *   - In the hot loop, read each overlapping 2-byte bigram as an unaligned
 *     uint16. On a little-endian host (every machine we care about) that is
 *     a single load — no shift, no or. The caller adapts its key table to
 *     match the LE bin id (bin = b1<<8 | b0).
 *
 * Errors are reported as POSIX errno; 0 means success.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

int histogram_count_file(const char *path, uint64_t *counts) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return errno ? errno : EIO;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        int err = errno;
        close(fd);
        return err ? err : EIO;
    }
    size_t n = (size_t)st.st_size;
    if (n < 2) {
        close(fd);
        return 0;
    }

    const uint8_t *data = mmap(NULL, n, PROT_READ, MAP_PRIVATE, fd, 0);
    if (data == MAP_FAILED) {
        int err = errno;
        close(fd);
        return err ? err : EIO;
    }
#ifdef POSIX_MADV_SEQUENTIAL
    posix_madvise((void *)data, n, POSIX_MADV_SEQUENTIAL);
#endif

    size_t pairs = n - 1;
    const uint8_t *q = data;
    size_t i = 0;

    /* 8x unrolled hot loop. Each iteration reads an overlapping unaligned
     * uint16 at q+0..q+7 and bumps the corresponding bin. The compiler is
     * trusted to fold memcpy(&u16, q+k, 2) into a single mov on x86/ARM. */
    for (; i + 8 <= pairs; i += 8) {
        uint16_t a0, a1, a2, a3, a4, a5, a6, a7;
        memcpy(&a0, q + 0, 2);
        memcpy(&a1, q + 1, 2);
        memcpy(&a2, q + 2, 2);
        memcpy(&a3, q + 3, 2);
        memcpy(&a4, q + 4, 2);
        memcpy(&a5, q + 5, 2);
        memcpy(&a6, q + 6, 2);
        memcpy(&a7, q + 7, 2);
        counts[a0]++;
        counts[a1]++;
        counts[a2]++;
        counts[a3]++;
        counts[a4]++;
        counts[a5]++;
        counts[a6]++;
        counts[a7]++;
        q += 8;
    }
    for (; i < pairs; i++) {
        uint16_t v;
        memcpy(&v, q, 2);
        counts[v]++;
        q++;
    }

    munmap((void *)data, n);
    close(fd);
    return 0;
}
