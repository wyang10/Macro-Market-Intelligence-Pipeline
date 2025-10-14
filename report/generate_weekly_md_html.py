import sys, re, os

ARCH_PATH = "./report_assets/architecture.png"

def md_to_html(md):
    t = md
    t = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img alt="\1" src="\2"/>', t)
    t = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'^# (.*)$', r'<h1>\1</h1>', t, flags=re.MULTILINE)
    t = re.sub(r'^## (.*)$', r'<h2>\1</h2>', t, flags=re.MULTILINE)
    t = re.sub(r'^- (.*)$', r'<ul><li>\1</li></ul>', t, flags=re.MULTILINE)
    t = '<p>' + t.replace('\n\n','</p><p>') + '</p>'; t = t.replace('</ul>\n<ul>','')
    return t

def wrap_html(body, arch_exists):
    img_html = f'<p><img src="{ARCH_PATH}" alt="Architecture Overview"/></p>' if arch_exists else ''
    return "<!doctype html><meta charset=\"utf-8\"><body style=\"max-width:860px;margin:40px auto;padding:0 16px;font-family:system-ui\">" + img_html + body + "</body>"

def main(md_path, out_html):
    with open(md_path,'r',encoding='utf-8') as f: md=f.read()
    arch_exists = os.path.exists(ARCH_PATH)
    html = wrap_html(md_to_html(md), arch_exists)
    with open(out_html,'w',encoding='utf-8') as f: f.write(html)
    print('HTML saved:', out_html, '| Architecture image:', 'ON' if arch_exists else 'OFF')

if __name__=='__main__':
    main(sys.argv[1], sys.argv[2])
