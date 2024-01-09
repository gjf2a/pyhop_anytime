from pyhop_anytime import State, TaskList, Planner, MonteCarloPlannerHeap
import random
import math
import heapq


def euclidean_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def random_coordinate(bound):
    return (random.random() * bound) - bound/2


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.locations = [(random_coordinate(width), random_coordinate(height)) for i in range(num_cities)]
    state.at = 0
    state.visited = set()
    return state, [('nondeterministic_choice',)]


# Adapted from: https://reintech.io/blog/pythonic-way-of-implementing-kruskals-algorithm
# In spite of what the author above says, this is actually Prim's Algorithm.
def spanning_tree(tsp_state):
    num_cities = len(tsp_state.locations)
    edges = [(euclidean_distance(tsp_state.locations[0], tsp_state.locations[i]), 0, i)
             for i in range(1, num_cities)]
    heapq.heapify(edges)
    visited = {0}
    mst = {i: [] for i in range(num_cities)}
    mst_cost = 0

    while edges:
        cost, src, dest = heapq.heappop(edges)
        if dest not in visited:
            visited.add(dest)
            mst[src].append(dest)
            mst_cost += cost
            for successor in range(num_cities):
                if successor not in visited:
                    heapq.heappush(edges, (euclidean_distance(tsp_state.locations[dest],
                                                              tsp_state.locations[successor]),
                                           dest,
                                           successor))
    return mst, mst_cost


def dfs_mst(mst):
    visited = []
    dfs_mst_help(mst, 0, visited)
    return visited


def dfs_mst_help(mst, node, visited):
    if node not in visited:
        visited.append(node)
        for child in mst[node]:
            dfs_mst_help(mst, child, visited)


def mst_tour_cost(mst, locations):
    visited = dfs_mst(mst)
    return sum([euclidean_distance(locations[visited[i]], locations[visited[(i + 1) % len(visited)]])
                for i in range(len(visited))])


def move(state, new_city):
    if new_city not in state.visited:
        state.visited.add(new_city)
        state.at = new_city
        return state


def nondeterministic_choice(state):
    if len(state.visited) == len(state.locations):
        return TaskList(completed=True)
    tasks = [[('move', city), ('nondeterministic_choice',)]
             for city in range(1, len(state.locations)) if city not in state.visited]
    if len(tasks) == 0:
        return TaskList([('move', 0)])
    else:
        return TaskList(tasks)


def tsp_planner():
    planner = Planner(cost_func=lambda state, step: euclidean_distance(state.locations[state.at],
                                                                       state.locations[step[1]]))
    planner.declare_operators(move)
    planner.declare_methods(nondeterministic_choice)
    return planner


def summarize(header, mst_size, mst_tour_size, plans):
    print(f"{header}: {len(plans)} plans")
    print(f"First cost {plans[0][1]:7.2f}\tMST Ratio: {plans[0][1] / mst_size:7.2f}\tMST Tour Ratio: {plans[0][1] / mst_tour_size:7.2f}\ttime {plans[0][2]:4.2f}")
    print(f"Last cost  {plans[-1][1]:7.2f}\tMST Ratio: {plans[-1][1] / mst_size:7.2f}\tMST Tour Ratio: {plans[-1][1] / mst_tour_size:7.2f}\ttime {plans[-1][2]:4.2f}")


# Experiment notes:
#  With 25 cities, 5 seconds produces nice results for incremental random.
#  With 50 cities, 5 seconds yields a length-7 prefix, and the results are indistinguishable from pure random.
#    35 seconds yields 1 full reset and a length-15 prefix, but the results still aren't better.
#    60 seconds yields 2 full resets and a length-3 prefix, and at that point the results improve a lot!
#    * MST: 974.42
#    * DFS: 5057.25
#    * Random: 4124.67
#    * Random no max: 3921.01
#    * Random incremental: 3533.25, after 45 seconds (!)
#
# Hypothesis: min of 4 is simply better than 2, so if we switch from 2 to 3 it should do better.
# Experiment: Start min at 3, then run for 30 seconds.
# Results:
# * MST: 983.72
# * DFS: 5082.02
# * Random: 4262.92
#   2710 attempts
# * Random no-max: 4210.91
#   2748 attempts
# * Random incremental: 3761.88
#   * 1 full reset, 1 prefix step, 4000 attempts
#
# It looks like throwing in the prefix increases the number of attempts we can make, and in a more favorable part
# of the search space as well.

