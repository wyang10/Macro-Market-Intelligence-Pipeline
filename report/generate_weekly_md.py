import os
from datetime import datetime
def main(base='..', out_dir='./report_out'):
    out = os.path.join(base, out_dir, f"ai_chips_weekly_{datetime.utcnow().strftime('%Y-%m-%d')}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not os.path.exists(out):
        with open(out,'w',encoding='utf-8') as f:
            f.write("# AI Chips Weekly\n\n## Executive Summary\n(placeholder)\n")
    print("Weekly MD:", out)
if __name__=='__main__': main()
