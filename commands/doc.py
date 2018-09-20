"""a karambot pydoc interface.
"""

import pydoc
import contextlib
import io

MSG_APOLOGY = '''Sorry {user}, I got nothing for "{text}".

I'll do a keyword search for "{text}" if you add -k before {text}.

Try "topics" or "modules" for more general help.
'''

MSG_FOUNDIT = '''Good news {user}, I found the following about {text}:
```
{result}
```
'''


MSG_HELP = '''
pydoc [-k keyword] [module_path_or_topic|topics|modules|help]

You can use pydoc to look up all sorts of pythonic things!

Use this to get the docstring for a module:

    pydoc list

Or do a keyword search to get a list of modules that match:

    pydoc -k keyword

Get a list of modules:

    pydoc modules

A list of python language topics, super interesting:

    pydoc topics

And information about the specific listed topics:

    pydoc LOOPING

'''

def doc_command(**kwargs: dict) -> str:
    '''Browse and search python documentation, "pydoc help"
    '''
    user, text = kwargs.get('user'), kwargs.get('text')

    if len(text) == 0 or text.lower() == 'help':
        return MSG_HELP

    apropos = '-k' in text
    
    if '-' in text and not apropos: # weed out switches that aren't -k
        return MSG_HELP

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        if apropos:
            pydoc.apropos(text.partition('-k')[-1])
        else:
            help(text)
    result = output.getvalue()

    if result.startswith('No'):
        return MSG_APOLOGY.format(user=user, text=text)
    
    return MSG_FOUNDIT.format(user=user, text=text, result=result)

if __name__ == '__main__':
    import sys

    kwargs = { 'user': 'Erik',
               'channel': '#unix',
               'text':' '.join(sys.argv[1:])}
    
    print(doc_command(**kwargs))
