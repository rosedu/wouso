import subprocess

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.dumpdata import Command as DumpdataCommand
from optparse import make_option
from wouso.core.magic.utils import setup_magic
from wouso.core.scoring import check_setup, setup_scoring
from wouso.core.user.models import update_display_name, Player
from wouso.core.user.utils import setup_user_groups, setup_staff_groups


def update_all_display_names():
    qs = Player.objects.all()
    for u in qs:
        update_display_name(u)
    print 'Updated ', qs.count(), 'players.'


class Command(BaseCommand):
    args = '[--check-setup|--setup|--save|--load]'
    help = 'Wouso management tasks'
    option_list = DumpdataCommand.option_list + (
        make_option('--check-setup',
                    action='store_true',
                    dest='check_setup',
                    default=False,
                    help='Check the current instance for scoring, artifacts and other running requirements.'
                    ),
        make_option('--setup',
                    action='store_true',
                    dest='setup',
                    default=False,
                    help='Setup the current instance, including a syncdb.'
                    ),
        make_option('--noinput',
                    action='store_true',
                    dest='noinput',
                    default=False,
                    help='Don\'t ask for input'
                    ),
        make_option('--load',
                    action='store',
                    dest='load',
                    default=False,
                    help='Load game configuration.'
                    ),
        make_option('--save',
                    action='store',
                    dest='save',
                    default=False,
                    help='Save game configuration to a file.'
                    ),
        make_option('--reset',
                    action='store_true',
                    dest='reset',
                    default=False,
                    help='Reset scoring and artifacts'
                    ),
        make_option('--update-display',
                    action='store_true',
                    dest='updatedisplay',
                    default=False,
                    help='Update display names according to config'
                    ),
    )

    def handle(self, *args, **options):
        save_load_labels = ['magic', 'scoring.coin', 'scoring.formula', 'config', 'pages', 'user.race', 'user.playergroup']
        reset_labels = ['magic', 'scoring', 'config', 'pages']
        if options['check_setup']:
            ok = True
            # Check scoring
            if not check_setup():
                self.stdout.write('FAIL: Scoring module not setup.')
                ok = False

            if ok:
                self.stdout.write('OK.\n')

        elif options['setup']:
            if options['noinput']:
                # YOLO: call_command does not work if I call the syncdb command
                # with the 'all' parameter, so we use subprocess
                subprocess.call(['python', 'manage.py', 'syncdb', '--all',
                                 '--noinput'])
            else:
                subprocess.call(['python', 'manage.py', 'syncdb', '--all'])
            call_command('migrate', fake=True)

            self.stdout.write('Setting up scoring...')
            setup_scoring()
            self.stdout.write('\n')
            self.stdout.write('Setting up user groups...')
            setup_user_groups()
            setup_staff_groups()
            self.stdout.write('\n')
            self.stdout.write('Setting up magic...')
            setup_magic()
            self.stdout.write('\n')
            self.stdout.write('Done.\n')

        elif options['save']:
            c = DumpdataCommand()
            with open(options['save'], 'w') as fout:
                data = c.handle(*save_load_labels, **options)
                fout.write(data)
            self.stdout.write('Saved!\n')

        elif options['load']:
            call_command('loaddata', options['load'])
            self.stdout.write('Loaded!\n')

        elif options['reset']:
            call_command('sqlreset', *reset_labels)

        elif options['updatedisplay']:
            update_all_display_names()

        else:
            self.print_help('wousoctl', '')
