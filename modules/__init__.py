# import os
# for name in os.listdir("plugins"):
#     if name.endswith(".py"):
#           #strip the extension
#          module = name[:-3]
#          # set the module name in the current global name space:
#          globals()[module] = __import__(os.path.join("plugins", name)