import numpy as np
import networkx as nx
from scipy.special import binom
from skimage import measure
import sys
import itertools
import time


def num_regions(p):
    '''
    counts the number of regions in p
    
    Parameters
    ----------
    p   :   list
        cube coordinates
    
    Returns
    -------
    int
        number of regions found from the cubes
    '''
    A = polycube_to_graph(p)
    
    G = nx.from_numpy_matrix(A)
    
    return nx.number_connected_components(G)


def convert_to_decimal(b, num):
    '''
    converts num in base b to 10
    this works for base 2 through 10
    
    Parameters
    ----------
    b   :   int
        base of num
    num :   int
        number to convert to decimal
    
    Returns
    -------
    int
        num in base 10
    '''
    
    if num == 0:
        return '0'
    else:
        numDigits = int(np.ceil(np.log10(num+1)/np.log10(b)))
    
    returnStr = ''
    
    for i in range(numDigits-1, -1, -1):
        digitToAdd = int(np.floor(num/(b**i)))
        returnStr += str(digitToAdd)
        num -= (b**i)*digitToAdd
        
    return returnStr
        

def unrank_kSubset(r, k, n):
    '''
    bijection that turns an integer to a k-subset
        of n elements
        
    Parameters
    ----------
    r   :   int
        rank of the subset
    k   :   int
        size of the subset 
    n   :   int
        size of the original set
    
    Returns
    -------
    list
        k-subset defined by (r,k,n) parameters
    '''
    
    T = [0]*k
    x = n
    for i in range(1,k+1):
        
        c = int(binom(x, k+1-i))
            
        while c > r:
            
            x -= 1
            c = int(binom(x, k+1-i))
            
        T[i-1] = x
        r -= int(binom(x, k+1-i))
    return T


def checkTree(edgeList, n):
    '''
    checks if a given edge list is a tree
    
    Parameters
    ----------
    edgeList    :   list
        edgelist of the graph
    n           :   int
        number of nodes the graph is on
    
    Returns
    -------
    bool
        True if edgeList defines a tree
    '''
    A = np.zeros((n,n))
    
    for edge in edgeList:
        A[edge] = 1
    
    G = nx.from_numpy_matrix(A)
    
    return nx.is_tree(G)
    
    
def brute_force_trees(n, E):
    '''
    Brute force search through all (n-1)-subsets in (E)
    
    Parameters
    ----------
    n   :   int
        Number of nodes (cubes)
    E   :   list
        edge list of the graph
        
    Returns
    -------
    list
        list containing the edge lists of the spanning trees
    '''
    
    validTrees = []
    
    m = len(E)
    
    numSubsets = int(binom(m, n-1))
    
    for i in range(numSubsets):
        
        subset = unrank_kSubset(i, n-1, m)
        
        edgeSubset = []
        
        for j in subset[::-1]:
            
            edgeSubset.append(E[j-1])
            
        if checkTree(edgeSubset, n):
        
            validTrees.append(edgeSubset)
        
    return validTrees


def check_all_isomorphism(p1, p2):
    """
    Performs all 48 symmetries on polycube2 (p2)
        and checks if it's equal to polycube1 (p1)
        
    48 symmetries come from the octahedral group with reflections
        (O48)
    
    Parameters
    ----------
    p1  :   list
        cube coordinates
    p2  :   list
        cube coordinates
        
    Returns
    -------
    bool
        True if p1 and p2 are isomorphic under O48 symmetries
    """
    
    #use p1 as the comparison
    fixedCoordinates = set(p1)
    
    #get all coordinates
    coordinateSet = p2
    
    #get all x coordinates in a list, all y in a list, all z in a list
    coordinatesSplit = list(zip(*coordinateSet))
    
    #offset to reflect each coordinate by 
    reflectPoints = [max(coor) for coor in coordinatesSplit]
    
    coorReflect = list(itertools.product('01', repeat=3))
    
    permutations = list(itertools.permutations('012'))
    
    #check each permutation of the coordinates
    for permute in permutations:
        
        #permutation indices
        i,j,k = permute[0], permute[1], permute[2]
        i = int(i)
        j = int(j)
        k = int(k)
        
        #get reflection args
        a,b,c = reflectPoints[i], reflectPoints[j], reflectPoints[k]
        
        #check each possible reflection of each coordinate
        for reflect in coorReflect:
            
            rX = int(reflect[0])
            rY = int(reflect[1])
            rZ = int(reflect[2])
            
            newCoordSet = set()
            
            for coord in coordinateSet:
                
                #permute the coordinates
                x,y,z = coord[i], coord[j], coord[k]
                
                #reflect the coordinates
                if rX:
                    x = a-x
                if rY:
                    y = b-y
                if rZ:
                    z = c-z
                
                #add new coordinate under the map
                newCoord = (x, y, z)
                newCoordSet.add(newCoord)
            
            #check if mapping equals the comparison set
            if newCoordSet == fixedCoordinates:
                return True
            
    #at this point, none match
    return False


