import numpy as np
import time
from Functions import zeroSupplement
from Functions import inputTransform


class Network:
    def __init__(self, iteration, dimension=3):
        self.iteration = iteration - 1
        self.dimension = dimension + 1
        self.node = np.zeros((self.dimension, 48), dtype=bool)   # 48bit address
        self.network = {}
        self.segmentNum = 0
        self.segCache = np.array([[]])      # Initialize segment

    def buildNetwork(self):
        timeStart = time.time()
        self.node[:, :6] = self.writeAddr(0)
        self.network['1'] = self.node.copy()       # First Epoch
        self.updateSeg(0)
        print("Iteration 1:\nSegment Num:%d\nNode Num:%d" % (self.dimension, self.dimension))

        i = 2
        iter = 1
        while True:
            for seg in self.segCache:       # Generate new nodes on existing segments
                self.node[:, :6 * (iter + 1)] = self.writeAddr(iter, segment=seg)
                self.network[str(seg)] = self.node.copy()
                i += 1
            self.updateSeg(iter)
            print("Iteration " + str(iter + 1) + ":\nSegment Num:%d\nNode Num:%d" %
                  (len(self.segCache), len(self.network) * self.dimension))
            if iter == self.iteration:
                self.segmentNum = i - 1
                break
            iter += 1

        timeEnd = time.time()
        timeUsage = timeEnd - timeStart
        print("Network has been created.Time Consumed: %.2fs" % timeUsage)
        print('Segment Num:', len(self.segCache))
        print('Node Num:', len(self.network) * self.dimension)
        # print(self.network)

    def writeAddr(self, iter, segment=[]):
        newAddrs = [ [] for _ in range(self.dimension) ]
        newNodes = np.empty((self.dimension, self.segCache.shape[1]+2), dtype=int)
        if iter == 0:
            for i in range(self.dimension): # Create new node on given segment
                newNodes[i] = np.append(self.segCache, [i + 1, 0])
        else:       # Create new node on given segment
            for i in range(self.dimension):
                newNodes[i] = np.append(segment, [i + 1, 0])

        for j in range(self.dimension):
            for i in range(len(newNodes[j])):
                addr = bin(int(newNodes[j][i]))[2:]
                a_temp = np.array([int(k) for k in addr], dtype=bool)  # Convert bin string to bool array
                a_temp = zeroSupplement(a_temp)
                newAddrs[j].append(a_temp.copy())

        return np.array(newAddrs).reshape(self.dimension, 6 + 6*iter).copy()

    def updateSeg(self, iter):
        if iter == 0:
            self.segCache = np.zeros((self.dimension, 2), dtype=int)
            for i in range(self.dimension):
                self.segCache[i][0] = i + 1
            return
        elif iter == 1:
            segmentTemp = np.array([], dtype=int)      # Segment update of first iteration(subscript0, 1)
            segmentTemp = np.append(segmentTemp, np.append(self.segCache[0], [1, 0]))
            for segment in self.segCache:
                for dim in range(self.dimension):
                    segmentTemp = np.vstack([segmentTemp, np.append(segment, [dim+1, 0])])
                    segmentTemp = np.vstack([segmentTemp, np.append(segment, [dim+1, 1])])
        else:                               # Segment of thr rest of iterations(subscript1, 2)
            segmentTemp = np.array([], dtype=int)
            segmentTemp = np.append(segmentTemp, np.append(self.segCache[0], [1, 0]))
            for segment in self.segCache:
                for dim in range(self.dimension):
                    segmentTemp = np.vstack([segmentTemp, np.append(segment, [dim+1, 1])])
                    segmentTemp = np.vstack([segmentTemp, np.append(segment, [dim+1, 2])])

        segmentTemp = np.delete(segmentTemp, 0, axis=0)
        i = 0
        toDelete = []
        for segment in segmentTemp:         # Remove abundant segments
            if segment[-4] == segment[-2]:
                toDelete.append(i)
            i += 1
        self.segCache = np.delete(segmentTemp, toDelete, axis=0)
        return

    def search(self):
        nodeAddr = list(input("Enter node address: "))
        timeStart = time.time()
        nodeAddr = inputTransform(nodeAddr)
        assert nodeAddr in self.network.keys(), "Node not found"
        timeEnd = time.time()
        timeUsed = timeEnd - timeStart
        print("Successfully locate target node!\nTime consumed:%.5fs\n" % timeUsed, self.network[nodeAddr])


iteration = int(input("Enter number of iterations: "))
dimension = int(input("Enter dimension: "))
n = Network(iteration, dimension)      # It will take a considerable amount of time to iterate 7 times or more
n.buildNetwork()
n.search()
