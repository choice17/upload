#ifdef _WIN32
#include <windows.h>
#else //
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#endif

#include <assert.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <signal.h>

#define SHM_FD_NAME "shmfd"
#define SHM_SIZE 4096

typedef struct {
    int signal;
    int flags;
} CFG;

void* read_shm(const char* fd_name, int size, void *handle)
{
    uint8_t* memptr = NULL;
#ifdef _WIN32
    HANDLE* hMapFile = (HANDLE*) handle;
    *hMapFile = OpenFileMapping(
        FILE_MAP_ALL_ACCESS,
        0,
        fd_name);
    if (*hMapFile == NULL) {
        printf("Cannot open shm fd!\n");
        return NULL;
    }
    memptr = (uint8_t*)MapViewOfFile(
        *hMapFile,
        FILE_MAP_ALL_ACCESS,
        0,
        0,
        size);
    if (memptr == NULL) {
        printf("Cannot open shm memory\n");
        CloseHandle(*hMapFile);
        return NULL;
    }
    return memptr;
#else
    int fd = shm_open(fd_name,
        O_RDWR, 0777);
    if (fd == 0) {
        printf("Cannot open shm fd\n");
        return NULL;
    }
    memptr = (uint8_t*) mmap(NULL,
        size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        fd,
        0
        );
    if (memptr == NULL) {
        printf("Cannot open shm memory!\n");
        return NULL;
    }
#endif
    return memptr;
}


void* open_shm(const char* fd_name, int size, void *handle)
{
    uint8_t *memptr = NULL;
#ifdef _WIN32
    printf("size handle:%u\n", sizeof(HANDLE));
    HANDLE* hMapFile = (HANDLE*) handle;
    *hMapFile = CreateFileMapping(
        INVALID_HANDLE_VALUE,
        NULL,
        PAGE_READWRITE,
        0,
        size,
        fd_name);
    if (*hMapFile == NULL) {
        printf("Cannot open shm fd!\n");
        return NULL;
    }
    memptr = (uint8_t*) MapViewOfFile(
        *hMapFile,
        FILE_MAP_ALL_ACCESS,
        0,
        0,
        SHM_SIZE);
    if (memptr == NULL) {
        printf("Cannot map shm memory!\n");
        CloseHandle(*hMapFile);
    }
    return memptr;
#else
    int fd;
    fd = shm_open(fd_name,
        O_RDWR | O_CREAT | O_EXCL,
        S_IRUSR | S_IWUSR);

    if (fd < 0) {
        printf("Cannot open shm fd!\n");
        return NULL;
    }
    ftruncate(fd, size);

    uint8_t* memptr = mmap(NULL,
                   size, // size
                   PROT_READ | PROT_WRITE, // access
                   MAP_SHARED, // shared memory
                   fd, 0);

    if (memptr == -1) {
        printf("Cannot map shared memory!\n")
        return NULL;
    }
#endif
    return memptr;
}

int unlink_shm(const char*fd_name, uint8_t* memptr, int size, void *handle)
{
    int ret = 0;
#ifdef _WIN32
    if (memptr)
        ret = UnmapViewOfFile(memptr);
    printf("ret of unmap:%d\n",ret);
    ret = CloseHandle(*(HANDLE*)handle);
    printf("ret of close fd:%d\n", ret);
#else
    if (memptr)
        ret = munmap(memptr, size);
    printf("ret of unmap:%d\n",ret);
    ret = unlink(fd_name);
    printf("ret of close fd:%d\n", ret);
#endif
    return 0;
}

uint8_t *g_memptr;
const char* g_fd_name;
int g_size;
void *g_handle;

void handler(int frame)
{
    unlink_shm(g_fd_name, g_memptr, g_size, g_handle);
    printf("Caught signal interrupt, exit!\n");
    exit(0);
}

int main(int argc, char **argv)
{
    struct timeval start;
#ifdef _WIN32
    HANDLE handle;
    //GetTimeFormat();
#else
    int handle;
    gettimeofday(&start, NULL);
    printf("%d.%06d\n", start.tv_sec, start.tv_usec);
#endif

    uint8_t* memptr;
    if (strcmp(argv[1], "1") == 0)
        memptr = open_shm(SHM_FD_NAME, SHM_SIZE, &handle);
    else
        memptr = read_shm(SHM_FD_NAME, SHM_SIZE, &handle);
    assert(memptr);
    CFG *cfg = (CFG*) memptr;

    g_memptr = memptr;
    g_fd_name = SHM_FD_NAME;
    g_size = SHM_SIZE;
    g_handle = (void*)&handle;
    signal(SIGINT, handler);

    if (strcmp(argv[1], "1")==0) {
        while (1) {
            sleep(1);
            cfg->flags += 1;
            printf("Process 1: signal:%d\n", cfg->signal);
        }
    } else {
        cfg->signal = 1;
        while (1) {
            sleep(1);
            cfg->signal += 1;
            printf("Process 2: flags:%d\n", cfg->flags);
        }
    } 
    return 0;
}
