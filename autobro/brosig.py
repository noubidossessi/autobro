#!/usr/bin/env python
# brosig.py

from Tools import *
import sys,os,glob

def getFileNames(filenames):
    filenames = list(filenames)
    files = list()
    for f in filenames:
        if os.path.isdir(f):
            for root, subfolders, subfiles in os.walk(f):
                for subfile in subfiles: 
                    files.append(os.path.realpath(os.path.join(root,subfile)))
        elif os.path.isfile(f):
            files.append(os.path.realpath(f))
        else:
            subfiles = glob.glob(f)
            for subfile in subfiles:
                files.append(os.path.realpath(subfile))
    return files

class Struct(dict):
    """
        This type is used to hold any kind of data. Especially, it is used here to make
        easy to pass informations, parameters or attributes of bro signatures...
    """
    pass

class Attributes(dict):
    def __init__(self,xml_file):
        self.max_len = 0
        from xml.etree.ElementTree import ElementTree

        __tree = ElementTree()
        __tree.parse(xml_file)
        __header = __tree.getiterator('Header')
        __contents = __tree.getiterator('Contents')
        __dependancy = __tree.getiterator('Dependancy')
        __context = __tree.getiterator('Context')
        __actions = __tree.getiterator('Actions')

        __conditions = [ __header, __contents, __dependancy, __context, __actions]

        for _condition in __conditions:
            tag = _condition[0].tag
            self[tag] = Struct()
            for k in _condition:
                setattr(self[tag], k.text.strip(), None)
                self.max_len = max(self.max_len, len(k.text.strip()))

    def __setdata__(self,key,data):
        for attr in data:
            setattr(self[key], attr, data[attr])
    
    def Header(self, data):
        for string in data:
            if string in ('ip-proto','src-port','dst-port'):
                if data[string][1] is not None:
                    data[string] = ' '.join(map(str,data[string]))
                else:
                    data[string] = None
            #print string,' ',data[string]

        self.__setdata__('Header',data)

    def Contents(self,data):
        self.__setdata__('Contents', data)

    def Dependancy(self,data):
        self.__setdata__('Dependancy', data)

    def Context(self,data):
        self.__setdata__('Context', data)

    def Actions(self,data):
        for string in data:
            data[string] = '\"%s\"' % data[string]
        self.__setdata__('Actions', data)

class Signature(object):
    def __init__(self,attributes,signature_id):
        self.attributes = attributes
        self.id = signature_id
        self._attr_len = self.attributes.max_len
        #self.ddbuild()


    def format(self,attribute):
        """
            Format the printing of the attributes identifiants
        """
        return '%s ' % attribute # attribute.ljust(self._attr_len)

    def formatOutput(self,attr):
        """
            Format the output of each attribute, including the value taken by the
            attribute.
            attr:   is a Struct an object holding some attributes
        """
        signature = ''
        _vars = vars(attr)
        #print _vars
        for k in _vars:
            #print "k: ", k
            #print "k test: ", _vars[k] is not None
            if _vars[k] is not None:
                if isinstance(_vars[k],list):
                    for data in _vars[k]:
                        signature = '%s\t%s %s\n' % (signature,k.replace('_','-'),\
                                data)
                else:
                    signature = '%s\t%s %s\n' % \
                    (signature,k.replace('_','-'),_vars[k])
        return signature 

    @property
    def signature(self):
        """
            Combine all defined attributes to produce the text for the over all signature
            self.attributes:    of type Attributes so is a dictionnary of Struct
                                Each Struct is a dictionnary and have attributes of a
                                signatures depending of type of attribute( conditions or
                                actions)
            self.id:            id of the signature

        """
        signature = ''
        for attr in self.attributes.values():
            signature = '%s%s' % (signature, self.formatOutput(attr))
        signature = 'signature %s{\n%s\n}\n' % (self.id,signature)
        #print signature
        return signature

    def header(self):
        """
            Same as self.combine() except that only header conditions
            are took into account
        """
        header = self.attributes['Header']
        return self.formatOutput(header)

    def contents(self):
        """
            Same as self.combine() except that only content conditions
            are took into account
        """
        contents = self.attributes['Contents']
        return self.formatOutput(contents)

    def dependancy(self):
        """
            Same as self.combine() except that only dependancy
            conditions are took into account
        """
        dependancy = self.attributes['Dependancy']
        return self.formatOutput(dependancy)

    def context(self):
        """
            Same as self.combine() except that only context conditions
            are took into account
        """
        context = self.attributes['Context']
        return self.formatOutput(context)

    def actions(self):
        """
            Same as self.combine() except that only actions are took
            into account
        """
        actions = self.attributes['Actions']
        return self.formatOutput(actions)
    
