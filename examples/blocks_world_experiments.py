from examples.blocks_world import parse_pddl_blocks, make_blocks_planner


def summarize(header, plans):
    print(f"{header}: {len(plans)} plans")
    print(f"First cost {plans[0][1]}\ttime {plans[0][2]}")
    print(f"Last cost  {plans[-1][1]}\ttime {plans[-1][2]}")


def experiment(filename, max_seconds):
    p = make_blocks_planner()
    state, goals = parse_pddl_blocks(filename)
    print(filename)
    summarize("DFS", p.anyhop(state, [('move_blocks', goals)], max_seconds=max_seconds))
    summarize("Random", p.anyhop_random(state, [('move_blocks', goals)], max_seconds=max_seconds))
    summarize("Random no-max", p.anyhop_random(state, [('move_blocks', goals)], use_max_cost=False,
                                               max_seconds=max_seconds))
    summarize("Random incremental", p.anyhop_random_incremental(state, [('move_blocks', goals)],
                                                                max_seconds=max_seconds))


if __name__ == "__main__":
    experiment("/Users/ferrer/Downloads/AIPS-2000DataFiles/2000-Tests/Blocks/Track1/Untyped/probBLOCKS-17-0.pddl", 1)
    experiment("/Users/ferrer/Downloads/AIPS-2000DataFiles/2000-Tests/Blocks/Track2/probBLOCKS-60-1.pddl", 10)
    #experiment("/Users/ferrer/Downloads/AIPS-2000DataFiles/2000-Tests/Blocks/Track2/Additional/probblocks-100-1.pddl", 10)