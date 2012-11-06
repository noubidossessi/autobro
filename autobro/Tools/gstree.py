#!/usr/bin/env python
# coding: utf8
#
# gstree.py
# by Rodrigue ALAHASSA
# 20 / 10 /2011 10 AM Suffix Extension Algorithm + Skip/Count 
# 22 / 10 /2011 09 AM Single Phase Algorithm 
# 22 / 10 /2011 01 PM All longest common substrings extraction
# 22 / 10 /2011 01 PM Longest common substring extraction
debug = 0

def format_Title(test,formatter,level):
    test_len = len(test)
    format_size = round((60 - test_len)/2)
    format_text = str(formatter) * int(format_size)
    return "%s%s %s %s" % ('\t'*level, format_text, test, format_text)

class Node(object):
    def __init__(self,parent = None, edge = None,leaf=0):
        self.parent = parent
        self.string = edge[0] if edge else None
        self.index = self.start = edge[1] if edge else 0
        self.end = edge[2] if edge else [0]
        self.leaf = leaf
        self.suffix = None
        self.visitors = {}
        self.children = {}
        self.e = [0]


    def __str__(self):
        return  "\n\
                    \tParent: %s\n\
                    \tString: %s\n\
                    \tIndex: %s\n\
                    \tStart: %s\n\
                    \tEnd: %s\n\
                    \tLeaf: %s\n\
                    \tSuffix: %s\n\
                    \tVisitors %s\n\
                    \tChildren: %s\n\
                " % (self.parent,\
                    self.string,\
                    self.index,\
                    self.start,\
                    self.end,\
                    self.leaf,\
                    self.suffix,\
                    self.visitors,\
                    self.children)

    __repr__ = __str__

