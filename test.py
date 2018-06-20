import numpy as np

class Layers:
    def __init__(self,name,func_,prev=None):       
        self.ops = func_
        self.name = name
        self.next_layer = []
        self.next_layer_count = 0
        self.prev = prev
        
    def get_info(self):
        def get_next_name():
            for i in self.next_layer:
                yield i.name
        if self.name.find('output') > -1:
            print(self.name,self.ops.__name__)
        else:
            print(self.name,self.ops.__name__,list(get_next_name()))        

    def add_next(self,list_):
        for name,func_ in list_: 
            self.next_layer.append(Layers(name,func_,prev=self))
            self.next_layer_count += 1
        if self.next_layer_count == 1:
            return self.next_layer[0] 
        elif self.next_layer_count ==2:
            return self.next_layer
    
    
    def run_ops(self,data):
        return self.ops(data)
        
    def input_node(self):
        if self.name != 'input':
            return self.prev.input_node()
        else:
            return self
    def feed(self,data=None):
        self.get_info()
        data = self.run_ops(data)
        if self.name.find('output')>-1:
            return data
        elif self.next_layer_count==1:
            return self.next_layer[0].feed(data)
        elif self.next_layer_count==2:
            return self.next_layer[0].feed(data),self.next_layer[1].feed(data)
        
        
       


for n in range(5,600,50):
    np.random.seed(147)
    npr = np.random.randn    
    w0 = npr(n,n)
    w1 = npr(n,n)
    w2 = npr(n,n)
    w3 = npr(n,n)
    w4 = npr(n,n)
    network = (Layers('input',lambda x: x)
                .add_next([('conv1',lambda x: x@w0)])
                .add_next([('conv2',lambda x: x@w1)])
                .add_next([('conv3',lambda x: x@w2)])
                .add_next([('conv4-1',lambda x: x@w3),('conv4-2',lambda x: x@w2)])
                )
    (network[0].add_next([('output-1',lambda x: x@w4)]))
    (network[1].add_next([('output-2',lambda x: x@w4)]))
    network = network[1].input_node()
    import time
    t = time.time
    ti = t()
    x = npr(n,n)
    output = network.feed(data=x)
    toc = t()-ti
    print('output shape: %s, time needed %s'%((output[0].shape,output[1].shape),toc))


