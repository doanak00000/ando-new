"""Build the static blog and sitemap for vattuinando.vn.

Posts live in blog/_src/<slug>.html: a front-matter comment followed by the article body.
Run from the repo root:  python _tools/build_blog.py

Generates blog/<slug>.html, blog/index.html, blog/feed.xml and sitemap.xml.
Folders starting with "_" are ignored by GitHub Pages (Jekyll), so sources are not published.
"""
import html
import json
import math
import os
import re
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'blog', '_src')
OUT = os.path.join(ROOT, 'blog')
SITE = 'https://vattuinando.vn'
PHONE, PHONE_TEL = '0979 324 567', '+84979324567'
EMAIL = 'prepress.ando@gmail.com'
AUTHOR = 'Phòng Kỹ thuật An Đô'

STATIC_PAGES = [  # (path, changefreq, priority)
    ('', 'weekly', '1.0'),
    ('menu.html', 'weekly', '0.9'),
    ('service.html', 'monthly', '0.8'),
    ('about.html', 'monthly', '0.7'),
    ('contact.html', 'monthly', '0.8'),
    ('reservation.html', 'monthly', '0.6'),
    ('blog/', 'weekly', '0.8'),
]


def slugify(text):
    table = str.maketrans('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ',
                          'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd')
    text = text.lower().translate(table)
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def parse(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'\s*<!--(.*?)-->(.*)', raw, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip()
    meta['slug'] = os.path.splitext(os.path.basename(path))[0]
    meta['body'] = m.group(2).strip()
    meta['updated'] = meta.get('updated') or meta['date']
    return meta


def enrich(post):
    """Add heading ids, TOC, FAQ list and reading time."""
    body = post['body']
    toc = []

    def add_id(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        text = re.sub('<[^>]+>', '', inner)
        hid = slugify(text)[:60]
        if level == '2':
            toc.append((hid, text))
        return f'<h{level} id="{hid}"{attrs}>{inner}</h{level}>'
    body = re.sub(r'<h([23])((?:\s(?!id=)[^>]*)?)>(.*?)</h\1>', add_id, body, flags=re.S)

    faq = []
    fm = re.search(r'<section class="faq">(.*?)</section>', body, re.S)
    if fm:
        for q, a in re.findall(r'<h3[^>]*>(.*?)</h3>\s*(.*?)(?=<h3|$)', fm.group(1), re.S):
            faq.append((re.sub('<[^>]+>', '', q).strip(), re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', a)).strip()))

    words = len(re.sub('<[^>]+>', ' ', body).split())
    post.update(body=body, toc=toc, faq=faq, words=words, minutes=max(3, math.ceil(words / 220)))
    return post


def fmt_date(d):
    y, m, dd = d.split('-')
    return f'{dd}/{m}/{y}'


NAV = [('../index.html', 'Trang Chủ'), ('../about.html', 'Giới Thiệu'), ('../service.html', 'Dịch Vụ'),
       ('../menu.html', 'Sản Phẩm'), ('./', 'Kiến Thức'), ('../contact.html', 'Liên Hệ')]


def head(title, desc, url, image, og_type, schema, extra=''):
    return f'''<!DOCTYPE html>
<html lang="vi">

<head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta name="description" content="{html.escape(desc)}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{url}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:type" content="{og_type}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{image}">
    <meta property="og:site_name" content="Vật Tư In An Đô">
    <meta property="og:locale" content="vi_VN">
    <meta name="twitter:card" content="summary_large_image">
    {extra}<link rel="alternate" type="application/rss+xml" title="Kiến thức ngành in - An Đô" href="{SITE}/blog/feed.xml">
    <link href="../img/favicon.ico" rel="icon">
    <link rel="icon" type="image/png" sizes="32x32" href="../img/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="../img/apple-touch-icon.png">
    <link rel="manifest" href="../manifest.json">
    <meta name="theme-color" content="#1e5aa8">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@200;400&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.0/css/all.min.css" rel="stylesheet">
    <link href="../css/style.min.css" rel="stylesheet">
    <link href="../css/blog.css" rel="stylesheet">
    <script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
    </script>
</head>
'''


def navbar():
    links = '\n'.join(
        f'                    <a href="{h}" class="nav-item nav-link{" active" if t == "Kiến Thức" else ""}">{t}</a>'
        for h, t in NAV)
    return f'''
<body>
    <div class="container-fluid p-0 nav-bar">
        <nav class="navbar navbar-expand-lg navbar-light py-3">
            <a href="../index.html" class="navbar-brand px-lg-4 m-0 d-flex align-items-center">
                <img src="../img/logo.png" alt="An Đô Logo" width="50" height="50" class="mr-2">
                <span class="brand-name m-0 display-4 text-uppercase">An Đô</span>
            </a>
            <button type="button" class="navbar-toggler" data-toggle="collapse" data-target="#navbarCollapse" aria-label="Mở menu">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse justify-content-between" id="navbarCollapse">
                <div class="navbar-nav ml-auto p-4">
{links}
                </div>
            </div>
        </nav>
    </div>
'''


def page_header(h1, crumbs):
    trail = ' <span class="px-2">/</span> '.join(
        f'<a href="{h}">{html.escape(t)}</a>' if h else f'<span>{html.escape(t)}</span>' for h, t in crumbs)
    return f'''
    <div class="container-fluid page-header mb-5 position-relative overlay-bottom">
        <div class="d-flex flex-column align-items-center justify-content-center pt-0 pt-lg-5" style="min-height: 400px">
            <h1 class="blog-title display-4 mb-3 mt-0 mt-lg-5 text-white">{html.escape(h1)}</h1>
            <nav class="breadcrumb-bar text-white mb-lg-5" aria-label="breadcrumb">{trail}</nav>
        </div>
    </div>
'''


def footer(posts):
    latest = ''.join(f'<li class="mb-1"><a class="text-white" href="{p["slug"]}.html">{html.escape(p["short"])}</a></li>'
                     for p in posts[:5])
    return f'''
    <div class="container-fluid footer text-white mt-5 pt-5 px-0 position-relative overlay-top">
        <div class="row mx-0 pt-5 px-sm-3 px-lg-5 mt-4">
            <div class="col-lg-4 col-md-6 mb-5">
                <h2 class="h4 text-white text-uppercase mb-4" style="letter-spacing: 3px;">Liên Hệ An Đô</h2>
                <p><i class="fa fa-map-marker-alt mr-2"></i>56/24 Tô Hiệu, Tân Thới Hòa, Tân Phú, Hồ Chí Minh</p>
                <p><i class="fa fa-phone-alt mr-2"></i><a class="text-white" href="tel:{PHONE_TEL}">{PHONE}</a></p>
                <p class="m-0"><i class="fa fa-envelope mr-2"></i><a class="text-white" href="mailto:{EMAIL}">{EMAIL}</a></p>
            </div>
            <div class="col-lg-4 col-md-6 mb-5">
                <h2 class="h4 text-white text-uppercase mb-4" style="letter-spacing: 3px;">Bài Viết Mới</h2>
                <ul class="list-unstyled m-0">{latest}</ul>
            </div>
            <div class="col-lg-4 col-md-6 mb-5">
                <h2 class="h4 text-white text-uppercase mb-4" style="letter-spacing: 3px;">Giờ Làm Việc</h2>
                <p class="mb-1 text-uppercase">Thứ Hai - Thứ Sáu</p>
                <p>8:00 - 17:00</p>
                <p class="mb-1 text-uppercase">Thứ Bảy - Chủ Nhật</p>
                <p>8:00 - 12:00</p>
            </div>
        </div>
        <div class="container-fluid text-center text-white border-top mt-4 py-4 px-sm-3 px-md-5" style="border-color: rgba(256, 256, 256, .1) !important;">
            <p class="m-0 text-white">Bản Quyền &copy; 2018-2026 <a class="font-weight-bold text-white" href="../index.html">An Đô - Vật Tư Ngành In</a>.</p>
        </div>
    </div>

    <a href="#" class="btn btn-lg btn-primary btn-lg-square back-to-top" aria-label="Lên đầu trang"><i class="fa fa-angle-double-up"></i></a>

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js"></script>
    <script src="../lib/easing/easing.min.js"></script>
    <script src="../lib/waypoints/waypoints.min.js"></script>
    <script src="../js/main.js"></script>
</body>

</html>
'''


def cta():
    return f'''
            <aside class="cta-box">
                <p class="h4">Cần tư vấn chọn vật tư cho máy in của bạn?</p>
                <p class="mb-1">Kỹ thuật An Đô hỗ trợ miễn phí chọn mực, bản kẽm, cao su và hóa chất phù hợp với máy, giấy và đơn hàng. Báo giá trong ngày, giao hàng toàn quốc.</p>
                <a class="btn btn-light" href="tel:{PHONE_TEL}"><i class="fa fa-phone-alt mr-2"></i>Gọi {PHONE}</a>
                <a class="btn btn-outline-light" href="../menu.html">Xem bảng giá</a>
                <a class="btn btn-outline-light" href="../reservation.html">Yêu cầu báo giá</a>
            </aside>
'''


def card(p, tag='h3'):
    return f'''
                <div class="col-md-6 col-lg-4 mb-4">
                    <article class="post-card">
                        <a href="{p["slug"]}.html"><img src="{p["image"]}" alt="{html.escape(p["title"])}" loading="lazy" decoding="async" width="400" height="190"></a>
                        <div class="card-body">
                            <span class="cat">{html.escape(p["category"])}</span>
                            <{tag}><a href="{p["slug"]}.html">{html.escape(p["title"])}</a></{tag}>
                            <p>{html.escape(p["description"])}</p>
                            <a class="more" href="{p["slug"]}.html">Đọc tiếp &rarr;</a>
                        </div>
                    </article>
                </div>'''


def related(post, posts):
    same = [p for p in posts if p is not post and p['category'] == post['category']]
    rest = [p for p in posts if p is not post and p not in same]
    wanted = [s.strip() for s in post.get('related', '').split(',') if s.strip()]
    picked = [p for p in posts if p['slug'] in wanted]
    for p in same + rest:
        if len(picked) >= 3:
            break
        if p not in picked and p is not post:
            picked.append(p)
    return picked[:3]


def render_post(post, posts):
    url = f'{SITE}/blog/{post["slug"]}.html'
    img_abs = SITE + '/' + post['image'].replace('../', '')
    graph = [
        {"@type": "BlogPosting", "@id": url + '#article', "mainEntityOfPage": url, "headline": post['title'],
         "description": post['description'], "image": [img_abs], "datePublished": post['date'],
         "dateModified": post['updated'], "inLanguage": "vi-VN", "wordCount": post['words'],
         "articleSection": post['category'], "keywords": post.get('keywords', ''),
         "author": {"@type": "Organization", "name": AUTHOR, "url": f"{SITE}/about.html"},
         "publisher": {"@type": "Organization", "@id": f"{SITE}/#business", "name": "An Đô - Vật Tư Ngành In",
                       "logo": {"@type": "ImageObject", "url": f"{SITE}/img/logo.png"}}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Kiến thức ngành in", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": post['short'], "item": url}]},
    ]
    if post['faq']:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in post['faq']]})
    schema = {"@context": "https://schema.org", "@graph": graph}
    extra = (f'<meta property="article:published_time" content="{post["date"]}">\n    '
             f'<meta property="article:modified_time" content="{post["updated"]}">\n    '
             f'<meta property="article:section" content="{html.escape(post["category"])}">\n    ')
    toc = ''.join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in post['toc'])
    rel = ''.join(card(p) for p in related(post, posts))
    updated = f'<span>Cập nhật {fmt_date(post["updated"])}</span>' if post['updated'] != post['date'] else ''
    out = head(post['seo_title'], post['description'], url, img_abs, 'article', schema, extra)
    out += navbar()
    out += page_header(post['title'], [('../index.html', 'Trang chủ'), ('./', 'Kiến thức ngành in'), ('', post['short'])])
    out += f'''
    <main class="container-fluid pb-3">
        <article class="post-wrap px-3">
            <p class="post-meta mb-3"><span>{html.escape(post["category"])}</span><span>Đăng {fmt_date(post["date"])}</span>{updated}<span>{post["minutes"]} phút đọc</span><span>{AUTHOR}</span></p>
            <img class="post-cover mb-4" src="{post["image"]}" alt="{html.escape(post["title"])}" width="820" height="420" fetchpriority="high">
            <nav class="toc" aria-label="Mục lục"><strong>Nội dung bài viết</strong><ol>{toc}</ol></nav>
            <div class="post-body">
{post["body"]}
            </div>
{cta()}
        </article>
        <section class="container py-4">
            <h2 class="h3 mb-4 text-center">Bài viết liên quan</h2>
            <div class="row">{rel}
            </div>
        </section>
    </main>
'''
    out += footer(posts)
    return out


