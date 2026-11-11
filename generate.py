#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
radiko-epg generator.

radiko の番組データをエリア別・日別に取得し、静的な番組表サイトを生成する。
- 対応エリア: JP1〜JP47 全て
- 期間: 実行時点の放送日（05:00 切り替え、JST）から7日分
- 出力: <out>/<area>/<yyyymmdd>.html と <out>/index.html

データ元（いずれも認証不要の公開フィード）:
- エリア別局一覧: http://radiko.jp/v2/station/list/{area}.xml
- 局・日別番組表: https://radiko.jp/v3/program/station/date/{yyyymmdd}/{station}.xml
"""
import html
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
DAYS = 7
WORKERS = 10

AREA_NAMES = [
    ("JP1", "北海道"), ("JP2", "青森"), ("JP3", "岩手"), ("JP4", "宮城"),
    ("JP5", "秋田"), ("JP6", "山形"), ("JP7", "福島"), ("JP8", "茨城"),
    ("JP9", "栃木"), ("JP10", "群馬"), ("JP11", "埼玉"), ("JP12", "千葉"),
    ("JP13", "東京"), ("JP14", "神奈川"), ("JP15", "新潟"), ("JP16", "富山"),
    ("JP17", "石川"), ("JP18", "福井"), ("JP19", "山梨"), ("JP20", "長野"),
    ("JP21", "岐阜"), ("JP22", "静岡"), ("JP23", "愛知"), ("JP24", "三重"),
    ("JP25", "滋賀"), ("JP26", "京都"), ("JP27", "大阪"), ("JP28", "兵庫"),
    ("JP29", "奈良"), ("JP30", "和歌山"), ("JP31", "鳥取"), ("JP32", "島根"),
    ("JP33", "岡山"), ("JP34", "広島"), ("JP35", "山口"), ("JP36", "徳島"),
    ("JP37", "香川"), ("JP38", "愛媛"), ("JP39", "高知"), ("JP40", "福岡"),
    ("JP41", "佐賀"), ("JP42", "長崎"), ("JP43", "熊本"), ("JP44", "大分"),
    ("JP45", "宮崎"), ("JP46", "鹿児島"), ("JP47", "沖縄"),
]
REGIONS = [
    ("北海道", ["JP1"]),
    ("東北", ["JP2", "JP3", "JP4", "JP5", "JP6", "JP7"]),
    ("関東", ["JP8", "JP9", "JP10", "JP11", "JP12", "JP13", "JP14"]),
    ("中部", ["JP15", "JP16", "JP17", "JP18", "JP19", "JP20", "JP21", "JP22", "JP23"]),
    ("近畿", ["JP24", "JP25", "JP26", "JP27", "JP28", "JP29", "JP30"]),
    ("中国", ["JP31", "JP32", "JP33", "JP34", "JP35"]),
    ("四国", ["JP36", "JP37", "JP38", "JP39"]),
    ("九州・沖縄", ["JP40", "JP41", "JP42", "JP43", "JP44", "JP45", "JP46", "JP47"]),
]
AREA_NAME = dict(AREA_NAMES)
WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]
DEFAULT_AREA = "JP13"

CSS = """
html, body { height: 100%; }
body { font-family: sans-serif; margin: 0; color: #222;
       display: flex; flex-direction: column; height: 100vh; height: 100dvh; }
