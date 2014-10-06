'''
This python program can be used in two different ways:
    1) Drag and drop your python file (e.g., "cw12_1.py") onto this one.
    2) At the very start of your python file, put "import checkme". If you use
        this approach, you MUST have a copy of this "checkme.py" file in the
        same directory as your python file (e.g., "cw12_1.py"). Otherwise you
        will get an ImportError.
    
If you use the first approach (dragging and dropping), then checkme.py will try
to explain compile errors - for example, if you haven't closed a parenthesis or
you have incorrect indentation. The second approach is probably more convenient,
but it can only explain runtime errors - like when you try to reference an
uninitialized variable. If you are unsure what the difference is, read:
    http://pc.net/helpcenter/answers/compile_time_vs_runtime
'''
__version__ = '1'

HEADER = {'User-Agent': 
          'CORGIS checkme library for educational purposes'}

import inspect
import random
from os.path import splitext, basename, isfile
import sys
import re
import traceback
import json
from textwrap import fill
from types import ModuleType
from cStringIO import StringIO
from socket import error as socket_error
import errno

PYTHON_3 = sys.version_info >= (3, 0)

if PYTHON_3:
    from urllib.error import HTTPError, URLError
    import urllib.request as request
    from urllib.parse import quote_plus
else:
    from urllib2 import HTTPError, URLError
    import urllib2
    from urllib import quote_plus


def exit_with_explanation():
    print('''Error: No file was given!

This python program can be used in two different ways:
    1) Drag and drop your python file (e.g., "cw12_1.py") onto this one.
    2) At the very start of your python file, put "import checkme". If you use
        this approach, you MUST have a copy of this "checkme.py" file in the
        same directory as your python file (e.g., "cw12_1.py"). Otherwise you
        will get an ImportError.
    
If you use the first approach (dragging and dropping), then checkme.py will try
to explain compile errors - for example, if you haven't closed a parenthesis or
you have incorrect indentation. The second approach is probably more convenient,
but it can only explain runtime errors - like when you try to reference an
uninitialized variable. If you are unsure what the difference is, read:
    http://pc.net/helpcenter/answers/compile_time_vs_runtime

If you're seeing this error and you're not sure why, make sure that you've
actually dragged and dropped a file onto this script, in order to pass it in.
Then, ask an instructor.
''')
    raw_input("Press Enter to exit...")
    sys.exit()

IS_MAGIC_MODULE = False
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if isfile(sys.argv[1]):
            FULL_FILE_PATH = sys.argv[1]
        else:
            exit_with_explanation()
    else:
        exit_with_explanation()
elif len(inspect.stack()) > 1:
    if not inspect.stack()[1][1].startswith('<pyshell'):
        FULL_FILE_PATH = inspect.stack()[1][1]
    else:
        print "Functionality is incomplete"
        # This isn't working yet, keep playing with it.
        # This is being imported at the main level of the intepreter
        # Therefore, we will treat it as a BLACK MAGIC module!
        class module(ModuleType):
            def __getattr__(self, name):
                if name == "__path__":
                    return __path__
                else:
                    print "Tried to load", name
                    return "banana"
        old_module = sys.modules['checkme']
        new_module = sys.modules['checkme'] = module('checkme')
        new_module.__dict__.update({
            '__file__' : __file__,
            '__package__' : 'checkme',
            #'__path__' : __path__,
            '__doc__' : __doc__
            })
        IS_MAGIC_MODULE = True
else:
    exit_with_explanation()
   

ORIGINAL_FILE_PATH = basename(FULL_FILE_PATH)
ORIGINAL_FILE_NAME = splitext(ORIGINAL_FILE_PATH)[0]
IMPORT_CHECKME_REGEX = re.compile(r'^import checkme\s*$')

__all__ = ['test']

try:
    with open(FULL_FILE_PATH, "r") as STUDENT_FILE:
        student_code = []
        checkme_offset = 0
        for line in STUDENT_FILE:
            if IMPORT_CHECKME_REGEX.match(line):
                checkme_offset += 1
            else:
                student_code.append(line)
        student_code_joined = "".join(student_code)
except IOError, e:
    print(e)
    print("The checker is having a hard time opening your student file, for some reason.")
    
def explain_exception(exc_info):
    exception, message, tb = exc_info
    print "="*32, "Crash Report!", "="*33
    print("The following code failed to execute:")
    for _, line_number, name, _ in traceback.extract_tb(tb)[1:]:
        if name == '<module>':
            name = 'main code'
        else:
            name = 'function definition of '+name
        line_number = line_number
        print 'File "{}", line {}, in the {}'.format(
                ORIGINAL_FILE_NAME+'.py', line_number+checkme_offset, name
            )
        if line_number-3 > 0:
            print "\t..."
        for sample_line in student_code[line_number-3:line_number+2]:
            print "\t", sample_line.rstrip()
        if line_number+2 < len(student_code):
            print "\t..."
        print ""
    print "-"*80
    print("Reason:")
    print exception.__name__+":", message
    if exception.__name__ in EXTENDED_ERROR_EXPLANATION:
        print "-"*80
        print EXTENDED_ERROR_EXPLANATION[exception.__name__]
    print "="*28, "End of Crash Report!", "="*28
    
    
