#!/usr/bin/perl -T
$ENV{PATH} = "/bin:/usr/bin";
use CGI::Carp qw(fatalsToBrowser);  #redirect all fatal error messages to the browser
# Xeoron's web-man version 0.3.1 beta 8/5/2004
# Project page here: http://linger.twisted-muse.org/~twilight
# Distributed under the GPL: http://www.gnu.org/copyleft/gpl.html
# Future features: 
# 	1) topic, and IP-address whitelisting/blacklisting.

#bug 1: If the man-data is many thousands of lines in length (~10534+), then characters are rendered crossed-out in GUI web-browsers (Mozilla, Opera, and IE tested). This seems to be some form of 'pre' tag buffer overflow.
#bug 2: topic 'xterm' renders twice with the 1st time line-wrapping as one line

my $v="0.4.1 beta";
my ($trLog, $tLogBool); 	# topic-request-log_name; topic-request-log
$tLogBool=1;  			# Turns on topic logging if >0
$trLog="wman_topicRequest.log";	# log filename
#my (@wlist, $whiteBool,@blist, $blackBool);    # whitelist, blacklist
#$whiteBool=0 $blackBool=0;     # 0 for off, 1 for on.



print "Content-type:text/html\n\n"; #CGI header
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
@pairs = split(/&/, $buffer);
foreach $pair (@pairs) {
    ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $FORM{$name} = $value;
}

