<?php
function dossh($session,$location) {
    shell_exec("picklerelay -z -v -s $session -l $location -d");
}
$court=filter_input(INPUT_POST,'Court');
$duration=filter_input(INPUT_POST,'Duration');
$start=filter_input(INPUT_POST,'Start');
$submit=filter_input(INPUT_POST,'Submit');
$dryrun=filter_input(INPUT_POST,'Dryrun');

$dayaftertomorrow=(new DateTime('now', new DateTimeZone('America/New_York')))->add(new DateInterval("P2D")); 
$sdate = $dayaftertomorrow->format("D, d M Y");

if (isset($court) and isset($duration) and isset($start) and $submit=="Reserve") 
   {
   $session=$duration.".".$start;
   dossh($session,$court);   
   }
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>The Pickle Controller</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <style>
      body{background-image:url("Pickleman.png");
	   background-color:rgba(0,0,0,0.2);
	   background-blend-mode:lighten}
      h1{text-align:center}
      h2{text-align:center}
      #pickleform {text-align:center;padding="10px";margin:"30px"}
      .entries {margin-top:10px;margin-bottom:2px;}
    </style>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js" type="text/javascript"></script>
    <script>
      function showduration(){d=$('#duration-select').value();alert(d)}
    </script>
    <H1>Cornichon Central</H1>
    <H2>Make a pickleball reservation for <?php echo "$sdate"?></H2>
    <div id="pickleform">
      <form method="post">
        <div class="entries">
	  <span class="stub">Choose Courts, most desirable first:</span>
	  <select name="Court" id="court-select">
		<option value="">Court Selector</option>
		<option value="Cherry">Cherry Street Tennis #1</option>
		<option value="Cherry">Cherry Street Tennis #2</option>
		<option value="Cherry">Cherry Street Pickleball #1</option>
		<option value="Cherry">Cherry Street Pickleball #2</option>
		<option value="Cherry">Cherry Street Pickleball #3</option>
		<option value="Cherry">Cherry Street Pickleball #4</option>
		<option value="Cavalier">Cavalier Trail Tennis #1</option>
		<option value="Cavalier">Cavalier Trail Tennis #2</option>
		<option value="Cavalier">Cavalier Trail Pickleball #1</option>
		<option value="Cavalier">Cavalier Trail Pickleball #2</option>
		<option value="Cavalier">Cavalier Trail Pickleball #3</option>
		<option value="Cavalier">Cavalier Trail Pickleball #4</option>
	  </select>
	</div>
	<div class="entries" id="add-court">
		<input type="submit" name="Add" value="Add" id="addb"></input>
		<input type="submit" name="Done" value="Done" id="doneb"></input>
	</div>
	<div class="entries" id="durations" style="display:none">
	  <span class="stub">Duration:</span>
	  <select name="Duration" id="duration-select">
	    <option value="">Select duration</option>
	    <option value="10">1.0</option>
	    <option value="15">1.5</option>
	    <option value="20">2.0</option>
	    <option value="25">2.5</option>
	    <option value="30">3.0</option>
	  </select>
	</div>
	<div class="entries" id="starttimes" style="display:none">
	  <span class="stub">Start Time:</span>
	  <select name="Start" id="start-select">
	    <option value="">Choose start time</option>
	    <option value="0800" class="10 15 20 30">     8:00 am</option>    
	    <option value="0830" class="10 20 25">        8:30 am</option>
		<option value="0900" class="10 20">           9:00 am</option>
	    <option value="0930" class="15 20 25 30">     9:30 am</option>        
	    <option value="1000" class="10 20">          10:00 am</option>
	    <option value="1030" class="10 20">          10:30 am</option>
		<option value="1100" class="10 15 20 25 30"> 11:00 am</option>
	    <option value="1130" class="10 20 25">       11:30 am</option>
		<option value="1200" class="10 20">          12:00 am</option>
	    <option value="1230" class="10 15 20 25 30"> 12:30 am</option>    
	    <option value="1300" class="10 20 25">        1:00 pm</option>
		<option value="1330" class="15 20 25">        1:30 pm</option>    
	    <option value="1400" class="10 20 15 25 30">  2:00 pm</option>       
		<option value="1430" class="15 20 25">        2:30 pm</option>    
	    <option value="1500" class="10 20">           3:00 pm</option>
	    <option value="1530" class="15 25 30">        3:30 pm</option>        
	    <option value="1600" class="10 20 25">        4:00 pm</option>          
		<option value="1630" class="15 20 25">        4:30 pm</option>    
	    <option value="1700" class="10 15 20 25 30">  5:00 pm</option>        
		<option value="1730" class="15 20 25">        5:30 pm</option>    
	    <option value="1800" class="10 20">           6:00 pm</option>
	    <option value="1830" class="15 25 30">        6:30 pm</option>         
	    <option value="1900" class="10 20 25">        7:00 pm</option>
		<option value="1930" class="15 20 25">        7:30 pm</option>    
	    <option value="2000" class="10 15 20">        8:00 pm</option>        
		<option value="2030" class="10 20">           8:30 pm</option>    
	    <option value="2100" class="10">              9:00 pm</option>
	  </select>
	</div>
	<div class="entries" id="submit" style="display:none">
	  <label for="drcheck">Dry Run?</label>
	  <input type="checkbox" name="Dryrun" id="drb" value="1"></input>
	  <input type="submit" name="Submit" value="Reserve" id="submitb"></input>
	</div>
      </form>
    </div>
    <script>$(function(){
	$('#court-select').change(
		function(){
		   $('#durations').show();
		});
	$('#duration-select').change(
		function(){
		   d="."+$('#duration-select').val();
		   console.log("duration:"+d);
		   $('#start-select option').not(d).remove()
		   $('#starttimes').show();
		});
	$('#start-select').change(
		function(){
		   $('#submit').show();
		});
	})</script>    
  </body>
</html>
