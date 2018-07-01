import click
import flask
import flask.cli


def _check_config(style):
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


@click.command()
@click.option('-s', '--style', default='cfg',
              help='Print style "triple" or "cfg"')
@flask.cli.with_appcontext
def check_config(style):
    """Check actual configuration used by repocribro

    Run the check-config command with given options in
    order to find out currently used configuration

    :param style: Printing style name for config
    :type style: str
    """
    _check_config(style)
