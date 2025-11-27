https://huggingface.co/spaces/NihalGazi/Text-To-Speech-Unlimited

# Setup

How to set up and run Rundle TTS app on host machine

## SSL Cert Setup

(macOS)

1. Open Keychain Access -> System Roots -> search "cloudflare"
2. Export Cloudflare root CA cert to project dir as `cert.pem`
3. Copy `cert.pem` to `~/.cloudflared/`

## Cloudflare Tunnel

Install cloudflared and set tunnel to run as a service:

```bash
brew install cloudflared && 
sudo cloudflared service install <token>
```

<details>
<summary>To run tunnel in current terminal session only:</summary>

```bash
cloudflared tunnel run --token <token>
```
</details>

## Gradio Web App

Setup and install dependencies:

```bash
git clone <repo_url>
cd rundle_tts
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
