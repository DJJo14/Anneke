Anneke
======

Ondemand dvblast with decription to iptv as backhand for tvheadend or mythtv

Working progress, this is the first working code.
Feel free to translate to English or correct my orthography

the idea is:
- that anneke_client whats for tvheadend or mythtv (backhand not tested) a udp (IPTV) port to open.
- the client sends it to the anneke_server.
- the anneke_server looks which "dvbworkers" and "decripters" are connected andfree. (or dvbworkers how has the frequency open)
- the anneke_server sends to the dvbworker to open a frequency. (the dvblastoptions (like the frequency) and the dvblast config file)
- the anneke_dvbworker runs the dvblast command and dvblast streams the iptv to decripterworker
- the anneke_drecrptworker runs the tsdecript command and tsdecript streams the iptv to directly to tvheadend mythtv. 
because of time out it only works with one drecrpt

See the config file for more information. 

tip: test it first with dvblast and tsdecript before running this script
