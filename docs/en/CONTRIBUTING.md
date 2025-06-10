# Contributing to Notipy

Thank you for your interest in Notipy!

Notipy is an open-source real-time notification system that integrates Notion with Discord. We welcome contributions that improve features, fix bugs, or enhance the user experience.

---

## 📌 Contribution Guidelines

- All contributions must be submitted via Pull Request to the `dev/main` branch.
- Please follow the coding style consistent with the existing codebase.
- Include a **clear description, related issue (if any), and test instructions** in your PR.
- Note: code formatting is automatically applied.

---

## 🧩 How to Contribute

1. **Fork** this repository.
2. Create a new branch in your fork (e.g., `feature/your-feature`, `fix/bug-description`).
3. Make your changes.
4. Commit and push your changes.
5. Create a Pull Request to the `dev/main` branch.
   - PR titles should follow this format: `[Feature] Your Feature` or `[Fix] Bug Description`.
   - Please provide as much detail as possible in the PR body.

---

## 🧪 Setting Up the Development Environment

This project runs on a Docker-based environment. Use the following commands:

```bash
# Build image and create networks
docker build -t notipy .
docker network create nginx-proxy
docker network create notipy_backend

# Run containers
docker compose up database backend discordbot -d
```

Create a `.env` file by copying from `var.env.example`. Make sure to test thoroughly in your local environment before submitting PRs.

---

## 🧠 Notes

* Each contributor must generate their own **Notion integration token** to test with the Notion API.
* If you need help with a PR, feel free to ask in the Discord support server.
* This project is licensed under Apache 2.0.

---

## 🙋 Need Help?

* [Discord Support Server](https://discord.gg/HzAnBSCN7t)
* Or open an issue in the GitHub repository
