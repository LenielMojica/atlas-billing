### atlas-billing

[![CI](https://github.com/LenielMojica/atlas-billing/actions/workflows/ci.yml/badge.svg)](https://github.com/LenielMojica/atlas-billing/actions/workflows/ci.yml)
[![Linters](https://github.com/LenielMojica/atlas-billing/actions/workflows/linter.yml/badge.svg)](https://github.com/LenielMojica/atlas-billing/actions/workflows/linter.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Built on Frappe](https://img.shields.io/badge/built%20on-Frappe%20%2F%20ERPNext-0089FF)](https://frappeframework.com/)

A point-of-sale and billing system for a hair salon, built as a custom
Frappe app on top of ERPNext. It handles day-to-day checkout at the salon —
running a client's tab, charging for services and retail products on the
same ticket, partial/credit payments, cancellations with a required reason,
and cash register reconciliation at close — plus the accounting and
reporting that comes with it (tax-exempt services, sales-by-category and
profitability reports, receivable tracking).

It's built as a thin layer on top of ERPNext's own Selling, Accounting, and
POS modules rather than a system from scratch: most of the work is
validation logic, a handful of custom fields, role permissions scoped to
salon staff, and print formats — not reinventing invoicing or accounting.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app atlas_billing
```

**Important — run the Setup Wizard first.** `atlas_billing`'s `after_install` creates a generic Item under the Item Group "Services", but that Item Group (and other ERPNext defaults) only exist once the Setup Wizard has run. On a brand new site, complete `install-app erpnext` → the Setup Wizard in the browser (Company, country, currency) → **then** `install-app atlas_billing`. If `atlas_billing` was installed before the Setup Wizard ran, `after_install` fails partway through but Frappe still marks the app as installed — re-running `bench install-app atlas_billing` afterwards just prints "already installed" and does nothing. Fix by re-running with `--force`:

```bash
bench --site $SITE install-app atlas_billing --force
```

### Post-install setup

Some settings depend on data (Company, Warehouse, chart of accounts, branding) that only exists once a real site is set up, so they can't be shipped as fixtures. Configure these by hand for each new site:

- **POS Profile → Allow Partial Payment** — enable this on every POS Profile used at checkout. Without it, POS Invoice submission is rejected whenever the client doesn't pay in full (blocks recording a sale on credit).
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

This app uses GitHub Actions:

- CI: installs the app and runs the test suite on every pull request.
- Linters: runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### Acknowledgments

Built on [Frappe](https://frappeframework.com/) and [ERPNext](https://erpnext.com/) — this app is a thin custom layer on top of both, not a from-scratch system. Development, debugging, and server setup were done with the help of [Claude Code](https://claude.com/claude-code) (Anthropic) throughout the project.

### License

See [LICENSE](LICENSE).
