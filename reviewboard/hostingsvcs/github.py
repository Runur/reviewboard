from django.utils import simplejson
from reviewboard.hostingsvcs.errors import AuthorizationError
                                 '%(github_public_repo_name)s/issues#issue/%%s',
    supports_bug_trackers = True
    API_URL = 'https://api.github.com/'
    def authorize(self, username, password, local_site_name=None,
                  *args, **kwargs):
                url=self.API_URL + 'authorizations',
                body=simplejson.dumps({
                    'scopes': [
                        'user',
                        'repo',
                    ],
                    'note': 'Access for Review Board',
                    'note_url': site_url,
                }))
                rsp = simplejson.loads(data)
        if plan == 'public':
            repo_name = repository.extra_data['github_public_repo_name']
        elif plan == 'private':
            repo_name = repository.extra_data['github_private_repo_name']
            owner = self.account.username
        elif plan == 'public-org':
            repo_name = repository.extra_data['github_public_org_repo_name']
            owner = repository.extra_data['github_public_org_name']
        elif plan == 'private-org':
            repo_name = repository.extra_data['github_private_org_repo_name']
            owner = repository.extra_data['github_private_org_name']

        return '%srepos/%s/%s/' % (self.API_URL, owner, repo_name)