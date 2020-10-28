#!/usr/bin/env python3

import json

import urllib3
from blessings import Terminal
from github import Github

from utils import get_env_var, timestamped_print

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
print = timestamped_print


def main():
    """Deletes the branch protection rules for a branch (with prefix 'contrib/') after it has been deleted.

    Specifically, when we create an internal PR from a merged external PR, and the base branch of the external
    PR now becames the head branch of the internal PR - we remove the branch protections of that 'contrib/'-prefixed
    branch so that our developers can push to the branch (and because the CLA does not need signing by our developers).
    What this does though, is create a branch protection rule specific to the 'contrib/'-prefixed branch in question.
    Once the contrib branch has been deleted (on merge of the internal PR to master), there is no longer a need for
    the branch protection rule that applied to that branch and therefore the rule needs to be cleaned up (deleted). 

    Performs the following operations:
    1. If the external PR's base branch is master we create a new branch and set it as the base branch of the PR.
    2. Labels the PR with the "Contribution" label. (Adds the "Hackathon" label where applicable.)
    3. Assigns a Reviewer.
    4. Creates a welcome comment

    Will use the following env vars:
    - CONTENTBOT_GH_ADMIN_TOKEN: token to use to update the PR
    - EVENT_PAYLOAD: json data from the pull_request event
    """
    t = Terminal()
    payload_str = get_env_var('EVENT_PAYLOAD')
    if not payload_str:
        raise ValueError('EVENT_PAYLOAD env variable not set or empty')
    payload = json.loads(payload_str)
    print(f'{t.cyan}Processing PR started{t.normal}')
    print(f'{t.cyan}event payload: {payload}{t.normal}')

    org_name = 'avidan-H'
    repo_name = 'content'
    gh = Github(get_env_var('CONTENTBOT_GH_ADMIN_TOKEN'), verify=False)
    content_repo = gh.get_repo(f'{org_name}/{repo_name}')
    branch_ref = payload.get('ref', {})
    branch = content_repo.get_branch(branch_ref)
    branch_protection = branch.get_protection()
    print(f'{branch_protection=}')
    branch.remove_protection()
    branch_protection = branch.get_protection()
    print(f'{branch_protection=}')


if __name__ == "__main__":
    main()
