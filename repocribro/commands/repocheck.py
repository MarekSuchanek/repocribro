import flask
import flask_script


class RepocheckCommand(flask_script.Command):
    """Perform check procedure of repository events"""

    option_list = (
        flask_script.Option('--name', '-n', dest='full_name'),
    )

    def run(self, full_name=None):
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
        from repocribro.repocribro import make_githup_api
        github = make_githup_api(flask.current_app.iniconfig)
        gh_repo = github.get('/repos/{}'.format(repo.full_name))
        if gh_repo.status_code != 200:
            print('GitHub doesn\'t know about that repo: {}'.format(
                gh_repo.json()['message']
            ))
            exit(3)
        # TODO: handle pagination
        gh_events = github.get('/repos/{}/events'.format(repo.full_name))
        for event in gh_events.json():
            new = self._process_event(repo, event)
            if not new:
                break

    def _process_event(self, repo, event):
        # TODO: check if new event or already registered
        # TODO: implement processing event
        pass
