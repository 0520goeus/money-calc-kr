#!/usr/bin/env python3
"""2026/2027 연봉 실수령액·주휴수당·퇴직금·적금이자 계산기 허브 (0520goeus/money-calc-kr) — 36개 고단가 금융 SEO 페이지."""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST)

SITE_NAME = "실수령액·금융 계산기 연구소"
SITE_URL = "https://0520goeus.github.io/money-calc-kr"
INDEXNOW_KEY = "d73a9021e84b49c1a650f293e184c711"
GOOGLE_FILE = "google873809343766a3b6.html"
ADSENSE_CLIENT = "ca-pub-8749404731911210"
COUPANG_TRACKING = "AF9170267"
COUPANG_WIDGET_ID = 1049499

DISCLOSURE = "이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
COUPANG_BOX = (
    '<section class="card shop">'
    f'<p class="disc">{DISCLOSURE}</p>'
    '<h3>직장인·자취생 생활비 절약 인기 상품</h3>'
    '<script src="https://ads-partners.coupang.com/g.js"></script>'
    f'<script>new PartnersCoupang.G({{"id":{COUPANG_WIDGET_ID},"template":"carousel",'
    f'"trackingCode":"{COUPANG_TRACKING}","width":"100%","height":"140","tsource":""}});</script>'
    "</section>"
)


def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def won(n) -> str:
    return f"{int(round(n)):,}원"


def calc_salary_breakdown(annual_manwon: int, non_tax_monthly: int = 200000) -> dict[str, int]:
    """2026 Korean 4대보험 + 근로소득세·지방소득세 실수령액 정밀 계산 (비과세 식대 20만원 기본)."""
    gross_m = int(round(annual_manwon * 10000 / 12.0))
    taxable = max(0, gross_m - non_tax_monthly)

    # 국민연금 4.5% (상한 월 617만원 기준 최대 277,650원)
    pension = int(min(taxable, 6170000) * 0.045)
    # 건강보험 3.545%
    health = int(taxable * 0.03545)
    # 장기요양보험 (건강보험의 12.95%)
    care = int(health * 0.1295)
    # 고용보험 0.9%
    emp = int(taxable * 0.009)

    # 근로소득 간이세액 근사 (1인 가구 기준)
    if taxable <= 1060000:
        inc_tax = 0
    elif taxable <= 2000000:
        inc_tax = int((taxable - 1060000) * 0.022)
    elif taxable <= 3000000:
        inc_tax = int(20680 + (taxable - 2000000) * 0.068)
    elif taxable <= 4500000:
        inc_tax = int(88680 + (taxable - 3000000) * 0.128)
    elif taxable <= 6500000:
        inc_tax = int(280680 + (taxable - 4500000) * 0.185)
    else:
        inc_tax = int(650680 + (taxable - 6500000) * 0.255)
    local_tax = int(inc_tax * 0.10)

    total_deduct = pension + health + care + emp + inc_tax + local_tax
    net_m = gross_m - total_deduct
    return {
        "annual_man": annual_manwon,
        "gross_m": gross_m,
        "net_m": net_m,
        "deduct_m": total_deduct,
        "pension": pension,
        "health": health,
        "care": care,
        "emp": emp,
        "inc_tax": inc_tax,
        "local_tax": local_tax,
    }


