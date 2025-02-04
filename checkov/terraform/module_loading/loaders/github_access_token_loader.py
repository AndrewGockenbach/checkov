import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GithubAccessTokenLoader(GenericGitLoader):
    def discover(self):
        self.module_source_prefix = "github.com"
        self.username = "x-access-token"
        self.token = os.getenv('GITHUB_PAT', '')

    def _is_matching_loader(self) -> bool:
        if self.token:
            # if GITHUB_PAT is set and previous loaders failed, convert source (github ssh or github http or generic git)
            # to use the token in generic format git::https://x-access-token:<token>@github.com/org/repo.git
            self.logger.debug("GITHUB_PAT found. Attempting to clone module using HTTP basic authentication.")
            # if module_source = github.com/org/repo
            if self.module_source.startswith(self.module_source_prefix):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source}"
                return True
            # if module_source = git::https://github.com/org/repo.git
            if self.module_source.startswith(f"git::https://{self.module_source_prefix}"):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source.split('git::https://')[1]}"
                return True
            # if module_source = git@github.com:org/repo.git
            if self.module_source.startswith(f"git@{self.module_source_prefix}:"):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source.split('git@')[1].replace(':', '/')}"
                return True
            # if module_source = git::ssh://git@github.com/org/repo.git
            if self.module_source.startswith(f"git::ssh://git@{self.module_source_prefix}"):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source.split('git::ssh://git@')[1]}"
                return True

        return False


loader = GithubAccessTokenLoader()
