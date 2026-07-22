import random as rd
from scamp import wait
import json

def save_json(filename, content, encoder = None):
    dumped_content = json.dumps(content, cls = encoder)
    json_file = open(filename, 'w')
    json_file.write(dumped_content)
    json_file.close()

def load_json(filename):
    json_file = open(filename, 'r')
    content = json.load(json_file)
    json_file.close()
    return content

def play_part(part_dict):
    events = part_dict['events']
    for pitch, dur in events:
        if pitch=='R':
            wait(float(dur))
        else:
            part_dict['inst'].play_chord(pitch, 1, float(dur))

def generate_neighbor(node, n, k, l, weights):

    bag = list(range(k))
    fixed_indices = []

    # TODO: usar probabilidades para decidir quem sai da tupla
    for _ in range(l):
        fixed_indices.append( bag.pop(rd.randint(0, len(bag)-1)) )

    neighbor = []

    for i in range(k):
        x = node[i]

        if i in fixed_indices:
            neighbor.append(x)
        
        else:
            bag = list(range(1, x)) + list(range(x+1, n+1))
            w = weights[:x-1] + weights[x:]
            y = rd.choices( bag, w, k=1)[0]
            neighbor.append(y)

    return tuple(neighbor)

    

def generate_sequence(n, k, l, measures, weights=None):

    if not weights:
        weights = [100/n]*n

    bag = list(range(1,n+1))

    #print(bag, weights)
    cur_node = tuple(rd.choices(bag, weights, k = k))
    sequence = [cur_node]

    for i in range(measures-1):

        cur_node = generate_neighbor(cur_node, n, k, l, weights)
        sequence.append(cur_node)
    
    return sequence