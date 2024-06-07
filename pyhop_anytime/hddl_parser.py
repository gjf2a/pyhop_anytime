import os
from typing import List, Union


def append_text(text: str, seq: List[str]):
    if len(text) > 0:
        seq.append(text)


def tokenize(s: str) -> List[str]:
    result = []
    current = ''
    in_comment = False
    for c in s:
        if in_comment:
            if c == '\n':
                in_comment = False
        elif c == ';':
            in_comment = True
            append_text(current, result)
            current = ''
        elif c == '(':
            append_text(current, result)
            current = ''
            result.append('[')
        elif c == ')':
            append_text(current, result)
            current = ''
            result.append(']')
        elif c.isspace():
            append_text(current, result)
            current = ''
        else:
            current += c
    append_text(current, result)
    return result


def coalesce(tokens: List[str]) -> str:
    result = ''
    for token in tokens:
        if len(result) > 0 and result[-1] != '[' and token != ']':
            result += ', '
        if token in '[]':
            result += token
        else:
            result += f'"{token}"'
    return result


class Domain:
    def __init__(self, name: str, domain_list: List):
        self.name = name
        self.tasks = {}
        self.methods = []
        self.actions = []
        for item in domain_list:
            tag = item[0]
            if tag == ':types':
                self.types = set(item[1:])
            elif tag == ':predicates':
                predicates = [make_pred(p) for p in item[1:]]
                self.predicates = {p.name: p for p in predicates}
            elif tag == ':task':
                task = make_task(item[1:])
                self.tasks[task.name] = task
            elif tag == ':method':
                self.methods.append(make_method(item[1:]))
            elif tag == ':action':
                self.actions.append(make_action(item[1:]))

    def types_for(self, name: str) -> List[str]:
        if name in self.predicates:
            return self.predicates[name].type_list()
        elif name in self.tasks:
            return self.tasks[name].type_list()
        else:
            print(f"{name} not found")
            assert False


class Parameter:
    def __init__(self, name, ptype):
        self.name = name
        self.ptype = ptype

    def __repr__(self):
        return f"Parameter('{self.name}', '{self.ptype}')"


class Predicate:
    def __init__(self, name: str, param_list: List[Parameter]):
        self.name = name
        self.param_list = param_list

    def __repr__(self):
        return f"Predicate('{self.name}', {self.param_list})"

    def type_list(self) -> List[str]:
        return [p.ptype for p in self.param_list]


def make_pred(pred_list: List) -> Predicate:
    return Predicate(pred_list[0], make_params(pred_list[1:]))


def make_params(param_list: List[str]) -> List[Parameter]:
    result = []
    pending_names = []
    pending_type = False
    for p in param_list:
        if p[0] == '?':
            pending_names.append(p)
        elif p == '-':
            pending_type = True
        elif pending_type:
            for name in pending_names:
                result.append(Parameter(name, p))
            pending_names = []
            pending_type = False
        else:
            assert False
    return result


class Task:
    def __init__(self, name: str, param_list: List[Parameter]):
        self.name = name
        self.param_list = param_list

    def __repr__(self):
        return f"Task('{self.name}', {self.param_list})"

    def type_list(self) -> List[str]:
        return [p.ptype for p in self.param_list]


def make_task(task_list) -> Task:
    name = task_list[0]
    assert task_list[1] == ':parameters'
    params = make_params(task_list[2])
    return Task(name, params)


class UntypedSymbol:
    def __init__(self, name: str, positive: bool, param_names: List[str]):
        self.name = name
        self.positive = positive
        self.param_names = param_names

    def __repr__(self):
        return f"UntypedSymbol('{self.name}', {self.positive}, {self.param_names})"


def make_untyped_symbol(symlist: List) -> UntypedSymbol:
    name = symlist[0]
    args = symlist[1:]
    positive = True
    if name == 'not':
        symlist = symlist[1]
        name = symlist[0]
        args = symlist[1:]
        positive = False
    return UntypedSymbol(name, positive, args)


class Conjunction:
    def __init__(self, predicates: List[UntypedSymbol]):
        self.predicates = predicates

    def __repr__(self):
        return f"Conjunction({self.predicates})"


class Universal:
    def __init__(self, param: Parameter, pred: UntypedSymbol):
        self.param = param
        self.pred = pred

    def __repr__(self):
        return f"Universal({self.param}, {self.pred})"


