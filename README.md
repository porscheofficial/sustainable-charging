# AI in Practice: Porsche Digital Challenge

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Linter](https://img.shields.io/badge/linter-ruff-blue)
![License: MIT](https://img.shields.io/github/license/konstantinjdobler/nlp-research-template?color=green)

This repository is part of the AI in Practice: Porsche Digital Challenge, a collaborative project focused on energy mix prediction.

## Contribution Guidelines

To streamline our collaboration and maintain the quality of our codebase, we follow a structured workflow using Git branches and pull requests. Here's how you can contribute:

### Getting Started

- **Familiarize Yourself with the Repository:** Spend some time understanding the current codebase and documentation.
- **Setup Your Local Environment:** Follow the instructions in the Setup section to prepare your local environment.

### Workflow

We use three types of branches:

- `main`: Stable version of the project. All changes eventually merge here.
- `dev`: Development branch for integrating various features before moving to main.
- Feature/Issue-Specific Branches: For working on new features or fixing issues.

#### 1. Creating a Branch

- Always create a new branch for your work, branching off from dev.
- Name your branch meaningfully, like `feature/add-nlp-model` or `fix/data-loading-issue`.

```bash
git checkout dev
git pull origin dev
git checkout -b [your_branch_name]
```

#### 2. Make Changes

- Work on your feature or fix in your branch.
- Commit your changes with clear, descriptive commit messages.

#### 3. Keep Your Branch Updated

- Regularly merge changes from dev into your branch to stay up-to-date.

```bash
git pull origin dev
```

#### 4. Submitting Changes

Once you are ready to share your work, push your branch to the remote repository.

```bash
git push origin [your_branch_name]
```

#### 5. Create a Pull Request (PR)

- Open a PR from your branch to dev on GitHub.
- Clearly describe the changes and link any relevant issues.

#### 6. Code Review

- Request a review from one or two team members.
- Address any feedback and make necessary revisions.

#### 7. Merge into dev

- After approval, merge your PR into dev.
- Delete your branch after merging, if it's no longer needed.

#### (8.) Staging to main

- Periodically, we will merge dev into main to update the stable version.
- This will be a collective decision after thorough testing and review.

### Requirements for merging

- Test your code thoroughly before submitting a PR.
- Document your code and update the README if necessary.
- Communicate with the team about what you're working on to avoid overlap.
