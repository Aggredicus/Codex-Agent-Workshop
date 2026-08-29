# Business Knowledge

This directory is the optional progressive-disclosure knowledge base for an organization using Codex Agent Workshop.

Suggested structure:

```text
business/
  brand/          voice, visual identity, positioning
  clients/        sanitized project briefs and approved client context
  ecommerce/      catalog, merchandising, conversion procedures
  finance/        pricing models, reporting procedures, non-secret templates
  marketing/      audiences, channels, campaigns, content standards
  offers/         services/products, scope, pricing logic
  operations/     SOPs, project lifecycle, scheduling
  policies/       business-specific authorization and quality policies
  sales/          pipeline stages, qualification, proposal/follow-up procedures
  services/       delivery standards and reusable deliverable structures
  reference/      curated domain knowledge
```

Team roles reference these paths from their `context` lists. Load files progressively instead of injecting the whole business into every model call.

## Sensitive information

Do not use this repository as a secret store. Avoid committing credentials, payment information, tax identifiers, unnecessary customer PII, private communications, or regulated/sensitive records.

Use connected systems and access-controlled stores for live business data. Repository documents should explain *how* to work with those systems and what approval boundaries apply.
