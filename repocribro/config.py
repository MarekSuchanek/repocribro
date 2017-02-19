import configparser
import os


class Config(configparser.ConfigParser):
    """Repocribro app configuration container"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mandatory = {}

    @property
    def default(self):
        """Access defaults as property

        :return: Default configuration options
        :rtype: dict
        """
        return self.defaults()

    def check(self):
        """Check and correct missing mandatory options and sections

        :return: List of errors (string with section and option)
        :rtype: list of str
        """
        errors = []
        for section in self.mandatory:
            if not self.has_section(section):
                errors.append('section: ' + section)
                continue
            for var in self.mandatory[section]:
                if not self.has_option(section, var):
                    errors.append('section: ' + section + ', option: ' + var)
        return errors

    def read_env(self, section, option, env_name):
        """Shorthand for reading ENV variable into config

        :param section: Target config section
        :type section: str
        :param option: Target config option
        :type option: str
        :param env_name: Name of ENV variable
        :type env_name: str
        """
        if env_name in os.environ:
            self.set(section, option, os.environ[env_name])

    def read_envs(self, prefix):
        """Shorthand for reading ENV variables with given prefix into config

        This will load all ENV variables with given prefix, the section name
        is after prefix and next underscore so section name can not contain
        undercore. For example ``REPOCRIBRO_FLASK_SECRET_KEY`` will be loaded
        to section ``FLASK`` and option ``SECRET_KEY`` (``REPOCRIBRO`` is
        the prefix).

        :param prefix: ENV variable name prefix
        :type prefix: str
        """
        for key in os.environ:
            if key.startswith(prefix + '_'):
                parts = key.split('_')
                if len(parts) > 2:
                    if not self.has_section(parts[1]):
                        self.add_section(parts[1])
                    self.set(
                        parts[1],
                        '_'.join(parts[2:]),
                        os.environ[key]
                    )

    def update_flask_cfg(self, app):
        """All options from flask section will be inserted to config of the
        given Flask app

        :param app: Flask application to be configured
        :type app: ``flask.Flask``
        """
        for key, value in self.items('flask'):
            app.config[key.upper()] = value

    def mark_mandatory(self, section, option):
        """Mark some option within section as mandatory

        :param section: Section with mandatory option
        :type section: str
        :param option: Option to be mandatory
        :type option: str
        """
        section = section.lower()
        option = option.lower()
        self.mandatory[section] = self.mandatory.get(section, set())
        self.mandatory[section].add(option)


def create_config(cfg_files, env_prefix='REPOCRIBRO'):
    """Factory for making Repocribro config object

    :param cfg_files: Single or more config file(s)
    :return: Constructed config object
    :rtype: ``repocribro.config.Config``
    """
    config = Config()
    config.read(cfg_files)
    config.mark_mandatory('flask', 'secret_key')
    config.mark_mandatory('flask', 'SQLALCHEMY_DATABASE_URI')
    config.default['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
    config.read_envs(env_prefix)
    return config


def check_config(config, exit_code=1):
    """Procedure for checking mandatory config

    If there are some missing mandatory configurations this
    procedure prints info on stderr and exits program with
    specified exit code.

    :param config: Configuration object
    :type config: ``repocribro.config.Config``
    :param exit_code: Exit code on fail
    :type exit_code: int
    :raises: SystemExit
    """
    import sys
    config_errors = config.check()
    if len(config_errors) == 0:
        return
    print('Missing configuration:', file=sys.stderr)
    for err in config_errors:
        print('-> ' + err, file=sys.stderr)
    sys.exit(exit_code)