class gstree(dict):
    def __init__(self, string=None):
        self.leaves = set()         # set of leaf node number
        self.nodes = 0              # number of current nodes
        self.e = [0]                # e for single phase algorithm
        self.strings = {}           # dictionary of strings
        self.strings_len = 0        # Number of strings
        self.string_len = 0         # Len of input string
        self.string_id = 0
        self.suffix = None          # suffix links
        self.v_id = 0               # id of v (suffix links)
        self.v_gamma = 0            # Gamma of v (suffix links)
        self.beta = None            # beta for Suffix Extension Algo
        self.beta_len = 0           # beta_len
        self.i = 0                  # i
        self.j = 0                  # j
        self.node = 0               # Current node to update
        self.stop = None            # Rule 3 is a rule stopper
        self.__cv = {}          # C(v)  to solve k-common substring problem {k:set(nodes)}
        self.__vk = {}          # V(k) as explained at page 128 of Dan Gusfield' book
        self.__lk = {}          # l(k) as explained at page 128 of Dan Gusfield's book
        self.__cn = set()       # Set of common nodes to all nodes
        self.__cs = {}          # Common substrings to all nodes
        self.__rs = {}           # Repeated substrings
        self._cs = {}           # Common substrings with reference to string 0
        self.__alcs = {}        # All longest common substrings
        self.__lcs ={}          # Longest common substring

        self[0] = Node()
        self.nodes += 1
        if string: self.add_String(string)

    def add_String(self,string):
        string_id = self.string_id = self.strings_len
        self.strings[string_id] = string
        string_len = len(string)
        self.strings_len  += 1
        strings = self.strings

        self.i = self.j = self.node = self.suffix = 0
        self.v_id = self.beta_len = 0
        self.v_gamma = [0,0,0]
        self.stop = self.beta = None
        
        self.e = [0]
        i_start = 0
        j_star = 0
        j_i = 0
        full_string_id = 0

        if debug:
            print format_Title("Adding a new string",'-',0)
            print "Input string: %s" % string
            print "string_len: %s" % string_len

        first_char = string[0]

        try: 
            # Find if the first character matches. If this is the case,
            # walk down from the top to next node and verify if its edge
            # match. Once we have a mismatch between the input string and
            # an edge, we compare each character of this edge to the
            # remaining part of the input string to identify the index i of
            # the last matching character. The Ukkonen's algorithm will be
            # resumed at i + 1
            node_id = self[0].children[first_char]
        except KeyError,e:
            # There is no substring starting with the first character of this
            # node :-( 
            edge = [string_id, 0, self.e]
            new_char = string[0]
            full_string_id = self.create_Leaf(0,\
                            edge,\
                            string_id,\
                            new_char,\
                            j=1)
            self.e[0] += 1
            self.node = 0
            i_start = 1
            j_star = 0
            pass
        else:
            # There already is a substring starting from this character
            node = self[node_id]
            beta = self.strings[node.string][node.start:node.end[0]]
            depth = node.end[0] - node.start
            break_condition = 0
            h = last_h = 0
            # last_h is used to know where v_gamma starts
            if debug:
                print format_Title("Adding a new string that has at least one match",'#',0)
                print "node_id: %s" % node_id
                print "beta: %s" % beta
                print "depth: %s" % depth
                print "h: %s" % h
            while beta == string[h:h+depth]:
                last_h = h
                h = h+depth
                node.visitors[string_id] = set((0,))
                # Last node to be updated is this node
                self.v_id = node_id
                try:
                    first_char = string[h]
                except IndexError,e:
                    # The string is exhausted
                    beta = string[h:]
                    beta = None if beta == '' else beta
                    break
                # If the test succeeded, then we need to update the
                # current node visitors
                if debug:
                    print format_Title(" Skip/Count ","?",0)
                    print "h: %s"  % h
                    print "first_char: %s" % first_char
                    print "node.children: %s" % node.children
                try:
                    node_id = self[node_id].children[first_char]
                except KeyError,e:
                    # The next character is not children of this node. We
                    # reach the end of a node. The input string will not match
                    # anymore :-(
                    # We set beta to empty to avoid doing any further check
                    # 
                    beta = None
                    break
                else:
                    node = self[node_id]
                    beta = self.strings[node.string][node.start:node.end[0]]
                    beta = None if beta == '' else beta
                    depth = node.end[0] - node.start
                if debug:
                    print "node_id: %s" % node_id
                    print "beta: %s" % beta
                    print "depth: %s" % depth
            # Match each character of the edge against the input string
            h_prime = h

            try:
                for index, char in enumerate(beta):
                    try:
                        next_char = string[h+index]
                    except IndexError,e:
                        # The string is exhausted
                        break
                    else:
                        if char == next_char:
                            h_prime += 1
                        else:
                            break
            except TypeError,e:
                # beta is empty, beta == None
                assert beta == None

            if debug:
                print format_Title(" After skip/count if any ","*",0)
                print "h: %s" % h
                print "beta: %s" % beta
                print "h_prime: %s" % h_prime
                print "self.e: %s" % self.e
                print "i_start: %s" % i_start
                print "j_star: %s" % j_star
                print "j_i: %s" % j_i

            # We need to know the last node updated. Since we walk down
            # along a path, we know the last substring S[j_star i] that
            # has been updated and then we know where it ends in the tree.
            # It can end either at a node or beyond a node. In the former
            # case, h == h_prime and v_id is node.parent. In the last case, 
            # h_prime > h and v_id is node_id

            if h == h_prime:
                assert h > last_h
                self.v_id = node.parent
                i_start =  h_prime
                #j_star = max(last_h - 1,0)
                self.e[0] = h_prime 
            elif h_prime > h:
                if self.v_id == 0:
                    self.node = self.v_id = node.parent
                    #j_star = 0
                else:
                    # The input string matched the tree beyond at least one
                    # node. So self.v_id should not be 0
                    #j_star = max(h-1,0) 
                    assert self.v_id != 0
                # At this stage, we now all the i first characters that have
                # matched. This sounds like the first time we have applied
                # we have applied all explicit extensions. So the next phase
                # will start with that. 
                # We should remember that h,h_prime indicate the index in
                # string and since indexing starts at 0 in Python. We know
                # also that h_prime is the index of the first mismatch, so the
                # latest match occurs at h_prime - 1. j and i
                # must be h_prime - 1 value incremented

                i_start = h_prime
                self.e[0] = h_prime 
            else:
                # If we reach this statement, that means that there were
                # an issue in the previous hypotheses.
                assert h <= h_prime
            self.v_gamma = [string_id,\
                            last_h if h == h_prime else h,\
                            h_prime]
            if debug:
                print format_Title("String matching End",'-',0)
                print "i_start: %s" % i_start
                print "j_star: %s" % j_star
                print "j_i: %s" % j_i
                print "v_id: %s" % self.v_id
                print "v_gamma: %s" % self.v_gamma
                print "self.e: %s" % self.e
                print "i_start: %s" % i_start

            pass
        finally:
            j_star = 0
            j_i = j_star

        m = string_len + 1

        for i in xrange(i_start, m):
            # Start Phase i+1 
            # Which will extend the tree to S[1 .. i+1]
            # 1. Do extensions from j = j* to i+1
            # 2. Set j* to the first j for which Rule 3 has been applied or to
            # i+1
            # 3. Set j_i to j* - 1. This will ensure that each phase will
            # start by the last extension done in the previous phase

            i_plus_one = i + 2
            j_i += 1
            self.suffix = None

            # Rule stopper apply if there  is a rule 3 extension in this
            # extension. So this value should be reseted before each
            # new extension begins to avoid that in the current phase, we
            # are betrayed by the value set in the previous phase to
            # self.stop
            self.stop = None
            
            # if i == i_start, this is the first extension of this phase. So
            # if h == h_prime, we match until a node (even the root node). The
            # next node which will be created will be a leaf node and the node
            # holding the full string. If h < h_prime, then we fall in the
            # middle of a node. In that case, the algorithm will first create
            # one internal node where there is a mismatch and only after that
            # it will create a leaf node; which will hold the full string.

            if not full_string_id:
                full_string_id = self.nodes if h == h_prime else self.nodes + 1
            if debug:
                print format_Title("Phase %s" % (i + 1),'*',1)
                print "\tself.v_id: %s" % self.v_id
                print "\tv.suffix: %s" % self[self.v_id].suffix
                print "\ti_plus_one: %s" % (i_plus_one - 1)
                print "\tj_i: %s" % j_i
                print "\tstop: %s" % self.stop
                print "\tself.suffix: %s" % self.suffix
                print "\tself.e: %s" % self.e
                print "\tfull_string_id: %s" % (full_string_id)

            if j_i >= 2:
                v_id = self.v_id
                v = self[v_id]
                if v.suffix is not None:
                    gamma = list(self.v_gamma)
                    beta = strings[gamma[0]][gamma[1]:gamma[2]]
                    beta = None if beta == '' else beta
                    self.beta = beta
                    self.beta_len = gamma[2]-gamma[1] if beta != None else 0
                    # This is the last extension of the previous phase
                    # and the first of this phase. Two consecutive
                    # phases share at least one phase. We need to
                    # perform this extension before following any
                    # suffix link
                    self.node = v_id
                    self.i = i
                    self.j = j
                    if debug:
                        print format_Title("Before following Suffix link",'*',1)
                        print "\t\tself.node: %s" % v_id
                        print "\t\tself.i: %s" % self.i
                        print "\t\tself.j: %s" % self.j
                        print "\t\tself.beta: %s" % self.beta
                        print "\t\tself.beta_len: %s" % self.beta_len
                    self.single_Extension_Algorithm()
                    self.v_id = v_id
                    self.v_gamma = gamma
                    if self.stop:
                        self.v_gamma[2] = i + 1
                        j_i = self.stop - 1 if i != (string_len -1) else 0
                        self.e[0] = i + 1 if i!= string_len else i
                        if debug:
                            print format_Title("Rule stopper applied",'*',1)
                            print "\tself.v_gamma: %s" % self.v_gamma
                        continue

            for j in xrange(j_i, i_plus_one):
                # 1. Find the last updated node and extend it
                # 2. Follow its suffix link if any
                # 3. Update this node and hand over the next extension
                if j >= 2:
                    v_id = self.v_id
                    v = self[v_id]
                    if v.suffix is not None:
                        gamma = self.v_gamma
                        beta = strings[gamma[0]][gamma[1]:gamma[2]]
                        self.beta = None if beta == '' else beta
                        self.beta_len = gamma[2]-gamma[1] if beta != None else 0
                        self.node = v.suffix
                        if debug:
                            print format_Title("Following Suffix links",'+',2)
                            print "\t\tv_id: %s" % v_id
                            print "\t\tv.suffix: %s" % v.suffix
                            print "\t\tGamma: %s" % gamma
                            print "\t\tBeta: %s" % self.beta
                            print "\t\tBeta_len: %s" % self.beta_len
                    else:
                        beta = string[j-1:i]
                        beta = None if beta == '' else beta
                        self.beta = beta
                        self.beta_len = i-j+1 if beta is not None else 0
                elif i!= i_start and full_string_id:
                    full_string_parent_node_id = self[full_string_id].parent 
                    full_string_node = self[full_string_id]
                    beta = string[full_string_node.start:full_string_node.end[0]]
                    beta = None if beta == '' else beta
                    beta_len = full_string_node.end[0] - full_string_node.start
                    beta_len = beta_len if beta is not None else 0
                    self.beta = beta
                    self.beta_len = beta_len
                    self.node = full_string_parent_node_id
                    if debug:
                        print format_Title("First Extension speedup",'*',1)
                        print "\tfull_string_parent_node_id: %s" % \
                                full_string_parent_node_id
                        print "\tbeta: %s" % beta
                        print "\tbeta_len: %s" % beta_len
                        print "\tself.node: %s" % self.node
                else:
                    beta = string[j-1:i]
                    self.beta = None if beta == '' else beta
                    self.beta_len = i-j+1 if beta is not None else 0
                self.i = i
                self.j = j
                self.single_Extension_Algorithm()
                self.node = 0
                if self.stop:
                    # When Rule 3 applies, we need to update self.v_gamma
                    # since self.e[0] increased
                    self.v_gamma[2] = i + 1                    
                    if debug:
                        print format_Title("Rule stopper applied",'*',1)
                        print "\tself.v_gamma: %s" % self.v_gamma
                    j_i = self.stop - 1 if i != (string_len -1) else 0
                    self.e[0] = i + 1 if i!= string_len else i

                    break

            else:
                #j_i = 0
                if debug:
                    print format_Title("Phase ends moothly",'*',1)
                j_i = i_plus_one - 2 if i != (string_len - 1) else 0
                self.e[0] = i + 1 if i !=string_len else i
                self.node  = 0

 
    def single_Extension_Algorithm(self):
        if debug:
            print format_Title("Extension %s" % self.j, '.', 2)

        strings = self.strings
        string_id = self.string_id
        string = strings[string_id]
        i = self.i
        j = self.j

        try:
            new_char = string[i]
        except IndexError,e:
            # This will be the case for the last phase we add to simulate
            # terminal character
            new_char = None

        beta = self.beta
        root_id = self.node
        root = self[root_id]
        beta_len = self.beta_len
        first_char = None if beta is None else beta[0]

        if debug:
            print "\t\ti: %s" % i
            print "\t\tj: %s" % j
            print "\t\tstring_id: %s" % string_id
            print "\t\tBeta: %s" %( beta ) 
            print "\t\tbeta_len: %s" % beta_len
            print "\t\tfirst_char: %s" % first_char
            print "\t\tnew_char: %s" % new_char
            print "\t\troot_id: %s" % root_id
            print "\t\troot.parent: %s" % root.parent
            print "\t\troot.visitors: %s" % root.visitors
            print "\t\troot.children: %s" % root.children
            print "\t\tself.stop: %s" % self.stop
            print "\t\troot: %s" % root


        if first_char is not None:
            node_id = root.children[first_char]
            node = self[node_id]
            g = node.end[0] - node.start
        elif first_char is None:
            node_id = root_id
            node = root
            g = 0
        else:
            # There is a missing condition here :-( 
            print format_Title("Missing condition :-(", "+",0)
            import sys
            sys.exit(0)

        if debug:
            print format_Title("Before Skip/Count",'_',3)
            print "\t\t\tfirst_char: %s" % first_char
            print "\t\t\tnew_char: %s" % new_char
            print "\t\t\tnode_id: %s" % node_id
            print "\t\t\tg: %s" % g
            print "\t\t\tbeta: %s" % beta
            print "\t\t\tbeta_len: %s" % beta_len
            print "\t\t\tnode: %s" % node

        h = g

        while beta_len > g:
            try:
                node.visitors[string_id].add(j-1)
            except KeyError,e:
                node.visitors[string_id] = set((j-1,))
            h += g
            beta_len -= g
            beta = beta[g:]
            first_char = beta[0]
            root_id = node_id
            node_id = node.children[first_char]
            node = self[node_id]
            g = node.end[0] - node.start
            if debug:
                print format_Title("Skip/Count",'!',3)
                print "\t\t\tbeta: %s" % (beta if beta else None)
                print "\t\t\tbeta_len: %s" % beta_len
                print "\t\t\tfirst_char: %s" % first_char
                print "\t\t\troot_id: %s " % root_id
                print "\t\t\tnode_id: %s" % node_id
                print "\t\t\tg: %s" % g
                print "\t\t\th: %s" % h
                print "\t\t\tnode: %s" % node


        if debug:
            print format_Title("After Skip/Count",'!',3)
            print "\t\t\tbeta: %s" % (beta)
            print "\t\t\tbeta_len: %s" % beta_len
            print "\t\t\tfirst_char: %s" % first_char
            print "\t\t\tnew_char: %s" % new_char
            print "\t\t\troot_id: %s " % root_id
            print "\t\t\tnode_id: %s" % node_id
            print "\t\t\tg: %s" % g
            print "\t\t\tnode: %s" % node



            
        if g == beta_len:
            # Beta ends at a node
            # Update suffix link information either for the current string or
            # for generalized suffix trees
            if debug:
                print format_Title("g == beta_len","-",3)
                print "\t\t\tnode.visitors: %s" % node.visitors
                print "\t\t\tself.suffix: %s" % self.suffix

            if not node.leaf:
                if self.suffix is not None:
                    last_internal_node = self[self.suffix]
                    if debug:
                        print format_Title("Suffix link setup",'+',3)
                        print "\t\t\tlast_internal_node.: %s" %\
                                last_internal_node
                        print "\t\t\tself.suffix: %s" % self.suffix
                        print "\t\t\tlast_internal_node.suffix: %s" %\
                                        (last_internal_node.suffix)
                    if last_internal_node.suffix is None:
                        last_internal_node.suffix = node_id
                        if debug:
                            print "\t\t\tnode_id: %s" % node_id
                            print "\t\t\tlast_internal_node.suffix: %s" %\
                                last_internal_node.suffix
                            print format_Title("Suffix link setup end",'+',3)
                if node.parent is not None:
                    # The root node cannot have suffix link from its node
                    self.suffix = node_id
                    if debug:
                        print "\t\t\tself.suffix: %s" % self.suffix
            elif node.leaf:
                # We can use suffix link to leaf nodes in the case where we
                # are dealing with a string different to the one used when
                # creating the suffix link. Because, in that case, the leaf
                # node can have more than one children( the terminal character
                # is always child of a leaf node)
                if node.string != string_id:
                    # This will be 
                    if self.suffix is not None:
                        last_internal_node = self[self.suffix]
                        if debug:
                            print format_Title("Suffix link setup",'+',3)
                            print "\t\t\tlast_internal_node.: %s" %\
                                    last_internal_node
                            print "\t\t\tlast_internal_node.suffix: %s" %\
                                            (last_internal_node.suffix)
                        if last_internal_node.suffix is None:
                            last_internal_node.suffix = node_id
                            if debug:
                                print "\t\t\tnode_id: %s" % node_id
                                print "\t\t\tlast_internal_node.suffix: %s" %\
                                    last_internal_node.suffix
                                print format_Title("Suffix link setup end",'+',3)
                    if node.parent is not None:
                        # The root node cannot have suffix link from its node
                        self.suffix = node_id
                        if debug:
                            print "\t\t\tself.suffix: %s" % self.suffix
                else:
                    # We cannot create suffix link to a leaf node while
                    # processing a string. 
                    pass
            else:
                assert node.leaf not in (1,0)

            if node.string != None:
                try:
                    node.visitors [string_id].add(j-1)
                except KeyError,e:
                    node.visitors[string_id] = set((j-1,))

            if node.leaf:
                # Extend it to have S(i+1)
                # This is done by incrementing self.e
                
                # Beta ends at a leaf node so the node above is root_id
                self.v_id = root_id
                #self.v_gamma = [node.string,\
                #               node.start,\
                #               node.end[0] if j<=i else node.end[0]+1]
                self.v_gamma = [string_id,\
                                i - beta_len,
                                i if j <= i else i+1 ]
                if debug:
                    print format_Title("Node is Leaf", '+',3)
                    print "\t\t\tself.v_id: %s" % self.v_id
                    print "\t\t\tself.v_gamma: %s" % self.v_gamma

               
                # For Generalized suffix tree
                # We end at a leaf node. If this is the terminal character, we
                # already know that this node exists. If this is not the
                # terminal character node, new_char will be evaluated to True.
                # Then we check if the new character already exists as a
                # children, if this 
                if string_id != node.string:
                    if debug:
                        print format_Title("Generalized suffix tree",'+',3)
                    if new_char is not None:
                        if debug:
                            print format_Title("New_char == True",'+',3)
                        if new_char not in node.children:
                            # Rule 2 applies
                            if debug:
                                print format_Title("New char not in children",'+',3)
                            edge = [string_id, i, self.e]
                            leaf_node_id = self.create_Leaf(node_id,\
                                                edge,\
                                                string_id,\
                                                new_char,\
                                                j)
                            self.v_id = node_id
                            self.v_gamma = [string_id,\
                                    i ,\
                                    i if j <= i else i + 1 ]
                            if debug:
                                print "\t\t\tedge: %s" % edge
                                print "\t\t\tnew_char: %s" % new_char 
                                print "\t\t\tself.v_id: %s" % self.v_id
                                print "\t\t\tself.v_gamma: %s"% self.v_gamma
                        elif new_char in node.children:
                            # New char is already in node 
                            # Rule 3 apply
                            # Last updated node is taken globally
                            if debug:
                                print format_Title("Rule 3 applies",'+',3)
                                print "\t\t\tself.v_id: %s" % self.v_id
                                print "\t\t\tself.v_gamma: %s" % self.v_gamma
                        else:
                            if debug:
                                print format_Title("Missing condition",'!',3)
                            import sys
                            sys.exit(0)

                    else: 
                        # This is the terminal character
                        # We do nothing here. We will take care of that later
                        # on
                        if debug:
                            print format_Title("Terminal Node should follow","+",3)
                            print "New char: %s" % new_char
                elif string_id == node.string:
                    # There is nothing to do.
                    # If the new char does not exist yet, the leaf will be
                    # extended at the end of the phase. So we do nothing
                    if debug:
                        print format_Title("string_id == node.string",'+',3)

                # Terminal character node
                if new_char is None and new_char not in node.children:
                    terminal_node_id = self.create_Terminal(node_id)
                    if debug:
                        print format_Title("Terminal Node",'+',3)
                        print "\t\t\tNode: %s" % self[terminal_node_id]

            elif new_char not in node.children:
                # No path from the end of beta starts with S(i+1)
                if debug:
                    print format_Title("Beta ends without S(i+1)",'+',3)
                    
                if new_char is not None:
                    # If this is not the terminal character
                    edge = [string_id, i, self.e]
                    self.create_Leaf(node_id,\
                                    edge,\
                                    string_id,\
                                    new_char,\
                                    j)
                    if debug:
                        print "\t\t\tedge: %s" % edge

                elif new_char is None:
                    terminal_node_id = self.create_Terminal(node_id)
                    if node.parent != None:
                        self.leaves.add(node_id)
                    if debug:
                        print "\t\t\tTerminal node: %s" %\
                        self[terminal_node_id]
                else:
                    print "\t\t\t There is a condition not took into\
                            account for g == beta_len"
                    import sys
                    sys.exit(1)

                self.v_id = node_id
                if j <= i:
                    # We are still in one phase
                    self.v_gamma = [string_id,\
                            i if new_char is not None else 0,\
                            i if new_char is not None else 0 ]
                elif j> i:
                    # We are at the end of the phase
                    self.v_gamma = [string_id,
                                    i if new_char is not None else 0,\
                                    i + 1 if new_char is not None else 0]
                else:
                    print "\t\t Condition missing for the end of the phase"
                    import sys
                    sys.exit(1)

                if debug:
                    print "\t\t\tself.v_id: %s"  % self.v_id
                    print "\t\t\tself.v_gamma: %s" % self.v_gamma
                    print "\t\t\ti: %s" % i
                    print "\t\t\tj: %s" % j

            elif new_char in node.children:
                # Rule 3 applied
                # There is nothing to do about extensions
                self.stop = j
                self.v_id = node_id
                self.v_gamma = [string_id,\
                             i,\
                             i + 1]
                if debug:
                    print format_Title("New char in node.children",'+',3)
                    print "\t\t\tself.v_id: %s" % self.v_id
                    print "\t\t\tself.v_gamma: %s" % self.v_gamma

            else:
                print "\t\t there is one condition not took into account for\
                        extensions when g == beta_len" 
                import sys
                sys.exit(1)
 
        elif g > beta_len:
            # The end of beta falls in the middle of an edge
            if debug:
                print format_Title("g > beta_len",'+',3)
                print "\t\t\tbeta_len: %s" % beta_len
                print "\t\t\tg: %s" % g

            char_after_beta = strings[node.string][node.start + beta_len]
                            
            if new_char != char_after_beta:
                # Rule 2 apply
                if debug:
                    print format_Title("new_char != char_after_beta",'+',3)
                    print "\t\t\tchar_after_beta: %s" % char_after_beta
                    print "\t\t\tparent: %s" % node.parent
                    print "\t\t\tlower_node_id: %s" % node_id 
                    print "\t\t\tfirst_char: %s" % first_char 

                parent = node.parent
                lower_node_id = node_id
                internal_node_id = self.create_Internal(parent,\
                                                        lower_node_id,\
                                                        beta_len,\
                                                        first_char,\
                                                        string_id,\
                                                        i,\
                                                        j)
                if new_char is not None:
                    parent = internal_node_id
                    edge = [string_id,\
                            i,\
                            self.e]
                    leaf_node_id = self.create_Leaf(parent,\
                                                    edge,\
                                                    string_id,\
                                                    new_char,\
                                                    j)
                    if debug:
                        print format_Title("New Char",'+',3)
                        print "\t\t\tedge: %s" % edge
                elif new_char is None:
                    terminal_node_id = self.create_Terminal(internal_node_id)
                    self.leaves.add(internal_node_id) 
                    if debug:
                        print format_Title("Terminal Node",'+',3)
                        print "\t\t\tnode: %s" % self[terminal_node_id]
                else:
                    print "\t\t\tYou need to be cleaver next time :-)"
            else:
                # Rule 3 apply
                # We do nothing apart from keeping track of last updated node data
                # This is the node above this one
                self.stop = j
                self.v_id = root_id
                self.v_gamma = [string_id,\
                        i - beta_len,
                        i if j <= i else i + 1
                        ]
                if debug:
                    print format_Title("New char after beta",'+',3)
                    print "\t\t\tself.v_id: %s" % self.v_id
                    print "\t\t\tself.v_gamma: %s" % self.v_gamma
        else:
            print "There is one condition forgotten here :-)"
            import sys
            sys.exit(0)
           
    def node_Label(self, node_id):
        node = self[node_id]
        return self.strings[node.string]\
                [node.index:node.end[0]] if node.string != None else None

    def create_Terminal(self,parent):
        node_id = self.nodes
        self[node_id] = Node(parent=parent)
        parent_node = self[parent]
        parent_node.children [None] = node_id
        self.nodes += 1
        if debug:
            print "\t\t\tTerminal_node_id: %s" % node_id
        return node_id

    def create_Leaf(self,parent = 0,\
                        edge = None,\
                        string_id = None,\
                        char = None,\
                        j = 0):
        assert edge != None
        assert j != 0
        assert type(edge[2]) is  list
        assert string_id != None
        assert char != None

        node_id = self.nodes
        node = self[node_id] = Node(parent,\
                                    edge,leaf = 1)
        node.index = j - 1
        
        node.visitors[edge[0]] = set((j-1,))
        # Inform the parent node that it has a child
        p_node = self[parent]
        p_children = p_node.children
        p_children[char] = node_id

        self.leaves.add(node_id)
        self.nodes += 1

        if debug:
            print format_Title("Create Leaf Node", ">",4)
            print "\t\t\t\tparent: %s" % parent
            print "\t\t\t\tparent.children: %s" % p_children
            print "\t\t\t\tfirst_char: %s" % char
            print "\t\t\t\tnode_id: %s" % node_id
            print "\t\t\t\tnode.string: %s" % node.string
            print "\t\t\t\tnode.index: %s" % node.index
            print "\t\t\t\tnode.start: %s" % node.start
            print "\t\t\t\tnode.end: %s" % node.end
            print "\t\t\t\tnode.visitors: %s" % node.visitors
            print "\t\t\t\tnode.label: %s" % self.node_Label(node_id)
        
        return node_id 

    def create_Internal(self,parent,\
                        lower_node_id,\
                        g,\
                        first_char,\
                        string_id,\
                        i,\
                        j):
        node_id = self.nodes

        lower_node = self[lower_node_id]
        upper_node_id = lower_node.parent
        upper_node = self[upper_node_id]
        upper_node.children[first_char] = node_id

        lower_node_first_char = self.\
                strings[lower_node.string][lower_node.start + g]

        edge = [lower_node.string,\
                lower_node.start,\
                [lower_node.start + g]]


        node = self[node_id] = Node(parent=upper_node_id, edge=edge)
        node.children[lower_node_first_char] = lower_node_id
        node.index = lower_node.index

        lower_node_visitors = lower_node.visitors
        node_visitors = node.visitors

        for visitor in lower_node_visitors:
            try:
                node_visitors[visitor].update(lower_node_visitors[visitor]) 
            except KeyError,e:
                node_visitors[visitor] = lower_node_visitors[visitor]

        node_visitors [string_id] = set((j-1,))

        lower_node.parent = node_id
        lower_node.start = lower_node.start + g
        
        # Last updated node
        # The last updated node is the one above this new internal node. It
        # ensures that suffix links will be used only for nodes that already
        # exist before this extension.
        self.v_id = upper_node_id
        self.v_gamma = [string_id,\
                            i-g ,\
                            i if j <= i else i+1]

        # Update internal node information for suffix link
        if debug:
            print format_Title("Suffix Link setup","*",4)
            print "\t\t\t\tself.suffix: %s" % self.suffix
        if self.suffix is not None:
            last_internal_node = self[self.suffix]
            if debug:
                print "\t\t\t\tNode before: %s" % last_internal_node 
            if last_internal_node.suffix is None:
                last_internal_node.suffix = node_id
            if debug:
                print "\t\t\t\tself.suffix After: self.suffix"
                print "\t\t\t\tNode after: %s" % last_internal_node
                print format_Title("Suffix link setup ends", '*',4)
        self.suffix = node_id

        self.nodes += 1
        if debug:
            print format_Title('Create Internal Node','<',4)
            print "\t\t\t\tl_first_char: %s" % lower_node_first_char
            print "\t\t\t\tl_node_id: %s" % lower_node_id 
            print "\t\t\t\tl_node.index: %s" % lower_node.index
            print "\t\t\t\tl_start: %s" % lower_node.start
            print "\t\t\t\tl_end: %s" % lower_node.end
            print "\t\t\t\tu_node_id: %s" % upper_node_id 
            print "\t\t\t\tu_node.children: %s" % upper_node.children
            print "\t\t\t\tu_node.index: %s" % upper_node.index
            print "\t\t\t\tu_node.start: %s" % upper_node.start
            print "\t\t\t\tu_node.end: %s" % upper_node.end
            print "\t\t\t\tnode_id: %s" % node_id
            print "\t\t\t\tnode.index: %s" % node.index
            print "\t\t\t\tnode.start: %s" % node.start
            print "\t\t\t\tnode.end: %s" % node.end
            print "\t\t\t\tnode.children: %s" % node.children
            print "\t\t\t\tnode.visitors: %s " % node.visitors
            print "\t\t\t\tself.v_id: %s" % self.v_id
            print "\t\t\t\tself.v_gamma: %s" % self.v_gamma
            print "\t\t\t\tself.suffix: %s" % self.suffix
        return node_id

    def set_Visitors(self):
        # The way the tree has been built provides sets the visitors for all
        # nodes in the tree. So we do not need to do it anymore. The function
        # is kept for historical reason and for any future need, purpose
        for leaf in self.leaves:
            node = self[leaf]
            if node.leaf:
                visitors = node.visitors
                parent = node.parent
                while parent:
                    p_visitors = self[parent].visitors
                    for visitor in visitors:
                        try:
                            p_visitors[visitor].update(visitors[visitor])
                        except KeyError,e:
                            p_visitors[visitor] = visitors[visitor]
                    parent = self[parent].parent

    @property
    def cv(self):
        # This will compute the C(v) numbers as explained in Dan  Gusfield's
        # Book at page 128
        if not self.__cv:
            for node_id in self:
                node = self[node_id]
                if 'string' in vars(node) (node.start != node.end): 
                    # This condition ensures that root node and terminal
                    # character nodes are not considered
                    k = len(self[node].visitors)
                    if k > 1:
                        # We are interested in node traversed by only one
                        # string.
                        depth = node.end - node.index
                        try:
                            self.__cv[k][depth].add(node_id)
                        except:
                            self.__cv[k] = {depth : set((node_id,))}
        return self.__cv

    @property
    def vk(self):
        # This will compute V(k) as explained in Dan Gusfield's book
        if not self.__cv:
            self.cv
        if not self.__vk:
            for k in self.__cv:
                # Sort the list from the longer to the lower
                __cv =  sorted(self.__cv, reverse=True)
                self.__vk[__cv[0]] = self.__cv[__cv[0]]
        return self.__vk
    
    @property
    def lk(self):
        if not self.__vk:
            self.vk
        if not self.__lk:
            __lk = sorted(self.__vk, reverse=True)
            self.__lk[__lk[0]] = self__vk[__lk[0]]
            for k in __lk[1:]:
                self.__lk[k] = self__lk[k-1] | self__vk[k]
        return self.__lk

    @property
    def cn(self):
        # Common nodes
        # List of nodes providing all common substrings
        # If a node has been visited by all the strings, then it is common to
        # all of them. Actually the substring on the path from root to this
        # node is common to all the nodes
        # Do a depth-first traversal, in fact the traversal is done from
        # bottom to up
        if not self.__cn:
            self.set_Visitors()
            # No need to use this anymore since we did it when building the
            # tree
            self.__cn = set([ node for node in self if (len(self[node].visitors) ==\
                    self.strings_len and self[node].string != None ) ])
        return self.__cn

    @property
    def cs(self):
        # Dictionary{longest common substring : (string_id, start, stop )}
        # The values are a set of (string, start, stop)
        # If we have not retrieved common nodes yet, then do it here
        if not self.__cn:
            self.cn
        # If this is the first time we look for common substrings , we do it
        # here . If not the value has already be calculated and just return it
        if not self.__cs:
            # Label node common to all strings
            # This is done to retrieve both the label and depth information.
            # For now it is not optimal. 
            # TO BE FIXED: gather the depth
            # information either when doing the traversal for visitors or in
            # the tree creation process
            # Collect data of all node traversed by all visited by all nodes
            for cn in self.__cn:
                lcs = self[cn]
                visitors = lcs.visitors
                label = self.node_Label(cn)
                depth = lcs.end[0] - lcs.index
                __occurences = set()
                for visitor in visitors:
                    # Visitor is a list dictionary like 
                    # {string_id : set(start_index,)}
                    # So start_indexes give back all starting indexes of the
                    # substring in the string visitor. This will give also
                    # back all repeated substrings.
                    start_indexes = visitors[visitor]
                    # visitor =  0 for the first input string so we keep only
                    # data related to that script and the extraction of the
                    # all longest common substring will be based on that one
                    for start_index in start_indexes:
                        _cs = (visitor, start_index, start_index + depth )
                        if not visitor:
                            # If this is the first string we keep only the
                            # substring related to the lowest index in string
                            # pointed by visitor. We do this to ensure the
                            # algorithm we will use to find all longest common
                            # substring will not be defeat since we check that
                            # the interval[start,end] of a substring is not
                            # include in the interval of another.
                            #small_index = sorted(start_indexes)[0]
                            #if start_index == small_index:
                            try:
                                self._cs[ label].add(_cs)
                            except KeyError,e:
                                self._cs[ label ] = set((_cs,))
                        __occurences.add(_cs)
                self.__cs[label] = __occurences
            # Filter out unlabeled nodes, especial the node use to emulated
            # the terminal character
            self.__cs =\
                    { label : self.__cs[label] for label in self.__cs if label }

        return self.__cs

    @property
    def alcs(self):
        if not self._cs:
            self.cs
        if not self.__alcs:
            # List of all common substrings
            # _cs is the list of label of common substrings
            # Sort them by their length to have the longest at the top
            _cs = sorted([cs for cs in self.__cs],\
                    key=lambda x: len(x), reverse = True)
            __cs = []

            # Feed the list of all longest common substrings with the longest
            # one which will be the first in _cs
            try:
                __cs.append(_cs[0])
            except IndexError,e:
                # There is no common substring
                self.__alcs = {}
            # Used to know if we break a for loop before its end
            break_it_here = 0             

            for k in _cs[1:]:
                # Common substrings occurrences in string 0
                cs_occurences = self._cs[k]
                for l in __cs:
                    # All common substrings already kept.
                    # We extract data for string 0
                    acs_occurences = self._cs[l]
                    for acs_occurence in acs_occurences:
                        acs_range = acs_occurence[1:]
                        for cs_occurence in cs_occurences:
                            cs_range = cs_occurence[1:]
                            if acs_range[0] <= cs_range[0] < cs_range[1] <= acs_range[1]:
                                # If a substring is included in another one
                                # already kept, we break
                                break_it_here = 1
                                break
                        if break_it_here:
                            break
                    if break_it_here:
                        # To prepare for the next substring
                        break_it_here = 0
                        break
                else:
                    __cs.append(k)
            for lcs in __cs:
                alcs = self.__cs[lcs]
                alcs_dict = {}
                for cs in alcs:
                    try:
                        alcs_dict[cs[0]].add(cs[1:])
                    except KeyError,e:
                        alcs_dict[cs[0]] = set((cs[1:],))

                self.__alcs[lcs] = alcs_dict
        return self.__alcs

    @property
    def lcs(self):
        # Dictionary{longest common substring : (string_id, start, stop )}
        # The values are a set of (string, start, stop)
        # If we haven't set visitors, then do it here
        if not self.__alcs:
            self.alcs
        # If we haven't retrieve the longest common substring yet, we do it
        # here 
        if not self.__lcs and self.__alcs :
            # Label node common to all strings
            # This is done to retrieve both the label and depth information.
            # For now it is not optimal. 
            # TO BE FIXED: gather the depth
            # information either when doing the traversal for visitors or in
            # the tree creation process
            __lcs = sorted( self.__alcs, key=lambda lcs: len(lcs), reverse=True)
            # Keep the longest one
            self.__lcs = { __lcs[0] : self.__alcs[ __lcs[0] ] }
        return self.__lcs


