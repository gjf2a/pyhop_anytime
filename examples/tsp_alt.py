# Alternative implementation of TSP, experimenting with using the MST to influence the probabilities of
# selecting particular actions.
#
# This is a fairly interesting solution.
# With a high weight (e.g. 40) on the MST tour edges, it gets great results on 25 cities, and pretty good results
# on 50 cities.

from pyhop_anytime import State, TaskList, Planner
from tsp import euclidean_distance, random_coordinate, spanning_tree, move, summarize, mst_tour_cost, dfs_mst


def make_metric_tsp_state(num_cities, width, height):
    state = State(f"tsp_{num_cities}_cities_{width}x{height}")
    state.locations = [(random_coordinate(width), random_coordinate(height)) for i in range(num_cities)]
    state.at = 0
    state.visited = set()

    state.good_edges = set()
    mst_tour = dfs_mst(spanning_tree(state)[0])
    for i, t_i in enumerate(mst_tour):
        next_one = mst_tour[(i + 1) % len(mst_tour)]
        state.good_edges.add((t_i, next_one))
        state.good_edges.add((next_one, t_i))

    return state, [('complete_tour_from', 0)]


def complete_tour_from(state, current):
    if len(state.visited) == len(state.locations):
        return TaskList(completed=True)
    tasks = []
    for city in range(1, len(state.locations)):
        if city not in state.visited:
            task = [('move', current, city), ('complete_tour_from', city)]
            tasks.append(task)
            if (state.at, city) in state.good_edges:
                for i in range(40):
                    tasks.append(task)
    if len(tasks) == 0:
        return TaskList([('move', current, 0)])
    else:
        return TaskList(tasks)


def tsp_planner():
    planner = Planner(cost_func=lambda state, step: euclidean_distance(state.locations[state.at],
                                                                       state.locations[step[2]]))
    planner.declare_operators(move)
    planner.declare_methods(complete_tour_from)
    return planner


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
    summarize("Random no-max", mst_size, visited_cost, p.anyhop_random(s, t, use_max_cost=False, max_seconds=max_seconds))
    summarize("Random action tracked", mst_size, visited_cost, p.anyhop_random_tracked(s, t, max_seconds=max_seconds))


if __name__ == '__main__':
    tsp_experiment(25, 5)
    tsp_experiment(50, 60)

