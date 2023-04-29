from sympy.logic.boolalg import to_cnf, And, Or
from sympy import SympifyError

class KnowledgeBase:

    def __init__(self):
        self.beliefs = []

    # adds belief if it does not already exist
    def add(self, query):
        exists = False
        for belief in self.beliefs:
            if belief == query:
                exists = True
        if not exists:
            self.beliefs.append(query)
    
    # removes identical beliefs
    def remove(self, query):
        for belief in self.beliefs:
            if belief == query:
                self.beliefs.remove(belief)
    
    def contract(self, query):
        query = to_cnf(query)
        # check if identical belief is in the belief base and remove it
        for belief in self.beliefs:
            if belief == query:
                self.remove(belief)

        tmp = self.beliefs.copy()
        # check if the remaining belief base entails the query
        if check_entailment(self.beliefs, query):
            for belief in self.beliefs:
                    #remove beliefs untill query is no longer entailed
                    if check_entailment(tmp, query):
                        tmp.remove(belief)
            """
            now we have a base subset of beliefs that dont entail the query
            but some of the removed beliefs may not have entailed the query 
            so we add them back 1 by 1 assuming they dont already
            exist in the subset and check if the new belief added
            makes the subset entail the query, if it does remove it again
            the result is a minimal subset that does not entail the query and is consistent
            """
            for belief in self.beliefs:
                for i in tmp:
                    if belief == i:
                        tmp.remove(i)
                tmp.append(belief)
                if check_entailment(tmp, query):
                    tmp.remove(belief)
        self.beliefs = tmp

    #revises a query from the database
    def revision(self, query):
        query = to_cnf(query)
        if check_entailment(self.beliefs, query):
            print("the query is already entailed by the knowledge base")
        else:
            #first remove the contradiction to the new belief
            self.contract(~query)
            #expand with new belief now that contradiction is gone and consistency is ensured
            self.add(query)
        

#check entailment of a belief in the knowledge base

def check_entailment(base, query):
    query = to_cnf(query)

    # Split base into conjunctions
    clauses = [c for f in base for c in conjunctions(f)]
    # Add contradiction for resolutipn check
    clauses += conjunctions(to_cnf(~query))

    # Special case if one clause is already False
    if False in clauses:
        return True

    result = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]

        resolvents = [r for p in pairs for r in resolution_rule(p[0], p[1])]
        if False in resolvents:
            return True
        result |= set(resolvents)

        if result.issubset(set(clauses)):
            return False
        clauses += [c for c in result if c not in clauses]


#generates clauses by applying resolution rule on pairs of conjuncts
def resolution_rule(ci, cj):

    clauses = []
    for di in disjunctions(ci):
        for dj in disjunctions(cj):
            # If di, dj are complementary
            if di == ~dj or ~di == dj:
                res = []
                for dk in disjunctions(ci | cj):
                    if dk != di and dk != dj:
                        res.append(dk)
                clauses.append(merge(Or, res))

    return clauses

def merge(logic_operator, args):
    if len(args) == 0:
        return logic_operator.identity
    elif len(args) == 1:
        return args[0]
    else:
        result = args[0]
        for i in range(1, len(args)):
            result = logic_operator(result, args[i])
        return result
    
#extract logic operator from arguments
def extract_atomic_propositions(logic_operator, args):
    stack = [args]
    result = []
    while stack:
        subset = stack.pop()
        for arg in subset:
            if isinstance(arg, logic_operator):
                stack.append(arg.args)
            else:
                result.append(arg)

    return result

#Extract all disjuncts from the given clause.
def disjunctions(clause):
    return extract_atomic_propositions(Or, [clause])

#Extract all conjuncts from the given clause.
def conjunctions(clause):
    return extract_atomic_propositions(And, [clause])

def handleinput():
    print('Select Action:')
    action = input().lower()
    if action == 'r':
        print('--- Revision ---')
        print('Enter belief to revise:')
        print('EG. A >> B for A -> B')
        query = input().upper()
        try:
            print()
            kb.revision(query)
            print('knowledge base:')
            print(kb.beliefs)
            print()
        except SympifyError:
            print('Invalid formula')
    if action == 'c':
        print('---Contraction ---')
        print('Enter belief to contract:')
        print('EG. A >> B for A -> B')
        query = input().upper()
        try:
            kb.contract(query)
            print()
            print('knowledge base')
            print(kb.beliefs)
            print()
        except SympifyError:
            print('Invalid formula')
    if action == 'p':
        print()
        print("knowledge base:")
        print(kb.beliefs)
        print()
    if action == 'e':
        print("---Entailment Check---")
        print('Enter belief to check for entailment')
        print('EG. A >> B for A -> B')
        query = input().upper()
        print()
        try:
            if check_entailment(kb.beliefs, query):
                print("Knowledge base entails query")
            else:
                print("Knowledge base does not entail query")
            print()
        except SympifyError:
            print('Invalid mula')
    if action == 'q':
        exit()

    handleinput()
    
if __name__ == '__main__':
    kb = KnowledgeBase()
    kb.add(to_cnf("B >> D"))
    kb.add(to_cnf("D >> F"))
    kb.add(to_cnf("A"))
    kb.add(to_cnf("B"))
    kb_print = str(kb.beliefs)
    print("     initial knowledge base:")
    print("     "+ str(kb.beliefs))
    print(
     """
     press r to revise knowledge base
     press c to contract from knowledge base
     press p to print knowledge base
     press e to check entailment of knowledge base
     press q to quit

     program uses the logic operators such as >>, |, &, ~, <<
     We have done so the input for the beliefs are automatically taken in as uppercase in case of mistype errors.
     """)
    
    handleinput()