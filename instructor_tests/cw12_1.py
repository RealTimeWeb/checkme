
from difflib import get_close_matches

if "get_forecasts(" not in __CODE:
    print "You are not currently calling get_forecasts"
elif "average" not in locals():
    print "The variable 'average' was not defined!"
    print "Potential variables in your source code:", ", ".join(get_close_matches("average", locals()))
elif __OUTPUT.strip() == "52":
    print "Everything looks correct from here!"
else:
    print "You do not have the right output."