#!/usr/bin/env python
# This script will process pcap files provided as input
# class Decoder is a dispatcher
# This script is based on another one from Impacket website
import sys
import os
#from exceptions import Exception
#from threading import Thread

try:
    import pcapy
except ImportError,e:
    print "You need to install the python module pcapy"
    sys.exit(1)
else:
    from pcapy import open_offline

try:
    import impacket
except ImportError,e:
    print "You need to install the python module impacket"
    sys.exit(1)
else:
    from impacket.ImpactDecoder import EthDecoder, LinuxSLLDecoder

decoder = None
ip_protos = {1: 'icmp',\
         6: 'tcp',\
        17: 'udp',\
        }

def realPath(file_name):
    assert(os.path.exists(file_name))
    return os.path.realpath(file_name)

def tcpFlags(tcp_pkt):
    # tcp_pkt is the upper layer of IP protocol identified as TCP so
    # that ip_proto = 6

    assert(hasattr(tcp_pkt,'get_th_flags'))

    flags = list()
    flags.append(tcp_pkt.get_CWR())
    flags.append(tcp_pkt.get_ECE())
    flags.append(tcp_pkt.get_URG())
    flags.append(tcp_pkt.get_ACK())
    flags.append(tcp_pkt.get_PSH())
    flags.append(tcp_pkt.get_RST())
    flags.append(tcp_pkt.get_SYN())
    flags.append(tcp_pkt.get_FIN())

    return int(''.join(map(str,flags)),2)

class Decoder(object):
    def __init__(self, pcap_file):
        # Query the type of the link and instantiate a decoder accordingly.
        # Only tcp and udp packets are handled
        pcap_filter = 'tcp or udp'
        pcap_file = realPath(pcap_file)
        pcap_obj = open_offline(pcap_file)
        pcap_obj.setfilter(pcap_filter)

        global decoder

        datalink = pcap_obj.datalink()
        if pcapy.DLT_EN10MB == datalink:
            decoder = EthDecoder()
        elif pcapy.DLT_LINUX_SLL == datalink:
            decoder = LinuxSLLDecoder()
        else:
            raise Exception("Datalink type not supported: " % datalink)

        self.pcap = pcap_obj
        self.services = Services()
        self.start()

    def start(self):
        # Sniff ad infinitum.
        # PacketHandler shall be invoked by pcap for every packet.
        try:
            self.pcap.loop(0, self.packetHandler)
        except Exception, e:
            print "======= Truncated pcap====="


    def packetHandler(self, hdr, data):
        """Handles an incoming pcap packet. This method only knows how
        to recognize TCP/IP connections.
        Be sure that only TCP packets are passed onto this handler (or
        fix the code to ignore the others).

        Setting r"ip proto \tcp" as part of the pcap filter expression
        suffices, and there shouldn't be any problem combining that with
        other expressions.
        """
        self.services.append((hdr,data)) 

class Stream(list):
    def __init__(self, pkt=None):
        if pkt is not None:
            self.append(pkt)

    def append(self,pkt):
        def tcp():
            if tcpFlags(upper_layer) == 24:
                super(self.__class__,self).append\
                        (upper_layer.get_data_as_string())

        def udp():
            super(self.__class__,self).append\
                    (upper_layer.get_data_as_string())

        def icmp():
            pass

        global decoder
        proto_data = {\
                1: icmp,\
                6: tcp,\
                17: udp,\
                }
        eth = decoder.decode(pkt[1])
        ip = eth.child()
        upper_layer = ip.child()
        proto = ip.get_ip_p()
        proto_data[proto]()

    @property
    def data(self):
        return ''.join(self)
    
class Session(dict):
    def __init__(self,pkt,proto, src, dst, sport, dport):
        self['src'] = src
        self['dst'] = dst
        self['sport'] = sport
        self['dport'] = dport
        self['proto'] = proto 
        self.__pcap = list()
        self.__originator = Stream(pkt)
        self.__responder = Stream()

        self.append(pkt)

    def append(self,pkt):
        # TO BE FIXED: tcp reordering
        self.__pcap.append(pkt)
        ip = decoder.decode(pkt[1]).child()
        if self['src'] == ip.get_ip_src():
            self.__originator.append(pkt)
        elif self['src'] == ip.get_ip_dst():
            self.__responder.append(pkt)

    @property
    def pcap(self):
        return self.__pcap
    
    @property
    def originator(self):
        return self.__originator.data
        pass

    @property
    def responder(self):
        return self.__responder.data
        pass

    #def 
    pass

