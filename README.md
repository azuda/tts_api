https://huggingface.co/spaces/NihalGazi/Text-To-Speech-Unlimited

# Setup

How to set up and run Rundle TTS app on host machine

## SSL Cert Setup

(macOS)

1. Open Keychain Access -> System Roots -> search "cloudflare"
2. Export Cloudflare root CA cert to project dir as `cert.pem`
3. Copy `cert.pem` to `~/.cloudflared/`

## Cloudflare Tunnel

Install cloudflared:

```bash
brew install cloudflared
```

<details>
<summary>Set tunnel to run as a service on system boot:</summary>

```bash
sudo cloudflared service install <token>
```
</details>

<details>
<summary>Manually run tunnel in current terminal session only:</summary>

```bash
cloudflared tunnel run --token <token>
```
</details>

## Gradio Web App

Setup and install dependencies:

```bash
git clone <repo_url>
cd tts_api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run script:

```bash
chmod +x run.sh
./run.sh
```
