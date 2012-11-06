#!/usr/bin/env python
# coding: utf-8
# 
# tree.py
#
# 22 / 10 / 2011 Pattern generation for Bro IDS 

"""
    This module will use results from gstree module to generate flex
    compliant regular expressions for Bro. For now, the module only takes into
    account byte sequence, no case detection, no integration of common
    substrings indexes.
"""

import gstree
import re
debug = 0
class patterns(object):
    def __init__(self,strings):
        gst = gstree.gstree()
        # We aim at providing hexadecimal strings as content conditions for
        # Bro. Because of that all kept data will be encoded in hexadecimal.
        # The main issue is that hexadecimal strings are a suit of digits and
        # letters from a to f. We know that, starting from the begin to
        # successive values form an hexadecimal value.
        # To be recognized by regular expression modules, these digits should
        # be preceded by "\x". So we use the re module of  Python to replace
        # all two characters values by their hexadecimal representation....
        re_search_pattern = r'([a-f0-9]{2})'
        re_replace_pattern = r'\x\1'

        [gst.add_String(string) for string in strings]

        alcs = dict(gst.alcs)
        del gst
        
        self.out = []
        if debug:
            for k in alcs:
                print k,alcs[k]

        # Determine  how many times each substring appear in all strings.
        # Retain the minimum of occurrences.
        # Find the number of strings

        for lcs in alcs:
            lcs_dict = alcs[lcs] 
            number_of_occurrences = min( map( len, lcs_dict.values()  )  )
            if debug:
                print "\tlcs: %s" % lcs
            for occurence in lcs_dict:
                if debug:
                    print "\t\toccurence: %s" % lcs_dict[occurence]
                lcs_dict[occurence] = sorted(lcs_dict[occurence],\
                                    key=(lambda x: x[0]))[0:1]
                if debug:
                    print "\t\toccurence sorted: %s" % lcs_dict[occurence]
            alcs[lcs] = lcs_dict
        # Let's form the token subsequence
        number_of_strings = len(strings)
        strings_dict = { string_id: [] for string_id in\
                range(number_of_strings)} 

        for lcs in alcs:
            lcs_dict = alcs[lcs]
            for occurrence in lcs_dict:
                indexes = lcs_dict[occurence]
                for index in indexes:
                    strings_dict[occurrence].append( (lcs,\
                                            index[0],index[1])  )
                    
        if debug:
            print "string_dict: %s" % strings_dict
        
        for token in strings_dict:
            strings_dict[token] = sorted(strings_dict[token],\
                                    key=(lambda x: x[1]))

        if debug:
            print "strings, ordered: %s" % strings_dict

        number_of_patterns = len (strings_dict[0])
        token_subsequence = []
        unordered_substrings = []
        for k in range(number_of_patterns):
            pattern = strings_dict[0][k]
            for l in strings_dict:
                if strings_dict[l][k][0] != pattern[0]:
                    unordered_substrings.append(pattern[0])
                    break
            else:
                token_subsequence.append(pattern[0])

        token_subsequence = '.*'.join(\
                map((lambda x:\
                    re.sub(re_search_pattern,\
                            re_replace_pattern,\
                            x.encode('hex'))),\
                token_subsequence\
                )) 
#                map((lambda x:\
#                            x),\
#                token_subsequence\
#                )) 
        token_subsequence = r'/.*%s.*/' % token_subsequence

        unordered_substrings = map((lambda x: r'/.*%s.*/' %\
                                    re.sub(re_search_pattern, \
                                        re_replace_pattern,x.encode('hex'))),\
#                                    x),\
                                 unordered_substrings)

        self.out = [token_subsequence]
        for k in unordered_substrings:
            self.out.append(k)
        
        if debug:
            print "token: %s"  % token_subsequence
            print "unordered: %s" % unordered_substrings
            print "self.out: %s" % self.out

def main():
    S = 'xabxa'
    S1 = 'bxabxa'
    S2 = 'babxba'
    S3 = 'axabxa'
    S4 = 'axabx'
    S5 = 'superiorcalifornialives'
    S6 = 'sealiveralive'
    S7 = 'zealiver'
    S8 = 'Bonjour_tout'
    S9 = "Bonsoir_tout"
    S10 = ''.join(file('Pcap/Mail/a').readlines())
    S11 = ''.join(file('Pcap/Mail/b').readlines())
    S12 = ''.join(file('Pcap/Mail/c').readlines())
    S13 = 'aimas.aisaisma'

    #g = gstree.gstree()
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
    #g.add_String(S10)
    #g.add_String(S11)
    #g.add_String(S12)
    #g.add_String(S13)
    #for node in g.leaves:
    #    print "%s: %s" % (node,g.node_Label(node))

    #for k in g.alcs:
    #    print "%s: %s" % (k, g.alcs[k])

    strings = [S5,S6]
    p = patterns(strings)

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
    #main()


