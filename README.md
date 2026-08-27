### atlas-biling

Billing app

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app atlas_billing
```

**Important — run the Setup Wizard first.** `atlas_billing`'s `after_install` creates a generic Item under the Item Group "Services", but that Item Group (and other ERPNext defaults) only exist once the Setup Wizard has run. On a brand new site, complete `install-app erpnext` → the Setup Wizard in the browser (Company, country, currency) → **then** `install-app atlas_billing`. If `atlas_billing` was installed before the Setup Wizard ran, `after_install` fails partway through but Frappe still marks the app as installed — re-running `bench install-app atlas_billing` afterwards just prints "already installed" and does nothing. Fix by re-running with `--force`:

```bash
bench --site $SITE install-app atlas_billing --force
```

### Post-install setup

Some settings depend on data (Company, Warehouse, chart of accounts, branding) that only exists once a real site is set up, so they can't be shipped as fixtures. Configure these by hand for each new site:

- **POS Profile → Allow Partial Payment** — enable this on every POS Profile used at checkout. Without it, POS Invoice submission is rejected whenever the client doesn't pay in full (blocks recording a sale on credit — US-07).
- **POS Profile → Print Format** — set this to the app's receipt print format (`Los gladiolos`). The POS screens (both the live sale and the past-order reprint) read the print format from this field, not from the DocType's default print format — leaving it unset means no format is selectable when printing a POS Invoice from the POS.
- **POS Profile → Warehouse** — required by ERPNext regardless of this app. The default Warehouse created by the Setup Wizard for your Company is fine to use as-is; it only matters once you sell items that carry real stock (e.g. retail products), since the salon's own service items are configured as non-stock and never move it.
- **Letter Head** — create one Letter Head record with the salon's logo/branding and mark it **Is Default**. Print formats pull whichever Letter Head has `Is Default` checked automatically; without one, invoices print with a blank header. This isn't fixtured on purpose — the logo is specific to each client, and file attachments (images) aren't carried over by `export-fixtures` anyway.
- **Hide unused Workspaces** — from the sidebar's Edit mode ("..." → Hide), hide the modules the salon doesn't use: Assets, Manufacturing, Projects, Quality, CRM, Support, Website, Integrations, ERPNext Integrations, Automation → Tools, Core → Build, and Core → Welcome Workspace. This can't be fixtured — Frappe's fixture sync deliberately ignores the `is_hidden` field on Workspace (`frappe/modules/import_file.py`'s `ignore_values`), always keeping whatever value is already in that site's database instead of the one being imported.

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