class Process:
    """
        Process all data to generate signatures and save to files
        self.conf:  configuration file
    """

    def __init__(self, conf, args):
        self.conf = os.path.realpath(conf)
        self.__processArguments(args)
        self.extractSignatures()


    def __processArguments(self, args):
        from xml.etree.ElementTree import ElementTree
        self.__tree = ElementTree()
        self.__tree.parse(self.conf)
        self.sigid = self.__tree.find("Database/Bro/Id").text
        self.sigfile = self.__tree.find("Database/Bro/File").text
        self.sigcount = int(self.__tree.find("Database/Bro/Count").text)
        self.inpcap = getFileNames(args.infile)
        self.inpcap = map(pcap.realPath, self.inpcap)
        from time import ctime
        self.outpcap = '%s%s%s' % ('/tmp/', ctime().replace(' ', '_').replace(':','_'),\
                                    '.pcap')
        if args.outdir is  None:
            output_dir = os.path.basename(self.outpcap).split('.')[0]
            self.outdir = os.path.dirname(self.outpcap) + '/' + output_dir
        else:
            self.outdir = os.path.realpath(args.outdir)
        
        # Args processing to override default values
        if args.sigfile is not None:
            _sigfile = os.path.splitext(args.sigfile)
            if _sigfile[1] is not '.sig':
                self.sigfile = os.path.realpath('%s%s' % (_sigfile[0], '.sig'))


    def extractSignatures(self):
        # Process all input files and make the pcap processing using
        # classes and function provided by the pcap module.
        # For each service (a pair proto/port) we process all sessions
        # data and extract the signature. 
        # For now we don't include the possibility to update existing
        # signatures of the databases. But we will work on that
        # soon...

        #import time
        #t_0 = time.time()
        print "Reading ..................... %s" % self.inpcap[0]
        services = pcap.Decoder(self.inpcap[0]).services
        
        for infile in self.inpcap[1:]:
            print "Reading ................... %s" % infile
            services.update(pcap.Decoder(infile).services)
        #print "Time for all reading .... ", time.time() - t_0

        
        for service in services:#.tcp:
            try:
                if services[service].dport != 22:
                    self.dumpSignature(services[service])
            except KeyError,e:
                print "%s Failed!!!" % service
                pass
            else:
                print '%s/%s' % (services[service].ip_proto,\
                       services[service].dport)

        self.__tree.find("Database/Bro/Count").text = \
                str(self.sigcount )
        self.__tree.write(self.conf)


    def dumpSignature(self,service):
        """
            For each service, meaning that each list of sessions
            specific to one service, extract signature data, generate
            the signature and dump it to a file specified in the
            configuration file provided as argument to the programm
        """
        originator_payload = filter((lambda x: x is not '')\
                ,service.originator)
        responder_payload = filter((lambda x: x is not '')\
                ,service.responder)
        #print originator_payload
        #print responder_payload 
        #print 70 * '*'
        
        originator_pattern = None
        originator_sig = None
        originator_sig_id = None
        originator_sig_attributes = None

        responder_pattern = None
        responder_sig = None
        responder_sig_id = None
        responder_sig_attributes = None

        originator_port = None
        responder_port = None
        ip_proto = service.ip_proto
        responder_port = service.dport
        self.sigcount += 1
        originator_sig_id = '%s-%i' % (self.sigid, self.sigcount)
        self.sigcount += 1 
        originator_attempt_sig_id = '%s-%i' % (self.sigid, self.sigcount)
        self.sigcount += 1
        responder_sig_id = '%s-%i' % (self.sigid, self.sigcount )

        try:
            originator_pattern = tree.patterns(originator_payload).out
        except KeyError,e:
            file(str(originator_sig_id),'a+').write('\n'.join([ k.encode('hex') for k in
                originator_payload  ]))
            return
        try:
            responder_pattern = tree.patterns(responder_payload).out
        except KeyError,e:
            file(str(responder_sig_id),'a+').write('\n'.join([ k.encode('hex') for k in
                responder_payload  ]))
            return


        if (len(responder_pattern) !=0):
            responder_sig_attributes = Attributes(self.conf)

            responder_sig_attributes.Header(\
                    {
                        'ip-proto': ('==', ip_proto),\
                    })
            responder_sig_attributes.Contents(\
                    {
                        'payload': responder_pattern,\
                    })
            responder_sig_attributes.Actions(\
                    {
                        'event': r'%s: %s' % ( responder_sig_id, 'Attack succeded :-('),\
                    })
            responder_sig_attributes.Dependancy(\
                    {
                        'requires-reverse-signature': originator_sig_id,\
                    })
            responder_signature = Signature(responder_sig_attributes,\
                responder_sig_id)
            with file(self.sigfile, 'a+') as f:
                f.write(responder_signature.signature)
        else:
            return

        
        if (len(originator_pattern) != 0):
            originator_sig_attributes = Attributes(self.conf)
            originator_attempt_sig_attributes = Attributes(self.conf)

            originator_sig_attributes.Header(\
                    {
                        'ip-proto': ('==', ip_proto),\
                        'dst-port': ('==', responder_port),\
                    })
            originator_sig_attributes.Contents(\
                    {
                        'payload': originator_pattern,\
                    })
            originator_sig_attributes.Actions(\
                    {
                        'event': r'%s: %s' % ( originator_sig_id, 'Attack attempt'),\
                    })
            originator_signature = Signature(originator_sig_attributes, \
                originator_sig_id)
            with file(self.sigfile, 'a+') as f:
                f.write(originator_signature.signature)

def main():
    # Options handling with module parser
    import argparse

    parser = argparse.ArgumentParser(description='Extract, \
            from saved pcap files, Bro signatures to charaterize traffic seen')
    parser.add_argument('-r', '--read',dest='infile', nargs='+', required=True, help='Input pcap files. There could be more than one')
    parser.add_argument('-c','--config', dest='config', required=True, help='Configuration file')
    parser.add_argument('-o', '--output',dest='outfile', required=False)
    parser.add_argument('-d', '--outdir',dest='outdir', required=False)
    parser.add_argument('-s', '--sig', dest='sigfile', required=False)


    args = parser.parse_args()
    if args.infile is None or args.config is None:
        parser.print_help()
        sys.exit(1)

    p = Process(args.config, args)

    sys.exit(0)

if __name__ == '__main__':
    import cProfile
    #cProfile.run('main()')
    main()
