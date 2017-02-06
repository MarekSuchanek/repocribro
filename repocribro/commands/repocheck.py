import flask
import flask_script


class RepocheckCommand(flask_script.Command):
    """Perform check procedure of repository events"""

    #: CLI command options for repocheck
    option_list = (
        flask_script.Option('--name', '-n', dest='full_name'),
    )

    def run(self, full_name=None):
        """Run the repocheck command to check repo(s) new events

        Obviously this procedure can check events only on public
        repositories. If name of repository is not specified, then
        procedure will be called on all registered public repositories
        in DB.

        :param full_name: Name of repository to be checked (if None -> all)
        :type full_name: str
        :raises SystemExit: If repository with given full_name does not exist
        """
        from ..database import db
        from ..models import Repository
        repos = []
        if full_name is None:
            print('Performing repository check on all public repositories')
            repos = db.session.query(Repository).filter_by(
                private=False
            ).all()
        else:
            print('Performing repository check on repository '+full_name)
            repo = db.session.query(Repository).filter_by(
                full_name=full_name
            ).first()
            if repo is None:
                print('Repository not found!')
                exit(1)
            repos.append(repo)
        for repo in repos:
            self._do_check(repo)

    def _do_check(self, repo):
        """Perform single repository check for new events

        :param repo: Repository to be checked
        :type repo: ``repocribro.models.Repository``
        :todo: Handle pagination of GitHub events

        :raises SystemExit: if GitHub API request fails
        """
        from repocribro.repocribro import make_githup_api
        github = make_githup_api(flask.current_app.iniconfig)
        gh_repo = github.get('/repos/{}'.format(repo.full_name))
        if gh_repo.status_code != 200:
            print('GitHub doesn\'t know about that repo: {}'.format(
                gh_repo.json()['message']
            ))
            exit(3)
        gh_events = github.get('/repos/{}/events'.format(repo.full_name))
        for event in gh_events.json():
            new = self._process_event(repo, event)
            if not new:
                break

    def _process_event(self, repo, event):
        """Process potentially new event for repository

        :param repo: Repository related to event
        :type repo: ``repocribro.models.Repository``
        :param event: GitHub event data
        :type event: dict
        :return: If the event was new or already registered before
        :rtype: bool

        :todo: Implement processing the event (check if new and add)
        """
        return False
