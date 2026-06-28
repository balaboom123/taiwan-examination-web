# Provider Spec: `gept_cert`

## Summary

- `provider_id`: `gept_cert`
- status: active
- target site: `default`
- source family: GEPT 全民英檢 official practice/material pages
- source domain: `www.gept.org.tw`

## Source Model

The provider scans the official GEPT level introduction pages:

- 初級: `t01_introduction.asp`
- 中級: `t02_introduction.asp`
- 中高級: `t03_introduction.asp`
- 高級: `t04_introduction.asp`
- 優級: `t05_introduction.asp`

Direct PDF/ZIP links are mirrored as `question`. Linked practice pages are scanned for `playAudio('*.mp3')` references, mirrored as `listening_audio`.

## Output Model

- one current-year exam: `gept-cert-materials`
- category: `GEPT全民英檢官方練習資料_<level>`
- file types: `question`, `listening_audio`
- provider data: `data/providers/gept_cert/`
- workflow: `.github/workflows/sync-gept-cert.yml`

## Plan

1. Fetch each level introduction page.
2. Parse official PDF/ZIP material links and practice-page links.
3. Fetch practice pages and parse direct MP3 audio references.
4. Percent-encode non-ASCII URLs before requests.
5. Mirror PDF, ZIP, and MP3 payloads through the standard sync pipeline.
