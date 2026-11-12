# GitHub 公式情報メモ（radiko-epg 照合用）

このサイトの運用中に起きた事象と照らし合わせるための、GitHub 公式発表の記録。
障害情報は GitHub Status、更新情報は GitHub Changelog と実行時の注釈から、Actions / Pages / API Requests に関係するものだけを残す。
各エントリは原文（英語）のタイトルと短い抜粋に、日本語の訳（長文は要約）を添える。時刻はすべて日本時間。
公式発表は「原因の証明」ではなく照合用の資料であり、時間が重なっても断定はしない。発表がなかった場合は、その旨を「照合」欄に残す。
このファイルの追記は GitHub Actions では行わない（監視対象自身に集めさせないため、Muse の定期確認のついでに追記する）。

## 障害情報（GitHub Status）

### 2026-11-12 05:48 – 06:21（critical / Webhooks, Actions, Pages, Copilot）
**Impact across multiple GitHub products including Actions, Pages, and Copilot products.**
- 原文抜粋: "The backlog of Actions jobs has been fully processed. We're observing full recovery across all impacted services."
- 訳: Actions、Pages、Copilot など複数製品に影響する障害。Actions ジョブの滞留が発生し、すべて処理されて復旧が確認された。
- 公式: https://www.githubstatus.com/incidents/dvy0t3mvh1lg

### 2026-11-11 01:10 – 02:55（critical / Pull Requests, Actions）
**Incident with Git Operations and Pull Requests**
- 原文抜粋: "We continue to investigate elevated response times for Git operations and pull requests. Actions workflows are recovering."
- 訳: Git 操作とプルリクエストの応答時間が悪化した障害。Actions のワークフローは回復に向かった。
- 公式: https://www.githubstatus.com/incidents/hnf21m9jkl3c

### 2026-11-10 03:12 – 03:59（critical / Webhooks, Actions, Pages）
**Incident with Actions and Checks API**
- 原文抜粋: "Pages is experiencing degraded performance. We are continuing to investigate."
- 訳: Actions と Checks API の障害。Pages も性能低下の対象になった。
- 公式: https://www.githubstatus.com/incidents/tp8cghg7tlc4

### 2026-11-09 19:00 – 20:50（major / Webhooks, Actions）
**Incident with Webhooks and Actions**
- 原文抜粋: "Webhooks is experiencing degraded performance. We are continuing to investigate."
- 訳: Webhooks と Actions の障害。
- 公式: https://www.githubstatus.com/incidents/xxb3l2bm76dr

### 2026-11-08 19:36 – 21:32（minor / API Requests）
**Increase in timeouts for some unauthenticated users**
- 原文抜粋: "The degradation affecting API Requests has been mitigated. We are monitoring to ensure stability."
- 訳: 一部の未認証ユーザーでタイムアウトが増えた障害（API Requests）。
- 公式: https://www.githubstatus.com/incidents/pyynvrm1vskw

### 2026-11-06 08:36 – 09:20（minor / Git Operations, Issues, Actions, Pages）
**Degraded performance for multiple GitHub services**
- 原文抜粋: "All affected services, including Git operations, Issues, Actions, and API access, have recovered and remained stable."
- 訳: 複数サービスの性能低下。Actions と Pages も対象に含まれた。
- 公式: https://www.githubstatus.com/incidents/pfbmpxxfq1cy

### 2026-11-06 01:50 – 02:42（minor / Actions）
**Incident with Actions**
- 原文抜粋: "Some GitHub Actions workflow runs may experience delays or errors when starting. We're investigating and preparing a mitigation."
- 訳: Actions のワークフロー実行の開始に、遅延やエラーが出る場合がある障害。
- 公式: https://www.githubstatus.com/incidents/t89g2q1800fr

### 2026-11-05 02:40 – 03:16（major / Actions）
**Incident with Actions**
- 原文抜粋: "We have identified an issue with events that might trigger Actions. We have applied mitigations and are monitoring for recovery at this point."
- 訳: Actions を起動するイベント側に問題があった障害。
- 公式: https://www.githubstatus.com/incidents/h02n9572mx9y

### 2026-11-05 01:05 – 02:01（major / Webhooks, Actions, Pages）
**Incident with Actions and Pages**
- 原文抜粋: "On November 4, 2026, between 15:49 UTC and 16:48 UTC, and again between 17:20 UTC and 17:55 UTC, GitHub Actions, Pages, Webhooks, Code Scanning, and Copilot code…"（解決後のまとめ文より）
- 訳: Actions と Pages の障害。別のインシデントと合わせた総括がこちらにまとめられた。
- 公式: https://www.githubstatus.com/incidents/xr3myzj7ms51

### 2026-11-04 18:49 – 20:50（major / Git Operations, API Requests, Issues, Pull Requests, Actions）
**Incident with Pull Requests, Git Operations and Issues**
- 原文抜粋: "The degradation affecting Actions has been mitigated. We are monitoring to ensure stability."
- 訳: プルリクエスト、Git 操作、Issues の障害。Actions と API Requests も対象に含まれた。
- 公式: https://www.githubstatus.com/incidents/smtdswd1h2w4

### 2026-11-03 22:25 – 22:56（minor / API Requests, Issues, Copilot）
**Incident with API, Git, and Copilot requests**
- 原文抜粋: "API Requests is operating normally."
- 訳: API、Git、Copilot へのリクエストに関する障害。
- 公式: https://www.githubstatus.com/incidents/rxlj89wpk7px

## 更新情報（GitHub Changelog / 実行時の注釈）

### 2026-11-12 に pages build and deployment の注釈で表示（Actions / Pages）
**Node.js 20 の廃止に伴う強制移行**
- 原文（注釈の抜粋）: "Node.js 20 is deprecated."（actions/upload-artifact@v4 が Node.js 24 で実行される旨の警告）
- 訳: Node.js 20 は廃止予定となり、対象のアクションは Node.js 24 で強制実行される。GitHub 側の Pages 公開まわりの仕組みの話で、このリポジトリのワークフローの問題ではない。

### 2026-11-12 に pages build and deployment の注釈で表示（Actions）
**ubuntu-latest の移行予告**
- 原文（注釈の抜粋）: "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026"
- 訳: ubuntu-latest ラベルは 2026 年 10 月 19 日から Ubuntu 26 へ移行する、という案内。generate.py は標準ライブラリのみで動くため、このリポジトリへの実害は小さい。

## 照合（うちの事象と公式発表）

### 2026-11-11 20:00 / 23:00 の schedule 枠不発
- うちの事象: 変更前の毎時0分の枠が 20:00 と 23:00 で発火しなかった。
- 公式発表: その時刻に重なるインシデントは GitHub Status に**なし**（該当なし）。スケジューラ側の小さな滞りは Status に載らないことがある、という前提の記録。

### 2026-11-12 08:07 枠の遅延発火（08:25 開始）
- うちの事象: 08:07 の枠が 18 分遅れて発火し、成功した。
- 公式発表: 同じ朝 05:48 – 06:21 に Actions ジョブ滞留を伴う障害（critical）があった。時刻は少し前であり、直接の原因とは断定しない。候補として記録する。
