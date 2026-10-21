-- Simulated routing scope: the CFPB products a Canadian bank's complaint intake would
-- plausibly receive, and the simulated product team that owns each one.
-- Single source of truth for scope; profiling, marts and evaluation join to this table.
-- Out of scope: credit reporting (handled by bureaus), debt collection and debt/credit
-- management (mostly third parties), student loans (US federal servicing).
CREATE OR REPLACE TABLE ref_product_team AS
SELECT * FROM (VALUES
    ('Checking or savings account',                             'Everyday Banking'),
    ('Credit card',                                             'Cards'),
    ('Prepaid card',                                            'Cards'),
    ('Money transfer, virtual currency, or money service',      'Payments'),
    ('Mortgage',                                                'Home Lending'),
    ('Vehicle loan or lease',                                   'Consumer Lending'),
    ('Payday loan, title loan, personal loan, or advance loan', 'Consumer Lending')
) AS t(product, routing_team);
