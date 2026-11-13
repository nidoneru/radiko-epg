# GitHub 公式情報メモ

時刻はすべて日本時間（UTC+9）。

### 2026-11-13 05:59
**Actions for ARM32 Linux & Windows retirement**
- 種別：更新（GitHub Changelog、対象：Actions）
- 原文抜粋: "GitHub Actions hosted runners will be ending support for ARM32 job execution on Windows and Linux by 8th Dec 2026."
- 訳：GitHub Actions のホストランナーは、2026年12月8日までに Windows/Linux での ARM32 ジョブ実行のサポートを終了する。Node 24 が ARM32 に対応していないため。このリポジトリは x86_64 環境で動くため実害なし。
- 公式：https://github.blog/changelog/2026-11-12-actions-for-arm32-linux-windows-retirement

### 2026-11-12（pages build and deployment の注釈で表示）
**Node.js 20 の廃止に伴う強制移行**
- 種別：更新（対象：Actions / Pages）
- 原文（注釈の抜粋）: "Node.js 20 is deprecated."（actions/upload-artifact@v4 が Node.js 24 で実行される旨の警告）
- 訳：Node.js 20 は廃止予定となり、対象のアクションは Node.js 24 で強制実行される。GitHub 側の Pages 公開まわりの仕組みの話で、このリポジトリのワークフローの問題ではない。

### 2026-11-12（pages build and deployment の注釈で表示）
**ubuntu-latest の移行予告**
- 種別：更新（対象：Actions）
- 原文（注釈の抜粋）: "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026"
- 訳：ubuntu-latest ラベルは 2026 年 10 月 19 日から Ubuntu 26 へ移行する、という案内。generate.py は標準ライブラリのみで動くため、このリポジトリへの実害は小さい。

### 2026-11-12 05:48 – 06:21
**Impact across multiple GitHub products including Actions, Pages, and Copilot products.**
- 種別：障害（GitHub Status / critical、対象：Webhooks, Actions, Pages, Copilot）
- 原文抜粋: "The backlog of Actions jobs has been fully processed. We're observing full recovery across all impacted services."
- 訳：Actions、Pages、Copilot など複数製品に影響する障害。Actions ジョブの滞留が発生し、すべて処理されて復旧が確認された。
- 公式：https://www.githubstatus.com/incidents/dvy0t3mvh1lg

### 2026-11-11 01:10 – 02:55
**Incident with Git Operations and Pull Requests**
- 種別：障害（GitHub Status / critical、対象：Pull Requests, Actions）
- 原文抜粋: "We continue to investigate elevated response times for Git operations and pull requests. Actions workflows are recovering."
- 訳：Git 操作とプルリクエストの応答時間が悪化した障害。Actions のワークフローは回復に向かった。
- 公式：https://www.githubstatus.com/incidents/hnf21m9jkl3c

### 2026-11-10 03:12 – 03:59
**Incident with Actions and Checks API**
- 種別：障害（GitHub Status / critical、対象：Webhooks, Actions, Pages）
- 原文抜粋: "Pages is experiencing degraded performance. We are continuing to investigate."
- 訳：Actions と Checks API の障害。Pages も性能低下の対象になった。
- 公式：https://www.githubstatus.com/incidents/tp8cghg7tlc4

### 2026-11-09 19:00 – 20:50
**Incident with Webhooks and Actions**
- 種別：障害（GitHub Status / major、対象：Webhooks, Actions）
- 原文抜粋: "Webhooks is experiencing degraded performance. We are continuing to investigate."
- 訳：Webhooks と Actions の障害。
- 公式：https://www.githubstatus.com/incidents/xxb3l2bm76dr

### 2026-11-09 18:01
**Secret scanning detects secrets in GitHub Actions workflow logs**
- 種別：更新（GitHub Changelog、対象：Actions）
- 原文抜粋: "GitHub secret scanning now detects secrets in GitHub Actions workflow logs, in addition to issues, wikis, discussions, and pull requests."
- 訳：GitHub のシークレットスキャンが、Issues・Wiki・Discussions・プルリクエストに加えて、Actions のワークフローログ内のシークレットも検出するようになった。パブリックプレビュー。
- 公式：https://github.blog/changelog/2026-11-09-secret-scanning-detects-secrets-in-github-actions-workflow-logs/

