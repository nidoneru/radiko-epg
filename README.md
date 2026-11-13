# radiko-epg

radiko の番組表を、エリア別・日別に見渡せるサイトを生成するスクリプトと、その運用記録を置いたリポジトリです。

- 公開先: https://nidoneru.github.io/radiko-epg/
- 全47エリア対応（プルダウンで切り替え、地方ごとにグループ表示）
- 今日（放送日：5時切り替え）から7日分
- 局名は radiko 公式の各局ライブページへのリンク
- 番組タイトルをタップすると紹介文・出演者がその場で開きます
- 「放送中」の判定は、開いた端末の時計で自動計算します
- 単一ページのアプリです。URL は常にルートのみで、エリアと日付はページ内で切り替えます（選んだエリアはブラウザに記憶されます）

## 仕組み

GitHub Actions が5時（JST）を起点に3時間おきに `generate.py` を実行し、
radiko の公開フィードから番組データを取得して、アプリ本体（index.html）と
エリア別・日別の JSON データを生成し、`gh-pages` ブランチへ公開します。
表示はブラウザ側で行います。

- エリア別局一覧: `http://radiko.jp/v2/station/list/{area}.xml`
- 局・日別番組表: `https://radiko.jp/v3/program/station/date/{yyyymmdd}/{station}.xml`

## リポジトリ内のファイル

- `generate.py`：radiko の公開フィードから番組データを取得し、アプリ本体（index.html）と JSON データを生成するスクリプト（Python 標準ライブラリのみで動作）
- `.github/workflows/generate.yml`：3時間おき（日本時間 02:07、05:07、…）に `generate.py` を実行し、`gh-pages` ブランチへ公開する GitHub Actions のワークフロー
- `README.md`：このファイル（サイトと仕組みの説明）
- `GITHUB-NOTES.md`：GitHub 公式発表（Actions / Pages の障害情報・更新情報）の記録。原文（英語）と日本語訳を併記し、運用中の事象との照合に使う資料
- `CROSS-CHECK.md`：このサイトで起きた事象（スケジュールの不発・遅延など）と、GitHub 公式発表を照らし合わせた記録

## 注記

- 番組情報の取得方法は radiko が公式に公開しているものではないため、仕様変更などにより動かなくなる場合がある
