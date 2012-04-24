import random
import globals

class Neuron():
    def __init__(self, inputs):
        self.inputs = inputs
        self.weights = [2 * random.random() - 1 for input in xrange(inputs)]

class NeuronLayer():
    
    def __init__(self, amount, inputs):
        self.amount_of_neurons = amount
        self.neurons = [Neuron(inputs) for a in xrange(amount)]
        
class NeuronNet():
    
    def __init__(self, inputs, outputs, hidden_layers, neurons_in_hidden):
        self.inputs = inputs
        self.outputs = outputs
        self.hidden_layers = hidden_layers
        self.neuron_in_hidden = neurons_in_hidden
        self.layers = []       
        inputs = self.inputs+1       
        for layer in xrange(self.hidden_layers):
            self.layers.append(NeuronLayer(self.neuron_in_hidden, inputs))
            inputs = self.neuron_in_hidden
        self.layers.append(NeuronLayer(self.outputs, inputs))
    
    def product(self, vec1, vec2):
        amount = 0
        for x, y in zip(vec1, vec2):
            amount += x * y
        return amount
     
    def process(self, input):
        #print input
        for layer in self.layers:
            output = []
            for neuron in layer.neurons:
                #print neuron.weights
                output.append(self.product(input, neuron.weights))
            input = output
        return output
    
    def mate(self, other):
        dad = self
        mum = other
        amount_of_neurons = self.outputs + self.neuron_in_hidden * self.hidden_layers
        newNet = NeuronNet(self.inputs, self.outputs, self.hidden_layers, self.neuron_in_hidden)
        
        if random.randint(0,100) < globals.CROSSOVERRATE:
            crossoverpoint = random.randint(1, amount_of_neurons)
        else: 
            crossoverpoint = 0
        counter = 0
        for layer, dadlayer, mumlayer in zip(newNet.layers, dad.layers, mum.layers):
            for neuron, dadneuron, mumneuron in zip(layer.neurons, dadlayer.neurons, mumlayer.neurons):
                if counter <= crossoverpoint:
                    neuron = dadneuron
                else:
                    neuron = mumneuron
                if random.randint(0, 1000) < globals.MUTATE:
                    if counter < self.neuron_in_hidden:
                        inputs = self.inputs
                    else:
                        inputs = self.neuron_in_hidden
                    neuron = Neuron(inputs)
                counter+=1
        return newNet
'''            
       
nets = [NeuronNet(16,3,1,2) for x in range(2)]
for net in nets:
    print 'new net'
    for h in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
        for i in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
            for j in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
                for k in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
                    lista = [item for sublist in [h,i,j,k,[-1]] for item in sublist]
                    #print lista
                    output = net.process(lista)
                    #print output,
                    if output[0] > output[1] and output[0] > output[2]: print 'l',
                    elif output[2] > output[1] and output[2] > output[0]: print 'r',
                    else: print 'm',
        print

for x in range(8):
    print 'births'    
    nets[0], nets[1] = nets[0].mate(nets[1])
    
    for net in nets:
        print 'new net'
        for h in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
            for i in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
                for j in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
                    for k in [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]:
                        lista = [item for sublist in [h,i,j,k,[-1]] for item in sublist]
                        #print lista
                        output = net.process(lista)
                        if output[0] > output[1] and output[0] > output[2]: print 'l',
                        elif output[2] > output[1] and output[2] > output[0]: print 'r',
                        else: print 'm',
            print
        
'''