$FORM{'topic'}=~s/(\;|\||\$|\%|\&|\*|\"|\'|\`|\,)//g; # remove any code-injection

#start generating html
print <<eof
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<!-- Project Web-man $v offical website is here:
 http://linger.twisted-muse.org/~twilight/projects/web-man.html
-->
<html lang="en">
 <head>
  <title>Web-Manpage: $FORM{'topic'} </title>
  <meta http-equiv="content-type" content="text/html;charset=iso-8859-1">
  <meta name="robots" content="NOINDEX, NOFOLLOW">
  <style type="text/css">
	<!--a:link{ text-decoration: none; color: #A13A13}
	 a:visited { text-decoration:none; color: #A13A13}
	 a:active {text-decoration: none; color: #FF0000}
	 a:hover{text-decoration: none;color: #FF0000}
	 body {background-color: #8098B0; padding-left: 0.8em; padding-right: 0.8em}-->
  </style>
 </head>
<body>
 <div>
  <form action="./man.cgi" method="POST">
   <span style="font-weight: bold">Enter man page request:</span>
   <input type="text" name="topic" size=16><input type="submit" value="Go">
  </form>
  <hr>
 </div>
eof
;

# The only allowed topics will be words that are alphanumeric, numbers, and 
# (a-zA-Z0-9). Dashes, periods, colons, (), digits, and spaces are also allowed; comas are not.
if ($FORM{'topic'}=~m/^([\w\-\.\s\d\:\,\(\)]+)$/) { $topic=$1; }  #/^([\w\-\.]+)$/
else { $topic = $FORM{'topic'}; }

sub aRLog{	# appendRequestLog
use Fcntl;
$trLog="wman_topicRequest.log";
 if ($tLogBool and !($trLog eq "")){
    $date=`date`; chomp $date;
    format ODATA =
IPs:@<<<<<<<<<<<<<<<< T:@<<<<<<<<<<<<<<<<<<<<<<<<<<<<< D:@<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$ENV{"REMOTE_ADDR"} $topic $date
.
    if (open (ODATA,">>$trLog")){ until (flock(ODATA,2)){ sleep .10;}
    }else { print " Error: Could not open the file $trLog\n"; return 0; }
    write(ODATA);
    flock(ODATA,8); close (ODATA);
    return 1;
 }
 return 0;
}#end aRLog

sub noData{ 	# exit from bad data
 $topic = "no topic provided" if ($topic eq "" or $topic=~m/^\s*$/);
print <<eof
 <div>
  <br><h2 style="padding-left:0.8em">$topic</h2>
  <br><big>U</big>nable to find information on this topic: <em style="font-weight:bold">$topic</em>.
 </div>
</body>\n</html>
eof
;
 aRLog if ($tLogBool); #log requests?
 exit; 
}#end of noData

noData if ($topic eq "" or $topic=~m/^\s*$/);	# end if empty

if ($topic eq "webman -bugs" or  $topic eq "wman"){		# bug info about web-man
 $topic="Known bugs are as followed--<br><ol style=\"color: #533B27\"><li>Bug 1: If the man-data is many thousands of lines in length (~10534+), then about 10534+ lines down characters are rendered crossed-out in GUI web-browsers (Mozilla, Opera, and IE tested). This seems to be some form of 'pre' tag buffer overflow.</li><li>Bug 2: Topic 'xterm' renders twice with the 1st time line-wrapping as one line.</li></ol><br>";
print <<eof
 <div>
  <br><h2 style="padding-left:0.8em">$topic</h2>
  <!--br><big>U</big>nable to find information on this topic: <em style="font-weight:bold">$topic</em>.-->
 </div>
</body>\n</html>
eof
;
 aRLog if ($tLogBool); #log requests?
 exit; 
}		


@out = `/usr/bin/man $topic`;	# grab man-page

if ($? > 0){				# if exit status failed
  my %es=(1=>'Usage, syntax or configuration file error.', 2=>'Operational error.', 3=>'A child process returned a non-zero exit status.', 16=>'At least one of the pages/files/keywords didn\'t exist or wasn\'t matched.');
  if ($?>16){$topic="'$topic' Man exit status ($?):<br>\n$es{16}";}
  else{$topic="'$topic' Man exit status ($?):<br>\n$es{$?}";}
  noData;
}

print "<table width=\"100%\" border=0 cellpadding=0 align=left>\n <tr><td>\n"; # start table struct
print "  <pre style=\"padding-left:0.9em\">\n<!--Start man-page topic: '$topic'-->\n";
# man pages are formatted with nroff, so we have to remove the
# nroff control characters from them with this substitution
my ($start, $end); 
 $start = shift @out; $start =~s/.\cH//g; $start=~s/\</&lt;/g; $start=~s/\>/&gt;/g;
 $end   = pop   @out; $end   =~s/.\cH//g; $end  =~s/\</&lt;/g; $end  =~s/\>/&gt;/g;

 print "<b>$start</b>";	# print header formatted

foreach $i (@out) { 	# remove nroff, bold stuff???, then print the line
	$i =~s/.\cH//g;
	#format < and > signs
	if ($i!=~m/^\s+$/){ $i=~s/\</&lt;/g;  $i=~s/\>/&gt;/g; }

	if ( $i eq "" or $i=~m/^\s*$/){print "\n";			#if empty
	}elsif($i =~m/^\s*([A-Z]|\d|\(\d+\)|\-|\#|\s)+$/) { 
		chomp $i; 
		if ($i eq "" or $i=~m/^\s+$/){ print "\n"; }    	# if now empty
		else {print "<b>$i</b>\n";}	    			# highlight sections
	}elsif($i =~s/(\s\-+(\[|\]|\w|\d|\+|\^|\=|\-)+)/<b>$1<\/b>/g){ 	# higlight most options 
		if ($i=~m/^\s*<b>\s*<\/b>\s*$/){ print "\n";}    	#strip out any bold tags on blank lines
		else{ print "$i"; }
	}else{print "$i";}
}
print "<b>$end</b>"; # print tail formatted

print <<eof
<!--End man-page topic: '$topic'-->
  </pre>
  <div style="text-align:center"><a href="#top" title="To the top">-^-</div>
 </td></tr>
 <tr><td>
  <div style="padding-left:0.8em"><hr>
   <form action="./man.cgi" method="POST">
    <span style="font-weight: bold">Enter man page request:</span> <input type="text" name="topic" size=16><input type="submit" value="Go">
   </form>
   <em>Generated by <a target=wm href="http://linger.twisted-muse.org/~twilight/projects/web-man.html" title="About Web-man">Web-man</a> version $v</em>
  </div>
 </td></tr>
</table>
</body>
</html>
eof
;
##### END OF CGI PUSHING CONTENT TO A BROWSER

aRLog if ($tLogBool); #log requests?

1;
