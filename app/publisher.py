from __future__ import annotations

import json
from html import escape
from pathlib import Path

from app.models import AliasRule, BundleAsset, FILE_TYPE_LABELS, NormalizedCatalog, NormalizedPaper, SourceExamPage, SyncFailure, to_plain_data


def _write_split_by_year(directory: Path, items: list, year_key: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    by_year: dict[int, list] = {}
    for item in items:
        year = item[year_key] if isinstance(item, dict) else getattr(item, year_key)
        by_year.setdefault(year, []).append(item)
    existing = {int(f.stem) for f in directory.glob("*.json") if f.stem.isdigit()}
    written = set()
    for year_ad, year_items in sorted(by_year.items()):
        written.add(year_ad)
        (directory / f"{year_ad}.json").write_text(
            json.dumps(to_plain_data(year_items), ensure_ascii=False), encoding="utf-8"
        )
    for stale_year in existing - written:
        (directory / f"{stale_year}.json").unlink(missing_ok=True)


def write_data_files(
    data_dir: Path,
    raw_pages: list[SourceExamPage],
    normalized: NormalizedCatalog,
    aliases: list[AliasRule],
    bundles: list[BundleAsset],
    failures: list[SyncFailure],
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_split_by_year(data_dir / "exams", raw_pages, "year_ad")
    papers_dir = data_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    by_year: dict[int, list] = {}
    for paper in normalized.papers:
        by_year.setdefault(paper.year_roc + 1911, []).append(paper)
    existing = {int(f.stem) for f in papers_dir.glob("*.json") if f.stem.isdigit()}
    written = set()
    for year_ad, year_papers in sorted(by_year.items()):
        written.add(year_ad)
        (papers_dir / f"{year_ad}.json").write_text(
            json.dumps(to_plain_data(year_papers), ensure_ascii=False), encoding="utf-8"
        )
    for stale_year in existing - written:
        (papers_dir / f"{stale_year}.json").unlink(missing_ok=True)
    for legacy in ("exams.raw.json", "papers.json"):
        (data_dir / legacy).unlink(missing_ok=True)
    (data_dir / "bundles.json").write_text(json.dumps(to_plain_data(bundles), ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "review-queue.json").write_text(
        json.dumps(to_plain_data(normalized.review_queue), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "sync-failures.json").write_text(
        json.dumps(to_plain_data(failures), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "aliases.json").write_text(json.dumps({"rules": to_plain_data(aliases)}, ensure_ascii=False, indent=2), encoding="utf-8")
    release_assets = [
        {"storage_key": bundle.storage_key, "asset_name": bundle.asset_name, "checksum": bundle.checksum}
        for bundle in bundles
    ]
    (data_dir / "release-assets.json").write_text(
        json.dumps(release_assets, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _group_options(papers: list[NormalizedPaper]) -> tuple[list[str], list[int]]:
    names = sorted({paper.canonical_name for paper in papers})
    years = sorted({paper.year_roc for paper in papers}, reverse=True)
    return names, years


def build_site(site_dir: Path, normalized: NormalizedCatalog, bundles: list[BundleAsset]) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    data_dir = site_dir / "data"
    papers_site_dir = data_dir / "papers"
    papers_site_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "bundles.json").write_text(
        json.dumps(to_plain_data(bundles), ensure_ascii=False), encoding="utf-8"
    )
    by_year: dict[int, list] = {}
    for paper in normalized.papers:
        by_year.setdefault(paper.year_roc + 1911, []).append(paper)
    available_years = sorted(by_year.keys(), reverse=True)
    existing_site_years = {int(f.stem) for f in papers_site_dir.glob("*.json") if f.stem.isdigit()}
    written_site_years: set[int] = set()
    for year_ad, year_papers in by_year.items():
        written_site_years.add(year_ad)
        (papers_site_dir / f"{year_ad}.json").write_text(
            json.dumps(to_plain_data(year_papers), ensure_ascii=False), encoding="utf-8"
        )
    for stale_year in existing_site_years - written_site_years:
        (papers_site_dir / f"{stale_year}.json").unlink(missing_ok=True)
    file_type_labels_json = json.dumps(FILE_TYPE_LABELS, ensure_ascii=False)
    canonical_names, years_roc = _group_options(normalized.papers)
    name_options = "".join(f'<option value="{escape(name, quote=True)}">{escape(name)}</option>' for name in canonical_names)
    year_options = "".join(f'<option value="{year}">{year}</option>' for year in years_roc)
    years_json = json.dumps(available_years)
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>考選部歷屆試題下載</title>
  <style>
    :root {{ color-scheme: light; --bg: #f2ede4; --card: #fffdf8; --ink: #202020; --accent: #0f766e; --line: #d9d2c5; }}
    body {{ margin: 0; font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; background: radial-gradient(circle at top, #fff8e8, var(--bg)); color: var(--ink); }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }}
    h1 {{ margin-bottom: 8px; font-size: 2rem; }}
    p {{ margin-top: 0; color: #555; }}
    .controls {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin: 24px 0; }}
    .bundle-grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin-bottom: 24px; }}
    .bundle-card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px; box-shadow: 0 8px 24px rgba(32,32,32,0.06); }}
    select {{ width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: white; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 16px; overflow: hidden; box-shadow: 0 14px 40px rgba(32,32,32,0.08); }}
    th, td {{ text-align: left; padding: 12px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    th {{ background: #f4efe4; font-weight: 700; }}
    a {{ color: var(--accent); }}
    .muted {{ color: #666; font-size: 0.9rem; }}
    #loading {{ text-align: center; padding: 24px; color: #888; }}
  </style>
</head>
<body>
  <main>
    <h1>考選部歷屆試題下載</h1>
    <p>依考試名稱與年度快速篩選，可直接下載整理好的中文壓縮檔，或回到原始來源頁面查看題目。</p>
    <section class="bundle-grid" id="bundleCards"></section>
    <div class="controls">
      <label>考試名稱<select id="canonicalFilter"><option value="">全部</option>{name_options}</select></label>
      <label>年度<select id="yearFilter"><option value="">全部</option>{year_options}</select></label>
    </div>
    <div id="loading">請選擇年度以顯示試題…</div>
    <table style="display:none" id="paperTable">
      <thead>
        <tr>
          <th>考試名稱</th>
          <th>年度</th>
          <th>科目</th>
          <th>分類</th>
          <th>下載整理包</th>
          <th>原始來源</th>
        </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
  </main>
  <script>
    const AVAILABLE_YEARS = {years_json};
    const FILE_TYPE_LABELS = {file_type_labels_json};
    const paperCache = {{}};
    const rows = document.getElementById('rows');
    const bundleCards = document.getElementById('bundleCards');
    const paperTable = document.getElementById('paperTable');
    const loading = document.getElementById('loading');
    const canonicalFilter = document.getElementById('canonicalFilter');
    const yearFilter = document.getElementById('yearFilter');

    fetch('data/bundles.json').then(r => {{
      if (!r.ok) throw new Error(`HTTP ${{r.status}}`);
      return r.json();
    }}).then(bundles => {{
      bundleCards.innerHTML = bundles.map(bundle => `
        <article class="bundle-card">
          <strong>${{bundle.canonical_name}}</strong>
          <div class="muted">年度：${{bundle.years.join(', ')}}</div>
          <div class="muted">檔案數：${{bundle.file_count}}</div>
          <div style="margin-top: 10px;">
            ${{bundle.download_url ? `<a href="${{bundle.download_url}}">下載壓縮檔</a>` : '<span class="muted">尚未提供</span>'}}
          </div>
        </article>
      `).join('');
    }}).catch(() => {{ bundleCards.innerHTML = '<p style="color:#c00">無法載入壓縮檔資料</p>'; }});

    async function loadYear(yearAd) {{
      if (paperCache[yearAd]) return paperCache[yearAd];
      const resp = await fetch(`data/papers/${{yearAd}}.json`);
      if (!resp.ok) throw new Error(`HTTP ${{resp.status}}`);
      const data = await resp.json();
      paperCache[yearAd] = data;
      return data;
    }}

    async function render() {{
      const canonical = canonicalFilter.value;
      const yearRoc = yearFilter.value;
      let yearsToLoad;
      if (yearRoc) {{
        yearsToLoad = [parseInt(yearRoc) + 1911];
      }} else {{
        loading.textContent = '載入全部年度…';
        loading.style.display = '';
        paperTable.style.display = 'none';
        yearsToLoad = AVAILABLE_YEARS;
      }}
      const allPapers = [];
      let loadFailed = false;
      for (const y of yearsToLoad) {{
        try {{ allPapers.push(...await loadYear(y)); }}
        catch (e) {{
          loading.textContent = `載入失敗：${{e.message}}`;
          loading.style.display = '';
          paperTable.style.display = 'none';
          loadFailed = true;
          break;
        }}
      }}
      if (loadFailed) return;
      const filtered = allPapers.filter(p => !canonical || p.canonical_name === canonical);
      loading.style.display = 'none';
      paperTable.style.display = '';
      rows.innerHTML = filtered.map(paper => `
        <tr>
          <td><strong>${{paper.canonical_name}}</strong></td>
          <td>${{paper.year_roc}}</td>
          <td>${{paper.subject_name_raw}}<div class="muted">${{FILE_TYPE_LABELS[paper.file_type] || paper.file_type}}</div></td>
          <td>${{paper.category_raw || paper.exam_name_raw}}</td>
          <td>${{paper.download_url_bundle ? `<a href="${{paper.download_url_bundle}}">下載壓縮檔</a>` : '<span class="muted">尚未提供</span>'}}</td>
          <td><a href="${{paper.download_url_source}}">查看來源</a></td>
        </tr>
      `).join('');
    }}
    canonicalFilter.addEventListener('change', render);
    yearFilter.addEventListener('change', render);
  </script>
</body>
</html>
"""
    (site_dir / "index.html").write_text(html, encoding="utf-8")
