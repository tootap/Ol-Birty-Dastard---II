# Autosend data when connecting to internet
# Setup ssh key first
sleep 300

while [ 0 ]; do
    ping -c 2 www.geirland.org

    if [[ $? == 0 ]]; then
        fn=$(ls -tc | head -n2 | tail -n1)
        cp $fn $fn.bakp
        scp $fn.bakp geirland.org:/home/nick/web/mhacksdata.json
    else
        sleep 1
    fi
done 