def check_poly_isomorphism(p1, p2):
    """
    Performs all 8 symmetries on polycube2 (p2)
        and checks if it's equal to polycube1 (p1)
        
    8 symmetries come from dihedral group of order 8 (D8)
        (treat the xy-plane as the square under symmetries)
        
    Parameters
    ----------
    p1  :   list
        cube coordinates
    p2  :   list
        cube coordinates
        
    Returns
    -------
    bool
        True if p1 and p2 are isomorphic under D8 symmetries in xy-plane
    """
    
    #use p1 as the comparison
    fixedCoordinates = set(p1)
    
    #get all coordinates
    coordinateSet = p2
    
    #get all x coordinates in a list, all y in a list, all z in a list
    coordinatesSplit = list(zip(*coordinateSet))
    
    #offset to reflect each coordinate by 
    reflectPoints = [max(coor) for coor in coordinatesSplit]
    
    #symmetries only on x and y
    coorReflect = list(itertools.product('01', repeat=2))
    permutations = list(itertools.permutations('01'))

    #check each permutation of the coordinates
    for permute in permutations:
        
        #permutation indices
        i,j = permute[0], permute[1]
        i = int(i)
        j = int(j)
        
        #get reflection args
        a,b = reflectPoints[i], reflectPoints[j]
        
        #check each possible reflection of each coordinate
        for reflect in coorReflect:
            
            rX = int(reflect[0])
            rY = int(reflect[1])
            
            newCoordSet = set()
            
            for coord in coordinateSet:
                
                #permute x and y coordinates
                x,y,z = coord[i], coord[j], coord[2]
                
                #reflect the coordinates
                if rX:
                    x = a-x
                if rY:
                    y = b-y
                
                #add new coordinate under the map
                newCoord = (x, y, z)
                newCoordSet.add(newCoord)
            
            #check if mapping equals the comparison set
            if newCoordSet == fixedCoordinates:
                return True
            
    #at this point, none match
    return False


def get_polycubes_of_size(k):
    '''
    finds all polycube structures of size k that
        exists in a 5x5x5 bounding box
    
    Parameters
    ----------
    k   :   int
        Number of polycubes
    
    Returns
    -------
    list
        list that contains lists of polycube cube coordinates
    '''
    
    totalPossibilities = int(binom(125, k))
    
    returnUnique = []
    
    for r in range(totalPossibilities):
        
        #get a list of coordinate ranks in base 5
        coordinateRanks = unrank_kSubset(r=r, k=k, n=125)
        
        #convert coordinates ranks to base 10
        coordinateBases = [convert_to_decimal(5, x) for x in coordinateRanks]
        
        #0 pad to length 3
        coordinateStrings = [x.zfill(3) for x in coordinateBases]
        
        #split string into coordinates
        coordinates = [[x for x in str] for str in coordinateStrings]
        
        #convert to ints
        coordinates = [tuple([int(x) for x in coor]) for coor in coordinates]
        
        #we want one connected component
        if num_regions(coordinates) != 1:
            continue
        
        #this handles translational symmetries
        minX = np.min([x[0] for x in coordinates])
        minY = np.min([x[1] for x in coordinates])
        minZ = np.min([x[2] for x in coordinates])
        coordinates = [(x[0]-minX, x[1]-minY, x[2]-minZ) for x in coordinates]
        
        #check against previously added polycubes
        unique = True
        for alreadyAdded in returnUnique:
            if check_poly_isomorphism(alreadyAdded, coordinates):
                #if isomorphic, skip
                unique = False
                break         
                
        if unique:
            #print(coordinates)
            returnUnique.append(coordinates)
        
    return returnUnique


