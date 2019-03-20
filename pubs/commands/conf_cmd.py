from __future__ import unicode_literals

from .. import uis
from .. import config
from .. import content


def parser(subparsers, conf):
    parser = subparsers.add_parser('conf',
            help='open the configuration in an editor')
    return parser


def command(conf, args):
    uis.init_ui(conf)
    ui = uis.get_ui()

    while True:
        # get modif from user
        ui.edit_file(conf.filename, temporary=False)

        new_conf = config.load_conf(path=conf.filename)
        try:
            config.check_conf(new_conf)
            ui.message('The configuration file was updated.')
            break
        except AssertionError as e: # TODO better error message
            ui.error('Error reading the modified configuration file [' + str(e) + '].')
            options = ['edit_again', 'abort']
            choice = options[ui.input_choice(
                options, ['e', 'a'],
                question=('Edit again or abort? If you abort, the changes will be reverted.')
                )]

            if choice == 'abort':
                config.save_conf(conf)
                ui.message('The changes have been reverted.')
                break
