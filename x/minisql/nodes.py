import abc


class Node(abc.ABC):
    pass



class Stmt(Node, abc.ABC):
    pass


class Select(Stmt):
    pass
