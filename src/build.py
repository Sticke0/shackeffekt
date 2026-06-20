#!/usr/bin/env python3
"""Generate index.html from site.md content."""

import re
from collections import OrderedDict
from pathlib import Path
import sys

SRC = Path(__file__).parent


def parse_md(text):
    sections = OrderedDict()
    current_type = None
    current = None
    in_list = False

    for line in text.split('\n'):
        s = line.strip()

        m = re.match(r'^##\s+(\w[\w-]*)', s)
        if m:
            if current_type and current:
                sections[current_type] = current
            current_type = m.group(1)
            current = {}
            in_list = False
            continue

        if current_type is None:
            continue
        if not s:
            in_list = False
            continue

        m = re.match(r'^-\s+(.*)', s)
        if m:
            in_list = True
            content = m.group(1)
            current.setdefault('items', [])
            km = re.match(r'\*\*(\w[\w ]*):\*\*\s*(.*)', content)
            if km:
                current['items'].append({km.group(1): km.group(2)})
            else:
                current['items'].append(content)
            continue

        if in_list and current.get('items') and isinstance(current['items'][-1], dict):
            km = re.match(r'\*\*(\w[\w ]*):\*\*\s*(.*)', s)
            if km:
                current['items'][-1][km.group(1)] = km.group(2)
                continue

        in_list = False

        m = re.match(r'\*\*(\w[\w ]*):\*\*\s*(.*)', s)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip()
            if key in current:
                if isinstance(current[key], list):
                    current[key].append(val)
                else:
                    current[key] = [current[key], val]
            else:
                current[key] = val
            continue

    if current_type and current:
        sections[current_type] = current

    return sections


def body_html(val):
    parts = val if isinstance(val, list) else [val]
    return '<p>' + '<br>\n'.join(parts) + '</p>'


