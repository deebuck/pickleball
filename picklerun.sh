#!/bin/bash
# This is in support of the pickleball reservation system.
# To enable a pickle reservation to be run from crontab on
# tarragon, this script will be put into /usr/local/bin.
# The intention is that the script be invoked under user dee. 
DEBUG=1
debug() {
    [[ -z "$DEBUG" ]] | echo "$@"
}
picklerun(){
    debug "cd pickle environment"
    cd /home/dee/pickle-environment
    debug "sourcing activate"
    source venv/bin/activate
    debug "cd git pickleball" 
    cd /home/dee/git/pickleball
    debug "running the pickle script" 
    python3 liz5.py $@
    debug "deactivating the environment"
    deactivate
    debug "done, returning"
}
LOG=/tmp/picklerun
echo "Pickle Run with $@" >$LOG 2>&1
picklerun $@ >> $LOG 2>&1
