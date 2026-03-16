# Antigravity Skills cho Cursor Projects

Tài liệu này tóm tắt cách áp dụng `antigravity-awesome-skills` cho project **ComputerVisionPj** trong Cursor trên Windows.

> **Project hiện tại:** `D:\ComputerVisionPj` — Skills đã được gắn qua junction tại `.cursor/skills`.

---

## 1) Cách setup nhanh

### Cách A - Dùng toàn bộ skills (khuyến nghị)

Tạo junction `.cursor/skills` của project đến kho skill trung tâm:

```powershell
powershell -ExecutionPolicy Bypass -File "D:\CursorSkill\setup-cursor-skills.ps1" -ProjectPath "D:\ComputerVisionPj" -Mode link-all
```

Ưu điểm:
- Một nguồn skill duy nhất, cập nhật ở một chỗ.
- Dùng được cho mọi project mà không copy 1,250+ skills.

### Cách B - Chỉ copy bộ skills cốt lõi

```powershell
powershell -ExecutionPolicy Bypass -File "D:\CursorSkill\setup-cursor-skills.ps1" -ProjectPath "D:\ComputerVisionPj" -Mode copy-core
```

Ưu điểm:
- Nhẹ hơn, dễ kiểm soát.
- Phù hợp nếu bạn muốn project độc lập.

## 2) Mục tiêu cho nhiều project

- Mỗi project có `.cursor/skills` riêng, nhưng có thể trỏ cùng 1 kho.
- Khi mở project trong Cursor, gọi skill bằng `@skill-name` trong chat.

Ví dụ:
- `@brainstorming` để lập kế hoạch.
- `@lint-and-validate` để rà soát và chuẩn hóa code.
- `@systematic-debugging` để debug có cấu trúc.
- `@api-security-best-practices` để hardening API.

## 3) Prompt mẫu để dùng hằng ngày

- `Use @brainstorming to break this feature into implementation tasks in this repo.`
- `Use @concise-planning then @test-driven-development for this bug fix.`
- `Use @lint-and-validate on changed files and suggest fixes only.`
- `Use @api-security-best-practices to review app/api routes.`

## 4) Lưu ý Windows

- Repo antigravity có symlink/junction trong một số skill. Nếu clone lại repo, ưu tiên:

```powershell
git clone -c core.symlinks=true https://github.com/sickn33/antigravity-awesome-skills.git
```

- Nếu script báo path đã tồn tại, thêm `-Force` để thay thế:

```powershell
powershell -ExecutionPolicy Bypass -File "D:\CursorSkill\setup-cursor-skills.ps1" -ProjectPath "D:\ComputerVisionPj" -Mode link-all -Force
```

## 5) Bộ skill nên dùng trước (gợi ý)

Bắt đầu với 5 skill:
- `@brainstorming`
- `@concise-planning`
- `@systematic-debugging`
- `@lint-and-validate`
- `@test-driven-development`

Sau đó bổ sung theo stack:
- Next.js/React: `@nextjs-best-practices`, `@react-best-practices`, `@web-design-guidelines`
- API/Backend: `@api-design-principles`, `@api-security-best-practices`
- Deploy: `@vercel-deployment`

## 6) Ví dụ thực tế: folder rỗng -> app React Native

Giả sử bạn có folder rỗng: `D:\Projects\rn-demo`

### Bước 1 - gắn skills vào project

```powershell
powershell -ExecutionPolicy Bypass -File "D:\CursorSkill\setup-cursor-skills.ps1" -ProjectPath "D:\Projects\rn-demo" -Mode link-all
```

Sau đó mở folder `D:\Projects\rn-demo` trong Cursor.

### Bước 2 - prompt khởi tạo architecture

Trong Cursor chat, gõ:

```text
Use @brainstorming and @react-native-architecture to design a React Native app architecture for this empty project.
Prefer Expo + TypeScript. Ask me for feature requirements first.
```

Mục tiêu: chốt structure, navigation, state management, env, API layer trước khi scaffold code.

### Bước 3 - scaffold app trong folder hiện tại

Nếu bạn muốn dùng Expo:

```text
Use @mobile-developer to scaffold an Expo React Native app in this current empty folder with TypeScript and recommended structure.
```

Nếu cần setup UI với Tailwind Native:

```text
Use @expo-tailwind-setup to add Tailwind setup for this Expo project and verify it compiles.
```

### Bước 4 - phát triển theo chu kỳ skill

Mỗi feature nên đi theo thứ tự:
- `@concise-planning` -> chốt task nhỏ
- `@test-driven-development` -> viết test/case trước (nếu phù hợp)
- `@mobile-developer` hoặc `@react-native-architecture` -> implement
- `@lint-and-validate` -> dọn dẹp và chuẩn hóa code
- `@systematic-debugging` -> xử lý lỗi build/runtime

### Bước 5 - một prompt chuỗi hoàn chỉnh

```text
Use @concise-planning to create tasks for building auth (login/register/forgot password) in this Expo app.
Then use @mobile-developer to implement the first task only.
After coding, run @lint-and-validate on changed files.
```

### Skill gợi ý cho React Native/Expo

- `@react-native-architecture`
- `@mobile-developer`
- `@expo-tailwind-setup`
- `@expo-dev-client`
- `@expo-cicd-workflows`
- `@expo-deployment`
