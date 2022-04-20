# Contributing

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Environment setup

Fork and clone the repository, then:

```bash
pip install -r requirements_dev.txt
pip install -e .
```

## Development

As usual:

1. create a new branch: `git checkout -b feature-or-bugfix-name`
1. edit the code and/or the documentation

**Before committing:**

1. run `mypy src` to check typings
2. run `flake8 src` to check formatting (fix any warning)
3. run `python -m pytest` to run the tests (fix any issue)
4. if you updated the documentation or the project dependencies:
   1. run `pip install -r requirements_docs.txt` install doc dependencies
   1. run `mkdocs serve`
   1. go to <http://localhost:8000> and check that everything looks good
5. follow our [commit message convention](#commit-message-convention)

If you are unsure about how to fix or ignore a warning,
just let the continuous integration fail,
and we will help you during review.

Don't bother updating the changelog, we will take care of this.

## Commit message convention

Commits messages must follow the
[Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message):

```
<type>[(scope)]: Subject

[Body]
```

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes which are not features nor bug fixes.
- `style`: A change in code style/format.
- `tests`: About tests.

**Subject (and body) must be valid Markdown.**
If you write a body, please add issues references at the end:

```
Body.

References: #10, #11.
Fixes #15.
```

## Pull requests guidelines

Link to any related issue in the Pull Request message.

During review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash main
```

And force-push:

```bash
git push -f
```

If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
