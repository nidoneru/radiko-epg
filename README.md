# radiko-epg

radiko の番組表を、エリア別・日別に見渡せる静的サイトです。

- 公開先: https://nidoneru.github.io/radiko-epg/
- 全47エリア対応（プルダウンで切り替え、地方ごとにグループ表示）
- 今日（放送日：5時切り替え）から7日分
- 局名は radiko 公式の各局ライブページへのリンク
- 番組タイトルをタップすると紹介文・出演者がその場で開きます
- 「放送中」の判定は、開いた端末の時計で自動計算します

## 仕組み

GitHub Actions が5時（JST）を起点に3時間おきに `generate.py` を実行し、
radiko の公開フィードから番組データを取得して HTML を生成、
`gh-pages` ブランチへ公開します。

- エリア別局一覧: `http://radiko.jp/v2/station/list/{area}.xml`
- 局・日別番組表: `https://radiko.jp/v3/program/station/date/{yyyymmdd}/{station}.xml`

## 注意

このサイトは radiko 公式のものではありません。番組データは株式会社radiko
および各放送局が提供する情報をもとに表示しています。番組の聴取は radiko
公式サイトをご利用ください。無料で聴取できるのは、お住まいのエリアで
配信されている放送局のみです。
