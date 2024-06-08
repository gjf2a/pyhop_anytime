import os
from hddl_parser import parse_hddl

prefix = 'c:/users/ferrer/pycharmprojects/ipc2020-domains/total-order'
for domain in os.listdir(prefix):
    print(f"Testing {domain}...")
    for problem in os.listdir(f"{prefix}/{domain}"):
        if problem.endswith("hddl"):
            try:
                test_str = open(f"{prefix}/{domain}/{problem}").read()
                test_domain = parse_hddl(test_str)
                print("parsed without errors")
            except Exception as e:
                print(f"{domain} {problem} Exception: {e}")
