from django.shortcuts import render,HttpResponse
from .bees import calculate
from querystring_parser import parser
import json

# Create your views here.
def homepage(request):
    return render (request,'base.html')

def answer(request):
    global data,population, scout_count, cycle_limit, forager_limit
    
    req = parser.parse(request.POST.urlencode())
    cities = req['city'] if 'city' in req.keys() else json.loads(request.session['cities'])

    if 'data' in req.keys():
        data = req['data']
        data = [[int(y) for x,y in v.items()] for k,v in data.items()]    
    else:
        data = json.loads(request.session['data'])
        data = [[int(x) for x in d] for d in data] 
    print(data)
    
    population = int(req['population']) if 'population' in req.keys() else 180
    scout_count = int(req['scout_count']) if 'scout_count' in req.keys() else 36
    cycle_limit = int(req['cycle_limit']) if 'cycle_limit' in req.keys() else 100
    forager_limit = int(req['forager_limit']) if 'forager_limit' in req.keys() else 500

    request.session['data'] = json.dumps(data)
    request.session['cities'] = json.dumps(cities)
    
    global s
    s = 0
    ans = calculate(data,population, scout_count, cycle_limit, forager_limit)
    return render (request,'result.html',{'ans':json.dumps(ans),'cities':cities, 'population' : population, 'scout_count':scout_count, 'cycle_limit':cycle_limit, 'forager_limit':forager_limit})


# Python3 program to implement traveling salesman 
# problem using naive approach. 
from sys import maxsize 
V = 5

def getDictArray(post, name):
    dic = {}
    for k in post.keys():
        if k.startswith(name):
            rest = k[len(name):]
			
			# split the string into different components
            parts = [p[:-1] for p in rest.split('[')][1:]
            id = int(parts[0])
			
			# add a new dictionary if it doesn't exist yet
            if id not in dic:
                dic[id] = {}
				
			# add the information to the dictionary
            dic[id][parts[1]] = post.get(k)
    return dic

# implementation of traveling Salesman Problem 
def travellingSalesmanProblem(graph, s): 

	# store all vertex apart from source vertex 
	vertex = [] 
	for i in range(V): 
		if i != s: 
			vertex.append(i) 

	# store minimum weight Hamiltonian Cycle 
	min_path = maxsize 

	while True: 

		# store current Path weight(cost) 
		current_pathweight = 0

		# compute current path weight 
		k = s 
		for i in range(len(vertex)): 
			current_pathweight += graph[k][vertex[i]] 
			k = vertex[i] 
		current_pathweight += graph[k][s] 

		# update minimum 
		min_path = min(min_path, current_pathweight) 

		if not next_permutation(vertex): 
			break

	return min_path 

# next_permutation implementation 
def next_permutation(L): 

	n = len(L) 

	i = n - 2
	while i >= 0 and L[i] >= L[i + 1]: 
		i -= 1

	if i == -1: 
		return False

	j = i + 1
	while j < n and L[j] > L[i]: 
		j += 1
	j -= 1

	L[i], L[j] = L[j], L[i] 

	left = i + 1
	right = n - 1

	while left < right: 
		L[left], L[right] = L[right], L[left] 
		left += 1
		right -= 1

	return True



