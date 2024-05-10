
def pretty_print(msg):
    print(f"My msg is: '{msg}'")

def load_ipython_extension(ipython):
    ipython.register_magic_function(pretty_print, 'line')


"""
https://ipython.readthedocs.io/en/stable/config/custommagics.html
def cellmagic(line, cell):
    pass

"""

