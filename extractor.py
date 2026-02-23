import email
from email import policy
import quopri
import base64
import os
import re

def convert_mhtml_to_html(mhtml_path, output_dir, output_main_html="index.html"):
    with open(mhtml_path, 'r', encoding='utf-8', errors='ignore') as f:
        msg = email.message_from_file(f, policy=policy.default)
        
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = ""
    resources = {}
    
    for part in msg.walk():
        content_type = part.get_content_type()
        content_location = part.get('Content-Location')
        
        if content_type == 'text/html':
            if not html_content:
                html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
        else:
            filename = part.get_filename()
            if not filename and content_location:
                filename = content_location.split('/')[-1].split('?')[0]
            
            if not filename:
                continue
                
            payload = part.get_payload(decode=True)
            if payload:
                # Extract filename without parameters
                safe_filename = filename.split('?')[0]
                # Replace invalid chars
                safe_filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', safe_filename)
                
                if not safe_filename:
                    continue
                resources[content_location] = safe_filename
                
                with open(os.path.join(output_dir, safe_filename), 'wb') as res_f:
                    res_f.write(payload)
                    
    # Now replace resources in HTML
    for loc, safe_filename in resources.items():
        if loc:
            html_content = html_content.replace(loc, safe_filename)
            
    # Clean up some angular attributes and comments for a cleaner HTML
    html_content = re.sub(r'\s_ngcontent-[a-zA-Z0-9-]+(="")?', '', html_content)
    html_content = re.sub(r'\s_nghost-[a-zA-Z0-9-]+(="")?', '', html_content)
    html_content = re.sub(r'\sng-reflect-[a-zA-Z0-9-]+="[^"]*"', '', html_content)
    html_content = re.sub(r'<!--\s*(ng-container|ng-template|bindings|router-outlet).*?-->', '', html_content)
    # Remove <base href="...">
    html_content = re.sub(r'<base\s+href="[^"]*">', '', html_content)


    with open(os.path.join(output_dir, output_main_html), 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    convert_mhtml_to_html("เข้าสู่ระบบ.mhtml", ".", "index.html")
