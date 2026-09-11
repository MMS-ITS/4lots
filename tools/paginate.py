#!/usr/bin/env python3
"""Two-pass pagination: measure the built artifact, then rebuild it with real page numbers.

Each .sheet starts on a fresh printed page (break-before:page) but may run onto a second
page. This measures every sheet against the A4 printable box, works out which printed pages
each sheet occupies, writes data/pagination.json, rebuilds index.html with those numbers in
the contents list and the footers, and finally verifies the PDF page count matches.

    python3 tools/paginate.py
"""
import json
import math
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
TMP = os.path.join(ROOT, '.measure.html')
PDF = os.path.join(ROOT, '.paginate-check.pdf')
PGJSON = os.path.join(ROOT, 'data', 'pagination.json')
CHROME = '/usr/local/bin/chrome'

# @page is A4 with 13mm top / 15mm sides / 14mm bottom, so the printable box is:
BOX_W_MM = 210 - 15 - 15
BOX_H_MM = 297 - 13 - 14

INJECT = """
<style id="printsim">
  body{background:#fff !important;}
  .sheet{margin:0 !important; box-shadow:none !important; width:%(w)smm !important;
         min-height:0 !important; padding:0 !important;}
  .foot{display:none !important;}
  .noprint{display:none !important;}
  .map{height:auto !important;}
  .map iframe{display:none !important;}
  .mapfall{display:block !important;}
  #leaf{display:none !important;}
  .tabs{display:none !important;}
</style>
<script>
window.addEventListener('load',function(){
  var probe=document.createElement('div');
  probe.style.cssText='position:absolute;height:100mm;width:1px;visibility:hidden';
  document.body.appendChild(probe);
  var mm=1/(probe.getBoundingClientRect().height/100);
  var rows=[];
  document.querySelectorAll('.sheet').forEach(function(s,i){
    rows.push((i+1)+':'+(s.getBoundingClientRect().height*mm).toFixed(1)+':'+(s.id||'-'));
  });
  var d=document.createElement('div'); d.id='RESULT';
  d.textContent='#M#'+rows.join('|')+'#M#';
  document.body.insertBefore(d,document.body.firstChild);
});
</script>
""" % {'w': BOX_W_MM}


def run_chrome(args, timeout=240):
    return subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox'] + args,
                          capture_output=True, text=True, timeout=timeout)


def measure():
    html = open(SRC).read().replace('</head>', INJECT + '</head>')
    open(TMP, 'w').write(html)
    out = run_chrome(['--virtual-time-budget=10000', '--window-size=900,1200',
                      '--dump-dom', 'file://' + TMP]).stdout
    m = re.search(r'id="RESULT"[^>]*>#M#(.*?)#M#', out)
    if not m:
        print("measurement failed", file=sys.stderr)
        sys.exit(1)
    rows = []
    for rec in m.group(1).split('|'):
        i, h, sid = rec.split(':')
        rows.append((int(i), float(h), None if sid == '-' else sid))
    os.remove(TMP)
    return rows


def build():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_artifact.py')],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(1)
    return r.stdout.strip()


def pdf_page_map():
    """Print the artifact and read the sheet markers back out, page by page."""
    run_chrome(['--no-pdf-header-footer', '--print-to-pdf=' + PDF, 'file://' + SRC])
    from pypdf import PdfReader
    reader = PdfReader(PDF)
    LIG = {'\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl', '\ufb03': 'ffi',
           '\ufb04': 'ffl', '\ufb05': 'st', '\ufb06': 'st'}
    starts = {}
    for i, page in enumerate(reader.pages, start=1):
        txt = page.extract_text() or ''
        for k, v in LIG.items():
            txt = txt.replace(k, v)
        for anchor in re.findall(r'\[\[S:([^\]]+)\]\]', txt):
            starts.setdefault(anchor, i)
    return starts, len(reader.pages)


def main():
    print("pass 1 — build")
    print("  " + build())

    print("\npass 2 — print, and read the sheet markers back out of the PDF")
    starts, total = pdf_page_map()
    order = [a for a, _, _ in ANCHORS if a]
    missing = [a for a in order if a not in starts]
    if missing:
        print("  markers not found for: %s" % ", ".join(map(str, missing)))
        sys.exit(1)
    sheets = {}
    for n, a in enumerate(order):
        nxt = starts[order[n + 1]] - 1 if n + 1 < len(order) else total
        sheets[a] = {'start': starts[a], 'end': max(starts[a], nxt)}
    multi = [(a, v) for a, v in sheets.items() if v['end'] > v['start']]
    for a, v in multi:
        print("  %-16s pages %d–%d" % (a, v['start'], v['end']))
    print("  %d of %d sheets span more than one page; %d printed pages in total"
          % (len(multi), len(order), total))

    json.dump({'total_pages': total, 'sheets': sheets}, open(PGJSON, 'w'), indent=1)

    print("\npass 3 — rebuild with the real page numbers")
    print("  " + build())

    print("\npass 4 — verify the rebuild did not move anything")
    starts2, total2 = pdf_page_map()
    drift = [a for a in order if starts2.get(a) != sheets[a]['start']]
    print("  %d printed pages; %d sheets moved" % (total2, len(drift)))
    if total2 != total or drift:
        print("  page numbers shifted on rebuild: %s" % ", ".join(map(str, drift[:8])))
        json.dump({'total_pages': total2,
                   'sheets': {a: {'start': starts2[a],
                                  'end': (starts2[order[n + 1]] - 1 if n + 1 < len(order) else total2)}
                              for n, a in enumerate(order)}}, open(PGJSON, 'w'), indent=1)
        print("  rewrote pagination.json from the second print; rebuilding once more")
        print("  " + build())
        starts3, total3 = pdf_page_map()
        drift3 = [a for a in order if starts3.get(a) != json.load(open(PGJSON))['sheets'][a]['start']]
        print("  settled at %d pages, %d sheets adrift" % (total3, len(drift3)))
        if drift3:
            sys.exit(2)
    else:
        print("  stable — the contents list and every footer carry the correct page number")
    os.remove(PDF)


ANCHORS = []


def load_anchors():
    """Read the sheet order straight out of the built HTML."""
    html = open(SRC).read()
    for m in re.finditer(r'<span class="smark" aria-hidden="true">\[\[S:([^\]]+)\]\]</span>', html):
        ANCHORS.append((m.group(1), None, None))


if __name__ == '__main__':
    build()
    load_anchors()
    main()
