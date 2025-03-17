import math
import random
import time
import numpy as np

from utils.Functions import input_transform


class Network:
    def __init__(self, iteration, dimension=3):
        """
        Construct a (N-1) dimensional snowflake networks where N = dimension + 1.
        For example, dimension=3 corresponds to a 3-dimensional fractal,
        i.e., 4 vertices of an orthotetrahedron.
        iteration：Total number of iterations (including initial state as layer 1)
        """
        self.iteration = iteration - 1  # Number of iterations other than the initial state
        self.N = dimension + 1  # Number of vertices in a positive N-simplex
        self.network = {}  # Stores all nodes, keyed by the address of the string obtained by input_transform.
        self.segCache = None  # Store all segments of the current iteration (array of integers)

    def build_network(self):
        timeStart = time.time()
        # ----- Initial Stage -----
        initial_nodes = []
        for i in range(1, self.N + 1):
            label = np.array([i, 0], dtype=int)
            key = input_transform(list(map(str, label)))
            self.network[key] = label.copy()
            initial_nodes.append(label)
        self.segCache = np.array(initial_nodes)
        print("Iteration 1: Node Num:", len(self.network))

        # ----- Iterations -----
        iter_count = 1
        while iter_count <= self.iteration:
            for seg in self.segCache:
                for i in range(1, self.N + 1):
                    new_label = np.concatenate((seg, [i, 0]))
                    key = input_transform(list(map(str, new_label)))
                    self.network[key] = new_label.copy()
            newSegList = []
            for seg in self.segCache:
                r = seg[-2]
                for i in range(1, self.N + 1):
                    if i == r:
                        newSegList.append(np.append(seg, [i, 0]))
                    else:
                        newSegList.append(np.append(seg, [i, 1]))
                        newSegList.append(np.append(seg, [i, 2]))
            newSegList = np.array(newSegList)
            toDelete = []
            for idx, seg in enumerate(newSegList):
                if len(seg) >= 4 and seg[-4] == seg[-2]:
                    toDelete.append(idx)
            newSegList = np.delete(newSegList, toDelete, axis=0)
            self.segCache = newSegList
            print("Iteration %d: Total Node Num: %d" % (iter_count + 1, len(self.network)))
            iter_count += 1

        timeEnd = time.time()
        print("Network has been created. Time Consumed: %.2fs" % (timeEnd - timeStart))
        print("Total Node Num:", len(self.network))
        self.print_nodes_by_level()

    def label_to_binary(self, label):
        """
        Converts a node's label to a full binary address
        Each sub-tag pair occupies ⌈log₂ N⌉ + 1 bit:
          - Fixed prefixes use a binary representation of N-1 (⌈log₂ N⌉ bits);
          - Each pair of sublabels: (a, b) is converted to (a-1) in binary (⌈log₂ N⌉ bits) + b (1 bit).
        """
        bits_first = math.ceil(math.log2(self.N))
        extra = format(self.N - 1, f'0{bits_first}b')
        bin_address = extra
        for i in range(0, len(label), 2):
            a = label[i]
            b = label[i + 1]
            bin_a = format(a - 1, f'0{bits_first}b')
            bin_b = format(b, '01b')
            bin_address += bin_a + bin_b
        return bin_address

    def print_nodes_by_level(self):
        """
        Hierarchical by the number of sub-label pairs, only node information of hierarchy 1~3 is printed.
        """
        level_dict = {}
        for key, label in self.network.items():
            level = len(label) // 2
            if level not in level_dict:
                level_dict[level] = []
            level_dict[level].append((label, self.label_to_binary(label)))
        print("\n===== Node information per layer (only the first three layers are shown) =====")
        for lvl in sorted(level_dict.keys()):
            if lvl > 3:
                continue
            print(f"Level {lvl} (共 {len(level_dict[lvl])} 个节点):")
            for lab, bin_addr in level_dict[lvl]:
                print("  Label:", lab, "-> Binary:", bin_addr)
            print("-------------------------")

    def route_path_nodes(self, source_label, dest_label):
        """
        Calculates the routing process from the source node to the destination node,
        returning each node  passed on the path.
        """

        time.sleep(0.03)        # Suppose the ping between nodes is 30ms
        def label_to_pairs(label):
            return [tuple(label[i:i + 2]) for i in range(0, len(label), 2)]

        src_pairs = label_to_pairs(source_label)
        dst_pairs = label_to_pairs(dest_label)
        # Find the longest common pair sequence
        common = 0
        for a, b in zip(src_pairs, dst_pairs):
            if a == b:
                common += 1
            else:
                break
        if common == 0:
            # If there is no common pair,
            # the initial nodes of the source and the target are used as
            # the upward endpoint and the downward starting point
            s_init = source_label[0:2].tolist()
            d_init = dest_label[0:2].tolist()
            common_label = s_init
            # Upward path: from the source node back upward to the source initial node
            upward = []
            curr = source_label.copy()
            while len(curr) // 2 > 1:
                upward.append(curr.copy().tolist())
                curr = curr[:-2]
            upward.append(s_init)
            # Downward path: extends from the target initial node down to the target node
            downward = []
            curr = d_init.copy()
            for pair in dst_pairs[1:]:
                curr.extend(pair)
                downward.append(curr.copy())
            # Construct complete paths:
            # up path + down path, with jumps in between using initial layer connectivity
            route_nodes = upward + [d_init] + downward
        else:
            common_label = []
            for i in range(common):
                common_label.extend(src_pairs[i])
            # Upward path
            upward = []
            curr = source_label.copy()
            while len(curr) // 2 > common:
                upward.append(curr.copy().tolist())
                curr = curr[:-2]
            upward.append(common_label)
            # Downward path
            downward = []
            curr = common_label.copy()
            for pair in dst_pairs[common:]:
                curr.extend(pair)
                downward.append(curr.copy())
            if downward:
                route_nodes = upward + downward
            else:
                route_nodes = upward
        return route_nodes

    def route_interactive(self):
        """
        Interactive Routing Tests:
        The user enters the source and destination node addresses to display the complete routing path (node label).
        """
        src_input = list(input("Enter source node address (Eg: 4 0 3 2 4 0): ").split())
        dst_input = list(input("Enter destination node address (Eg: 2 0 2 0): ").split())
        src_key = input_transform(src_input)
        dst_key = input_transform(dst_input)
        if src_key not in self.network or dst_key not in self.network:
            print("The source or target node was not found!")
            return
        src_label = self.network[src_key]
        dst_label = self.network[dst_key]
        path_nodes = self.route_path_nodes(src_label, dst_label)
        print("Routing Process (node labels):")
        for node in path_nodes:
            print("  ", node)

    def simulate_routing(self, num_tests=100):
        """
        Routing simulation for randomly selected source and target nodes in the network.
        Counting the average route computation time and average path hops.
        Ensure that the source and target nodes are randomly selected differently each time.
        """
        keys = list(self.network.keys())
        total_time = 0.0
        path_lengths = []
        for _ in range(num_tests):
            src_key = random.choice(keys)
            dst_key = random.choice(keys)
            while dst_key == src_key:
                dst_key = random.choice(keys)
            src_label = self.network[src_key]
            dst_label = self.network[dst_key]
            start = time.time()
            path = self.route_path_nodes(src_label, dst_label)
            elapsed = time.time() - start
            total_time += elapsed
            path_lengths.append(len(path))
        avg_time = total_time / num_tests
        avg_path_length = sum(path_lengths) / num_tests
        print("\n===== Routing Performance Simulation =====")
        print("Average routing computation time. {:.6f} Secs".format(avg_time))
        print("Average path hops: {:.2f}".format(avg_path_length))
        return avg_time, avg_path_length, len(self.network)