CSS = """
:root{--bg:#f8fafc;--card:#ffffff;--ink:#0f172a;--sub:#475569;--line:#e2e8f0;--accent:#2563eb;--green:#059669}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 -apple-system,"Apple SD Gothic Neo",sans-serif}
header{background:#0f172a;color:#fff;padding:16px 20px}
.wrap{max-width:940px;margin:0 auto;padding:0 18px}
header .wrap{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
header a{color:#cbd5e1;text-decoration:none;font-size:14px;font-weight:600}
header .brand{color:#fff;font-size:19px;font-weight:800}
nav{display:flex;gap:14px;flex-wrap:wrap}
main{padding:28px 0 60px;display:grid;gap:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px}
h1{font-size:27px;line-height:1.35;margin:0 0 8px}h2{font-size:20px;margin:0 0 12px}h3{font-size:17px;margin:0 0 8px}
.sub{color:var(--sub);margin:0 0 14px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.tile{display:grid;gap:3px;padding:13px 15px;border:1px solid var(--line);border-radius:11px;background:#fff;text-decoration:none;color:var(--ink)}
.tile:hover{border-color:var(--accent)}
.tile b{font-size:15.5px}.tile span{color:var(--green);font-weight:800;font-size:15px}
.big-box{background:#0f172a;color:#fff;border-radius:14px;padding:22px;display:grid;gap:8px}
.big-num{font-size:36px;font-weight:800;color:#38d9a9}
input{width:100%;padding:11px 13px;border:1px solid var(--line);border-radius:10px;font:inherit;font-size:15px}
label{display:grid;gap:5px;font-size:13.5px;color:var(--sub);margin-bottom:10px}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}
thead th{background:#f1f5f9;font-size:13px;color:var(--sub)}
.faq{background:#f8fafc;padding:14px 16px;border-left:4px solid var(--accent);border-radius:8px;margin:10px 0}
.shop .disc{font-size:12.5px;color:var(--sub);margin:0 0 8px}
footer{border-top:1px solid var(--line);padding:24px 0 44px;color:var(--sub);font-size:13.5px}
footer a{color:var(--accent);text-decoration:none}
"""


def write_page(rel: str, title: str, desc: str, body: str, faqs: list[tuple[str, str]] | None = None) -> str:
    canon = f"{SITE_URL}/" if rel == "index.html" else f"{SITE_URL}/{rel}"
    ld = ""
    if faqs:
        obj = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
        }
        ld = f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<link rel="stylesheet" href="{SITE_URL}/style.css">
{ld}
</head>
<body>
<header><div class="wrap">
  <a class="brand" href="{SITE_URL}/">💰 {SITE_NAME}</a>
  <nav>
    <a href="{SITE_URL}/">연봉 실수령액표</a>
    <a href="{SITE_URL}/juhyu-allowance.html">알바 주휴수당</a>
    <a href="{SITE_URL}/severance-pay.html">퇴직금 계산기</a>
    <a href="{SITE_URL}/savings-interest.html">적금·예금 이자</a>
    <a href="https://0520goeus.github.io/vs-pick/">가성비 VS 사전</a>
    <a href="https://0520goeus.github.io/elec-calc/">전기세 얼마</a>
  </nav>
</div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">
  <p>패밀리 사이트: <a href="https://0520goeus.github.io/price-note/">해뎐 가격노트</a> · <a href="https://0520goeus.github.io/elec-calc/">전기세 얼마</a> · <a href="https://0520goeus.github.io/life-money-lab/">생활비 물가 연구소</a> · <a href="https://0520goeus.github.io/vs-pick/">가성비 VS 비교 사전</a> · <a href="https://0520goeus.github.io/seller-margin-calc/">셀러 마진 계산기</a> · <a href="https://lifefixnote-kr.blogspot.com/">생활해결 노트</a></p>
