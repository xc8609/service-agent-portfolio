import {expect, test, type Page} from '@playwright/test';

const runsPath = '**/v1/research/runs';
async function loadComparison(page: Page) {
  await page.goto('/');
  await expect(page.getByRole('button', {name: 'Generate research draft', exact: true})).toBeDisabled();
  await page.getByRole('button', {name: 'Load comparison', exact: true}).click();
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toBeVisible();
}

test('generate a cited research brief through the actual tools and explicitly append it to notes', async ({page}) => {
  await loadComparison(page);
  await page.getByLabel('Analyst notes', {exact: true}).fill('My independent observation.');
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  const draft = page.getByLabel('Research draft', {exact: true});
  await expect(draft.getByLabel('Draft facts', {exact: true})).toContainText('14.93');
  await expect(draft.getByLabel('Draft facts', {exact: true})).toContainText('17.45');
  await expect(draft.getByLabel('Draft facts', {exact: true})).toContainText('14.86');
  await expect(draft.getByLabel('Draft company explanations', {exact: true})).not.toContainText('No supported explanation');
  await expect(draft.getByLabel('Draft company explanations', {exact: true}).getByRole('link').first()).toHaveAttribute('href', 'https://www.microsoft.com/investor/reports/ar25/index.html');
  await expect(draft.getByLabel('Draft open questions', {exact: true})).toBeVisible();
  await page.getByText('Evidence retrieval steps', {exact: true}).click();
  await expect(draft).toContainText('offline-scripted-v1');
  await expect(draft).toContainText('read_passages · ok');
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('My independent observation.');
  await page.getByRole('button', {name: 'Append draft to notes', exact: true}).click();
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue(/^My independent observation\.\n\nResearch draft/);
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue(/Company explanations \(summarized\)/);
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue(/https:\/\/www\.microsoft\.com\/investor\/reports\/ar25\/index\.html/);
  await expect(page.getByRole('button', {name: 'Appended to notes', exact: true})).toBeDisabled();
});

test('a failed Agent request leaves the manual comparison and notes usable', async ({page}) => {
  await loadComparison(page);
  await page.getByLabel('Analyst notes', {exact: true}).fill('Keep my evidence review.');
  await page.route(runsPath, route => route.fulfill({status: 503, json: {error: {code: 'SOURCE_UNAVAILABLE', safe_message: 'The selected evidence is unavailable.'}}}));
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  await expect(page.getByRole('alert')).toContainText('Draft unavailable');
  await expect(page.getByRole('table', {name: 'Operating metric comparison'})).toBeVisible();
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('Keep my evidence review.');
  await page.getByLabel('Analyst notes', {exact: true}).fill('Still editing manually.');
  await expect(page.getByLabel('Research draft', {exact: true})).toHaveCount(0);
});

test('question changes invalidate an in-flight draft without changing analyst notes', async ({page, request}) => {
  const source = (await (await request.get('/v1/research/sources/msft-ar2025/comparison')).json()).source;
  let release!: () => void;
  let completed!: () => void;
  const delayed = new Promise<void>(resolve => {release = resolve;});
  const finished = new Promise<void>(resolve => {completed = resolve;});
  await page.route(runsPath, async route => {
    const body = route.request().postDataJSON();
    await delayed;
    try {
      await route.fulfill({json: {status: 'draft', question: body.question, source_id: source.id, source_hash: source.sha256, provider: 'offline-scripted-v1', findings: [{kind: 'calculated_fact', text: 'Stale draft should never appear', citations: []}], open_questions: [], trace: [], issues: []}});
    } finally {completed();}
  });
  await loadComparison(page);
  await page.getByLabel('Analyst notes', {exact: true}).fill('Preserve this note.');
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  await expect(page.getByRole('button', {name: 'Preparing research draft…', exact: true})).toBeVisible();
  await page.getByLabel('Research question', {exact: true}).fill('What changed in operating cash flow?');
  release(); await finished;
  await expect(page.getByText('Stale draft should never appear')).toHaveCount(0);
  await expect(page.getByRole('button', {name: 'Generate research draft', exact: true})).toBeEnabled();
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue('Preserve this note.');
});

test('comparison refresh invalidates an existing draft and keeps the appended analyst text', async ({page}) => {
  await loadComparison(page);
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  await expect(page.getByLabel('Research draft', {exact: true})).toBeVisible();
  await page.getByRole('button', {name: 'Append draft to notes', exact: true}).click();
  const note = await page.getByLabel('Analyst notes', {exact: true}).inputValue();
  await page.getByRole('button', {name: 'Refresh comparison', exact: true}).click();
  await expect(page.getByLabel('Research draft', {exact: true})).toHaveCount(0);
  await expect(page.getByRole('button', {name: 'Generate research draft', exact: true})).toBeEnabled();
  await expect(page.getByLabel('Analyst notes', {exact: true})).toHaveValue(note);
});

test('incomplete tool execution is distinct from a failed request and cannot be appended as a finished draft', async ({page, request}) => {
  const source = (await (await request.get('/v1/research/sources/msft-ar2025/comparison')).json()).source;
  await page.route(runsPath, route => route.fulfill({json: {status: 'incomplete', question: route.request().postDataJSON().question, source_id: source.id, source_hash: source.sha256, provider: 'offline-scripted-v1', findings: [], open_questions: ['Which evidence should be checked next?'], trace: [{tool: 'read_passages', status: 'error'}], issues: [{code: 'TOOL_FAILED', message: 'Report passages could not be read.'}]}}));
  await loadComparison(page);
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  await expect(page.getByRole('status')).toContainText('Draft incomplete');
  await expect(page.getByLabel('Research draft', {exact: true})).toContainText('Report passages could not be read.');
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect(page.getByRole('button', {name: 'Append draft to notes', exact: true})).toBeDisabled();
});

test('a response for a different report or question never becomes the current draft', async ({page, request}) => {
  const source = (await (await request.get('/v1/research/sources/msft-ar2025/comparison')).json()).source;
  await page.route(runsPath, route => route.fulfill({json: {status: 'draft', question: 'A different question', source_id: source.id, source_hash: source.sha256, provider: 'offline-scripted-v1', findings: [], open_questions: [], trace: [], issues: []}}));
  await loadComparison(page);
  await page.getByRole('button', {name: 'Generate research draft', exact: true}).click();
  await expect(page.getByRole('alert')).toContainText('does not match the current report and question');
  await expect(page.getByLabel('Research draft', {exact: true})).toHaveCount(0);
});
