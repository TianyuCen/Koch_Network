import random
import time
import matplotlib.pyplot as plt

from network.network import Network


class Task:
    def __init__(self):
        # Shared variables
        self.dimension = None
        self.num_tests = None
        self.iteration = None
        self.mode = None

        # For simulation_mode
        self.iteration_input = None
        self.iterations_list = []

        # For fault simulation mode
        self.fault_rate = None

    def run(self):
        self.mode = input("Select mode (1: Interactive Mode, 2: Simulation Mode, 3: Fault Simulation Mode): ")
        if self.mode.strip() == "1":
            self.interactive_mode()
        elif self.mode.strip() == "2":
            self.simulation_mode()
        elif self.mode.strip() == "3":
            self.fault_simulation_mode()
        else:
            raise IndexError("Invalid mode. Mode must be either 1, 2 or 3")

    def interactive_mode(self):
        """
        Interaction mode: the user inputs the number of iterations and the fractal dimension to construct the network.
        Print the first three layers of node information,
        then enter the source and destination nodes to display the routing path.
        """
        self.iteration = int(input("Enter number of iterations: "))
        self.dimension = int(input("Enter dimension: "))
        net = Network(self.iteration, self.dimension)
        net.build_network()
        net.print_nodes_by_level()
        net.route_interactive()

    def simulation_mode(self):
        """
        Simulation mode: user inputs fractal dimension and multiple iterations, the
        Automatically builds networks and simulates and tests routing performance,
        generating independent performance charts.
        """
        self.dimension = int(input("Enter dimension: "))
        iteration_input = input("Enter iteration counts (comma separated, e.g., 2,3,4,5): ")
        self.iterations_list = [int(x.strip()) for x in iteration_input.split(",")]
        self.num_tests = int(input("Enter number of tests for each iteration count: "))
        self.performance_visualization()

    def fault_simulation_mode(self):
        """
        Failure simulation mode:
        The user enters the fractal dimension, the number of iterations and the failure rate (percentage of nodes failing),
        as well as the number of tests.
        Constructs the network and then randomly removing a certain percentage of nodes to update the network to only healthy nodes.
        The routing algorithm is then executed on the healthy network and the routes are verified using fractal connectivity.
        """
        self.dimension = int(input("Enter dimension: "))
        self.iteration = int(input("Enter number of iterations: "))
        self.fault_rate = float(input("Enter fault rate (e.g., 0.1 indicates that 10% of the nodes failed): "))
        self.num_tests = int(input("Enter number of tests for fault simulation: "))

        # Building a complete network
        net = Network(self.iteration, self.dimension)
        net.build_network()
        total_nodes = len(net.network)
        print("Original Total Node Count:", total_nodes)

        # Simulate node failures: randomly remove nodes with fault_rate proportions
        healthy_count = int(total_nodes * (1 - self.fault_rate))
        healthy_keys = random.sample(list(net.network.keys()), healthy_count)
        healthy_network = {k: net.network[k] for k in healthy_keys}
        print("Healthy Node Count after fault simulation:", len(healthy_network))

        # Updating the network to a healthy one
        net.network = healthy_network

        total_time = 0.0
        path_lengths = []
        successful = 0
        for _ in range(self.num_tests):
            keys = list(healthy_network.keys())
            src_key = random.choice(keys)
            dst_key = random.choice(keys)
            while dst_key == src_key:
                dst_key = random.choice(keys)
            src_label = healthy_network[src_key]
            dst_label = healthy_network[dst_key]
            start = time.time()
            path = net.route_path_nodes(src_label, dst_label)
            elapsed = time.time() - start
            # Determine the success of a route
            if path and path[-1] == dst_label.tolist():
                successful += 1
                total_time += elapsed
                path_lengths.append(len(path))
        success_rate = successful / self.num_tests if self.num_tests > 0 else 0
        avg_time = total_time / successful if successful > 0 else 0
        avg_path_length = sum(path_lengths) / successful if successful > 0 else 0

        print("\n===== Fault Simulation Results =====")
        print("Fault Rate: {:.0%}".format(self.fault_rate))
        print("Routing Success Rate: {:.2%}".format(success_rate))
        print("Average Routing Time (successful routes): {:.6f} 秒".format(avg_time))
        print("Average Path Hops (successful routes): {:.2f}".format(avg_path_length))

    def performance_visualization(self):
        """
        Simulating the network under different number of iterations and counting the network size,
        average route computation time and average path hop count.
        Draw three separate charts, making sure that the chart layouts do not overlap and that the horizontal scales are clear.
        """
        avg_times = []
        avg_hops = []
        total_nodes = []

        for iters in self.iterations_list:
            print("\n---------- Number of iterations: {} ----------".format(iters))
            net = Network(iters, self.dimension)
            net.build_network()
            avg_time, avg_path_length, node_count = net.simulate_routing(self.num_tests)
            avg_times.append(avg_time)
            avg_hops.append(avg_path_length)
            total_nodes.append(node_count)

        # Network size
        plt.figure(figsize=(8, 6))
        plt.plot(self.iterations_list, total_nodes, marker='o')
        plt.xlabel("Iteration Count")
        plt.ylabel("Total Node Count")
        plt.title("Network Scale")
        plt.xticks(self.iterations_list, rotation=45)
        plt.tight_layout()
        plt.show()

        # Average Routing Computation Time
        plt.figure(figsize=(8, 6))
        plt.plot(self.iterations_list, avg_times, marker='o', color='r')
        plt.xlabel("Iteration Count")
        plt.ylabel("Avg Routing Time (sec)")
        plt.title("Routing Computation Time")
        plt.xticks(self.iterations_list, rotation=45)
        plt.tight_layout()
        plt.show()

        # Average Path Hops
        plt.figure(figsize=(8, 6))
        plt.plot(self.iterations_list, avg_hops, marker='o', color='g')
        plt.xlabel("Iteration Count")
        plt.ylabel("Avg Path Hops")
        plt.title("Routing Path Length")
        plt.xticks(self.iterations_list, rotation=45)
        plt.tight_layout()
        plt.show()
