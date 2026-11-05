"""
Ndërtimi i pemës së kërkimit (Search Tree) – modul i përbashkët
================================================================

Përdoret nga eight_puzzle.py, missionaries_cannibals.py dhe rotating_workforce.py.

Çdo problem duhet të ofrojë:
    initial              gjendja fillestare
    goal_test(state)     True nëse gjendja është qëllim
    expand(state)        lista e (veprimi, gjendja_e_re, statusi);
                         statusi = None për fëmijë të vlefshëm,
                         ose një tekst që tregon pse fëmija është i pavlefshëm
    format(state)        teksti me të cilin shfaqet gjendja

Trajtimi i gjendjeve të përsëritura (repeated states):
    "none"   kërkim në pemë pa kontroll: e njëjta gjendje mund të shfaqet shumë herë
    "path"   gjendja nuk zgjerohet nëse shfaqet më parë në rrugën nga rrënja
    "graph"  gjendja nuk zgjerohet nëse është gjeneruar më parë kudo në pemë
"""

from collections import deque


class Node:
    """Nyje e pemës së kërkimit."""

    def __init__(self, state, parent=None, action=None, status=None):
        self.state = state
        self.parent = parent
        self.action = action                  # veprimi që e krijoi këtë nyje
        self.depth = 0 if parent is None else parent.depth + 1
        self.status = status                  # None, "goal", "repeated" ose arsyeja e pavlefshmërisë
        self.children = []

    def path_states(self):
        """Gjendjet nga rrënja deri te kjo nyje."""
        node, states = self, []
        while node is not None:
            states.append(node.state)
            node = node.parent
        return list(reversed(states))

    def path_actions(self):
        node, actions = self, []
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        return list(reversed(actions))


def build_tree(problem, max_depth, repeated="graph"):
    """Ndërton pemën e kërkimit nivel pas niveli (BFS), deri në thellësinë max_depth.
    Nyjet qëllim, të pavlefshme dhe të përsëritura janë gjethe: nuk zgjerohen.
    Kthen (rrënja, lista e të gjitha nyjeve)."""
    root = Node(problem.initial)
    if problem.goal_test(root.state):
        root.status = "goal"
    nodes = [root]
    seen = {root.state}
    queue = deque([root])

    while queue:
        node = queue.popleft()
        if node.status is not None or node.depth >= max_depth:
            continue
        for action, state, invalid in problem.expand(node.state):
            child = Node(state, node, action)
            node.children.append(child)
            nodes.append(child)
            if invalid:
                child.status = invalid
            elif problem.goal_test(state):
                child.status = "goal"
            elif repeated == "path" and state in node.path_states():
                child.status = "repeated"
            elif repeated == "graph" and state in seen:
                child.status = "repeated"
            else:
                queue.append(child)
            seen.add(state)
    return root, nodes


def level_counts(nodes):
    """Numri i nyjeve në çdo nivel të pemës (vetëm nyjet e vlefshme)."""
    counts = {}
    for node in nodes:
        if node.status in (None, "goal", "repeated"):
            counts[node.depth] = counts.get(node.depth, 0) + 1
    return [counts[d] for d in sorted(counts)]


def count_by_status(nodes):
    result = {"valid": 0, "goal": 0, "repeated": 0, "invalid": 0}
    for node in nodes:
        if node.status is None:
            result["valid"] += 1
        elif node.status in ("goal", "repeated"):
            result[node.status] += 1
        else:
            result["invalid"] += 1
    return result


def bfs_solution(problem, max_nodes=2_000_000):
    """Kërkim BFS me kontroll të gjendjeve të përsëritura (graph search).
    Kthen (nyja qëllim ose None, numri i nyjeve të gjeneruara)."""
    root = Node(problem.initial)
    if problem.goal_test(root.state):
        return root, 1
    seen = {root.state}
    queue = deque([root])
    generated = 1
    while queue and generated < max_nodes:
        node = queue.popleft()
        for action, state, invalid in problem.expand(node.state):
            if invalid or state in seen:
                continue
            child = Node(state, node, action)
            generated += 1
            if problem.goal_test(state):
                return child, generated
            seen.add(state)
            queue.append(child)
    return None, generated


def print_tree(root, problem, max_children=None):
    """Vizaton pemën në terminal me ├── dhe └──."""
    def label(node):
        text = problem.format(node.state)
        if node.action is not None:
            text = f"{node.action}: {text}"
        marks = {"goal": "  [QËLLIMI]", "repeated": "  [përsëritje]"}
        if node.status in marks:
            text += marks[node.status]
        elif node.status:
            text += f"  [X {node.status}]"
        return text

    lines = [label(root)]

    def walk(node, prefix):
        children = node.children
        if max_children is not None and len(children) > max_children:
            children = children[:max_children]
        for i, child in enumerate(children):
            last = i == len(children) - 1 and len(children) == len(node.children)
            lines.append(prefix + ("└── " if last else "├── ") + label(child))
            walk(child, prefix + ("    " if last else "│   "))
        if len(children) < len(node.children):
            lines.append(prefix + f"└── ... ({len(node.children) - len(children)} të tjerë)")

    walk(root, "")
    return "\n".join(lines)


def to_mermaid(root, problem):
    """Kthen pemën në formatin Mermaid, që GitHub e vizaton në README."""
    lines = ["graph TD"]
    ids = {}

    def node_id(node):
        if id(node) not in ids:
            ids[id(node)] = f"n{len(ids)}"
        return ids[id(node)]

    def walk(node):
        text = problem.format(node.state).replace('"', "'").replace(" / ", "<br/>")
        if node.status == "goal":
            text += "<br/>QËLLIMI"
        elif node.status == "repeated":
            text += "<br/>përsëritje"
        elif node.status:
            text += f"<br/>X {node.status}"
        lines.append(f'    {node_id(node)}["{text}"]')
        for child in node.children:
            walk(child)
            lines.append(f"    {node_id(node)} -->|\"{child.action}\"| {node_id(child)}")

    walk(root)
    return "\n".join(lines)