def tsp_experiment(num_cities, max_seconds):
    print(f"{num_cities} cities, {max_seconds}s time limit")
    p = tsp_planner()
    s, t = make_metric_tsp_state(num_cities, 200, 200)
    print(s.locations)
    mst, mst_size = spanning_tree(s)
    print(mst)
    visited_cost = mst_tour_cost(mst, s.locations)
    print(f"Minimum spanning tree: {mst_size:7.2f}")
    print(f"MST tour cost: {visited_cost:7.2f}\tMST Ratio: {visited_cost / mst_size:7.2f}")
    summarize("DFS", mst_size, visited_cost, p.anyhop(s, t, max_seconds=max_seconds))
    summarize("Random", mst_size, visited_cost, p.anyhop_random(s, t, max_seconds=max_seconds))
    summarize("Random no-max", mst_size, visited_cost, p.anyhop_random(s, t, use_max_cost=False, max_seconds=max_seconds))
    summarize("Random incremental", mst_size, visited_cost, p.anyhop_random_incremental(s, t, max_seconds=max_seconds))
    summarize("Random action tracked", mst_size, visited_cost, p.anyhop_random_tracked(s, t, max_seconds=max_seconds))
    #summarize("MC", p.anyhop(s, t, max_seconds=3, queue_init=lambda: MonteCarloPlannerHeap(p, go_deep_first=False)))
    #summarize("MC go deep", p.anyhop(s, t, max_seconds=3, queue_init=lambda: MonteCarloPlannerHeap(p, go_deep_first=True)))


if __name__ == '__main__':
    tsp_experiment(25, 5)
    tsp_experiment(50, 30)