EXTENDED_ERROR_EXPLANATION = {
    'ParseError': '''Extended Error Explanation:
A parse error means that Python does not understand the syntax on the line the
error message points out.  Common examples are forgetting commas beteween
arguments or forgetting a : on a for statement.
    
Suggestion:
To fix a parse error you just need to look carefully at the line with the
error and possibly the line before it.  Make sure it conforms to all of
Python's rules.''',
    'TypeError': '''Extended Error Explanation:
Type errors most often occur when an expression tries to combine two objects
with types that should not be combined.  Like using "+" to add a number to a
list instead of ".append", or dividing a string by a number.

Suggestion:
To fix a type error you will most likely need to trace through your code and
make sure the variables have the types you expect them to have.  It may be
helpful to print out each variable along the way to be sure its value is what
you think it should be. The "type" function will be very useful here, as in
the following example:

my_age = 47
print(type(my_name))
# <type 'int'>

my_name = "Cory Bart"
print(type(my_name))
# <type 'str'>

my_favorite_colors = ["blue", "silver", "green"]
print(type(my_favorite_colors))
# <type 'list'>''',

    'SyntaxError': '''Extended Error Explanation:
This message indicates that Python can't figure out the syntax of a
particular statement.  Some examples are assigning to a literal, or a
function call.
    
Suggestion:
Check your assignment statements and make sure that the left hand side of
the assignment is a variable, not a literal (e.g., 7 or "hello") or a
function.''',
    
    'NameError': '''Extended Error Explanation:
A name error almost always means that you have used a variable before it has a
value.  Often this may be a simple typo, so check the spelling carefully.

Suggestion:
Check the right hand side of assignment statements and your function calls,
this is the most likely place for a NameError to be found. It really helps to
step through your code, one line at a time, mentally keeping track of your
variables. You could also use :
    http://www.pythontutor.com/visualize.html
''',
    
    'ValueError': '''Extended Error Explanation:
A ValueError most often occurs when you pass a parameter to a built-in
function, and the function is expecting one type and you pass something 
different. For instance, if you try to convert a non-numeric string to an
int, you will get a ValueError:

int("Corgi")
# ValueError: invalid literal for int() with base 10

Suggestion:
The error message gives you a pretty good hint about the name of the
function as well as the value that is incorrect.  Look at the error message
closely and then trace back to the variable containing the problematic value.
}''',

    'AttributeError': '''Extended Error Explanation:
This happens when you try to do something like

X.Y

This error message is telling you that the object on the left hand side of
the dot, does not have the attribute or method on the right hand side.
    
Suggestion:
The most common variant of this message is that the object undefined does not
have attribute X. This might be because you had a typo in the thing on the
right side. This tells you that the object on the left hand side of
the dot is not what you think. Trace the variable back and print it out in
various places until you discover where it becomes undefined.  Otherwise check
the attribute on the right hand side of the dot for a typo.''',

    'TokenError': '''Extended Error Explanation:
Most of the time this error indicates that you have forgotten a right
parenthesis or have forgotten to close a pair of quotes.

Suggestion:
Check each line of your program and make sure that your parenthesis are
balanced.''',

    'IndexError': '''Extended Error Explanation:
This message means that you are trying to index past the end of a string or
a list.  For example, if your list has 3 things in it and you try to access
the item at position 5.

Suggestion:
Remember that the first item in a list or string is at index position 0,
quite often this message comes about because you are off by one. 
Remember in a list of length 3 the last legal index is 2.

favorite_colors = ["red", "blue", "green"]
favorite_colors[2]
# prints green
favorite_color[3]
# raises an IndexError
''',

    'ImportError': '''Extended Error Explanation:
This error message indicates that you are trying to import a module that does
not exist, or is not in the same directory as your python script.

Suggestion:
One problem may simply be that you have a typo - remember, you must not
capitalize the module name. Another common problem is that you have placed the
module in a different directory. Finally, if you're using a special module,
then it might not be installed. Come ask an instructor on how to install new
modules if it's one that you must use!''',

    'ReferenceError': '''Extended Error Explanation:
This is a really hard error to get, so I'm not entirely sure what you did.

Suggestion:
Bring this code to the instructor.
''',

    'ZeroDivisionError': '''Extended Error Explanation:
This tells you that you are trying to divide by 0. Typically this is because
the value of the variable in the denominator of a division expression has
the value 0.

Suggestion:
You may need to protect against dividing by 0 with an if statment, or you
may need to rexamine your assumptions about the legal values of variables,
it could be an earlier statment that is unexpectedly assigning a value of
zero to the variable in question.''',

    'IndentationError': '''Extended Error Explanation:
This error occurs when you have not indented your code properly.  This is
most likely to happen as part of an if, for, while or def statement.

Suggestion:
Check your if, def, for, and while statements to be sure the lines are
properly indented beneath them.  Another source of this error comes from
copying and pasting code where you have accidentally left some bits of
code lying around that don't belong there anymore. Finally, a very sinister
possibility is that you have some tab characters in your code, which look
identical to four spaces. Never, ever use tabs, and carefully check code from
the internet to make sure it doesn't have tabs. Note: if you press the TAB
key, IDLE will smartly create 4 spaces instead of a tab character, so you
shouldn't have any problems there.''',

    'EOFError': '''Extended Error Explanation:
If you are using input() or raw_input() commands, then this error happens when
they don't get the right ending.

Suggestion:
It's hard to protect against users. However, if you're using input(), you
might be able to use raw_input() instead to avoid this problem.
''',

    'IOError': '''Extended Error Explanation:
This is a very easy error to get. The most common reason is that you were
trying to open a file and it wasn't in the right place. 

Suggestion:
Make sure that the file is in the right place - print out the file path, and
then check that it's definitely on your computer at that location. If you
need help doing file processing, you should probably check with an instructor.''',

    'KeyError': '''Extended Error Explanation:
A dictionary has a bunch of keys, but until a key is defined, you cannot
reference it. In fact, this is very similar to how a variable works. This
error is caused by you trying to refer to a key that does not exist.

Suggestion:
The most common reason you get this exception is that you have a typo in your
dictionary access. It is also possible that the key does not exist yet but
should. Use the .keys() function to find out the current keys in a dictionary.

weather = get_current_weather("Newark, DE")
print weather.keys()
# prints "temperature", "description", "humidity", ...''',
    
    'MemoryError': '''Extended Error Explanation:
Somehow, you have run out of memory. This is crazy hard to get, so consider
yourself impressive!

Suggestion:
Bring your code to an instructor.
''',
    
    'OSError': '''Extended Error Explanation:
It's hard to say what an OSError is without deep checking. Many things can
cause it.

Suggestion:
Bring your code to an instructor.
    
''',

}

