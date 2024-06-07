from typing import List


def append_text(text: str, seq: List[str]):
    if len(text) > 0:
        seq.append(text)


def tokenize(s: str) -> List[str]:
    result = []
    current = ''
    for c in s:
        if c == '(':
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
                self.actions.append(item[1:])

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
    def __init__(self, name: str, param_names: List[str]):
        self.name = name
        self.param_names = param_names

    def __repr__(self):
        return f"UntypedSymbol('{self.name}', {self.param_names})"


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
            if method_list[i + 1][0] == 'and':
                preconds = []
                for precond_list in method_list[i + 1][1:]:
                    name = precond_list[0]
                    params = precond_list[1:]
                    preconds.append(UntypedSymbol(name, params))
                preconditions = Conjunction(preconds)
            elif method_list[i + 1][0] == 'forall':
                param = make_params(method_list[i + 1][1])[0]
                pred = UntypedSymbol(method_list[i + 1][2][0], method_list[i + 1][2][1:])
                preconditions = Universal(param, pred)
            else:
                assert False
        elif method_list[i] == ':ordered-tasks':
            assert method_list[i + 1][0] == 'and'
            ordered_tasks = []
            for task_list in method_list[8][1:]:
                name = task_list[0]
                params = task_list[1:]
                ordered_tasks.append(UntypedSymbol(name, params))
        elif method_list[i] == ":ordered-subtasks":
            ordered_tasks = [UntypedSymbol(method_list[i + 1][0], method_list[i + 1][1:])]
        else:
            print(f"Unknown tag: {method_list[i]}")
            assert False
    return Method(name, params, task_name, preconditions, ordered_tasks)


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
    test_str = open("c:/users/ferrer/pycharmprojects/ipc2020-domains/total-order/Blocksworld-HPDDL/domain.hddl").read()
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