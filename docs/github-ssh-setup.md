# GitHub SSH Setup (WSL2)

Steps taken to configure SSH push for `anna-belle-zhang/superpowerwithcodex` on 2026-06-24.

## 1. Authenticate GitHub CLI

```bash
gh auth login
# Choose: GitHub.com → HTTPS → browser-based login
```

## 2. Grant SSH key management scope

```bash
gh auth refresh -h github.com -s admin:public_key
```

## 3. Generate an SSH key

```bash
ssh-keygen -t ed25519 -C "anna.belle.sophie.zhang@gmail.com" -f ~/.ssh/id_ed25519 -N ""
```

## 4. Add the public key to GitHub

```bash
gh ssh-key add ~/.ssh/id_ed25519.pub --title "WSL2-main" --type authentication
```

## 5. Switch remotes from HTTPS to SSH

```bash
git remote set-url origin git@github.com:anna-belle-zhang/superpowerwithcodex.git
```

## 6. Verify

```bash
ssh -T git@github.com
# Expected: Hi anna-belle-zhang! You've successfully authenticated...
```

## Repeat for other repos

For any other repo currently using HTTPS:

```bash
git remote set-url origin git@github.com:<owner>/<repo>.git
```

No need to re-add the key — the same `~/.ssh/id_ed25519` is reused.
