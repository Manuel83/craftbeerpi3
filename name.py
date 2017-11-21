import re

recipe_name = "Manuel 8881881  18181 "
print re.match("^[\sA-Za-z0-9_-]*$", recipe_name)