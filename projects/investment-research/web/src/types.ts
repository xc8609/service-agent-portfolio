export type Period = {id: string; start: string; end: string};
export type Source = {
  id: string;
  issuer: {id: string; name: string; cik: string};
  title: string;
  url: string;
  periods: Period[];
};
export type Fact = {id: string; metric: string; period_id: string; value: string; currency: string; unit: string; source_id: string; locator: string};
export type Derived = {value: string | null; input_fact_ids: string[]; reason: string | null};
export type Comparison = {
  schema_version: number;
  issuer: Source['issuer'];
  source: {id: string; title: string; url: string; retrieved_at: string; sha256: string};
  periods: Period[];
  facts: Fact[];
  currency: string | null;
  unit: string | null;
  metrics: Record<string, {actuals: Record<string, {value: string; fact_id: string} | null>; delta: Derived; growth_pct: Derived}>;
  operating_margin_pct: Record<string, Derived>;
  operating_margin_change_pp: Derived;
  gaps: {metric: string; period_id: string; reason: string}[];
};
