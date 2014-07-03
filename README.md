Anneke
======

Ondemand dvblast with decription to iptv as backhand for tvheadend or mythtv

Working progress, this is the first working code.
Feel free to translate to English or correct my orthography

the idea is: that anneke_client whats for tvheadend or mythtv (backhand not tested) a udp (IPTV) port to open.
the client sends it to the anneke_server.
the anneke_server looks which "dvbworkers" and "decripters" are connected andfree. (or dvbworkers how has the frequency open)
the anneke_server sends to the dvbworker to open a frequency. (the dvblastoptions (like the frequency) and the dvblast config file)
the anneke_worker runs the dvblast command and dvblast streams the iptv directly to tvheadend mythtv. 
TODO: or to a decripter running tsdecript (can be running at a other server))

See the config file for more information. tip test it first with dvblast and tsdecript
