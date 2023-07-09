$location = Read-Host "Please enter location, Cherry or Cavalier"
$session = Read-Host "Please enter session, e.g. 30.185"
python3 liz5.py -l $location -s $session --dry-run --width 1200 --height 1200 --immediate > picklejuice.txt
#| TeeObject -FilePath \\.\CON > /Users/dee/Downloads/picklejuice.txt 