def main():
    S = 'xabxa'
    S1 = 'bxabxa'
    S2 = 'babxba'
    S3 = 'axabxa'
    S4 = 'axabx'
    S5 = 'superiorcalifornialives'
    S6 = 'sealiver'
    S7 = 'zealiver'
    S8 = 'Bonjour_tout'
    S9 = "Bonsoir_tout"
    S10 = ''.join(file('Pcap/Mail/a').readlines())
    S11 = ''.join(file('Pcap/Mail/b').readlines())
    S12 = ''.join(file('Pcap/Mail/c').readlines())
    S13 = 'aimas.aisaisma'
    S14 = 'aimas.aisaisma.bonjour.bonsoir\n'
    S15 = ''.join(file('Pcap/Mail/d').readlines())
    S16 = ''.join(file('a.txt').readlines())
    S17 = file('a').readlines()
    S18 = file('b').readlines()
    S19 = file('c').readlines()
    S20 = '0000\n'
    S21 = '00005\n'


    g = gstree()
    #g.add_String(S)
    #g.add_String(S1)
    #g.add_String(S2)
    #g.add_String(S3)
    #g.add_String(S4)
    #g.add_String(S5)
    #g.add_String(S6)
    #g.add_String(S7)
    #g.add_String(S8)
    #g.add_String(S9)
    #g.add_String(S10.encode('hex'))
    #g.add_String(S11.encode('hex'))
    #g.add_String(S12)
    #g.add_String(S13)
    #g.add_String(S14)
    #g.add_String(S15)
    #g.add_String(S16)
    #g.add_String(S18)
    #g.add_String(S19)
    #g.add_String(S20)
    #g.add_String(S21)

    [g.add_String(string) for string in S17]

    #for node in g.leaves:
    #    print "%s: %s" % (node,g.node_Label(node))

    alcs = g.cs
    for k in alcs:
        print "%s: %s" % (k, alcs[k])


if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
    #main()