def render_index(posts):
    url = f'{SITE}/blog/'
    title = 'Kiến Thức Ngành In: Mực In, Bản Kẽm, Kỹ Thuật In Offset | An Đô'
    desc = ('Chuyên mục kiến thức ngành in của An Đô: hướng dẫn chọn mực in offset, bản kẽm CTP, cao su, '
            'dung dịch máng, xử lý lỗi in offset từ kỹ thuật viên nhiều năm kinh nghiệm.')
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": url + '#blog', "url": url, "name": "Kiến thức ngành in - An Đô", "description": desc,
         "inLanguage": "vi-VN", "publisher": {"@id": f"{SITE}/#business"},
         "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": f"{SITE}/blog/{p['slug']}.html",
                       "datePublished": p['date']} for p in posts]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Kiến thức ngành in", "item": url}]}]}
    cats = []
    for p in posts:
        if p['category'] not in cats:
            cats.append(p['category'])
    catnav = ''.join(f'<a href="#{slugify(c)}">{html.escape(c)}</a>' for c in cats)
    sections = ''
    for c in cats:
        cards = ''.join(card(p, 'h3') for p in posts if p['category'] == c)
        sections += f'''
        <section class="container py-3" id="{slugify(c)}">
            <h2 class="h3 mb-4">{html.escape(c)}</h2>
            <div class="row">{cards}
            </div>
        </section>'''
    out = head(title, desc, url, f'{SITE}/img/carousel-1.jpg', 'website', schema)
    out += navbar()
    out += page_header('Kiến Thức Ngành In', [('../index.html', 'Trang chủ'), ('', 'Kiến thức ngành in')])
    out += f'''
    <main>
        <div class="container text-center mb-4">
            <p class="lead mx-auto" style="max-width: 760px;">Tổng hợp kinh nghiệm thực tế về mực in offset, bản kẽm CTP, cao su, hóa chất và cách xử lý lỗi trên máy in, do đội ngũ kỹ thuật An Đô biên soạn cho chủ nhà in, thợ máy và bộ phận mua hàng.</p>
            <nav class="cat-nav" aria-label="Chuyên mục">{catnav}</nav>
        </div>{sections}
        <div class="container">{cta()}        </div>
    </main>
'''
    out += footer(posts)
    return out


