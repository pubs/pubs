# install command

# Probably useless if setup.py is provided

#import shutil
# def parser(subparsers, config):
#     parser = subparsers.add_parser('install', help="install papers on the system")
#     return parser
#
# def command():
#     """Install command on the system"""
#     print '{}file to install : {}{}{}'.format(grey, cyan, __file__, end)
#     default = '/usr/local/bin'
#     print "{}folder to install the papers command [{}{:s}{}] : {}".format(grey, cyan, default, grey, end),
#     sys.stdout.flush()
#     path = raw_input()
#     if path == '':
#         path = default
#     if not os.path.exists(path):
#         print "{}error{}: {}{:s}{} does not exist - installation aborted".format(red, end, cyan, path, end)
#     else:
#         if os.path.exists(path+'/papers'):
#             if os.path.samefile(path+'/papers', __file__):
#                 return
#         shutil.copy(__file__, path)