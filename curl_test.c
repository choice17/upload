#include <stdio.h>
#include <string.h>
#include "curl/curl.h"

/* multipart */
/* https://curl.haxx.se/libcurl/c/multi-post.html */
/* curl mime only available since libcurl ver7.56 */
/* use curl-formadd https://curl.haxx.se/libcurl/c/postit2-formadd.html  */
/* https://curl.haxx.se/libcurl/c/curl_formadd.html */

/* post callback to read callback https://curl.haxx.se/libcurl/c/post-callback.html */
/* use CURL_FORMBUFFER to emulate request post behavior */

#define CURL_API_FACEREC "face_rec"
#define CURL_API_CLASSIFY "classify"
#define CURL_API_DETECT "detect"

struct MemoryStruct 
{
    char memory[4096];
    size_t size;
};

size_t WriteMemoryCallback(void *ptr, size_t size, size_t nmemb, void *data)
{
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)data;

    memcpy(&(mem->memory), ptr, realsize);
    mem->size = realsize;
    return realsize;
}


#define LOAD_SIZE 4096 * 128
typedef struct {
    char url[128];
    int method;
} PARAM_S;

typedef struct {
    unsigned int payload_size;
    char payload[LOAD_SIZE];
} INTSTA_S;

#define UT_CURL_TEST_IMG "/mnt/nfs/ethnfs/lena.jpg"
void setupPayload(INTSTA_S *intsta)
{
    int data_size = 0;
    char *data = (char *)intsta->payload;
    FILE *fp = fopen(UT_CURL_TEST_IMG,"r"); // file open
    if (!fp) {
        printf("File opening failed, cannot open %s\n", UT_CURL_TEST_IMG);
    }
    fseek(fp, 0, SEEK_END);
    unsigned int fpSize = ftell(fp); //current file position
    fseek(fp, 0, SEEK_SET);
    /* Setup payload metadata*/
    fread(&data[data_size], 1, fpSize, fp); // Read file
    fclose(fp);
    intsta->payload_size = fpSize;
}

#include <stdio.h>
#include <string.h>
 
#include <curl/curl.h>
 