def render_sections(sections):
    out = []

    h = sections.get('header', {})
    f = sections.get('footer', {})
    brand = h.get('brand', 'Schackeffekt')
    tagline = h.get('tagline', 'Bättre tänkande – starkare samspel')
    email = h.get('email', 'info@schackeffekt.se')
    email_footer = f.get('email', email)
    phone = f.get('phone', '')

    out.append(f'''    <header>
        <div class="container flex-row">
          <section class="brand">
            <span aria-hidden="true" style="font-size: 3rem; padding: 0; margin: 0;">♟️</span>
            <span class="brand-text">
              <h1 style="font-size: 1.8rem; color: var(--text-dark);">{brand}</h1>
              <p style="color: var(--color-primary); font-size: 0.8rem;">{tagline}</p>
            </span>
          </section>
            <nav>
                <a href="#what" class="hero-active">Hem</a>
                <a href="mailto:{email}">Kontakt</a>
                <a href="mailto:{email}" class="btn btn-primary" style="padding: 8px 20px;">Kontakta oss</a>
            </nav>
        </div>
    </header>''')

    if 'hero' in sections:
        d = sections['hero']
        hi = d.get('title_highlight', '')
        title = d.get('title', '')
        subtitle = d.get('subtitle', '')
        btn1 = d.get('button_primary', '')
        btn2 = d.get('button_secondary', '')
        if hi:
            title = f'{title}\n            <span style="color: var(--color-primary)">{hi}</span>'
        out.append(f'''    <section id="hero">
        <div class="container" style="padding: 0;">
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <a href="mailto:{email}" class="btn btn-primary">{btn1}</a>
          <a href="#program" class="btn btn-secondary">{btn2}</a>
        </div>
    </section>''')

    if 'what' in sections:
        d = sections['what']
        heading = d.get('heading', '')
        body = body_html(d.get('body', ''))
        out.append(f'''    <section id="what" class="section-bg-light">
        <div class="container">
          <div>
            <section style="display: flex; flex-direction: row; margin-right: 0; margin-left: auto;">
              <span aria-hidden="true" style="font-size: 3rem;">♟️</span>
              <h2 class="h2-no-underline">{heading}</h2>
            </section>
          </div>
          <div class="divider"></div>
          <div>
            {body}
          </div>
        </div>
    </section>''')

    if 'programs' in sections:
        d = sections['programs']
        heading = d.get('heading', '')
        cards = ''
        for item in d.get('items', []):
            if isinstance(item, dict):
                t = item.get('title', '')
                desc = item.get('desc', '')
            else:
                t = item
                desc = ''
            cards += f'''                <div class="program-card">
                    <div class="image"></div>
                    <h3>{t}</h3>
                    <p>{desc}</p>
                </div>
'''
        out.append(f'''    <section id="program">
        <div class="container">
            <h2>{heading}</h2>
            <div class="program-grid">
{cards}            </div>
        </div>
    </section>''')

    out.append('''    <section id="how" class="section-bg-dark">
        <div class="container">
            <h2>Så fungerar schackeffekt</h2>
            <div class="how-steps">
                <div class="how-step">
                    <span class="step-circle" aria-hidden="true"><span class="step-icon">♟️</span></span>
                    <h3>Upplev</h3>
                    <p>Spela och testa direkt – lär genom att göra.</p>
                </div>
                <div class="how-step">
                    <span class="step-circle" aria-hidden="true">
                        <img src="images/brain-idea-mind-svgrepo-com.svg" alt="" class="icon-white" style="width:2.5rem;height:2.5rem;">
                    </span>
                    <h3>Reflektera</h3>
                    <p>Förstå hur du tänker och fattar beslut.</p>
                </div>
                <div class="how-step">
                    <span class="step-circle" aria-hidden="true">
                        <img src="images/arrows-rotate-svgrepo-com.svg" alt="" class="icon-white" style="width:2.5rem;height:2.5rem;">
                    </span>
                    <h3>Överför</h3>
                    <p>Använd insikterna i verkliga situationer.</p>
                </div>
            </div>
        </div>
    </section>''')

    if 'why' in sections:
        d = sections['why']
        heading = d.get('heading', '')
        body = body_html(d.get('body', ''))
        img = d.get('image', 'images/hero-bg.jpg')
        out.append(f'''    <section id="why" class="section-bg-light split-section">
      <div class="container">
        <div class="split-section-body" style="gap:20px;">
          <div class="split-section-text" style="flex:1;">
            <div class="split-section-text-inner">
              <h2 class="h2-underline-left">{heading}</h2>
              {body}
            </div>
          </div>

          <div class="split-section-image" style="flex:1;">
            <img src="{img}" alt="">
          </div>

        </div>
      </div>
    </section>''')

    if 'reviews' in sections:
        d = sections['reviews']
        heading = d.get('heading', '')
        img = d.get('image', 'images/hero-bg.jpg')
        items = d.get('items', [])
        quotes = ''
        for i, item in enumerate(items):
            q = item if isinstance(item, str) else item.get('quote', '')
            if i > 0:
                quotes += '                        <div class="review-divider"></div>\n'
            quotes += '                        <div class="review-quote">\n'
            quotes += f'                            <p>{q}</p>\n'
            quotes += '                        </div>\n'
        out.append(f'''    <section id="reviews" class="section-bg-dark split-section">
        <div class="container">
            <div class="split-section-body">
                <div class="split-section-text" style="flex:7; padding-left: 11%;">
                    <h2 class="h2-underline-left" style="margin-bottom: 2rem;">{heading}</h2>
                    <div class="reviews-row">
{quotes}                    </div>
                </div>
                <div class="split-section-image" style="flex:5;">
                    <img src="{img}" alt="Schackeffekt">
                </div>
            </div>
        </div>
    </section>''')

    if 'cta' in sections:
        d = sections['cta']
        heading = d.get('heading', '')
        subtitle = d.get('subtitle', '')
        button = d.get('button', 'Kontakta oss')
        out.append(f'''    <section id="cta">
        <div class="container">
            <div class="cta-row flex-row">
                <div class="brand">
                    <span class="cta-icon"><span class="icon-white" aria-hidden="true">♟️</span></span>
                    <span class="brand-text">
                        <h2>{heading}</h2>
                        <p class="cta-sub">{subtitle}</p>
                    </span>
                </div>
                <a href="mailto:{email}" class="btn btn-dark">{button}</a>
            </div>
        </div>
    </section>''')

    out.append(f'''    <footer class="section-bg-dark" style="padding: 30px 0;">
        <div class="container flex-row">
            <section class="brand">
                <span aria-hidden="true" style="font-size: 2rem; padding: 0; margin: 0;">♟️</span>
                <span class="brand-text">
                    <h1 style="font-size: 1.4rem; margin-bottom: 0;">{brand}</h1>
                    <p style="color: var(--color-primary); font-size: 0.7rem;">{tagline}</p>
                </span>
            </section>
            <div style="color: var(--text-dark); font-size: 0.9rem; text-align: center;">
                <p style="margin-bottom: 4px;">{email_footer}</p>
                <p>{phone}</p>
            </div>
            <div style="display: flex; gap: 16px;">
                <a href="#" aria-label="LinkedIn" style="display: block;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22.23 0H1.77C0.79 0 0 0.77 0 1.72v20.56C0 23.23 0.79 24 1.77 24h20.46c0.98 0 1.77-0.77 1.77-1.72V1.72C24 0.77 23.21 0 22.23 0zM7.12 20.45H3.56V9h3.56v11.45zM5.34 7.55c-1.14 0-2.06-0.92-2.06-2.06s0.92-2.06 2.06-2.06 2.06 0.92 2.06 2.06-0.92 2.06-2.06 2.06zM20.45 20.45h-3.56v-5.57c0-1.33-0.48-2.24-1.67-2.24-0.91 0-1.45 0.61-1.69 1.2-0.09 0.21-0.11 0.51-0.11 0.81v5.8h-3.56V9h3.56v1.55c0.47-0.73 1.32-1.77 3.21-1.77 2.34 0 4.1 1.53 4.1 4.82v6.85z"/>
                    </svg>
                </a>
                <a href="#" aria-label="Instagram" style="display: block;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2.16c3.2 0 3.58.01 4.85.07 3.25.15 4.77 1.69 4.92 4.92.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.15 3.23-1.66 4.77-4.92 4.92-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-3.26-.15-4.77-1.7-4.92-4.92-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.15-3.23 1.66-4.77 4.92-4.92 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 2.7.27.27 2.7.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.2 4.35 2.63 6.78 6.98 6.98 1.28.06 1.69.07 4.95.07s3.67-.01 4.95-.07c4.35-.2 6.78-2.63 6.98-6.98.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.2-4.35-2.63-6.78-6.98-6.98C15.67.01 15.26 0 12 0z"/>
                        <path d="M12 5.84c-3.4 0-6.16 2.76-6.16 6.16s2.76 6.16 6.16 6.16 6.16-2.76 6.16-6.16S15.4 5.84 12 5.84zm0 10.16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
                        <circle cx="18.41" cy="5.59" r="1.44"/>
                    </svg>
                </a>
            </div>
        </div>
    </footer>''')

    return '\n'.join(out)


def main():
    md_path = SRC / 'site.md'
    if not md_path.exists():
        print(f"Error: {md_path} not found", file=sys.stderr)
        sys.exit(1)

    sections = parse_md(md_path.read_text())
    body = render_sections(sections)

    html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schackeffekt – Strategiskt lärande</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700;900&display=swap" rel="stylesheet">
    <link href="./stylesheet.css" rel="stylesheet"/>
</head>
<body>

{body}

</body>
</html>
'''

    out_path = SRC / 'index.html'
    out_path.write_text(html)
    print(f"Generated {out_path}")


if __name__ == '__main__':
    main()
