$if(episode)$
# $episode$
$endif$
$if(flashback)$
**In a flashback to $date$** $body$
$endif$
$if(return)$
**In the 1988 interview** $body$
$endif$
$if(new)$
$if(exact_date)$
**On $date$** $body$ 
$else$ 
**In $date$** $body$ 
$endif$
$endif$
$if(that_day)$
**Later that day** $body$ 
$endif$
$if(next_day)$
**The following day** $body$
$endif$
$if(that_week)$
**A few days later** $body$
$endif$
$if(continue)$
$body$
$endif$

