#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
radiko-epg generator (SPA version).

radiko の番組データをエリア別・日別に取得し、単一ページアプリとして生成する。
- 対応エリア: JP1〜JP47 全て
- 期間: 実行時点の放送日（05:00 切り替え、JST）から7日分
- 出力: <out>/index.html（アプリ本体）、<out>/data/<area>/<yyyymmdd>.json、
  <out>/manifest.json（生成時刻と対象日）、favicon 一式、404.html
  URL は常にサイトのルートのみ（エリア・日付はアプリ内状態で保持）。

データ元（いずれも認証不要の公開フィード）:
- エリア別局一覧: http://radiko.jp/v2/station/list/{area}.xml
- 局・日別番組表: https://radiko.jp/v3/program/station/date/{yyyymmdd}/{station}.xml
"""
import base64
import html
import json
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

AREA_NAMES = [('JP1', '北海道'), ('JP2', '青森'), ('JP3', '岩手'), ('JP4', '宮城'), ('JP5', '秋田'), ('JP6', '山形'), ('JP7', '福島'), ('JP8', '茨城'), ('JP9', '栃木'), ('JP10', '群馬'), ('JP11', '埼玉'), ('JP12', '千葉'), ('JP13', '東京'), ('JP14', '神奈川'), ('JP15', '新潟'), ('JP16', '富山'), ('JP17', '石川'), ('JP18', '福井'), ('JP19', '山梨'), ('JP20', '長野'), ('JP21', '岐阜'), ('JP22', '静岡'), ('JP23', '愛知'), ('JP24', '三重'), ('JP25', '滋賀'), ('JP26', '京都'), ('JP27', '大阪'), ('JP28', '兵庫'), ('JP29', '奈良'), ('JP30', '和歌山'), ('JP31', '鳥取'), ('JP32', '島根'), ('JP33', '岡山'), ('JP34', '広島'), ('JP35', '山口'), ('JP36', '徳島'), ('JP37', '香川'), ('JP38', '愛媛'), ('JP39', '高知'), ('JP40', '福岡'), ('JP41', '佐賀'), ('JP42', '長崎'), ('JP43', '熊本'), ('JP44', '大分'), ('JP45', '宮崎'), ('JP46', '鹿児島'), ('JP47', '沖縄')]

REGIONS = [('北海道', ['JP1']), ('東北', ['JP2', 'JP3', 'JP4', 'JP5', 'JP6', 'JP7']), ('関東', ['JP8', 'JP9', 'JP10', 'JP11', 'JP12', 'JP13', 'JP14']), ('中部', ['JP15', 'JP16', 'JP17', 'JP18', 'JP19', 'JP20', 'JP21', 'JP22', 'JP23']), ('近畿', ['JP24', 'JP25', 'JP26', 'JP27', 'JP28', 'JP29', 'JP30']), ('中国', ['JP31', 'JP32', 'JP33', 'JP34', 'JP35']), ('四国', ['JP36', 'JP37', 'JP38', 'JP39']), ('九州・沖縄', ['JP40', 'JP41', 'JP42', 'JP43', 'JP44', 'JP45', 'JP46', 'JP47'])]

AREA_NAME = dict(AREA_NAMES)

WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

DEFAULT_AREA = 'JP13'

CSS = '\nhtml, body { height: 100%; }\nbody { font-family: sans-serif; margin: 0; color: #222;\n       display: flex; flex-direction: column; height: 100vh; height: 100dvh; }\nheader { flex: none; padding: 8px 8px 0; background: #fff; }\nh1 { font-size: 18px; margin: 4px 0; }\n.note { font-size: 12px; color: #666; }\n.bar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin: 8px 0; }\nselect { font-size: 15px; padding: 4px; }\n.tabs { display: flex; gap: 4px; flex-wrap: wrap; margin: 6px 0; }\n.tab { padding: 4px 10px; border: 1px solid #999; border-radius: 12px; font-size: 13px;\n       color: #333; text-decoration: none; background: #f4f4f4; }\n.tab.on { background: #01378E; color: #fff; border-color: #01378E; }\n.wrap { flex: 1; overflow: auto; border-top: 1px solid #ccc; }\ntable { border-collapse: separate; border-spacing: 0; font-size: 11.5px; min-width: 100%; }\nth, td { border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 3px 4px;\n         vertical-align: top; min-width: 118px; background: #fff; }\nthead th { background: #01378E; color: #fff; position: sticky; top: 0; z-index: 2; font-size: 12px; }\nthead th a { color: #fff; text-decoration: underline; }\nth.hr { background: #eef1f6; min-width: 30px; text-align: center; position: sticky; left: 0; z-index: 1; }\nthead th.hr { background: #01378E; z-index: 3; }\n.pr { margin-bottom: 5px; line-height: 1.35; }\n.tm { color: #666; font-size: 10.5px; display: block; }\n.ti.has { cursor: pointer; text-decoration: underline dotted #999; }\n.dt { margin-top: 2px; padding: 4px; background: #f6f8fb; border-left: 3px solid #01378E;\n      font-size: 11px; color: #444; }\n.pr.now { background: #fff3bf; outline: 2px solid #f5a623; border-radius: 3px; }\n.pr.now::before { content: "放送中 "; color: #c00; font-weight: bold; font-size: 10.5px; }\nfooter { flex: none; padding: 4px 8px 8px; }\nfooter details { font-size: 10px; color: #666; }\nfooter summary { cursor: pointer; padding: 2px 0; }\nfooter ul { margin: 4px 0 2px; padding-left: 16px; line-height: 1.6; }\n@media (min-width: 641px) { footer summary { display: none; } }\n'

FAVICON_FILES = {'favicon.ico': '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', 'favicon-16x16.png': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACZUlEQVR42nWTz0tUURTHP+e+++aXjD9SBF2okwUptmlhhZBQyxZRuGnXrm24C0RqEe4KCtr4H0hYtmhRILQLCrca/sgiE1s4NqLvzbx372kxM1qgB87iwPl+7/d7zj0CwNx2iULHQ9JkGJcaRIWTQkUJrMeGy8TxDBPtG8JCuYQGi7QUB6jGgEATrv+ApVkrZHNwsP+DWnTDkuo0rcUB2S/XjIhtopr9Tk9QEh862s704ZNHFmGIaqzqsc6p+e9lA9hjN4GAV1ADxJGicsEGIt45ZKzL6uT5HFYgb4WtyLPwK+HNVoIYEAGXKBiBABARBG8MCB76C4Y7vSFjnZaigXt9GV5faWG824JTfKpMj+QpFQ2kdXEoYpryDp2SKrzcqHJ1bo/HKzEAI20BGik3ezPc6gmZGc4jSl1SwyU0rFqB8S7Lg9ECt3tC1g4877YSBrss90sZdqqe/oLhbJvBO8UI2CaBaTBeag+43FUgCzxdq/JtN2W8P0NHRign9em2WIGY/xUkqjiF2c0ana/KfCk7Js9ludaX4eP3Gm+3EzpCIfbKasUhQX1ZRwQZqa+paOEgUqaWIwCeXcxjc8LztSqVVHmxXiWqKUYEVbAeFIGtWHn/O2VpzyM54cNOyuxmjVLB0N8asP7HcffzIZWqQig4VRBUmN/9RJgfpRYpDoORY12pHk+48cGMgEc9YU6oxUsGkRVyORHUmVC8GPVQzyDEG8tRLaLeox6vjmxeEPkqzO8NYswiLcU+4uhov6eGKmTzcLj/k0Cv17vndwYJi1N4N4RLDXrKOUvjnINwhbjyhInu1b8XJAuQXnFXPgAAAABJRU5ErkJggg==', 'favicon-32x32.png': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAFP0lEQVR42r2XWYwUVRSGv3PrVnVPDzNNo7IooLghxIVE4xIjiWDCg0YWI24PJr7woHGLC4kxPjgx7gnqkw9GfQCjQUB5cIl7NMSFSCCigAEixEHAaXqmp7ur6t7jQ/WMPcMAnRG8yU1X+lbV+c85/3/OKWFoqQoiysZyCcLrcW42zkfgQUUYzxJVMBDaGGN30Gh8ybLi4cxWdoMFFZ5CEPFs6H8QNQ8jwQyiHCd1+RRsuJ/1R1Yh8gKqknn2rgYsF8favjeZNPFu+quQxB5BTyoARbCRobsT+srvsHTinbyHyUK79u/7mVRaRV85BrUghlOxVBUhoVSKKJcfZ2npeWFjuUTsfyXMnU7S4JQZbwURRkoSH6HDzjYkuoCoMJn4fzAOICIkDch3lqiniyxO55C32przQECOmcrmVsZPEhHFBIrXORYRyyh7LjnB202GMhBw40UhCCLWjvwP1MP8qSHnFAxeGaJppiSFSqrsHfRsO+JwsWIiwY8BwjSjeCKAdvRDzimPXZjnxin2uA/+0u/o2V5nzd4YEx4NwrsM8Vhno4N51OpPlFSh7iHVsXkwtytg9ZWdLDozxCdKIC3Z8TCnGLBkRoSP/z1rG4ARsC376V/rrPhpkJVba2yrOIQMnAL3npcbwRcRcA1Pz9w8667u5LZzItxxQNh2+PLGnpg9fSkA7/cmbF3YTdTM8fS8AZuFORBQB4tn5Vi7P2FeMeDNKwpsLjt2VRzGHp2OtnQ/KRLCnGDzhn01T81pxheFQafgMw+dgw4L66/pZMWsiEe21cgb4ck5edSPLe22ANQcJGlG0DumRxRDIWl6vLE3BZcpZEIoLDkz4rkddeafbpmSM3xzOGX5WSFdHQY3Boi2UrDmygKDqVIMhbndQSZPYGNvwqqddWxOSGNl6cyIty8vsGRTlXKi3DTV8tXBlOtOs5zbadhyOMWEMkKabQG4rBgMX6dNz9/aG3PPpioSCjbIpFG0mX8zC4ZDDWVyzlB1DgUmWGlfBWNpfkvZEftMFV7hrhkRPfM60CF3DOyqevbXPLsGPGcXDNv7HVNy2exxsJHFX8cD4LbvB5n3SYWrvujnj5pHmv3iidl55k8NSWLFhsJHvQmLvq3y6AU5QgPr/0y4aVrIgYZnd9VDIOh4VGCaHerngyn3bakNKwDgmbn5Yc8MsGfAcXF3wMu7GswqGM7vNLz6e0zSUOx4I9Ds44Qdwgf7E37sc0QGEg/XnmZZOC3Mik0AVQeXflqht+556ZIOtvc7XtlZP4p8xwXgNCPb0NaWZoVTenbUAUg0K9krL8gPP2cD6B3wnNcZcKChLP6uSn+SyUbbJWExFKxAs8gxRGCnYELhw30J2yqOQpDdd8Nky80zI3ySmZBIeGhrjXmfV9h5jAo4pgy9Zrl+fXeDrw8lw+14X92DyV4iAl6VezYPsuAMS+rBmiYnmgpRgVqq1BJO2A3t6C6HgQ1/xGzwLQehDBNNFbDCD4dSfjiQjoylFXxLUxoCdPx5QDRlVHqCUEaUTDd6QFIwVjAt8D0jjZ1wUFIUkdSC+Q2fCsqw1XbGLK/gxz8ZC94Jqr8ZGPic+uAhwlxzIDvFS1WxETQGj2DDjw3Lph/GyLN0FQyQoqqn1DgkdE8weH2RxV0Hsk+zW/GsK6+mNPF2KgOQxh6Rk/xppoINDd1d0Ne3jrR0a1ZbVGV4Vl9fWYmxDxAEUzFBS/X5T9+EzV8Hzv2FT1/j5q6e1kl8CEgGYnXvFIrdC0ncReAjnPtvEIJAMTbGyA4aA59xy+Q/m4gERP8BWttwMB9Zmj0AAAAASUVORK5CYII=', 'apple-touch-icon.png': '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'}

FAVICON_LINKS = '<link rel="icon" href="{p}favicon.ico" sizes="any"><link rel="icon" href="{p}favicon-32x32.png" sizes="32x32" type="image/png"><link rel="icon" href="{p}favicon-16x16.png" sizes="16x16" type="image/png"><link rel="apple-touch-icon" href="{p}apple-touch-icon.png" sizes="180x180">'

NOT_FOUND_HTML = '<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<title>radiko-epg</title>\n</head>\n<body>\n<p>このページは移動しました。<a href="/radiko-epg/">radiko-epg トップへ</a></p>\n<script>\ntry {\n  if (!sessionStorage.getItem(\'epg404\')) {\n    sessionStorage.setItem(\'epg404\', \'1\');\n    location.replace(\'/radiko-epg/\');\n  }\n} catch (e) {}\n</script>\n</body>\n</html>\n'

APP_JS = '// radiko-epg SPA prototype: renders the guide client-side from per-area/day JSON.\n// Data sources: window.EPG_EMBED (single-file demo) or fetch(\'data/<area>/<date>.json\').\nvar META = window.EPG_META;\nvar state = { area: \'JP13\', date: META.days[0], data: null };\ntry {\n  state.area = localStorage.getItem(\'radiko-epg-area\') || \'JP13\';\n} catch (e) {}\n// URL is always the bare root (Suto\'s decision 2026-11-13): no query params\n// are read or written; area/date live only in app state + localStorage.\n\nfunction esc(s) {\n  return (s || \'\').replace(/&/g, \'&amp;\').replace(/</g, \'&lt;\')\n                  .replace(/>/g, \'&gt;\').replace(/"/g, \'&quot;\');\n}\nfunction p2(n) { return (n < 10 ? \'0\' : \'\') + n; }\nfunction fmt(d) {\n  return \'\' + d.getFullYear() + p2(d.getMonth() + 1) + p2(d.getDate()) +\n         p2(d.getHours()) + p2(d.getMinutes()) + p2(d.getSeconds());\n}\nfunction broadcastToday() {\n  var n = new Date();\n  if (n.getHours() < 5) n.setDate(n.getDate() - 1);\n  return \'\' + n.getFullYear() + p2(n.getMonth() + 1) + p2(n.getDate());\n}\nfunction hm(ts) { return parseInt(ts.substr(8, 2), 10) + \':\' + ts.substr(10, 2); }\nfunction endLabel(ft, to) {\n  var e = hm(to);\n  if (to.substr(0, 8) !== ft.substr(0, 8) && parseInt(to.substr(8, 2), 10) < 12) {\n    e = (parseInt(to.substr(8, 2), 10) + 24) + \':\' + to.substr(10, 2);\n  }\n  return e;\n}\nfunction bkey(ft, date) {\n  var h = parseInt(ft.substr(8, 2), 10);\n  if (ft.substr(0, 8) === date) return h >= 5 ? h : h + 24;\n  return h + 24;\n}\nfunction dateLabel(ds, withYear) {\n  var y = parseInt(ds.substr(0, 4), 10), m = parseInt(ds.substr(4, 2), 10),\n      d = parseInt(ds.substr(6, 2), 10);\n  var wd = META.weekdays[new Date(y, m - 1, d).getDay() === 0 ? 6 : new Date(y, m - 1, d).getDay() - 1];\n  return (withYear ? y + \'/\' : \'\') + m + \'/\' + d + \'(\' + wd + \')\';\n}\n\nfunction buildHeader() {\n  var sel = document.getElementById(\'area\');\n  var html = \'\';\n  META.regions.forEach(function(rg) {\n    html += \'<optgroup label="\' + esc(rg[0]) + \'">\';\n    rg[1].forEach(function(c) {\n      html += \'<option value="\' + c + \'"\' + (c === state.area ? \' selected\' : \'\') +\n              \'>\' + esc(META.areaName[c]) + \'</option>\';\n    });\n    html += \'</optgroup>\';\n  });\n  sel.innerHTML = html;\n  var tabs = \'\';\n  META.days.forEach(function(ds, i) {\n    tabs += \'<a class="tab\' + (ds === state.date ? \' on\' : \'\') + \'" href="#" data-date="\' +\n            ds + \'">\' + (i === 0 ? \'今日 \' : \'\') + dateLabel(ds) + \'</a>\';\n  });\n  document.getElementById(\'tabs\').innerHTML = tabs;\n}\n\nfunction render(data) {\n  state.data = data;\n  document.getElementById(\'h1note\').textContent =\n    META.areaName[state.area] + \' \' + dateLabel(state.date) + \' の番組表\';\n  document.getElementById(\'gen\').textContent = \'最終更新 \' + META.generated;\n  document.title = META.areaName[state.area] + \'の番組表 \' + dateLabel(state.date) + \' | radiko-epg\';\n  var head = \'<tr><th class="hr">時</th>\';\n  data.stations.forEach(function(st) {\n    head += \'<th><a href="https://radiko.jp/#!/live/\' + st[0] +\n            \'" target="_blank" rel="noopener">\' + esc(st[1]) + \'</a></th>\';\n  });\n  head += \'</tr>\';\n  document.querySelector(\'thead\').innerHTML = head;\n  // bucket programs per station per hour\n  var buckets = data.stations.map(function(st) {\n    var byHour = {};\n    (data.progs[st[0]] || []).forEach(function(pr) {\n      var k = bkey(pr.f, state.date);\n      (byHour[k] = byHour[k] || []).push(pr);\n    });\n    return byHour;\n  });\n  var rows = \'\';\n  for (var hour = 5; hour < 29; hour++) {\n    rows += \'<tr><th class="hr">\' + (hour < 24 ? hour : hour - 24) + \'</th>\';\n    data.stations.forEach(function(st, si) {\n      rows += \'<td>\';\n      (buckets[si][hour] || []).forEach(function(pr) {\n        var body = pr.d || \'\';\n        if (pr.p) body += (body ? \'<br>\' : \'\') + \'出演者：\' + esc(pr.p);\n        rows += \'<div class="pr" data-ft="\' + pr.f + \'" data-to="\' + pr.t + \'">\' +\n                \'<span class="tm">\' + hm(pr.f) + \'–\' + endLabel(pr.f, pr.t) + \'</span> \' +\n                \'<span class="ti\' + (body ? \' has\' : \'\') + \'">\' + esc(pr.ti) + \'</span>\' +\n                (body ? \'<div class="dt" hidden>\' + body + \'</div>\' : \'\') + \'</div>\';\n      });\n      rows += \'</td>\';\n    });\n    rows += \'</tr>\';\n  }\n  document.querySelector(\'tbody\').innerHTML = rows;\n  buildHeader();\n  var cur = markNow();\n  if (cur && state.date === broadcastToday()) {\n    var wrap = document.querySelector(\'.wrap\');\n    var er = cur.getBoundingClientRect(), wr = wrap.getBoundingClientRect();\n    wrap.scrollTop += (er.top - wr.top) - (wrap.clientHeight - er.height) / 2;\n  }\n}\n\nfunction markNow() {\n  var now = fmt(new Date()), cur = null;\n  document.querySelectorAll(\'.pr\').forEach(function(el) {\n    var on = el.dataset.ft <= now && now < el.dataset.to;\n    el.classList.toggle(\'now\', on);\n    if (on) cur = el;\n  });\n  return cur;\n}\n\nfunction load(area, date) {\n  state.area = area; state.date = date;\n  if (window.EPG_EMBED) {\n    var d = window.EPG_EMBED[area + \'/\' + date];\n    if (d) { render(d); }\n    else {\n      document.querySelector(\'tbody\').innerHTML =\n        \'<tr><td style="min-width:300px">この試作デモには東京（JP13）のデータだけが入っています。</td></tr>\';\n      buildHeader();\n    }\n    return;\n  }\n  fetch(\'data/\' + area + \'/\' + date + \'.json\')\n    .then(function(r) { return r.json(); })\n    .then(render)\n    .catch(function() {\n      document.querySelector(\'tbody\').innerHTML =\n        \'<tr><td style="min-width:300px">データを読み込めませんでした。</td></tr>\';\n    });\n}\n\ndocument.getElementById(\'area\').addEventListener(\'change\', function() {\n  try { localStorage.setItem(\'radiko-epg-area\', this.value); } catch (e) {}\n  load(this.value, state.date);\n});\ndocument.getElementById(\'tabs\').addEventListener(\'click\', function(ev) {\n  var a = ev.target.closest(\'a[data-date]\');\n  if (!a) return;\n  ev.preventDefault();\n  load(state.area, a.dataset.date);\n});\ndocument.querySelector(\'tbody\').addEventListener(\'click\', function(ev) {\n  var ti = ev.target.closest(\'.ti.has\');\n  if (!ti) return;\n  var dt = ti.parentElement.querySelector(\'.dt\');\n  if (dt) dt.hidden = !dt.hidden;\n});\nvar fd = document.querySelector(\'footer details\');\nif (fd && window.matchMedia(\'(min-width: 641px)\').matches) fd.open = true;\nsetInterval(markNow, 60000);\nload(state.area, state.date);\n'

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


def broadcast_today(now_jst):
    d = now_jst.date()
    if now_jst.hour < 5:
        d -= timedelta(days=1)
    return d



def area_day_json(area, date_str, stations, data):
    progs = {}
    for sid, _name in stations:
        items = []
        for pr in data.get((sid, date_str), []):
            items.append({
                "f": pr["ft"], "t": pr["to"], "ti": pr["title"],
                "d": clean_desc(pr["desc"]) if pr["desc"] else "",
                "p": pr["pfm"],
            })
        if items:
            progs[sid] = items
    return {"area": area, "date": date_str,
            "stations": [[s, n] for s, n in stations], "progs": progs}


def app_html(meta):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>radiko-epg</title>
{FAVICON_LINKS.format(p='')}
<style>{CSS}</style>
</head>
<body>
<header>
<h1>radiko-epg <span class="note" id="h1note"></span></h1>
<div class="bar">
  <label>エリア <select id="area"></select></label>
  <span class="note" id="gen"></span>
</div>
<div class="tabs" id="tabs"></div>
</header>
<div class="wrap">
<table>
<thead></thead>
<tbody></tbody>
</table>
</div>
<footer>
<details>
<summary>注記</summary>
<ul>
<li>放送中の表示は、端末の時計で判定</li>
<li>このサイトは radiko 公式ではない</li>
<li>番組データは株式会社radikoと各放送局の提供情報に基づく</li>
<li>番組内容は変更される場合がある</li>
<li>聴取は radiko 公式サイトで</li>
<li>無料で聴けるのは、自分のエリアの放送局のみ</li>
</ul>
</details>
</footer>
<script>window.EPG_META = {json.dumps(meta, ensure_ascii=False)};</script>
<script>{APP_JS}</script>
</body>
</html>
"""


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "site"
    now_jst = datetime.now(JST)
    first = broadcast_today(now_jst)
    days = [(first + timedelta(days=i)).strftime("%Y%m%d") for i in range(DAYS)]
    print(f"broadcast days: {days[0]} .. {days[-1]} (now {now_jst:%Y-%m-%d %H:%M} JST)")

    area_map = {}
    all_stations = set()
    for code, _ in AREA_NAMES:
        sts = area_stations(code)
        area_map[code] = sts
        all_stations.update(sid for sid, _ in sts)
    print(f"areas: {len(area_map)}, unique stations: {len(all_stations)}")

    jobs = [(sid, ds) for sid in sorted(all_stations) for ds in days]
    data = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for (sid, ds), progs in zip(jobs, ex.map(lambda j: station_day(*j), jobs)):
            data[(sid, ds)] = progs
    got = sum(1 for v in data.values() if v)
    print(f"station-days fetched: {got}/{len(jobs)} non-empty")

    meta = {
        "days": days,
        "generated": now_jst.strftime("%Y/%m/%d %H:%M"),
        "areaName": AREA_NAME,
        "regions": [[name, codes] for name, codes in REGIONS],
        "weekdays": WEEKDAYS,
    }

    os.makedirs(out_dir, exist_ok=True)
    for name, b64 in FAVICON_FILES.items():
        with open(os.path.join(out_dir, name), "wb") as fp:
            fp.write(base64.b64decode(b64))
    with open(os.path.join(out_dir, "404.html"), "w", encoding="utf-8") as fp:
        fp.write(NOT_FOUND_HTML)
    manifest = {"generated": meta["generated"],
                "generated_iso": now_jst.isoformat(timespec="seconds"),
                "days": days}
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, ensure_ascii=False)
    total = 0
    for code, _ in AREA_NAMES:
        adir = os.path.join(out_dir, "data", code)
        os.makedirs(adir, exist_ok=True)
        for ds in days:
            payload = area_day_json(code, ds, area_map[code], data)
            with open(os.path.join(adir, f"{ds}.json"), "w", encoding="utf-8") as fp:
                json.dump(payload, fp, ensure_ascii=False)
            total += 1
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(app_html(meta))
    print(f"done -> {out_dir} ({total} area-day JSON files)")


if __name__ == "__main__":
    main()
