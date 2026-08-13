### atlas-biling

Billing app

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app atlas_billing
```

### Post-install setup

Some settings depend on data (Company, Warehouse, chart of accounts) that only exists once a real site is set up, so they can't be shipped as fixtures. Configure these by hand for each new site:

- **POS Profile** — for each POS Profile used at checkout, enable **Allow Partial Payment**. Without this, POS Invoice submission is rejected whenever the client doesn't pay in full (blocks recording a sale on credit — US-07).

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/atlas_billing
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