header { flex: none; padding: 8px 8px 0; background: #fff; }
h1 { font-size: 18px; margin: 4px 0; }
.note { font-size: 12px; color: #666; }
.bar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
select { font-size: 15px; padding: 4px; }
.tabs { display: flex; gap: 4px; flex-wrap: wrap; margin: 6px 0; }
.tab { padding: 4px 10px; border: 1px solid #999; border-radius: 12px; font-size: 13px;
       color: #333; text-decoration: none; background: #f4f4f4; }
.tab.on { background: #01378E; color: #fff; border-color: #01378E; }
.wrap { flex: 1; overflow: auto; border-top: 1px solid #ccc; }
table { border-collapse: separate; border-spacing: 0; font-size: 11.5px; min-width: 100%; }
th, td { border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 3px 4px;
         vertical-align: top; min-width: 118px; background: #fff; }
thead th { background: #01378E; color: #fff; position: sticky; top: 0; z-index: 2; font-size: 12px; }
thead th a { color: #fff; text-decoration: underline; }
th.hr { background: #eef1f6; min-width: 30px; text-align: center; position: sticky; left: 0; z-index: 1; }
thead th.hr { background: #01378E; z-index: 3; }
.pr { margin-bottom: 5px; line-height: 1.35; }
.tm { color: #666; font-size: 10.5px; display: block; }
.ti.has { cursor: pointer; text-decoration: underline dotted #999; }
.dt { margin-top: 2px; padding: 4px; background: #f6f8fb; border-left: 3px solid #01378E;
      font-size: 11px; color: #444; }
.pr.now { background: #fff3bf; outline: 2px solid #f5a623; border-radius: 3px; }
.pr.now::before { content: "放送中 "; color: #c00; font-weight: bold; font-size: 10.5px; }
footer { flex: none; padding: 4px 8px 8px; }
"""

JS = """
function fmt(d) {
  function p(n) { return (n < 10 ? '0' : '') + n; }
  return '' + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) +
         p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
}
function markNow() {
  var now = fmt(new Date());
  var cur = null;
  document.querySelectorAll('.pr').forEach(function(el) {
    var on = el.dataset.ft <= now && now < el.dataset.to;
    el.classList.toggle('now', on);
    if (on) cur = el;
  });
  return cur;
}
var first = markNow();
if (first && document.body.dataset.today === '1') {
  first.scrollIntoView({ block: 'center' });
}
setInterval(markNow, 60000);
document.querySelectorAll('.ti.has').forEach(function(el) {
  el.addEventListener('click', function() {
    var dt = el.parentElement.querySelector('.dt');
    if (dt) dt.hidden = !dt.hidden;
  });
});
var sel = document.getElementById('area');
if (sel) {
  try { localStorage.setItem('radiko-epg-area', sel.dataset.current); } catch (e) {}
  sel.addEventListener('change', function() {
    try { localStorage.setItem('radiko-epg-area', sel.value); } catch (e) {}
    location.href = '../' + sel.value + '/' + document.body.dataset.date + '.html';
  });
}
"""

INDEX_JS = """
try {
  var a = localStorage.getItem('radiko-epg-area') || 'JP13';
  location.replace(a + '/__TODAY__.html');
} catch (e) {
  location.replace('JP13/__TODAY__.html');
}
"""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "radiko-epg/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if data[:2] == b"\x1f\x8b":  # some radiko endpoints answer gzip unasked
        import gzip
        data = gzip.decompress(data)
    return data


def area_stations(area):
    """[(station_id, name), ...] for one area, in radiko's own order."""
    root = ET.fromstring(fetch(f"http://radiko.jp/v2/station/list/{area}.xml"))
    out = []
    for st in root.iter("station"):
        sid = st.findtext("id")
        name = st.findtext("name")
        if sid:
            out.append((sid.strip(), (name or sid).strip()))
    return out


def station_day(sid, date_str):
    """Programs of one station on one broadcast date; [] on any failure."""
    try:
        root = ET.fromstring(fetch(
            f"https://radiko.jp/v3/program/station/date/{date_str}/{sid}.xml"))
    except Exception as e:  # a missing day must not kill the whole build
        print(f"WARN: {sid} {date_str}: {e}", file=sys.stderr)
        return []
    progs = []

    def txt(p, tag):
        el = p.find(tag)
        return (el.text or "").strip() if el is not None and el.text else ""

    for p in root.iter("prog"):
        progs.append({"ft": p.get("ft"), "to": p.get("to"),
                      "title": txt(p, "title"), "desc": txt(p, "desc"),
                      "pfm": txt(p, "pfm")})
    return progs


def clean_desc(s):
    """Feed descriptions carry raw HTML (<br>, <a ...>) as text.
    Keep <br> as line breaks, strip every other tag (its text stays),
    escape the rest. Links are intentionally left untappable."""
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    lines = [ln.strip() for ln in s.split("\n")]
    return "<br>".join(html.escape(ln) for ln in lines if ln)


def hm(ts):
    return f"{int(ts[8:10])}:{ts[10:12]}"


def bkey(ts, date_str):
    h = int(ts[8:10])
    if ts[:8] == date_str:
        return h if h >= 5 else h + 24
    return h + 24


def end_label(ft, to):
    end = hm(to)
    if to[:8] != ft[:8] and int(to[8:10]) < 12:
        end = f"{int(to[8:10]) + 24}:{to[10:12]}"
    return end


def render_page(area, date_str, days, stations, data, is_today, now_jst):
    """data: {(station_id, date_str): [prog, ...]}"""
    d = datetime.strptime(date_str, "%Y%m%d").date()
    area_opts = []
    for region, codes in REGIONS:
        opts = "".join(
            f'<option value="{c}"{" selected" if c == area else ""}>{AREA_NAME[c]}</option>'
            for c in codes)
        area_opts.append(f'<optgroup label="{region}">{opts}</optgroup>')

    tabs = []
    for i, ds in enumerate(days):
        dd = datetime.strptime(ds, "%Y%m%d").date()
        label = ("今日 " if i == 0 else "") + f"{dd.month}/{dd.day}({WEEKDAYS[dd.weekday()]})"
        cls = "tab on" if ds == date_str else "tab"
        tabs.append(f'<a class="{cls}" href="{ds}.html">{label}</a>')

    cols = []
    for sid, name in stations:
        by_hour = {}
        for pr in data.get((sid, date_str), []):
            by_hour.setdefault(bkey(pr["ft"], date_str), []).append(pr)
        cols.append((sid, name, by_hour))

    head_cells = "".join(
        f'<th><a href="https://radiko.jp/#!/live/{sid}" target="_blank" '
        f'rel="noopener">{html.escape(n)}</a></th>' for sid, n, _ in cols)

    rows = []
    for hour in range(5, 29):
        disp_h = hour if hour < 24 else hour - 24
        cells = [f'<th class="hr">{disp_h}</th>']
        for sid, name, by_hour in cols:
            items = []
            for pr in by_hour.get(hour, []):
                body = clean_desc(pr["desc"]) if pr["desc"] else ""
                if pr["pfm"]:
                    body += ("<br>" if body else "") + "出演者：" + html.escape(pr["pfm"])
                detail = f'<div class="dt" hidden>{body}</div>' if body else ""
                tcls = ' class="ti has"' if body else ' class="ti"'
                items.append(
                    f'<div class="pr" data-ft="{pr["ft"]}" data-to="{pr["to"]}">'
                    f'<span class="tm">{hm(pr["ft"])}–{end_label(pr["ft"], pr["to"])}</span> '
                    f'<span{tcls}>{html.escape(pr["title"])}</span>{detail}</div>')
            cells.append(f"<td>{''.join(items)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    gen = now_jst.strftime("%Y/%m/%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{AREA_NAME[area]}の番組表 {d.month}/{d.day}({WEEKDAYS[d.weekday()]}) | radiko-epg</title>
<style>{CSS}</style>
</head>
<body data-date="{date_str}" data-today="{1 if is_today else 0}">
<header>
<h1>radiko-epg <span class="note">{AREA_NAME[area]} {d.month}/{d.day}({WEEKDAYS[d.weekday()]}) の番組表</span></h1>
<div class="bar">
  <label>エリア <select id="area" data-current="{area}">{''.join(area_opts)}</select></label>
  <span class="note">最終更新 {gen}</span>
</div>
<div class="tabs">{''.join(tabs)}</div>
</header>
<div class="wrap">
<table>
<thead><tr><th class="hr">時</th>{head_cells}</tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>
<footer>
<p class="note">放送中の判定はこのページが端末の時計で自動で行います。このサイトは radiko 公式のものではありません。番組データは株式会社radikoおよび各放送局が提供する情報をもとに表示しています。番組内容は変更される場合があります。番組の聴取は radiko 公式サイトをご利用ください。無料で聴取できるのは、お住まいのエリアで配信されている放送局のみです。</p>
</footer>
<script>{JS}</script>
</body>
</html>
"""


def broadcast_today(now_jst):
    d = now_jst.date()
    if now_jst.hour < 5:
        d -= timedelta(days=1)
    return d


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "site"
    now_jst = datetime.now(JST)
    first = broadcast_today(now_jst)
    days = [(first + timedelta(days=i)).strftime("%Y%m%d") for i in range(DAYS)]
    print(f"broadcast days: {days[0]} .. {days[-1]} (now {now_jst:%Y-%m-%d %H:%M} JST)")

    # 1) station lists for all areas
    area_map = {}
    all_stations = set()
    for code, _ in AREA_NAMES:
        sts = area_stations(code)
        area_map[code] = sts
        all_stations.update(sid for sid, _ in sts)
    print(f"areas: {len(area_map)}, unique stations: {len(all_stations)}")

    # 2) fetch every (station, day) once, in parallel
    jobs = [(sid, ds) for sid in sorted(all_stations) for ds in days]
    data = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for (sid, ds), progs in zip(jobs, ex.map(lambda j: station_day(*j), jobs)):
            data[(sid, ds)] = progs
    got = sum(1 for v in data.values() if v)
    print(f"station-days fetched: {got}/{len(jobs)} non-empty")

    # 3) render
    os.makedirs(out_dir, exist_ok=True)
    for code, _ in AREA_NAMES:
        adir = os.path.join(out_dir, code)
        os.makedirs(adir, exist_ok=True)
        for i, ds in enumerate(days):
            page = render_page(code, ds, days, area_map[code], data,
                               is_today=(i == 0), now_jst=now_jst)
            with open(os.path.join(adir, f"{ds}.html"), "w", encoding="utf-8") as fp:
                fp.write(page)
    index = ("<!DOCTYPE html>\n<html lang=\"ja\"><head><meta charset=\"utf-8\">"
             "<title>radiko-epg</title></head><body>"
             f"<script>{INDEX_JS.replace('__TODAY__', days[0])}</script>"
             f'<noscript><a href="{DEFAULT_AREA}/{days[0]}.html">番組表を開く</a></noscript>'
             "</body></html>\n")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(index)
    print(f"done -> {out_dir}")


if __name__ == "__main__":
    main()
