Anneke
======
Create IPTV from dvb-t/c/s and decript it, only if it is needed. Created for tvheadend but it wil work for mythtv or udpxy (not tested)
It can work as a alternative to the decript DVBLoopback adapter like sasc-ng. 

The server, client(s) and workerd does not have to run on the same device. You can spread the workload such as running dvbworker on a PI and the decriptworker on a other PI or high end pc.

It is a working progress, this is the first working code.
Feel free to translate to English or correct my orthography

Anneke Works as follows:
- Anneke_client keeps track of the open udp ports, from tvheadend or mythtv.
- If a port opens or closed the Anneke_client sends it to the anneke_server.
- the anneke_server looks which "dvbworkers" and "decriptworker" are connected and free. (or a dvbworkers witch has a the same frequentie open)
- the anneke_server gives assignments to the anneke_dvbworkers.
- A dvbworker runs the dvblast command. Dvblast streams the iptv to decripterworker.
- The drecrptworker runs the tsdecript command and tsdecript creates a (uncripted) IPTV udp stream. 

Bug of dvblast
--------------
A bug in dvblast does not stream the descrambel PID when remaping. Anneke uses the remap function. 
A quick workaround is to manually add the PID in the Channels.cfg, like this.
```
[[Channels]]
1='/ifindex=1      1       11	1010,1011,1012,1013,1019'
```

install
-------
- build dvblast and tsdecript from source 
- Test dvblast and tsdecript before running this script (look for example at the github of dvblast and tsdecript)
- Install python 2.7 on all devices.
- Install python-psutil 2.2.0 on the client device(s).
- Download the scripts from the website
- Edit the config files to your configuration.
- create a playlist to your configuration. (see playlist.m3u as an explanation)
(there is no need for decripting in tvheadend 3.9)
- For tvheadend use the "m3u2hts" script to import the channels and muxes. 
https://github.com/grudolf/m3u2hts edit the script if nesessry.

Usage
-----
- start the anneke_server first
- start the anneke_worker(s) as sudo (because of dvblast rights)
- start tvheadend or other watched processes 
- start the anneke_client(s) as sudo (because of psutil)

Tips
----
- start with a smal configuration and expand if it is working.
- create or edit a service for the anneke_client.
- If the decriptworker and dvbworker run on the same device use the loopback network interface. (option /ifindex=0 in the Chanels.cfg)
- In tvheadend 3.9 set the "max input streams" to a number like 5. else tvheadend wil open ALL channels at startup.
- Without the dvblast "-u" or "--budget-mode" option, the dvb device wil only output 2 or 3 channels
- run "./dvblast --help" and "./tsdecrypt --help" for all the options.



