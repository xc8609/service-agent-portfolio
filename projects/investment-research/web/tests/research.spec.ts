import {expect, test} from '@playwright/test';

const comparisonPath = '/v1/research/sources/msft-ar2025/comparison';

test('complete a manual research task with real reported figures and source references', async ({page}) => {
  await page.goto('/');
  await expect(page.getByLabel('Company & report')).toContainText('Microsoft Corporation');
  await expect(page.getByText('FY2024 · 2023-07-01 to 2024-06-30')).toBeVisible();
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  const revenue = page.getByRole('row', {name: /^Revenue /});
  await expect(revenue).toContainText('245,122');
  await expect(revenue).toContainText('281,724');
  await expect(revenue).toContainText('36,602');
  await expect(revenue).toContainText('14.93%');
  await expect(page.getByRole('row', {name: /^Operating income /})).toContainText('17.45%');
  await expect(page.getByRole('row', {name: /^Operating cash flow /})).toContainText('14.86%');
  await expect(page.getByText('0.98 pp', {exact: true})).toBeVisible();
  await expect(page.getByText('USD · millions · Annual periods', {exact: true})).toBeVisible();
  await page.getByRole('link', {name: 'Revenue FY2025: 281,724, view source'}).click();
  await expect(page.locator('#revenue-fy2025')).toContainText('Income Statements / Total revenue / 2025');
  await expect(page.getByRole('link', {name: 'Open annual report'})).toHaveAttribute('href', 'https://www.microsoft.com/investor/reports/ar25/index.html');
  await page.getByLabel('Analyst notes', {exact: true}).fill('Revenue grew 14.93%; operating income grew 17.45%. Margin increased 0.98 percentage points.');
  await page.getByLabel('Open questions', {exact: true}).fill('Which report passages explain the margin movement?');
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue(/14.93%/);
  await expect(page.getByText('Notes stay in this open page.', {exact: false})).toBeVisible();
});

test('failed refresh removes comparison but preserves research edits and supports retry', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toBeVisible();
  await page.getByLabel('Research question', {exact: true}).fill('Did cash generation keep pace with sales?');
  await page.getByLabel('Analyst notes', {exact: true}).fill('Keep this observation.');
  await page.getByLabel('Open questions', {exact: true}).fill('Review working capital.');
  await page.route(`**${comparisonPath}`, route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: {code: 'SOURCE_UNAVAILABLE', safe_message: 'The reviewed source pack is unavailable.'}})}));
  await page.getByRole('button', {name: 'Refresh comparison', exact: true}).click();
  await expect(page.getByRole('alert')).toContainText('Comparison unavailable');
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toHaveCount(0);
  await expect(page.getByLabel('Research question', {exact: true})).toHaveValue('Did cash generation keep pace with sales?');
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('Keep this observation.');
  await expect(page.getByLabel('Open questions', {exact: true})).toHaveValue('Review working capital.');
  await page.unroute(`**${comparisonPath}`);
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toBeVisible();
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('Keep this observation.');
});

test('missing facts remain explicit while other comparisons are available', async ({page}) => {
  await page.route(`**${comparisonPath}`, async route => {
    const response = await route.fetch();
    const data = await response.json();
    data.facts = data.facts.filter((fact: {id: string}) => fact.id !== 'operating_cash_flow-fy2025');
    data.metrics.operating_cash_flow.actuals.FY2025 = null;
    for (const field of ['delta', 'growth_pct']) data.metrics.operating_cash_flow[field] = {value: null, input_fact_ids: ['operating_cash_flow-fy2024'], reason: 'missing_fact'};
    data.gaps = [{metric: 'operating_cash_flow', period_id: 'FY2025', reason: 'missing_fact'}];
    await route.fulfill({response, json: data});
  });
  await page.goto('/');
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  await expect(page.getByRole('status')).toContainText('Some source facts are missing');
  await expect(page.getByRole('row', {name: /^Operating cash flow /})).toContainText('Unavailable');
  await expect(page.getByRole('row', {name: /^Revenue /})).toContainText('14.93%');
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('catalog failure supports a clear retry without pretending no reports exist', async ({page}) => {
  await page.route('**/v1/research/sources', route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: {code: 'SOURCE_UNAVAILABLE', safe_message: 'Source catalogue unavailable.'}})}));
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Source catalogue unavailable.');
  await expect(page.getByText('No reviewed reports are available yet.')).toHaveCount(0);
  await page.unroute('**/v1/research/sources');
  await page.getByRole('button', {name: 'Retry sources'}).click();
  await expect(page.getByLabel('Company & report')).toContainText('Microsoft Corporation');
});

test('changing report selection invalidates a delayed result and keeps notes with their source', async ({page, request}) => {
  const original = await (await request.get(comparisonPath)).json();
  const originalSource = (await (await request.get('/v1/research/sources')).json()).sources[0];
  await page.route('**/v1/research/sources', route => route.fulfill({json: {sources: [originalSource, {...originalSource, id: 'second-report', title: 'Second report — selection test'}]}}));
  let release!: () => void;
  const delayed = new Promise<void>(resolve => { release = resolve; });
  await page.route(`**${comparisonPath}`, async route => { await delayed; await route.fulfill({json: original}); });
  await page.goto('/');
  await page.getByLabel('Analyst notes', {exact: true}).fill('Notes for the original report.');
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  await expect(page.getByRole('button', {name: 'Loading comparison…', exact: true})).toBeVisible();
  await page.getByLabel('Company & report').selectOption('second-report');
  const delivered = page.waitForResponse(response => response.url().endsWith(comparisonPath));
  release();
  await delivered;
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toHaveCount(0);
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('');
  await page.getByLabel('Company & report').selectOption('msft-ar2025');
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('Notes for the original report.');
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toHaveCount(0);
});
