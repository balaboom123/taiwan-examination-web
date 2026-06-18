from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from html import escape
from pathlib import Path
from typing import TypeVar
from urllib.parse import quote

from app.bundler import build_bundles
from app.manifest import SourceManifest, write_source_manifest
from app.models import AliasRule, BundleAsset, FILE_TYPE_LABELS, NormalizedCatalog, NormalizedPaper, SourceExamPage, SyncFailure, to_plain_data
from app.paths import legacy_paths, provider_paths, site_paths
from app.release_tags import assign_release_tags
from app.site_registry import get_site_config
from app.state import load_provider_state, load_site_bundles

T = TypeVar("T")


def _write_split_by_year(directory: Path, items: list[T], year_of: Callable[[T], int]) -> dict[int, list[T]]:
    directory.mkdir(parents=True, exist_ok=True)
    by_year: dict[int, list[T]] = {}
    for item in items:
        by_year.setdefault(year_of(item), []).append(item)
    existing = {int(f.stem) for f in directory.glob("*.json") if f.stem.isdigit()}
    for year_ad, year_items in sorted(by_year.items()):
        (directory / f"{year_ad}.json").write_text(
            json.dumps(to_plain_data(year_items), ensure_ascii=False), encoding="utf-8"
        )
    for stale_year in existing - by_year.keys():
        (directory / f"{stale_year}.json").unlink(missing_ok=True)
    return by_year