# A representative experiment:
#
# 25 cities, 5s time limit
# [(53.14653407797698, 48.1796044161905), (49.86132724735944, -21.053511444324613), (-1.7466982052801967, -14.646153378304177), (-6.715679702785508, -63.08452451968718), (63.61272040620432, -16.08009576773692), (-97.2939243500907, 16.562185261869416), (30.65189825178166, -33.716361631326166), (22.55370819546154, -93.33185242273794), (57.26814550686663, 46.97393874346753), (-45.172566464242124, -59.45537409318425), (-73.4698876811911, 55.526543142764325), (16.058587868303633, -73.23161909408076), (41.6735962548199, 82.71295738782786), (-90.90279339104134, -51.128048147654816), (-44.37397399119336, 48.256178321517154), (-40.488947561126885, 1.8370410705164488), (77.26803243092169, 46.70550868228008), (-78.50513913163354, -9.122639952812833), (6.064738998611688, 36.39754800967333), (-37.12352909016745, -57.806694546130856), (32.5202655790591, 15.562142525799175), (4.579728318483006, 2.08178976812367), (15.478012715952232, -86.37620012937776), (-10.17266811647653, 68.75293413274989), (-62.5787504598698, 68.43845344419395)]
# {0: [8, 12, 20], 1: [4], 2: [6, 15], 3: [19], 4: [], 5: [], 6: [1, 11], 7: [], 8: [16], 9: [], 10: [], 11: [22, 3], 12: [], 13: [], 14: [24], 15: [17], 16: [], 17: [5, 13], 18: [23], 19: [9], 20: [21, 18], 21: [2], 22: [7], 23: [14], 24: [10]}
# Minimum spanning tree:  663.73
# MST tour cost: 1023.88	MST Ratio:    1.54
# attempts: 731
# Random max: 6 plans
# First cost 1345.80	MST Ratio:    2.03	time 0.01
# Last cost   983.40	MST Ratio:    1.48	time 4.59
# attempts: 606
# Random no-max: 7 plans
# First cost 1319.43	MST Ratio:    1.99	time 0.01
# Last cost   991.74	MST Ratio:    1.49	time 2.54
# attempts: 806 Full resets: 1 Prefix steps: 6
# Random incremental: 9 plans
# First cost 1663.68	MST Ratio:    2.51	time 0.01
# Last cost  1137.42	MST Ratio:    1.71	time 1.83
# 50 cities, 30s time limit
# [(20.645376939828537, -29.002663676772997), (-69.22815815301726, 42.31024704549921), (-68.90942423603781, -46.78931176456273), (43.69767328265496, 98.06618116293956), (6.443556473984174, -48.04080900261616), (-30.064222037305214, -80.25320795405028), (22.78757548207342, -20.47493381854224), (83.03137026641895, -57.47914517136987), (-51.34772864006039, -74.75992225314604), (15.337280418836755, -1.6582055072087627), (-97.1973891825385, 51.52198188868985), (79.89973656844458, 87.52523728997238), (-11.877550588102181, -63.588619049802666), (-16.431032562098366, -69.91362496504021), (50.866918350607136, -0.6106520483428994), (-4.206972734358615, -15.49023280894582), (-79.22394986893333, -47.37735915837475), (35.245544400616154, -85.51740856733818), (-55.45651266452776, 30.73865562482166), (19.667613959476654, 38.702397676230106), (-68.14028135140387, -11.926154248830073), (-75.23334620438973, 58.34952276003983), (-4.839336150724321, 54.63099746528155), (75.58079118056384, 30.71146389359822), (-59.49531562853316, 50.515723256853306), (-88.51368676483193, -99.09354224334308), (80.07938364900124, 19.8185217482294), (-77.60758544366897, 2.2235328329932855), (97.82363655400817, 4.62326436476836), (5.880530307350227, -74.94366101929242), (33.750082587414795, -95.74115822064068), (92.8033023320248, 7.564208448358741), (-24.76428464226703, -74.78903453491412), (-95.6998455891467, 83.82288817085504), (-57.456195744610824, -31.811894752266554), (42.95468062756339, 15.237445333235016), (27.33909185359356, -0.5331835713090527), (33.278497472121046, 32.20680482458252), (88.4619535802129, 94.02062365758673), (-29.29050006763427, 17.464756098231533), (-38.66453808338712, 46.213971349656305), (1.0791312578535326, 69.01075396850734), (-35.900218305045996, -0.709205544865469), (60.56885053161676, -62.21018910331757), (95.87251984228377, -50.38353251725027), (-84.09532172906755, 24.08404664843499), (-32.578649217222065, 43.46734285230852), (-47.04779086747155, -61.039378344414416), (-91.96271057866525, -16.20267839189478), (94.17197100871121, -40.21789469948551)]
# {0: [6, 4], 1: [24, 21, 18], 2: [16, 34], 3: [11], 4: [12], 5: [8], 6: [9], 7: [44], 8: [47, 25], 9: [36, 15], 10: [33], 11: [38], 12: [13, 29], 13: [32], 14: [26], 15: [], 16: [], 17: [30, 43], 18: [], 19: [22], 20: [27], 21: [10], 22: [41], 23: [], 24: [40], 25: [], 26: [23, 31], 27: [45, 48], 28: [], 29: [17], 30: [], 31: [28], 32: [5], 33: [], 34: [20], 35: [14, 37], 36: [35], 37: [19], 38: [], 39: [42], 40: [46], 41: [3], 42: [], 43: [7], 44: [49], 45: [1], 46: [39], 47: [2], 48: [], 49: []}
# Minimum spanning tree:  995.11
# MST tour cost: 1531.23	MST Ratio:    1.54
# attempts: 1340
# Random max: 9 plans
# First cost 2942.11	MST Ratio:    2.96	time 0.03
# Last cost  2347.32	MST Ratio:    2.36	time 20.69
# attempts: 1039
# Random no-max: 9 plans
# First cost 4390.36	MST Ratio:    4.41	time 0.03
# Last cost  2256.00	MST Ratio:    2.27	time 25.66
# attempts: 1310 Full resets: 0 Prefix steps: 42
# Random incremental: 3 plans
# First cost 2983.89	MST Ratio:    3.00	time 0.03
# Last cost  2571.16	MST Ratio:    2.58	time 0.93