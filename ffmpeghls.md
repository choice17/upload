## HLS Specification  

* Reference  
** https://developer.apple.com/documentation/http_live_streaming  
** https://developer.apple.com/streaming/  
** https://tools.ietf.org/html/rfc8216  

* FFMPEG HLS command  
** https://www.ffmpeg.org/ffmpeg-formats.html#hls-1  
** https://www.ffmpeg.org/ffmpeg-formats.html#Options-5  


* convert video to .ts  

case 0 input from file (video)  
```
$ ./ffmpeg -re -r 12 -i /tmp/video_FEN105_0 -f h264 -c:v cop
y -c:a copy -f hls -hls_time 2 -hls_list_size 2 -hls_flags delete_segments /tmp/
test.m3u8
```
 
Case 1. pipe input (video + audio)  
```
$ cat /mnt/nfs/hls/video_FEN105_0 | /mnt/nfs/tools/ffmpeg -re -i pipe: -sample_rate 8000 -channels 1 -f alsa -i "default" -c:a libfdk_aac -c:v copy -f hls -hls_time 2 -hls_list_size 2 -hls_flags delete_segments /mnt/nfs/hls/test.m3u8
```

Case 2. pipe output (video + audio)  
```
$ /mnt/nfs/dump_stream | /mnt/nfs/tools/ffmpeg -r 12 -probesize 10000 -analyzeduration 0 -i pipe: -sample_rate 8000 -channels 1 -f alsa -thread_queue_size 1024 -itsoffset 1 -i "default" -c:v copy -c:a libfdk_aac -f hls -hls_time 5 -hls_list_size 3 -hls_flags delete_segments /tmp/live/test.m3u8
```