def make_precond(prelist: List) -> Union[None, Conjunction, Universal, UntypedSymbol]:
    if len(prelist) == 0:
        return None
    elif prelist[0] == 'forall':
        param = make_params(prelist[1])[0]
        pred = make_untyped_symbol(prelist[2])
        return Universal(param, pred)
    else:
        return make_conjunction(prelist)


def make_conjunction(conjunct_list: List) -> Union[None, Conjunction, UntypedSymbol]:
    if len(conjunct_list) == 0:
        return None
    elif conjunct_list[0] == 'and':
        conjuncts = []
        for conjunct in conjunct_list[1:]:
            conjuncts.append(make_untyped_symbol(conjunct))
        return Conjunction(conjuncts)
    else:
        return make_untyped_symbol(conjunct_list)


class Method:
    def __init__(self, name: str, params: List[Parameter], task_name: str, preconditions: Conjunction, ordered_tasks: List[UntypedSymbol]):
        self.name = name
        self.params = params
        self.task_name = task_name
        self.preconditions = preconditions
        self.ordered_tasks = ordered_tasks

    def __repr__(self):
        return f"Method('{self.name}', {self.params}, '{self.task_name}', {self.preconditions}, {self.ordered_tasks})"


def make_method(method_list: List) -> Method:
    name = method_list[0]
    params = task_name = preconditions = ordered_tasks = None
    for i in range(1, len(method_list), 2):
        if method_list[i] == ':parameters':
            params = make_params(method_list[i + 1])
        elif method_list[i] == ':task':
            task_name = method_list[i + 1][0]
        elif method_list[i] == ':precondition':
            preconditions = make_precond(method_list[i + 1])
        elif method_list[i] == ':ordered-tasks':
            assert method_list[i + 1][0] == 'and'
            ordered_tasks = []
            for task_list in method_list[i + 1][1:]:
                ordered_tasks.append(make_untyped_symbol(task_list))
        elif method_list[i] == ":ordered-subtasks":
            ordered_tasks = [make_untyped_symbol(method_list[i + 1])]
        else:
            print(f"Unknown tag: {method_list[i]}")
            assert False
    return Method(name, params, task_name, preconditions, ordered_tasks)


class Action:
    def __init__(self, name, parameters, precondition, effects):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effects = effects

    def __repr__(self):
        return f"Action('{self.name}', {self.parameters}, {self.precondition}, {self.effects})"


def make_action(action_list: List) -> Action:
    name = action_list[0]
    parameters = precondition = effects = None
    for i in range(1, len(action_list), 2):
        if action_list[i] == ':parameters':
            parameters = make_params(action_list[i + 1])
        elif action_list[i] == ':precondition':
            precondition = make_precond(action_list[i + 1])
        elif action_list[i] == ':effect':
            effects = make_conjunction(action_list[i + 1])
        else:
            assert False
    return Action(name, parameters, precondition, effects)


def parse_problem(name: str, prob_list: List):
    assert False


def parse_hddl(domain_str: str):
    py_list_form = eval(coalesce(tokenize(domain_str)))
    assert py_list_form[0] == 'define'
    category = py_list_form[1][0]
    name = py_list_form[1][1]
    if category == 'domain':
        return Domain(name, py_list_form[2:])
    elif category == 'problem':
        return parse_problem(name, py_list_form[2:])
    else:
        assert False


if __name__ == '__main__':
    prefix = 'c:/users/ferrer/pycharmprojects/ipc2020-domains/total-order'
    for domain in os.listdir(prefix):
        print(f"Testing {domain}...")
        try:
            test_str = open(f"{prefix}/{domain}/domain.hddl").read()
            test_domain = parse_hddl(test_str)
            print("parsed without errors")
        except Exception as e:
            print(f"Exception: {e}")

    test_str = open("c:/users/ferrer/pycharmprojects/ipc2020-domains/total-order/Robot/domain.hddl").read()
    tokens = tokenize(test_str)
    py_list_form = eval(coalesce(tokens))
    print(py_list_form)

    test_domain = parse_hddl(test_str)
    print(test_domain.name)
    print(test_domain.types)
    print(test_domain.predicates)
    print(test_domain.tasks)
    print(test_domain.methods)
    print(test_domain.actions)