print "="*33, "Your output", "="*34
glbls, lcls = {}, {}
old_stdout = sys.stdout
redirected_output = sys.stdout = StringIO()
try:
    exec(student_code_joined) in glbls, lcls
except Exception, e:
    sys.stdout = old_stdout
    explain_exception(sys.exc_info())
sys.stdout = old_stdout
print redirected_output.getvalue(),
print "="*31, "Instructor Tests", "="*31
lcls['__CODE'] = student_code_joined
lcls['__OUTPUT'] = redirected_output.getvalue()
    
def _get(url):
    """
    Internal method to convert a URL into it's response (a *str*).

    :param str url: the url to request a response from
    :returns: the *str* response
    """
    try:
        if PYTHON_3:
            req = request.Request(url, headers=HEADER)
            response = request.urlopen(req)
            return response.read().decode('utf-8')
        else:
            req = urllib2.Request(url, headers=HEADER)
            response = urllib2.urlopen(req)
            return response.read()
    except socket_error:
        print "There was a temporary internet or server error. Please try again in a little bit."
        sys.exit()
    except URLError, err:
        print "There was a connection error with the internet. Check your internet connection, and then try again. If it's still not working, check to make sure the internet is working."
        sys.exit()
    except HTTPError, err:
        if err.code == 404:
            print "For some reason, checkme could not access the right book website.\nPerhaps you are using an out-of-date version, or you do not have internet access."
        elif err.code == 301 or err.code == 302:
            print "You are using an out-of-date version of checkme.\nPlease download a new version from \n\thttp://think.cs.vt.edu/book/get_checkme/"
        elif err.code in (400, 401, 403):
            print "You had a bad request, an unauthorized request, or a forbidden request. That's strange. Please contact Cory Bart!"
        elif err.code in (408, 503, 504):
            print "The connection with the server timed out, probably because it's under heavy load. Take a minute to {}, and then try again.".format(random.choice(["grab a snickers", "pet a dog", "beat another level", "find a new subreddit", "tell someone you love them", "smell a flower", "do that thing you're forgetting about", "do another class' homework (by which I mean watch netflix)"]))
        elif err.code == 500:
            print "There was an internal server error (so it's not a problem with your code). This usually happens when a last minute edit was introduced into the system. Let Cory know what happened and he'll fix it."
        else:
            raise
        sys.exit()
        
result = _get('http://localhost:8080/check/'+ORIGINAL_FILE_NAME+"?version="+__version__)
glbls = {}
server_response = json.loads(result)
if server_response['success']:
    instructor_tests = server_response['output']
else:
    print(server_response['message'])
    sys.exit()
try:
    exec(instructor_tests) in glbls, lcls
except Exception, e:
    print "There was an error with the server code. Please report the following to Cory Bart"
    print e
    
sys.exit()