# A representative run
#
# 25 cities, 5s time limit
# [(64.19429414643298, 32.31289600313076), (-96.28192586066695, 97.10403502125001), (-19.12668577195265, -64.99574982854568), (61.401576009136306, -27.432968112193763), (-53.11937282091144, 80.98285546550008), (64.38150877187587, -59.646897635990626), (23.009431276645316, 29.92845685519299), (-27.181024402249193, -10.567419381568726), (-72.12015163242793, 75.990944164995), (-46.411854384273354, -17.023773569511107), (7.5752743500411555, -66.56205764220749), (-89.38133129110074, 84.53008666614048), (-97.0608027764861, 12.855871794799441), (-81.97380055365862, -40.45953131104578), (-38.00879915964357, 4.064157885491213), (-99.31289910235522, 9.50864944640324), (82.40450099499611, -90.5614490850647), (60.63427700857312, 7.549917190470865), (58.76870023168385, 92.53723020947953), (3.5631910387187986, -93.13353315781205), (-59.684116758744146, -69.97746260834859), (50.235777419560605, -30.781611975755553), (-82.11854473732237, -12.104742873275057), (-47.647791987385226, 90.46774162724586), (-45.80177658101272, 17.656737763627234)]
# {0: [17, 6, 18], 1: [], 2: [20], 3: [21], 4: [23, 8], 5: [16], 6: [], 7: [14], 8: [11], 9: [7], 10: [2, 19], 11: [1], 12: [], 13: [22], 14: [24], 15: [12], 16: [], 17: [3], 18: [], 19: [], 20: [13], 21: [5, 10], 22: [15, 9], 23: [], 24: [4]}
# Minimum spanning tree:  706.62
# MST tour cost: 1104.49	MST Ratio:    1.56
# DFS: 16 plans
# First cost 2840.39	MST Ratio:    4.02	time 0.01
# Last cost  2251.94	MST Ratio:    3.19	time 0.70
# attempts: 2068
# Random: 8 plans
# First cost 3160.68	MST Ratio:    4.47	time 0.00
# Last cost  1966.17	MST Ratio:    2.78	time 2.67
# attempts: 1704
# Random no-max: 9 plans
# First cost 2525.10	MST Ratio:    3.57	time 0.00
# Last cost  1867.20	MST Ratio:    2.64	time 2.84
# attempts: 2202 Full resets: 1 Prefix steps: 12
# Random incremental: 14 plans
# First cost 2841.96	MST Ratio:    4.02	time 0.00
# Last cost  1746.25	MST Ratio:    2.47	time 1.71
# 50 cities, 30s time limit
# [(45.832775659228616, 60.98885032988915), (15.133127718919809, 24.952139084117064), (-53.07466401758383, -8.349343085095228), (-53.58312930568972, 33.55302995115704), (59.45271681678969, 91.58596840193692), (2.5603857880141874, 64.94609611190455), (-4.568397896473229, -53.29786147852782), (51.3642154378995, 43.01906470305309), (89.53567238902218, -19.419906665826247), (68.67271222379847, 78.70261513595383), (-74.45591188704641, 4.016635233672488), (-42.793437850000316, -35.372425178530165), (-67.17867996314011, -57.19504060410636), (-78.98869739792545, -56.450409294172466), (55.88104030970467, -12.034156452065332), (96.84390607732706, 96.13360604421425), (-6.631730660424196, -30.652308221456323), (45.29416114417734, 8.508059040404035), (53.800886686857524, 73.59144726730298), (58.24857618265028, -16.272323288427515), (76.36648442258846, -69.20593145181732), (-40.71609893685664, 20.767602729304443), (-23.079611528686257, -71.82818994697726), (89.67098168425673, 93.57756874665958), (32.26888821214581, 5.820716567459044), (-50.91970335773508, -55.85700907191005), (-75.73918406365141, 66.7321678524761), (15.609112242500984, 24.383092629367113), (-45.20257365028053, 5.0909242895730245), (-75.69795868787918, 65.52351708843827), (17.06783296075895, -50.35957022138729), (-64.18812656534196, -94.42708260332466), (-63.00155953294349, -40.42021647328866), (-93.1736321964139, 74.90345844434881), (20.28499958180265, -22.16383399266067), (-82.74600583188673, 25.840387087630774), (63.34783929826867, 31.09340447286425), (-53.886008553111694, 35.87499105181453), (-83.14250307251655, -14.863741496731592), (-14.77921756416309, 43.95042293788819), (57.203269740602934, -78.87102473072403), (-33.449821492909294, -93.52825769556236), (80.50780672980045, -35.58714557222147), (37.53969582639675, 57.96234241935488), (22.445772296106497, -23.842825482123843), (-17.04844991271453, 26.67460773711656), (75.0773661081968, -90.87653281536431), (-43.945959164297776, 55.0133327478481), (92.73053294140658, -61.62707490186048), (39.48263892268204, -25.79388032589209)]
# {0: [43, 18, 7], 1: [], 2: [28, 10], 3: [37], 4: [], 5: [], 6: [16, 22], 7: [36], 8: [], 9: [4, 23], 10: [38, 35], 11: [2], 12: [13, 32], 13: [], 14: [19], 15: [], 16: [], 17: [24, 14], 18: [9], 19: [49, 42], 20: [40], 21: [3, 45], 22: [41, 25], 23: [15], 24: [27], 25: [12], 26: [33], 27: [1], 28: [21], 29: [26], 30: [6], 31: [], 32: [11], 33: [], 34: [], 35: [], 36: [17], 37: [47], 38: [], 39: [5], 40: [46], 41: [31], 42: [8, 48], 43: [], 44: [34, 30], 45: [39], 46: [], 47: [29], 48: [20], 49: [44]}
# Minimum spanning tree:  944.55
# MST tour cost: 1543.06	MST Ratio:    1.63
# DFS: 25 plans
# First cost 5090.74	MST Ratio:    5.39	time 0.01
# Last cost  4724.40	MST Ratio:    5.00	time 23.86
# attempts: 2987
# Random: 7 plans
# First cost 5165.01	MST Ratio:    5.47	time 0.01
# Last cost  3860.95	MST Ratio:    4.09	time 12.51
# attempts: 2545
# Random no-max: 5 plans
# First cost 4630.95	MST Ratio:    4.90	time 0.01
# Last cost  4187.71	MST Ratio:    4.43	time 22.71
# attempts: 3836 Full resets: 1 Prefix steps: 1
# Random incremental: 14 plans
# First cost 4692.73	MST Ratio:    4.97	time 0.01
# Last cost  3404.81	MST Ratio:    3.60	time 25.94

