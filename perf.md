## PERF  

if you are developing linux system, and want to analysis performance of your program under linux.
Especially threading performance, 

```
$SDK_DIR/linux/
make menuconfig
```

```
Go to "General setup" and then "Kernel Performance Events And Counters".
Select "Kernel performance events and counters".
steps to enable frame pointer
Save the config and exit.

edit $SDK_DIR/linux/.config

CONFIG_PERF_EVENTS=y
CONFIG_HW_PERF_EVENTS=y
CONFIG_FRAME_POINTER=y

```

```
#define _GNU_SOURCE
...
pthread_create(&tid, foo, NULL);
...
pthread_setname_np(tid, name);
```

at Makefile, add cflags: -fno-omit-frame-pointer

Using Perf


*  for whole system  
$ perf record -F 61 -a -g -o /tmp/whole_system.data -- sleep 180
$ perf script -i /tmp/whole_system.data > $NFS/whole_system.perf


* for one process  

$ perf record -F 61 -p <PID> -g -o /tmp/process_name.data -- sleep 180
$ perf script -i /tmp/process_name.data > $NFS/process_name.perf  
 
Other example.  
Sample on-CPU functions for the specified command, at 61 Hertz.
$ perf record -F 61 <command>  

Sample on-CPU functions for the specified PID, at 61 Hertz, until Ctrl-C.  
$ perf record -F 61 -p <PID>   

Sample on-CPU functions for the specified PID, at 61 Hertz, for 180 seconds.  
$ perf record -F 61 -p <PID> -- sleep 180  

Sample CPU stack traces (via frame pointers) for the specified PID, at 61 Hertz, for 180 seconds.  
$ perf record -F 61 -p PID -g -- sleep 180  

Sample CPU stack traces for the entire system, at 61 Hertz, for 180 seconds (< Linux 4.11).  
$ perf record -F 61 -ag -- sleep 180  

Sample CPU stack traces for the entire system, at 61 Hertz, for 180 seconds (>= Linux 4.11).  
$ perf record -F 61 -g -- sleep 180  


* Report  

Show perf.data in an Text User Interface.
$ perf report

Show perf.data with a column for sample count.  
$ perf report -n

Show perf.data as a text report, with data coalesced and percentages.  
Copy the perf.data from step one to pc and run this command Since busybox curses support is limited.  
$ perf report --stdio

List all events from perf.data.  
$ perf script > out.perf   

List all perf.data events, with customized fields (< Linux 4.1).  
$ perf script -f time,event,trace  
 
Dump raw contents from perf.data as hex (for debugging).  
$ perf script -D  

Disassemble and annotate instructions with percentages (needs some debuginfo).  
$ perf annotate --stdio  

* Analysis  

```
$ cd $FLAME_GRAPH_DIR
$ ./stackcollapse-perf.pl whole_system.perf > whole_system.folded
$ ./flamegraph.pl whole_system.folded > whole_system.svg
```

```
$ python ./perfToFlame.py --prog $FLAME_GRAPH_DIR --input $INPUT_FOLDER --out $OUTPUT_FOLDER
```

from
`https://github.com/brendangregg/FlameGraph.`

```
import os
import argparse
import subprocess

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

class perfFile:
    def __init__(self):
        self.setup()
        self.genFlameGraph()
    
    def genFlameGraph(self):
                
        for f in os.listdir(self.input_path):
            if f.endswith(".perf"):
                f_in = os.path.join(self.input_path, f)
                file_name = os.path.splitext(f)[0]
                
                f_fold = os.path.join(self.tmp_output_path, file_name+'.folded')
                f_out = os.path.join(self.output_path, file_name+'.svg')
                
         
                stackcmd = self.stackcollapse+' '+ f_in + ' > '+ f_fold
                flamecmd = self.flamegraph+' '+f_fold + ' > ' + f_out
                ret = os.system(stackcmd)
                ret = os.system(flamecmd)
                
    def setup(self):
        parsed_args = self.parse_argurment()
        
        stack_name = 'stackcollapse-perf.pl'
        flame_name = 'flamegraph.pl'
        
        self.input_path = parsed_args.input
        self.output_path = parsed_args.out
        self.tmp_output_path = parsed_args.out+'\\tmp'
        self.stackcollapse = parsed_args.prog+'\\'+stack_name
        self.flamegraph = parsed_args.prog+'\\'+flame_name
        
        try:
            os.stat(self.output_path)
        except:
            os.mkdir(self.output_path) 
        
        try:
            os.stat(self.tmp_output_path)
        except:
            os.mkdir(self.tmp_output_path) 
        
        if not os.path.exists(self.stackcollapse):
            raise NotADirectoryError(self.stackcollapse)

        if not os.path.exists(self.flamegraph):
            raise NotADirectoryError(self.flamegraph)
            
    def parse_argurment(self):
        parser = argparse.ArgumentParser(description='Perf')
        parser.add_argument('--input', help='Input file path', type = dir_path)
        parser.add_argument('--prog', help='Flamegraph program path', type = dir_path)
        parser.add_argument('--out', help='Output file path')
        
        return parser.parse_args()
           
```
