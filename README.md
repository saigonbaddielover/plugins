# saigonbaddielover plugins

Canonical public plugin catalog for Claude Code and Codex.

## Install

Claude Code:

~~~
/plugin marketplace add saigonbaddielover/plugins
/plugin install overseer@saigonbaddielover
~~~

Codex:

~~~
codex plugin marketplace add saigonbaddielover/plugins
codex plugin add overseer@saigonbaddielover
~~~

## Update

Claude Code:

~~~
claude plugin marketplace update saigonbaddielover
claude plugin update overseer@saigonbaddielover
~~~

Codex:

~~~
codex plugin marketplace upgrade saigonbaddielover
codex plugin add overseer@saigonbaddielover
~~~

Catalog entries point only to release-gated plugin-release refs owned by their plugin repositories. Plugin versions and release artifacts remain authoritative in those repositories.

## Migrating an existing saigonbaddielover marketplace

If the marketplace name saigonbaddielover is already configured from an older source, replace that registration before reinstalling Overseer.

Claude Code:

    claude plugin marketplace remove saigonbaddielover
    claude plugin marketplace add saigonbaddielover/plugins
    claude plugin install overseer@saigonbaddielover

Codex:

    codex plugin marketplace remove saigonbaddielover
    codex plugin marketplace add saigonbaddielover/plugins
    codex plugin add overseer@saigonbaddielover