int main(int argc, char *argv[])
{
    CURL *curl;
    CURLcode res;
    INTSTA_S intsta = { 0 };
    setupPayload(&intsta);
    struct curl_httppost *formpost = NULL;
    struct curl_httppost *lastptr = NULL;
    struct curl_slist *headerlist = NULL;
    static const char buf[] = "Expect:";

    curl_global_init(CURL_GLOBAL_ALL);
    int a[3] = {1920,1080,3};

    const char data_name[] = "image";
    const char format_name[] = "format";
    const char shape_name[] = "shape";
    const char time_name[] = "time";
    const char meta_name[] = "meta";
    char *format = "jpg";
    char *times = "123234235";
    char *meta = "{\"od\":[{\"obj\":{\"id\":0,\"rect\":[0,0,270,270],"
                                         "\"vel\":[0,10],\"cat\":\"\",\"shaking\":0}}],\"sz\":\"288 288\"}";

    /* Fill in the file upload field */ 
    curl_formadd(&formpost,
               &lastptr,
               CURLFORM_COPYNAME, "format",
               CURLFORM_BUFFER, format_name,
               CURLFORM_BUFFERPTR, format,
               CURLFORM_BUFFERLENGTH, strlen(format),
               CURLFORM_END);

    /* Fill in the file upload field */ 
    curl_formadd(&formpost,
               &lastptr,
               CURLFORM_COPYNAME, "shape",
               CURLFORM_BUFFER, shape_name,
               CURLFORM_BUFFERPTR, a,
               CURLFORM_BUFFERLENGTH, sizeof(int)*3,
               CURLFORM_END);

    /* Fill in the filename field */ 
    curl_formadd(&formpost,
               &lastptr,
               CURLFORM_COPYNAME, "time",
               CURLFORM_BUFFER, time_name,
               CURLFORM_BUFFERPTR, times,
               CURLFORM_BUFFERLENGTH, strlen(times),
               CURLFORM_END);


    /* Fill in the submit field too, even if this is rarely needed */ 
    curl_formadd(&formpost,
               &lastptr,
               CURLFORM_COPYNAME, "meta",
               CURLFORM_BUFFER, meta_name,
               CURLFORM_BUFFERPTR, meta,
               CURLFORM_BUFFERLENGTH, strlen(meta),
               CURLFORM_END);

    struct MemoryStruct resp = { { 0 } };
    /* Fill in the submit field too, even if this is rarely needed */ 

    curl_formadd(&formpost,
               &lastptr,
               CURLFORM_COPYNAME, "image",
               CURLFORM_BUFFER, data_name,
               CURLFORM_BUFFERPTR, intsta.payload,
               CURLFORM_BUFFERLENGTH, intsta.payload_size,
               CURLFORM_END);

    curl = curl_easy_init();
    /* initialize custom header list (stating that Expect: 100-continue is not
     wanted */ 
    headerlist = curl_slist_append(headerlist, "Content-Type: multipart/form-data");
    headerlist = curl_slist_append(headerlist, buf);
    if(curl) {
    /* what URL that receives this POST */ 
    curl_easy_setopt(curl, CURLOPT_URL, "http://192.168.10.121:80/face_rec");
    //if((argc == 2) && (!strcmp(argv[1], "noexpectheader")))
      /* only disable 100-continue header if explicitly requested */ 
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerlist);
    curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
    curl_easy_setopt(curl, CURLOPT_ACCEPT_ENCODING, "gzip,deflate");
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 5L);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &resp);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    /* Perform the request, res will get the return code */ 
    res = curl_easy_perform(curl);
    /* Check for errors */ 
    if(res != CURLE_OK)
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
            curl_easy_strerror(res));

    /* always cleanup */ 
    curl_easy_cleanup(curl);

    /* then cleanup the formpost chain */ 
    curl_formfree(formpost);
    /* free slist */ 
    curl_slist_free_all(headerlist);
    }
    return 0;
}