</div></footer>
</body></html>"""
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return canon


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "style.css").write_text(CSS, encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / GOOGLE_FILE).write_text(f"google-site-verification: {GOOGLE_FILE}", encoding="utf-8")
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (DIST / "ads.txt").write_text(f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")

    # 32 Individual Salary SEO pages (2400만원 ~ 1억원)
    salaries = list(range(2400, 7200, 200)) + [7500, 8000, 8500, 9000, 9500, 10000, 12000, 15000]
    urls: list[str] = []
    tiles: list[str] = []
    table_rows: list[str] = []

    for sal in salaries:
        b = calc_salary_breakdown(sal)
        rel = f"salary/{sal}.html"
        title = f"연봉 {sal:,}만원 실수령액 | 월급 세후 {won(b['net_m'])} (4대보험·소득세 공제표)"
        desc = f"연봉 {sal:,}만 원(세전 월급 {won(b['gross_m'])})의 4대보험(국민연금·건강보험·고용보험) 및 소득세 공제 후 실제 월 실수령액은 {won(b['net_m'])}입니다."
        faqs = [
            (
                f"연봉 {sal:,}만원이면 한 달에 통장에 실제로 얼마가 찍히나요?",
                f"비과세 식대 20만 원(1인 가구) 기준, 세전 월급 {won(b['gross_m'])}에서 4대보험 및 세금 {won(b['deduct_m'])}을 공제한 월 실수령액은 약 {won(b['net_m'])}입니다.",
            ),
            (
                f"연봉 {sal:,}만원에서 비과세 식대가 없으면 실수령액이 어떻게 바뀌나요?",
                "비과세 식대(월 20만 원 한도)가 없으면 과세표준이 20만 원 늘어나 월 실수령액이 약 2~3만 원 줄어들 수 있습니다.",
            ),
        ]
        neighbors = [s for s in salaries if abs(s - sal) <= 600 and s != sal][:6]
        neighbor_links = "".join(
            f'<a class="tile" href="{SITE_URL}/salary/{ns}.html"><b>연봉 {ns:,}만원</b><span>월 {won(calc_salary_breakdown(ns)["net_m"])}</span></a>'
            for ns in neighbors
        )
        body = f"""
        <section class="card">
          <h1>연봉 {sal:,}만 원 실수령액 계산 결과</h1>
          <p class="sub">2026년 4대보험 요율 및 간이세액표(비과세 식대 월 20만 원, 부양가족 1인 기준)를 반영한 세후 월급 명세표입니다.</p>
          <div class="big-box">
            <div>연봉 {sal:,}만 원의 세후 월 실수령액</div>
            <div class="big-num">{won(b['net_m'])}</div>
            <div style="color:#94a3b8;font-size:14px">세전 월급 {won(b['gross_m'])} − 월 총공제액 {won(b['deduct_m'])} (공제율 {b['deduct_m']/b['gross_m']*100:.1f}%)</div>
          </div>
        </section>
        {COUPANG_BOX}
        <section class="card">
          <h2>항목별 4대보험·세금 공제 내역</h2>
          <table>
            <thead><tr><th>공제 항목</th><th>산출 기준</th><th>월 공제 금액</th></tr></thead>
            <tbody>
              <tr><td>국민연금</td><td>과세월급의 4.5% (상한 적용)</td><td>{won(b['pension'])}</td></tr>
              <tr><td>건강보험</td><td>과세월급의 3.545%</td><td>{won(b['health'])}</td></tr>
              <tr><td>장기요양보험</td><td>건강보험료의 12.95%</td><td>{won(b['care'])}</td></tr>
              <tr><td>고용보험</td><td>과세월급의 0.9%</td><td>{won(b['emp'])}</td></tr>
              <tr><td>근로소득세</td><td>간이세액표 (1인 가구)</td><td>{won(b['inc_tax'])}</td></tr>
              <tr><td>지방소득세</td><td>근로소득세의 10%</td><td>{won(b['local_tax'])}</td></tr>
              <tr><td><strong>월 총공제 합계</strong></td><td>4대보험 + 세금</td><td><strong>{won(b['deduct_m'])}</strong></td></tr>
              <tr><td><strong>세후 월 실수령액</strong></td><td>통장 입금액</td><td><strong style="color:var(--green)">{won(b['net_m'])}</strong></td></tr>
            </tbody>
          </table>
        </section>
        <section class="card">
          <h2>인접 연봉 실수령액 비교</h2>
          <div class="grid">{neighbor_links}</div>
        </section>
        <section class="card">
          <h2>자주 묻는 질문</h2>
          {"".join(f'<div class="faq"><strong>Q. {esc(q)}</strong><p class="sub" style="margin:6px 0 0">A. {esc(a)}</p></div>' for q, a in faqs)}
        </section>
        """
        urls.append(write_page(rel, title, desc, body, faqs))
        tiles.append(f'<a class="tile" href="{SITE_URL}/{rel}"><b>연봉 {sal:,}만원</b><span>월 {won(b["net_m"])}</span></a>')
        table_rows.append(
            f'<tr><td><a href="{SITE_URL}/{rel}"><strong>{sal:,}만 원</strong></a></td>'
            f'<td>{won(b["gross_m"])}</td><td>{won(b["deduct_m"])}</td>'
            f'<td style="color:var(--green);font-weight:800">{won(b["net_m"])}</td></tr>'
        )

    # Interactive calculator pages: 주휴수당, 퇴직금, 예적금 이자
    urls.append(write_page(
        "juhyu-allowance.html",
        "알바 주휴수당 계산기 | 시급·근무시간 넣으면 주휴수당 포함 주급·월급 자동 계산",
        "주 15시간 이상 근무 시 지급되는 주휴수당과 주급, 월 환산 급여를 즉시 계산합니다.",
        f"""<section class="card">
          <h1>알바 주휴수당 & 주급·월급 실시간 계산기</h1>
          <p class="sub">주 소정근로시간이 15시간 이상이고 개근한 경우 법정 주휴수당이 지급됩니다.</p>
          <div class="grid2">
            <div>
              <label>시급 (원) <input id="wage" type="number" value="10320" oninput="calcJ()"></label>
              <label>주 총 근무시간 (시간) <input id="wh" type="number" step="0.5" value="20" oninput="calcJ()"></label>
            </div>
            <div class="big-box">
              <div>이번 주 주휴수당</div>
              <div class="big-num" id="jOut">0원</div>
              <div id="jSub" style="color:#94a3b8;font-size:14px"></div>
            </div>
          </div>
        </section>{COUPANG_BOX}
        <script>
        function calcJ(){{
          const w=parseFloat(document.getElementById('wage').value)||0;
          const h=parseFloat(document.getElementById('wh').value)||0;
          const jh = h>=15 ? Math.min(40, h)/40*8 : 0;
          const jPay = Math.round(jh * w);
          const wk = Math.round(h*w + jPay);
          document.getElementById('jOut').textContent = jPay.toLocaleString('ko-KR') + '원';
          document.getElementById('jSub').textContent = h>=15 ? `주 총급여 ${{wk.toLocaleString('ko-KR')}}원 (월 환산 약 ${{Math.round(wk*4.345).toLocaleString('ko-KR')}}원)` : '주 15시간 미만은 주휴수당 대상이 아닙니다.';
        }}
        calcJ();
        </script>""",
    ))

    urls.append(write_page(
        "severance-pay.html",
        "퇴직금 계산기 | 근속연수·월평균임금 기준 예상 퇴직금 간편 계산",
        "1년 이상 근무 시 지급되는 법정 퇴직금을 월평균 임금과 재직일수로 즉시 계산합니다.",
        f"""<section class="card">
          <h1>법정 퇴직금 실시간 계산기</h1>
          <p class="sub">최근 3개월 평균 월급(세전)과 총 재직 개월 수를 넣으면 예상 퇴직금을 즉시 계산합니다.</p>
          <div class="grid2">
            <div>
              <label>최근 3개월 평균 세전 월급 (원) <input id="mPay" type="number" value="3200000" oninput="calcS()"></label>
              <label>총 근무 개월 수 (12개월 이상) <input id="months" type="number" value="24" oninput="calcS()"></label>
            </div>
            <div class="big-box">
              <div>예상 세전 퇴직금</div>
              <div class="big-num" id="sOut">0원</div>
              <div id="sSub" style="color:#94a3b8;font-size:14px"></div>
            </div>
          </div>
        </section>{COUPANG_BOX}
        <script>
        function calcS(){{
          const m=parseFloat(document.getElementById('mPay').value)||0;
          const mo=parseFloat(document.getElementById('months').value)||0;
          const sev = mo>=12 ? Math.round(m * (mo/12)) : 0;
          document.getElementById('sOut').textContent = sev.toLocaleString('ko-KR') + '원';
          document.getElementById('sSub').textContent = `재직 약 ${{(mo/12).toFixed(1)}}년 기준 (1년당 약 30일분 평균임금)`;
        }}
        calcS();
        </script>""",
    ))

    urls.append(write_page(
        "savings-interest.html",
        "적금·예금 이자 계산기 | 세전·세후(15.4%) 만기 수령액 자동 계산",
        "월 적립액(또는 예치금), 금리, 기간을 넣으면 이자소득세(15.4%) 공제 후 실제 만기 수령액을 계산합니다.",
        f"""<section class="card">
          <h1>적금 만기 이자 & 세후 수령액 계산기</h1>
          <p class="sub">일반과세(15.4%) 공제 후 만기에 실제로 받는 원금+이자를 즉시 계산합니다.</p>
          <div class="grid2">
            <div>
              <label>매월 납입 금액 (원) <input id="dep" type="number" value="500000" oninput="calcI()"></label>
              <label>연 금리 (%) <input id="rate" type="number" step="0.1" value="4.0" oninput="calcI()"></label>
              <label>가입 기간 (개월) <input id="term" type="number" value="12" oninput="calcI()"></label>
            </div>
            <div class="big-box">
              <div>세후 만기 수령액 (원금+세후이자)</div>
              <div class="big-num" id="iOut">0원</div>
              <div id="iSub" style="color:#94a3b8;font-size:14px"></div>
            </div>
          </div>
        </section>{COUPANG_BOX}
        <script>
        function calcI(){{
          const d=parseFloat(document.getElementById('dep').value)||0;
          const r=(parseFloat(document.getElementById('rate').value)||0)/100;
          const n=parseFloat(document.getElementById('term').value)||0;
          const prin = d * n;
          const grossInt = d * (n*(n+1)/2) * (r/12);
          const netInt = Math.round(grossInt * (1 - 0.154));
          document.getElementById('iOut').textContent = (prin + netInt).toLocaleString('ko-KR') + '원';
          document.getElementById('iSub').textContent = `원금 ${{prin.toLocaleString('ko-KR')}}원 + 세후 이자 ${{netInt.toLocaleString('ko-KR')}}원 (세전 ${{Math.round(grossInt).toLocaleString('ko-KR')}}원)`;
        }}
        calcI();
        </script>""",
    ))

    # Homepage
    home_body = f"""
    <section class="card">
      <h1>2026 연봉 실수령액 계산기 & 구간별 월급 표</h1>
      <p class="sub">4대보험(국민연금·건강보험·장기요양·고용보험)과 근로소득세·지방소득세를 모두 공제한 실제 통장 입금액을 연봉 구간별로 바로 확인하세요.</p>
      <div class="grid">{"".join(tiles[:16])}</div>
    </section>
    {COUPANG_BOX}
    <section class="card">
      <h2>전체 연봉 구간별 세후 월 실수령액 한눈에 보기 (2,400만 ~ 1.5억)</h2>
      <table>
        <thead><tr><th>연봉 (상세 내역 클릭)</th><th>세전 월급</th><th>월 공제 합계</th><th>세후 월 실수령액</th></tr></thead>
        <tbody>{"".join(table_rows)}</tbody>
      </table>
    </section>
    """
    urls.insert(0, write_page(
        "index.html",
        "2026 연봉 실수령액 계산기 & 연봉별 세후 월급 표 (2400만원~1억5천만원)",
        "2026년 4대보험·소득세 공제 후 연봉별 실제 월 실수령액 표와 주휴수당·퇴직금·적금이자 계산기.",
        home_body,
    ))

    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc><lastmod>{NOW.strftime('%Y-%m-%d')}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    print(f"실수령액·금융 계산기 연구소 빌드 완료: 총 {len(urls)}페이지")


if __name__ == "__main__":
    main()
