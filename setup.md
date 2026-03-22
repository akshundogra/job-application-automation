# Setup Guide

Complete step-by-step installation for the Job Application Automation.

---

## 1. Prerequisites

Install the following on your Mac:

### LibreOffice (PDF conversion)
```bash
brew install --cask libreoffice
```

### ExifTool (metadata scrubbing)
```bash
brew install exiftool
```

### Python dependencies
```bash
pip install flask python-docx
```

### Verify installations
```bash
which soffice        # should return path to LibreOffice
which exiftool       # should return path to ExifTool
python3 --version    # should return Python 3.x
```

---

## 2. n8n Setup

### Start n8n via Docker

```bash
mkdir ~/.n8n-files

docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -v ~/.n8n-files:/home/node/.n8n-files \
  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false \
  -e NODE_FUNCTION_ALLOW_EXTERNAL=mammoth \
  -e NODE_FUNCTION_ALLOW_BUILTIN=fs,path,child_process \
  docker.n8n.io/n8nio/n8n
```

### Install mammoth inside Docker
```bash
docker exec -u root n8n npm install -g mammoth
```

### Import the workflow
1. Open `http://localhost:5678`
2. Go to **Workflows** → **Import from file**
3. Upload `n8n/workflow.json`

---

## 3. Claude API Setup

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account and add credits ($10 is enough for hundreds of applications)
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-api...`)

### Add to n8n
1. Go to n8n → **Settings** → **Credentials**
2. Click **Add Credential** → **Anthropic**
3. Name: `Anthropic account`
4. Paste your API key
5. Save

---

## 4. Resume Files

Copy your resume DOCX files to the n8n-files folder:

```bash
cp your-resume-EN.docx ~/.n8n-files/Resume-EN.docx
cp your-resume-DE.docx ~/.n8n-files/Resume-DE.docx
```

If you only apply in one language, you only need one file.

---

## 5. Python Script Configuration

Open `apply_changes.py` and update:

```python
# Update these paths to match your system
source_resume = '/Users/YOUR_USERNAME/.n8n-files/Resume-EN.docx'

# Update your portfolio domain
# Replace 'YOUR_PORTFOLIO_DOMAIN' with your actual domain
```

Also update the output directory in the n8n **Write Config** nodes:
```javascript
outputDir: '/Users/YOUR_USERNAME/Desktop/JobApplications/' + fileBase,
```

---

## 6. Personalizing the Workflow

> ⚠️ **This is the most important step.** After importing the workflow, you must replace all placeholders with your own details.

### Required replacements

| Placeholder | Replace with | Where |
|---|---|---|
| `YOUR_NAME` | Your full name | Cover Letter EN/DE, Resume Analysis nodes |
| `YOUR_EMAIL` | Your email address | Cover Letter EN/DE nodes |
| `YOUR_PHONE` | Your phone number | Cover Letter EN/DE nodes |
| `YOUR_CITY, YOUR_COUNTRY` | Your location | Cover Letter EN/DE nodes |
| `YOUR_LINKEDIN` | Your LinkedIn URL | Cover Letter EN/DE nodes |
| `YOUR_PORTFOLIO_DOMAIN` | Your portfolio website | Edit Fields node, Cover Letter EN/DE nodes |
| `YOUR_LASTNAME_FIRSTNAME_` | Your name for file naming | Edit Fields node |
| `YOUR_METRIC_1` to `YOUR_METRIC_5` | Your real work metrics | Cover Letter EN/DE nodes |
| `YOUR_ROLE` | Your professional title | Resume Analysis nodes |
| `YOUR_USERNAME` | Your Mac username | Write Config nodes, apply_changes.py |

### How to find and replace in n8n

1. Open each LLM node (Cover Letter EN, Cover Letter DE, Analyse Resume EN, Analyse Resume DE)
2. Click on the prompt field
3. Search for `YOUR_` to find all placeholders
4. Replace with your actual information

### Metrics format examples

```
English: **ROAS 36x+**, **400% traffic increase**, **80% manual effort reduction**
German:  **ROAS 36x+**, **400% Traffic-Steigerung**, **80% weniger manueller Aufwand**
```

### Resume Analysis prompt — update your profile

In the **Analyse Resume EN** and **Analyse Resume DE** nodes, replace the candidate profile section with your actual background, skills, tools and key metrics. The more specific you are here, the better the tailoring will be.

---

## 7. Webhook Server Setup

The webhook server allows n8n to trigger the Python script automatically.

### Start manually
```bash
python3 scripts/webhook_server.py
```

### Auto-start on Mac boot

```bash
cat > ~/Library/LaunchAgents/com.jobautomation.webhook.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jobautomation.webhook</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/job-application-automation/scripts/webhook_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/.n8n-files/webhook.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/.n8n-files/webhook_error.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.jobautomation.webhook.plist
```

### Verify it's running
```bash
curl http://localhost:5001/health
# Should return: {"status": "ok"}
```

---

## 8. n8n Workflow Configuration

After importing the workflow, update these nodes:

### Edit Fields node
Update UTM base URL and file naming:
```javascript
'https://YOUR_PORTFOLIO_DOMAIN/?utm_source=cover-letter-english...'
'YOUR_LASTNAME_FIRSTNAME_' + companyName + '_' + jobTitle
```

### Analyse Resume EN/DE nodes
Replace the candidate profile in the system prompt with your own:
- Name, current role, years of experience
- Skills and tools list
- Key metrics from your work

### Cover Letter EN/DE nodes
Update contact information:
```
YOUR_NAME | YOUR_CITY, YOUR_COUNTRY
YOUR_EMAIL | YOUR_PHONE
YOUR_LINKEDIN
```

### Write Config EN/DE nodes
Update output directory:
```javascript
outputDir: '/Users/YOUR_USERNAME/Desktop/JobApplications/' + fileBase,
```

### Trigger Python Script EN/DE nodes
Default webhook URL — update only if using a different port:
```
http://host.docker.internal:5001/run
```

---

## 9. Connect n8n to Docker network

If cloudflared is running as a Docker container, connect n8n to the same network:

```bash
docker network connect n8n-local_tunnel n8n
```

---

## 10. Publish the Workflow

1. Click **Publish** in the top right of n8n
2. Click the Form Trigger node
3. Copy the **Production URL**
4. Bookmark it in your browser

---

## 11. Test It

Submit a test application:
1. Open your bookmarked form URL
2. Fill in any job title, company, and paste a job description
3. Select English or German
4. Submit
5. Wait ~60 seconds
6. Check `Desktop/JobApplications/` for your files

Check the application log:
```bash
cat ~/.n8n-files/applications_log.csv
```

---

## Troubleshooting

**LibreOffice not found:**
```bash
which soffice
# Update the path in apply_changes.py if different
```

**Webhook server not reachable from n8n:**
```bash
curl http://host.docker.internal:5001/health
```

**mammoth module not found in n8n:**
```bash
docker exec -u root n8n npm install -g mammoth
docker restart n8n
```

**ATS scores showing N/A in log:**
- Check the Analyse Resume node output format
- The regex matches `before: XX%` and `after: XX%` patterns

**n8n expressions showing red:**
- Check node names match exactly (case sensitive)
- Use `$('Exact Node Name').first().json.fieldName`

**Grant File Access popup from Word:**
- Switch PDF conversion to LibreOffice in `apply_changes.py`
- LibreOffice has no macOS sandbox restrictions