#if 0
int main(void)
{
    struct MemoryStruct resp = { { 0 } };
    unsigned int respond_tmp;

    PARAM_S param = {.url = "http://192.168.10.147:5000", .method=1};
    INTSTA_S intsta = { 0 };
    char req_url[256];
    CURL *curl;
    CURLM *multi_handle;

    curl_mime *form = NULL;
    curl_mimepart *field = NULL;
    struct curl_slist *headerlist = NULL;
    static const char buf[] = "Expect:";

	curl_global_init(CURL_GLOBAL_ALL);
	curl = curl_easy_init();
	if (curl == NULL) {
		return -1;
	}
    multi_handle = curl_multi_init();

    sprintf(req_url, "%s/detect\0", param.url);

	/* Setup curl header */
    //setupPayload(&intsta);

    if(curl && multi_handle) {
        form = curl_mime_init(curl);
        field = curl_mime_addpart(form);
        curl_mime_name(field, "method");
        curl_mime_filename(field, "method");
        curl_mime_data(field, "0\0", CURL_ZERO_TERMINATED);

        field = curl_mime_addpart(form);
        curl_mime_name(field, "shape");
        curl_mime_filename(field, "shape");
        int shape[] = {1920,1080,3}
        char shape_str[4*3];
        memcpy(shape_str, shape, sizeof(int)*3);
        curl_mime_data(field, shape_str, sizeof(int)*3);
    }
   	struct curl_slist *headers = NULL;
	curl_slist_append(headers, "Accept: application/json");
	curl_slist_append(headers, "Content-Type: application/json");
	curl_slist_append(headers, "charsets: utf-8");
	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_MIMEPOST, form);
	curl_easy_setopt(curl, CURLOPT_URL, req_url);

    //curl_easy_setopt(curl, CURLOPT_HEADER, 0L);
    //curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);

    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &resp);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);

    curl_multi_add_handle(multi_handle, curl);
    curl_multi_perform(multi_handle, &still_running);

    while(still_running) {
        struct timeval timeout;
        int rc; /* select() return code */ 
        CURLMcode mc; /* curl_multi_fdset() return code */ 

        fd_set fdread;
        fd_set fdwrite;
        fd_set fdexcep;
        int maxfd = -1;

        long curl_timeo = -1;

        FD_ZERO(&fdread);
        FD_ZERO(&fdwrite);
        FD_ZERO(&fdexcep);

        /* set a suitable timeout to play around with */ 
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;

        curl_multi_timeout(multi_handle, &curl_timeo);
        if(curl_timeo >= 0) {
            timeout.tv_sec = curl_timeo / 1000;
        if(timeout.tv_sec > 1)
            timeout.tv_sec = 1;
        else
            timeout.tv_usec = (curl_timeo % 1000) * 1000;
        }
        /* get file descriptors from the transfers */ 
        mc = curl_multi_fdset(multi_handle, &fdread, &fdwrite, &fdexcep, &maxfd);

        if(mc != CURLM_OK) {
            fprintf(stderr, "curl_multi_fdset() failed, code %d.\n", mc);
            break;
        }
        if(maxfd == -1) {
#ifdef _WIN32
            Sleep(100);
            rc = 0;
#else
            /* Portable sleep for platforms other than Windows. */ 
            struct timeval wait = { 0, 100 * 1000 }; /* 100ms */ 
            rc = select(0, NULL, NULL, NULL, &wait);
#endif
        } else {
            /* Note that on some platforms 'timeout' may be modified by select().
                If you need access to the original value save a copy beforehand. */ 
            rc = select(maxfd + 1, &fdread, &fdwrite, &fdexcep, &timeout);
        }

        switch(rc) {
        case -1:
            /* select error */ 
            break;
        case 0:
        default:
            /* timeout or readable/writable sockets */ 
            printf("perform!\n");
            curl_multi_perform(multi_handle, &still_running);
            printf("running: %d!\n", still_running);
            break;
        }
    }
    curl_multi_cleanup(multi_handle);
 
    /* always cleanup */ 
    curl_easy_cleanup(curl);
 
    /* then cleanup the form */ 
    curl_mime_free(form);
 
    /* free slist */ 
    curl_slist_free_all(headerlist);
    return 0;
    /*
	if (param.method == 1) {
		curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "POST");
		curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, (long) intsta.payload_size);
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, (char *)intsta.payload);
	} else {
			printf("[CURL] WARN:: Get method not support get!\n");
		curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "GET");
		return -1;
	} */

	/* Send request & wait response*/
    char tmp[200];
    memcpy(tmp, intsta.payload, 200);
    printf("size:%d payload:%s\n", intsta.payload_size, tmp);
	CURLcode res = curl_easy_perform(curl);
    if(res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s %d on %s\n",
              curl_easy_strerror(res), res, param.url);

     /* always cleanup */ 
     printf("get return\n");
    curl_easy_cleanup(curl);
	/* Clean up */
	curl_global_cleanup();
    return 0;
}
#endif
#if 0
int main(int argc, char **argv)
{
  CURL *curl;
  CURLcode res;
    if (argc != 2) {
        return 0;
    }
  curl_global_init(CURL_GLOBAL_ALL);
    printf("request %s %d\n",argv[argc-1], argc);
  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, argv[argc-1]);
 
    /* Perform the request, res will get the return code */ 
    res = curl_easy_perform(curl);
    /* Check for errors */ 
    if(res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s %d\n",
              curl_easy_strerror(res), res);
 
    /* always cleanup */ 
    curl_easy_cleanup(curl);
  }
 
  curl_global_cleanup();
 
  return 0;
}
#endif
