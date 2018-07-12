## lib ffmpeg useful command

## Content table
- **[ffplay](#ffplay)**
- **[ffmpeg](#ffmpeg)**
- **[ffprobe](#ffprobe)**
- **[useful links](#useful-links)**
- **[misc](#misc)**  

## ffplay

`ffplay -i {inputfile}`

## ffmpeg  

`ffmpeg -i {inputfile} {outputfile}`


to dump the streaming (audio/video)   
`-acodec copy -vcodec copy`
`-c copy`
`-c:s copy`  `# specify for subtitle`
`-t <time>`  `# specify the duration of recording`
`-ss {input/output} `#specify the start time of the stream`

example  
`ffmpeg -i url -c copy -t 00:00:15 abc.mp4`

embed subtitle to the file / streaming  
`ffmpeg -i {input} -f srt -i {.srt} -map 0:0 -map 0:1 -map 1:0 -c:v copy -c:a copy -c:s mov_text {output}`

map extra srt into streaming  
`ffmpeg -y -v panic -i {input} -f srt -i {.srt} -map 0 -map 1 -c copy -c:s mov_text {output}`

map attachment -> only work for .mkv  -> matroska format
`ffmpeg -y -i {input} -attach {input} -metadata:s:t:0 mimetype=text\plain -f matroska {out}.mkv`

extract streams from input  
`ffmpeg -dump_attachment:#streams {outfile} -i {input} {optional:outputfile}`

stdout fata error only  
`-v {quiet}:0 {panic}:8 {fatal}:16 {warning}:24 {info/debug} `

mapping streams to input
`-map {#input}:{#stream} # eg. -map 0:2 -map 1:0 maps i#0:s#2->out#0:s#0, i#1:s#0->o#0:s#1` 

replace dst file  
`-y`

output to pipe stream
`ffmpeg -re -r 30 -i {input} -c copy -sn -f matroska pipe:1 | ffplay pipe:0`

output rtp streaming  
`ffmpeg -re -r 30 -i {input} -map 0 -sn -f rtp_mpegts rtp://{localhost}:{port}`
**-re** flag means re-streaming at the rate of video, **-r 30** specifies the streaming rate  

broadcast to 2 channels outputs (udp and pipe:)  
`ffmpeg -i {input} -an -f mpegts {udp} -vn -f srt - (pipe:1)`  

snapshot using ffmpeg with defined fps 
`ffmpeg -i {input} -vf fps=1 out%d.png`
snapshot with fps but only update one file  
`ffmpeg -i {input} -vf fps=1 -update 1 tmp.png`
snapshot at a specific time  
`ffmpeg -i {input} -ss 00:00:xx.000 -vframes output.jpg`

pipe jpeg into program  
`ffmpeg -v fatal -i {input} -vf scale=1954:1544 -map v:0 -vsync -c:v mjpeg -pix_fmt yuv420p -f image2pipe -`  
pipe bmp into program  
`ffmpeg -v fatal -i {input} -vf scale=1954:1544 -map v:0 -vsync -c:v rawvideo -pix_fmt brg24 -f image2pipe -`  

## ffprobe  

simply get file metadata  
`ffprobe -i {inputfile}`

simply get streaming meta data  
`ffprobe -show_streams -i {in}`

## useful links   
- [common ffmpeg commands](https://www.labnol.org/internet/useful-ffmpeg-commands/28490/)
- [all commands](https://ffmpeg.org/ffmpeg.html)

## misc
- srt format
```
168
00:20:41,150 --> 00:20:45,109
How did he do that?
```
- summary of attach file:  
`able to attach file to mkv as metadata`
`able to attach text as srt into mp4`