import lcs
lcs = lcs.lcs

a = ("Bonjour tout le monde", "Bonsoir tout le monde")
substringSets = ['Pcap/Mail/a','Pcap/Mail/b']
responder = ['Pcap/Lamp/Mail05July/010.067.001.085.00025-010.067.180.184.34903',\
        'Pcap/Lamp/Mail05July/010.067.180.184.00025-010.067.180.152.35051',\
        'Pcap/Lamp/Mail05July/010.067.180.184.00025-010.067.180.152.49651',\
        'Pcap/Lamp/Mail05July/010.067.001.085.00025-010.067.180.184.51216',\
        'Pcap/Lamp/Mail05July/010.067.001.085.00025-010.067.180.184.51217',\
        'Pcap/Lamp/Mail05July/010.067.001.085.00025-010.067.180.184.51218',\
        'Pcap/Lamp/Mail05July/010.067.001.085.00025-010.067.180.184.55098',\
        'Pcap/Lamp/Mail05July/010.067.180.184.00025-010.067.180.152.58854']

originator = ['Pcap/Lamp/Mail05July/010.067.180.152.35051-010.067.180.184.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.152.49651-010.067.180.184.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.152.58854-010.067.180.184.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.184.34903-010.067.001.085.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.184.51216-010.067.001.085.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.184.51217-010.067.001.085.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.184.51218-010.067.001.085.00025',\
        'Pcap/Lamp/Mail05July/010.067.180.184.55098-010.067.001.085.00025',\
        ]   
files_handle = [ file(k) for k in substringSets  ]
strings = [k.read() for k in files_handle]
[k.close() for k in files_handle]
out = lcs(strings)
for k in out.lcs:
    print k