### 2026-11-09 14:59 – 18:09
**Increased timeouts due to surge in anonymous users**
- 種別：障害（GitHub Status / minor、対象：API Requests）
- 原文抜粋: "CI jobs and release downloads may fail with a 504 Gateway Timeout status if they make anonymous calls."
- 訳：匿名ユーザーの急増でタイムアウトが増えた障害。匿名での呼び出しでは CI ジョブやリリースのダウンロードが 504 Gateway Timeout で失敗する場合があった。
- 公式：https://www.githubstatus.com/incidents/c9px7cw2ghrs

### 2026-11-08 19:36 – 21:32
**Increase in timeouts for some unauthenticated users**
- 種別：障害（GitHub Status / minor、対象：API Requests）
- 原文抜粋: "The degradation affecting API Requests has been mitigated. We are monitoring to ensure stability."
- 訳：一部の未認証ユーザーでタイムアウトが増えた障害（API Requests）。
- 公式：https://www.githubstatus.com/incidents/pyynvrm1vskw

### 2026-11-06 08:36 – 09:20
**Degraded performance for multiple GitHub services**
- 種別：障害（GitHub Status / minor、対象：Git Operations, Issues, Actions, Pages）
- 原文抜粋: "All affected services, including Git operations, Issues, Actions, and API access, have recovered and remained stable."
- 訳：複数サービスの性能低下。Actions と Pages も対象に含まれた。
- 公式：https://www.githubstatus.com/incidents/pfbmpxxfq1cy

### 2026-11-06 01:50 – 02:42
**Incident with Actions**
- 種別：障害（GitHub Status / minor、対象：Actions）
- 原文抜粋: "Some GitHub Actions workflow runs may experience delays or errors when starting. We're investigating and preparing a mitigation."
- 訳：Actions のワークフロー実行の開始に、遅延やエラーが出る場合がある障害。
- 公式：https://www.githubstatus.com/incidents/t89g2q1800fr

### 2026-11-05 02:40 – 03:16
**Incident with Actions**
- 種別：障害（GitHub Status / major、対象：Actions）
- 原文抜粋: "We have identified an issue with events that might trigger Actions. We have applied mitigations and are monitoring for recovery at this point."
- 訳：Actions を起動するイベント側に問題があった障害。
- 公式：https://www.githubstatus.com/incidents/h02n9572mx9y

### 2026-11-05 01:05 – 02:01
**Incident with Actions and Pages**
- 種別：障害（GitHub Status / major、対象：Webhooks, Actions, Pages）
- 原文抜粋: "On November 4, 2026, between 15:49 UTC and 16:48 UTC, and again between 17:20 UTC and 17:55 UTC, GitHub Actions, Pages, Webhooks, Code Scanning, and Copilot code…"（解決後のまとめ文より）
- 訳：Actions と Pages の障害。別のインシデントと合わせた総括がこちらにまとめられた。
- 公式：https://www.githubstatus.com/incidents/xr3myzj7ms51

### 2026-11-04 18:49 – 20:50
**Incident with Pull Requests, Git Operations and Issues**
- 種別：障害（GitHub Status / major、対象：Git Operations, API Requests, Issues, Pull Requests, Actions）
- 原文抜粋: "The degradation affecting Actions has been mitigated. We are monitoring to ensure stability."
- 訳：プルリクエスト、Git 操作、Issues の障害。Actions と API Requests も対象に含まれた。
- 公式：https://www.githubstatus.com/incidents/smtdswd1h2w4

### 2026-11-03 22:25 – 22:56
**Incident with API, Git, and Copilot requests**
- 種別：障害（GitHub Status / minor、対象：API Requests, Issues, Copilot）
- 原文抜粋: "API Requests is operating normally."
- 訳：API、Git、Copilot へのリクエストに関する障害。
- 公式：https://www.githubstatus.com/incidents/rxlj89wpk7px