def render_feed(posts):
    items = ''.join(f'''
    <item>
      <title>{html.escape(p["title"])}</title>
      <link>{SITE}/blog/{p["slug"]}.html</link>
      <guid>{SITE}/blog/{p["slug"]}.html</guid>
      <pubDate>{format_datetime(datetime.fromisoformat(p["date"]).replace(hour=8, tzinfo=timezone.utc))}</pubDate>
      <category>{html.escape(p["category"])}</category>
      <description>{html.escape(p["description"])}</description>
    </item>''' for p in posts)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Kiến thức ngành in - An Đô</title>
    <link>{SITE}/blog/</link>
    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Kiến thức mực in, bản kẽm, kỹ thuật in offset từ An Đô - vật tư ngành in TP.HCM</description>
    <language>vi</language>{items}
  </channel>
</rss>
'''


def render_sitemap(posts):
    today = date.today().isoformat()
    newest = max(p['updated'] for p in posts)
    urls = []
    for path, freq, prio in STATIC_PAGES:
        lastmod = newest if path == 'blog/' else today
        urls.append((f'{SITE}/{path}', lastmod, freq, prio, None))
    for p in posts:
        img = SITE + '/' + p['image'].replace('../', '')
        urls.append((f'{SITE}/blog/{p["slug"]}.html', p['updated'], 'monthly', '0.7', img))
    body = ''.join(f'''
  <url>
    <loc>{u}</loc>
    <lastmod>{m}</lastmod>
    <changefreq>{f}</changefreq>
    <priority>{pr}</priority>{f"""
    <image:image><image:loc>{img}</image:loc></image:image>""" if img else ''}
  </url>''' for u, m, f, pr, img in urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{body}
</urlset>
'''


def main():
    posts = [enrich(parse(os.path.join(SRC, f))) for f in os.listdir(SRC) if f.endswith('.html')]
    posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    for p in posts:
        with open(os.path.join(OUT, p['slug'] + '.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(render_post(p, posts))
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(render_index(posts))
    with open(os.path.join(OUT, 'feed.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(render_feed(posts))
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(render_sitemap(posts))
    for p in posts:
        print(f'{p["slug"]}: {p["words"]} words, {len(p["toc"])} h2, {len(p["faq"])} faq, '
              f'title {len(p["seo_title"])} chars, desc {len(p["description"])} chars')


if __name__ == '__main__':
    main()
