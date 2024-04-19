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
        self.segCache = np.array([])      # Initialize segment

    def buildNetwork(self):
        timeStart = time.time()
        self.node[0][:6], self.node[1][:6], self.node[2][:6], self.node[3][:6] = self.writeAddr(0)
        self.network['1'] = self.node.copy()       # First Epoch
        self.updateSeg(0)
        print("Iteration 1:\nSegment Num:4\nNode Num:4")

        i = 2
        iter = 1
        while True:
            for seg in self.segCache:       # Generate new nodes on existing segments
                (self.node[0][:6 * (iter + 1)], self.node[1][:6 * (iter + 1)], self.node[2][:6 * (iter + 1)],
                     self.node[3][:6 * (iter + 1)]) = self.writeAddr(iter, segment=seg)
                self.network[str(seg)] = self.node.copy()
                i += 1
            self.updateSeg(iter)
            print("Iteration " + str(iter + 1) + ":\nSegment Num:%d\nNode Num:%d" %
                  (len(self.segCache), len(self.network) * 4))
            if iter == self.iteration:
                self.segmentNum = i - 1
                break
            iter += 1

        timeEnd = time.time()
        timeUsage = timeEnd - timeStart
        print("Network has been created.Time Consumed: %.2fs" % timeUsage)
        print('Segment Num:', len(self.segCache))
        print('Node Num:', len(self.network) * 4)

    def writeAddr(self, iter, segment=[]):
        newAddr1 = np.array([], dtype=bool)
        newAddr2 = np.array([], dtype=bool)
        newAddr3 = np.array([], dtype=bool)
        newAddr4 = np.array([], dtype=bool)

        if iter == 0:
            newNode1 = np.append(self.segCache, [1, 0])       # Create new node on given segment
            newNode2 = np.append(self.segCache, [2, 0])
            newNode3 = np.append(self.segCache, [3, 0])
            newNode4 = np.append(self.segCache, [4, 0])
        else:
            newNode1 = np.append(segment, [1, 0])  # Create new node on given segment
            newNode2 = np.append(segment, [2, 0])
            newNode3 = np.append(segment, [3, 0])
            newNode4 = np.append(segment, [4, 0])

        for i in range(0, len(newNode1)):
            addr = bin(int(newNode1[i]))[2:]                                           # Convert subscript to bin string
            a_temp = np.array([int(j) for j in addr], dtype=bool)       # Convert bin string to bool array
            a_temp = zeroSupplement(a_temp)
            newAddr1 = np.append(newAddr1, a_temp)

        for i in range(0, len(newNode2)):
            addr = bin(int(newNode2[i]))[2:]                                           # Convert subscript to bin string
            a_temp = np.array([int(j) for j in addr], dtype=bool)       # Convert bin string to bool array
            a_temp = zeroSupplement(a_temp)
            newAddr2 = np.append(newAddr2, a_temp)

        for i in range(0, len(newNode3)):
            addr = bin(int(newNode3[i]))[2:]                                           # Convert subscript to bin string
            a_temp = np.array([int(j) for j in addr], dtype=bool)       # Convert bin string to bool array
            a_temp = zeroSupplement(a_temp)
            newAddr3 = np.append(newAddr3, a_temp)

        for i in range(0, len(newNode4)):
            addr = bin(int(newNode4[i]))[2:]                                           # Convert subscript to bin string
            a_temp = np.array([int(j) for j in addr], dtype=bool)       # Convert bin string to bool array
            a_temp = zeroSupplement(a_temp)
            newAddr4 = np.append(newAddr4, a_temp)

        return newAddr1, newAddr2, newAddr3, newAddr4

    def updateSeg(self, iter):
        if iter == 0:
            self.segCache = np.array([[1, 0], [2, 0], [3, 0], [4, 0]])
            return
        elif iter == 1:
            segmentTemp = np.array([], dtype=int)      # Segment update of first iteration(subscript0, 1)
            segmentTemp = np.append(segmentTemp, np.append(self.segCache[0], [1, 0]))
            for segment in self.segCache:
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [1, 0])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [2, 0])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [3, 0])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [4, 0])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [1, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [2, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [3, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [4, 1])])
        else:                               # Segment of thr rest of iterations(subscript1, 2)
            segmentTemp = np.array([], dtype=int)
            segmentTemp = np.append(segmentTemp, np.append(self.segCache[0], [1, 0]))
            for segment in self.segCache:
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [1, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [2, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [3, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [4, 1])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [1, 2])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [2, 2])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [3, 2])])
                segmentTemp = np.vstack([segmentTemp, np.append(segment, [4, 2])])

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
