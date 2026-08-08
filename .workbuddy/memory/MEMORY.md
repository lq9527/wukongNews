# 项目长期记忆

## SSH 密钥分工约定
- `id_ed25519`(默认旧密钥):用于**公司代码仓库**及其他非 GitHub 主机。
- `id_ed25519_githup`(2026-08-09 新建,邮箱 1534946877@qq.com):专用于个人 GitHub(`git@github.com:lq9527/*`)。
- `id_rsa_gitee`:用于 Gitee。
- `~/.ssh/config` 已加 `Host github.com` 块,`IdentityFile ~/.ssh/id_ed25519_githup` + `IdentitiesOnly yes`,强制 GitHub 走新密钥;其他主机不受影响、仍走默认 `id_ed25519`。
- 注意:若公司仓库也托管在 github.com 域名,需单独加 Host 块指回 `id_ed25519`。