class SessionList(dict):
    def __init__(self,pkt):
        self.append(pkt)
        global decoder
        self.__proto = decoder.decode(pkt[1]).child().get_ip_p()
        self.__proto = ip_protos[self.__proto]
        self.__src = list()
        self.__dst = list()
        #self.__sport = list()
        #self.__dport = list()

    def append(self,pkt):
        global decoder
        header = pkt[0]
        data = pkt[1]
        p = decoder.decode(data)
        ip = p.child()
        upper_layer = ip.child()
        
        src = ip.get_ip_src()
        dst = ip.get_ip_dst()
        proto = ip.get_ip_p()
        sport = None
        dport = None

        if proto == 17:
            sport = upper_layer.get_uh_sport()
            dport = upper_layer.get_uh_dport()
        elif proto == 6:
            sport = upper_layer.get_th_sport()
            dport = upper_layer.get_th_dport()

        session = frozenset((src, sport, dst, dport))
        if session in self:
            self[session].append(pkt)
        else:
            self[session] = Session(pkt,proto,src,dst,sport,dport)
            self.__dport = dport # (Too basic, to be fixed because
                                 # evaluated each time
        pass

    @property
    def originator(self):
        data = list()
        for session in self:
            data.append(self[session].originator)
        return data

    @property
    def responder(self):
        data = list()
        for session in self:
            data.append(self[session].responder)
        return data

    @property
    def src(self):
        pass

    @property
    def dst(self):
        pass

    @property
    def sport(self):
        pass

    @property
    def dport(self):
        return self.__dport
        pass

    @property
    def ip_proto(self):
        return self.__proto

class Services(dict):
    
    def __init__(self):
        self.tcp = set()
        self.udp = set()

    def update(self,services):
        super(self.__class__,self).update(services)
        for service in services.tcp:
            self.tcp.add(service)
        for service in services.udp:
            self.udp.add(service)

    def append(self,pkt):
        header = pkt[0]
        data = pkt[1]
        global decoder

        p = decoder.decode(data)
        ip = p.child()
        upper_layer = ip.child()
        
        # Find IP protocol and Destination port
        proto = None
        try:
            proto = ip.get_ip_p()
        except AttributeError, e:
            # IP Protocol not supported, may be IPV6 (TO BE FIXED)
            return
        port = None
        if proto == 6:
            # This is TCP protocol at upper layer
            dport = upper_layer.get_th_dport()
            sport = upper_layer.get_th_sport()
        elif proto == 17:
            # This is UDP protocol at upper layer
            dport = upper_layer.get_uh_dport()
            sport = upper_layer.get_uh_sport()

        # Construct the key to identify the service

        service = frozenset((proto, dport))

        # Verify if the service has been already registered. If not
        # check if the packet is the first of the session. This check
        # is only done for TCP connections. For UDP we proceed the
        # packet.

        try:
            self[service]
        except KeyError, e:
            service = frozenset((sport, proto))
            try:
                self[service]
            except KeyError, e:
                service = frozenset((dport, proto))
        finally:
            if service in self:
                self[service].append(pkt)
            else:
                if proto == 17: # UDP
                    self[service] = SessionList(pkt)
                    self.udp.add(service)
                elif proto == 6: # TCP
                    # if only the SYN flag is set, that is the beginning
                    # of a new connection. In this case we register a new
                    # service and append the new packet to it
                    if tcpFlags(upper_layer) == 2:
                        self[service] = SessionList(pkt)
                        self.tcp.add(service)

    pass



if __name__ == '__main__':
    # Parse input arguments 
    import argparse
    parser = argparse.ArgumentParser(description='Process pcap files')
    parser.add_argument('-i', '--input',dest='infile', nargs='+')
    parser.add_argument('-o', '--output',dest='outfile')

    args = parser.parse_args()
    if args.infile is None:
        parser.print_help()
        sys.exit(1)

    args.infile = list(args.infile)
    args.infile = map(os.path.realpath, args.infile)
    services = Decoder(args.infile[0]).services
    for infile in args.infile[1:]:
        services.update(Decoder(infile).services)
    tcp = services.tcp
    udp = services.udp

    print "TCP Proto ..."
    for service in tcp:
        print service

    print "UDP Proto ..."
    for service in udp:
        print service


    #print services
