# Hướng dẫn kết nối Google Stitch qua MCP (Model Context Protocol)

## 1. Cơ chế hoạt động với Django MVT

Google Stitch (Google Labs) là công cụ AI thiết kế giao diện từ prompt/ý tưởng. Khi kết nối qua **MCP**:
1. AI Agent (Antigravity) có thể truy cập dự án trên Google Stitch để đọc layout, CSS tokens, và xuất HTML/Tailwind.
2. AI Agent sẽ tự động bóc tách các component giao diện và đặt vào:
   - Thư mục `templates/` (ví dụ: `templates/home.html`, `templates/components/navbar.html`).
   - Thư mục `static/css/` hoặc sử dụng trực tiếp các class Tailwind CSS.
3. Liên kết trực tiếp với Django Views và Models.

---

## 2. Chuẩn bị công cụ kết nối (Cần hỗ trợ từ bạn)

Hiện tại máy bạn đã có sẵn **Python 3.12** và **Git**. Để kết nối Stitch MCP Server trực tiếp:

1. **Cài đặt Node.js LTS**:
   - Stitch MCP Server và SDK vận hành trên hệ sinh thái npm (`npx @davideast/stitch-mcp` hoặc `stitch-skills`).
   - Tải và cài đặt tại: [https://nodejs.org](https://nodejs.org) (chọn bản LTS).
2. **Lấy API Key / Access Token từ Google Stitch**:
   - Truy cập Google Stitch (Google Labs).
   - Lấy `API Key` (hoặc OAuth token) và `Project ID`.
   - Điền vào file `.env`:
     ```env
     STITCH_API_KEY=your_key_here
     STITCH_PROJECT_ID=your_project_id_here
     ```

---

## 3. Cấu hình MCP Server (Ví dụ trong `mcp.json`)

Khi bạn đã có Node.js và Token Stitch:

```json
{
  "mcpServers": {
    "google-stitch": {
      "command": "npx",
      "args": ["-y", "@davideast/stitch-mcp"],
      "env": {
        "STITCH_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```
*(Nếu chưa muốn cài Node.js ngay, bạn hoàn toàn có thể copy mã xuất HTML từ web Google Stitch vào chat, AI sẽ tự động phân giải thành các Django Templates chuẩn).*
