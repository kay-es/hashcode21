import csv
import jgrapht
from collections import Counter
from math import ceil

input_files = ['a', 'b', 'c', 'd', 'e', 'f']
for input_file in input_files:
    input_name = input_file + ".txt"
    with open('data/' + input_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        line_count = 0
        data = list(csv_reader)

        # parse data
        header = data[0] # e.g. 6s, 4 vertices, 5 edges, 2 cars, 1000 bonus
        duration = int(header[0])
        bonus = int(header[4])
        intersections = list(range(0, int(header[1])))
        streets = data[1:1+int(header[2])]
        routes = data[-int(header[3]):]
        
        # build graph
        street_mapping = {s[2]: i for i, s in enumerate(streets)}
        reverse_street_mapping = {i: s[2] for i, s in enumerate(streets)}
        g = jgrapht.create_graph(directed=True, weighted=True, allowing_self_loops=False, allowing_multiple_edges=False)
        g.add_vertices_from(intersections)
        for s in streets:
            g.add_edge(int(s[0]), int(s[1]), weight=int(s[3]), edge=street_mapping[s[2]])
         
        # use of the roads
        all_streets = []
        for s in streets:
            all_streets += [s[2]]
        all_streets = list(set(all_streets))
        used_streets = []
        used_first_streets = []
        for r in routes:
            used_streets += list(set(r[1:]))
            used_first_streets += [r[1]]
        used_streets_counted = Counter(used_streets)
        used_first_streets_counted = Counter(used_first_streets)
        used_streets = list(set(used_streets))
        unused_streets = [street_mapping[x] for x in list(set(all_streets) - set(used_streets))]
        
        # build solution with prepared data and simple heuristics
        solution = []
        vertices_counter = 0
        for v in g.vertices:
            incoming_edges = sorted(list(set(g.inedges_of(v)) - set(unused_streets)), key=lambda x: (used_first_streets_counted.get(reverse_street_mapping[x], 0), used_streets_counted[reverse_street_mapping[x]]), reverse=True)
            no_adjustments = len(incoming_edges)
            if no_adjustments > 0:
                vertices_counter += 1
                solution.append(v)
                solution.append(no_adjustments)
                # heuristic 1: high use of street ~ average green w.r.t. weight of street: count(usage) / weight
                # heuristic 2: give a maximum (e.g. 5) and minimum (e.g. 1) duration for green
                edge_durations = [int(ceil(used_streets_counted[reverse_street_mapping[incoming_edge]] / g.get_edge_weight(incoming_edge))) for incoming_edge in incoming_edges]
                edge_durations = [int((d-min(edge_durations))/max(max(edge_durations), (max(edge_durations) - min(edge_durations)))*4 + 1) for d in edge_durations]
                
                for incoming_edge, edge_duration in zip(incoming_edges, edge_durations):
                    street_name = reverse_street_mapping[incoming_edge]
                    solution.append(f"{street_name} {min(5, min(edge_duration, duration))}")

        with open('submission/' + input_name, 'w') as f:
            f.write(f"{vertices_counter}\n")
            for item in solution:
                f.write("%s\n" % item)
            print(input_name + " done")
        