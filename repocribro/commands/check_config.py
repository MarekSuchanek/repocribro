import flask
import flask_script


class CheckConfigCommand(flask_script.Command):
    """Check actual configuration used by repocribro"""

    #: CLI command options for check-config
    option_list = (
        flask_script.Option('--style', '-s', dest='style', default='cfg',
                            help='Print style "triple" or "cfg"'),
    )

    def run(self, style):
        """Run the check-config command with given options in
        order to find out currently used configuration

        :param style: Printing style name for config
        :type style: str
        """
        config = flask.current_app.container.get('config')
        if style.lower() == 'triple':
            for section in config.sections():
                for (key, value) in config.items(section):
                    print(section, key, value)
        else:
            for section in config.sections():
                print('[{}]'.format(section))
                for (key, value) in config.items(section):
                    print('{} = {}'.format(key, value))
