import csv
import math
import random
import sys

from scipy.spatial import distance

class Bee:
    def __init__(self, node_set):
        self.role = ''
        self.path = list(node_set) 
        self.distance = 0
        self.cycle = 0 


def read_data_from_csv(file_name):
    data_list = []
    with open(file_name) as f:
        reader = csv.reader(f)
        data_list = [[int(s) for s in row.split(',')] for row in f]
    return data_list


def get_distance_between_nodes(n1, n2):
    return distance.euclidean([int(x) for x in n1], [int(y) for y in n2])


def make_distance_table(data_list):
    length = len(data_list)
    table = [[get_distance_between_nodes(
        (data_list[i][1],data_list[i][2]), (data_list[j][1],data_list[j][2]))
        for i in range(0, length)] for j in range(0, length)]
    return table


def get_total_distance_of_path(path, table):
    new_path = list(path)
    new_path.insert(len(path), path[0])
    new_path = new_path[1:len(new_path)]

    coordinates = zip(path, new_path)
    distance = sum([table[i[0]][i[1]] for i in coordinates])
    return round(distance, 3)


def initialize_hive(population, data):
    path = [x[0] for x in data]
    hive = [Bee(path) for i in range (0, population)]
    return hive


def assign_roles(hive, role_percentiles, table):
    population = len(hive)
    onlooker_count = math.floor(population * role_percentiles[0])
    forager_count = math.floor(population * role_percentiles[1])

    for i in range(0, onlooker_count):
        hive[i].role = 'O'

    for i in range(onlooker_count, (onlooker_count + forager_count)):
        hive[i].role = 'F'
        random.shuffle(hive[i].path)
        hive[i].distance = get_total_distance_of_path(hive[i].path, table)

    return hive

def mutate_path(path):
    random_idx = random.randint(0, len(path) - 2)
    new_path = list(path)
    new_path[random_idx], new_path[random_idx + 1] = new_path[random_idx + 1], new_path[random_idx]
    return new_path

def forage(bee, table, limit):
    new_path = mutate_path(bee.path)
    new_distance = get_total_distance_of_path(new_path, table)

    if new_distance < bee.distance:
        bee.path = new_path
        bee.distance = new_distance
        bee.cycle = 0 
    else:
        bee.cycle += 1
    if bee.cycle >= limit:
        bee.role = 'S'
    return bee.distance, list(bee.path)


def scout(bee, table):
    new_path = list(bee.path)
    random.shuffle(new_path)
    bee.path = new_path
    bee.distance = get_total_distance_of_path(new_path, table)
    bee.role = 'F'
    bee.cycle = 0


def waggle(hive, best_distance, table, forager_limit, scout_count):
    best_path = []
    results = []

    for i in range(0, len(hive)):
        if hive[i].role == 'F':
            distance, path = forage(hive[i], table, forager_limit)
            if distance < best_distance:
                best_distance = distance
                best_path = list(hive[i].path)
            results.append((i, distance))

        elif hive[i].role == 'S':
            scout(hive[i], table)

    results.sort(reverse = True, key=lambda tup: tup[1])
    scouts = [ tup[0] for tup in results[0:int(scout_count)] ]
    for new_scout in scouts:
        hive[new_scout].role = 'S'
    return best_distance, best_path


def recruit(hive, best_distance, best_path, table):
    for i in range(0, len(hive)):
        if hive[i].role == 'O':
            new_path = mutate_path(best_path)
            new_distance = get_total_distance_of_path(new_path, table)
            if new_distance < best_distance:
                best_distance = new_distance
                best_path = new_path
    return best_distance, best_path


def print_details(cycle, path, distance, bee):
    text = "\\nCYCLE: {}".format(cycle)
    text += "\\nDISTANCE: {}".format(distance)
    text += "\\nBEE: {}".format(bee)
    text += "\\n"
    return text

def calculate(data, population, scout_count, cycle_limit, forager_limit):
    log = ""
    forager_percent = 0.5
    onlooker_percent = 0.5
    role_percent = [onlooker_percent, forager_percent]
    
    cycle = 1

    best_distance = sys.maxsize
    best_path = []
    result = ()
    result_file = "results/{}_nodes/results_{}_nodes_{}_bees_{}_scouts_{}_cycles_{}_forager_limit.csv".format(len(data), len(data), population, scout_count, cycle_limit, forager_limit)

    table = make_distance_table(data)
    hive = initialize_hive(population, data)
    assign_roles(hive, role_percent, table)


    while cycle < cycle_limit:
        waggle_distance, waggle_path = waggle(hive, best_distance, table, forager_limit, scout_count)
        if waggle_distance < best_distance:
            best_distance = waggle_distance
            best_path = list(waggle_path)
            log += print_details(cycle, best_path, best_distance,'F')
            result = {'cycle':cycle, 'best_path':best_path, 'best_distance':best_distance, 'stage':'F'}

        recruit_distance, recruit_path = recruit(hive, best_distance, best_path, table)
        if recruit_distance < best_distance:
            best_distance = recruit_distance
            best_path = list(recruit_path)
            log += print_details(cycle, best_path, best_distance,'R')
            result = {'cycle':cycle, 'best_path':best_path, 'best_distance':best_distance, 'stage':'R'}

        cycle += 1
    result["log"] = log
    return result
#------------------------------------------------------------------------------------#