def write_data_files(
    data_dir: Path,
    raw_pages: list[SourceExamPage],
    normalized: NormalizedCatalog,
    aliases: list[AliasRule],
    bundles: list[BundleAsset],
    failures: list[SyncFailure],
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_split_by_year(data_dir / "exams", raw_pages, lambda page: page.year_ad)
    _write_split_by_year(data_dir / "papers", normalized.papers, lambda paper: paper.year_roc + 1911)
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
        {
            "storage_key": bundle.storage_key,
            "asset_name": bundle.asset_name,
            "checksum": bundle.checksum,
            "legacy_asset_names": bundle.legacy_asset_names,
        }
        for bundle in bundles
    ]
    (data_dir / "release-assets.json").write_text(
        json.dumps(release_assets, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_provider_state(
    provider,
    raw_pages: list[SourceExamPage],
    normalized: NormalizedCatalog,
    aliases: list[AliasRule],
    failures: list[SyncFailure],
    manifest: SourceManifest | None,
) -> None:
    provider.data_dir.mkdir(parents=True, exist_ok=True)
    _write_split_by_year(provider.exams_dir, raw_pages, lambda page: page.year_ad)
    _write_split_by_year(provider.papers_dir, normalized.papers, lambda paper: paper.year_roc + 1911)
    provider.review_queue_path.write_text(
        json.dumps(to_plain_data(normalized.review_queue), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    provider.sync_failures_path.write_text(
        json.dumps(to_plain_data(failures), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    provider.aliases_path.write_text(
        json.dumps({"rules": to_plain_data(aliases)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if manifest is not None:
        write_source_manifest(provider.source_manifest_path, manifest)


def write_site_state(
    site,
    bundles: list[BundleAsset],
    frontend_bundles: list[dict],
    lootlabs_manifest: dict | None,
    *,
    legacy_paths=None,
    write_legacy: bool = False,
) -> None:
    site.data_dir.mkdir(parents=True, exist_ok=True)
    site.bundles_path.write_text(
        json.dumps(
            {"schema_version": 1, "site_id": site.site_id, "bundles": to_plain_data(bundles)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    site.release_assets_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "site_id": site.site_id,
                "assets": [
                    {
                        "release_tag": bundle.release_tag,
                        "storage_key": bundle.storage_key,
                        "asset_name": bundle.asset_name,
                        "checksum": bundle.checksum,
                        "legacy_asset_names": bundle.legacy_asset_names,
                    }
                    for bundle in bundles
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    site.frontend_bundles_path.write_text(
        json.dumps(
            {"schema_version": 1, "site_id": site.site_id, "bundles": frontend_bundles},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if lootlabs_manifest is not None:
        site.lootlabs_manifest_path.write_text(json.dumps(lootlabs_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if write_legacy and legacy_paths is not None:
        legacy_paths.data_dir.mkdir(parents=True, exist_ok=True)
        legacy_paths.bundles_path.write_text(json.dumps(to_plain_data(bundles), ensure_ascii=False, indent=2), encoding="utf-8")
        legacy_paths.release_assets_path.write_text(
            json.dumps(
                [
                    {
                        "release_tag": bundle.release_tag,
                        "storage_key": bundle.storage_key,
                        "asset_name": bundle.asset_name,
                        "checksum": bundle.checksum,
                        "legacy_asset_names": bundle.legacy_asset_names,
                    }
                    for bundle in bundles
                ],
                ensure_ascii=False,
                indent=2,
                ),
            encoding="utf-8",
        )
        if lootlabs_manifest is not None:
            legacy_paths.lootlabs_manifest_path.write_text(
                json.dumps(lootlabs_manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )


def apply_bundle_download_urls(
    normalized: NormalizedCatalog,
    bundles: list[BundleAsset],
    *,
    repository: str,
) -> tuple[NormalizedCatalog, list[BundleAsset], list[dict]]:
    updated_bundles: list[BundleAsset] = []
    bundle_index: dict[str, BundleAsset] = {}
    for bundle in bundles:
        download_url = ""
        if repository and bundle.release_tag:
            download_url = f"https://github.com/{repository}/releases/download/{bundle.release_tag}/{quote(bundle.asset_name)}"
        updated_bundle = replace(bundle, download_url=download_url)
        updated_bundles.append(updated_bundle)
        bundle_index[updated_bundle.canonical_id] = updated_bundle

    updated_papers = [
        replace(
            paper,
            download_url_bundle=bundle_index.get(paper.canonical_id).download_url
            if paper.canonical_id in bundle_index
            else "",
        )
        for paper in normalized.papers
    ]

    frontend_bundles = [
        {
            "id": bundle.canonical_id,
            "name": bundle.canonical_name,
            "years": bundle.years,
            "fileCount": bundle.file_count,
            "url": bundle.download_url,
        }
        for bundle in updated_bundles
    ]
    return (
        NormalizedCatalog(papers=updated_papers, review_queue=normalized.review_queue),
        updated_bundles,
        frontend_bundles,
    )


def _site_bundle_storage_key(site_id: str, asset_name: str) -> str:
    return f"bundles/sites/{site_id}/{asset_name}"


def _site_scoped_bundles(site_id: str, bundles: list[BundleAsset]) -> list[BundleAsset]:
    return [replace(bundle, storage_key=_site_bundle_storage_key(site_id, bundle.asset_name)) for bundle in bundles]


def _format_bundle_failures(failures: list[SyncFailure]) -> str:
    details = []
    for failure in failures:
        parts = [failure.stage, failure.source_exam_id]
        if failure.paper_code:
            parts.append(failure.paper_code)
        if failure.file_type:
            parts.append(failure.file_type)
        details.append(f"{' '.join(parts)}: {failure.message}")
    return "\n".join(details)


def publish_site(
    repo_root: Path,
    *,
    site_id: str,
    repository: str,
) -> tuple[NormalizedCatalog, list[BundleAsset]]:
    site_config = get_site_config(site_id)
    aggregated_papers: list[NormalizedPaper] = []
    aggregated_review_queue = []
    for provider_id in site_config.provider_ids:
        _raw_pages, provider_catalog, _failures = load_provider_state(provider_paths(repo_root, provider_id))
        aggregated_papers.extend(provider_catalog.papers)
        aggregated_review_queue.extend(provider_catalog.review_queue)

    normalized = NormalizedCatalog(papers=aggregated_papers, review_queue=aggregated_review_queue)
    site = site_paths(repo_root, site_id)
    existing_bundles = load_site_bundles(site)
    bundle_result = build_bundles(
        bundle_dir=site.bundle_dir,
        mirror_dir=repo_root / "mirror",
        normalized=normalized,
        bundle_base_url="",
        min_years=1,
    )
    if bundle_result.failures:
        raise ValueError(_format_bundle_failures(bundle_result.failures))
    site_scoped_bundles = _site_scoped_bundles(site_id, bundle_result.bundles)
    tagged_bundles = assign_release_tags(
        release_tag_prefix=site_config.release_tag_prefix,
        existing_bundles=existing_bundles,
        bundles=site_scoped_bundles,
        max_assets_per_release=site_config.release_shard_size,
    )
    normalized_with_urls, bundles_with_urls, frontend_bundles = apply_bundle_download_urls(
        normalized,
        tagged_bundles,
        repository=repository,
    )
    write_site_state(
        site,
        bundles_with_urls,
        frontend_bundles,
        lootlabs_manifest=None,
        legacy_paths=legacy_paths(repo_root) if site_id == "default" else None,
        write_legacy=site_id == "default",
    )
    build_site(repo_root / "site", normalized_with_urls, bundles_with_urls)
    return normalized_with_urls, bundles_with_urls


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
    by_year = _write_split_by_year(papers_site_dir, normalized.papers, lambda paper: paper.year_roc + 1911)
    available_years = sorted(by_year.keys(), reverse=True)
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