def matrix_minor(A, r, c):
    '''
    Removes a row and a column from an adjacency matrix
    
    Parameters
    ----------
    A   :   numpy 2-d array
        adjacency matrix
    r   :   int
        row index to delete
    c   :   int
        column index to delete
        
    Returns
    -------
    numpy 2-d array
        adjacency matrix after deletions
    '''
    #delete row
    Ar = np.delete(A, r, 0)
    
    #delete column
    Arc = np.delete(Ar, c, 1)
    
    return Arc


def taxi_distance(v1, v2):
    '''
    taxi cab metric distance between v1 and v2
    
    Parameters
    ----------
    v1  :   list
        first point
    v2  :   list
        second point
    
    Returns
    -------
    float
        taxi cab distance between v1 and v2 
    '''
    
    assert len(v1)==len(v2), "taxi_distance: v1 and v2 are not of the same dimension"
    
    d = 0
    for x,y in zip(v1, v2):
        d += np.abs(x-y)
    
    return d
    
    
def polycube_to_graph(p):
    '''
    converts a polycube into a graph by connecting
        polycubes (nodes) if they share a face
    
    Parameters
    ----------
    p   :   list
        list of cube coordinates
        
    Returns
    -------
    numpy 2-d array
        adjacency matrix of the cubes
    '''
    N = len(p)
    
    A = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            if int(taxi_distance(p[i], p[j])) == 1:
                A[i, j] = 1
    
    return A
    

def get_edge_list(G):
    '''
    Returns an edge list of the given graph
    
    Parameters
    ----------
    G   :   networkx graph object
        graph to find the edge list of
        
    Returns
    -------
    list
        edge list where edges are 2-tuples of ints
    '''
    edges = []
    
    for line in nx.generate_edgelist(G):
        
        line = line.split()
        
        x = int(line[0])
        y = int(line[1])
        
        edges.append((x, y))
        
    return edges    
        
    
if __name__ == '__main__':
    
    test = sys.argv[1]
    
    d1 = [(0,0,0), 
          (0,0,1),
          (0,1,1),
          (0,1,2),
          (1,1,1),
          (1,1,2)]

    d2 = [(0,0,0), 
          (1,0,0),
          (2,0,0),
          (3,0,0),
          (4,0,0),
          (5,0,0)]
    
    d3 = [(0,0,0), 
          (0,1,0),
          (0,2,0),
          (0,3,0),
          (0,4,0),
          (0,5,0)]

    d4 = [(0,0,0), 
          (1,0,0),
          (1,1,0),
          (2,1,0),
          (1,1,1),
          (2,1,1)]
    
    if test == 'all':
        #all checks
        print(check_all_isomorphism(d1, d2))
        print(check_all_isomorphism(d1, d3))
        print(check_all_isomorphism(d1, d4))
        print(check_all_isomorphism(d2, d3))
        print(check_all_isomorphism(d2, d4))
        print(check_all_isomorphism(d3, d4))
        
    elif test == 'poly':
        #polycube checks
        print(check_poly_isomorphism(d1, d2))
        print(check_poly_isomorphism(d1, d3))
        print(check_poly_isomorphism(d1, d4))
        print(check_poly_isomorphism(d2, d3))
        print(check_poly_isomorphism(d2, d4))
        print(check_poly_isomorphism(d3, d4))
        
    elif int(test):
        
        numCubes = int(test)
        
        begin = time.time()
        listOfPolycubes = get_polycubes_of_size(numCubes)
        
        print('Number of Structures Found: %d'%len(listOfPolycubes))
        
        print('Structure  :  Number of Articulations  :  Trees')
        print('-------------------------------------')
        for polycube in listOfPolycubes:
            
            #kirchoff's matrix-tree theorem to count 
            # #number of spanning trees
            A = polycube_to_graph(polycube)
            G = nx.from_numpy_matrix(A)
            #Q = nx.laplacian_matrix(G).todense()
            #Q_star = matrix_minor(Q, 1, 1)
            #numTrees = int(np.linalg.det(Q_star))
            
            edges = get_edge_list(G)
            trees = brute_force_trees(numCubes, edges)
            numTrees = len(trees)
            
            print(polycube, ':      ', numTrees, ':      ', trees)

        print('Time to run: %0.2f seconds'%(time.time() - begin))
        