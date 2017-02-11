import iso8601
import flask
import flask_script
import pytz
from werkzeug.exceptions import HTTPException


class RepocheckCommand(flask_script.Command):
    """Perform check procedure of repository events"""
    event2webhook = {
        'PushEvent': 'push',
        'ReleaseEvent': 'release',
        'RepositoryEvent': 'repository',
    }

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
        from ..models import Repository
        self.db = flask.current_app.container.get('db')
        self.gh_api = flask.current_app.container.get('gh_api')

        ext_master = flask.current_app.container.get('ext_master')

        hooks_list = ext_master.call('get_gh_event_processors', default={})
        self.hooks = {}
        for ext_hooks in hooks_list:
            for hook_event in ext_hooks:
                if hook_event not in self.hooks:
                    self.hooks[hook_event] = []
                self.hooks[hook_event].extend(ext_hooks[hook_event])

        repos = []
        if full_name is None:
            print('Performing repository check on all public repositories')
            repos = self.db.session.query(Repository).filter_by(
                private=False
            ).all()
        else:
            print('Performing repository check on repository '+full_name)
            repo = self.db.session.query(Repository).filter_by(
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
        gh_repo = self.gh_api.get('/repos/{}'.format(repo.full_name))
        if gh_repo.status_code != 200:
            print('GitHub doesn\'t know about that repo: {}'.format(
                gh_repo.json()['message']
            ))
            exit(3)
        gh_events = self.gh_api.get('/repos/{}/events'.format(repo.full_name))
        if gh_events.status_code != 200:
            print('GitHub doesn\'t returned events for: {}'.format(
                repo.full_name
            ))
            return
        for event in gh_events.json():
            new = self._process_event(repo, event)
            if not new:
                break
        repo.events_updated()
        self.db.session.commit()

    def _process_event(self, repo, event):
        """Process potentially new event for repository

        :param repo: Repository related to event
        :type repo: ``repocribro.models.Repository``
        :param event: GitHub event data
        :type event: dict
        :return: If the event was new or already registered before
        :rtype: bool
        """
        last = pytz.utc.localize(repo.last_event)
        if iso8601.parse_date(event['created_at']) <= last:
            return False
        hook_type = self.event2webhook.get(event['type'], 'uknown')
        for event_processor in self.hooks.get(hook_type, []):
            try:
                event_processor(db=self.db, repo=repo,
                                payload=event['payload'],
                                actor=event['actor'])
                print('Processed {} from {} event for {}'.format(
                    event['type'], event['created_at'], repo.full_name
                ))
            except HTTPException:
                print('Error while processing #{}'.format(event['id']))
        return True
