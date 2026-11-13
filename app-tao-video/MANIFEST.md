# MANIFEST — App Tạo Video (danh sách file nguồn chuẩn)

Mục đích: đối chiếu file nguồn của app khi dựng lại theo BOOTSTRAP C5.
Sinh ngày 14/11/2026 từ cây repo tại commit 2a20b90b (đợt đẩy toàn bộ 13/11/2026).

Tổng 48 file trong cây app-tao-video/ trên repo, trong đó:
- 47 file nguồn (đối chiếu theo manifest này).
- 1 file tự sinh: `app-tao-video/server/.generated/privileged.contract.ts` — KHÔNG đối chiếu, KHÔNG sửa tay (hệ thống tự sinh khi dựng, xem BOOTSTRAP C5).

Quy tắc: khi thêm/bớt file nguồn thì cập nhật manifest này trong cùng đợt.
File migration mới chỉ hợp lệ khi đã đăng ký trong `drizzle/meta/_journal.json`.
Không dùng số đếm file cứng làm điều kiện dừng — đối chiếu theo danh sách này.

## File nguồn (47 file)

- app-tao-video/AGENTS.md
- app-tao-video/DATA-PLAN.md
- app-tao-video/bun.lock
- app-tao-video/bunfig.toml
- app-tao-video/client/build.mjs
- app-tao-video/client/index.html
- app-tao-video/client/src/App.tsx
- app-tao-video/client/src/api.ts
- app-tao-video/client/src/components/AudioTab.tsx
- app-tao-video/client/src/components/AutoPanel.tsx
- app-tao-video/client/src/components/FinishTab.tsx
- app-tao-video/client/src/components/InfoTip.tsx
- app-tao-video/client/src/components/MediaTab.tsx
- app-tao-video/client/src/components/PreviewTab.tsx
- app-tao-video/client/src/components/ProjectList.tsx
- app-tao-video/client/src/components/ProjectView.tsx
- app-tao-video/client/src/components/ScenesTab.tsx
- app-tao-video/client/src/components/ScriptTab.tsx
- app-tao-video/client/src/components/shared.tsx
- app-tao-video/client/src/globals.d.ts
- app-tao-video/client/src/lib.ts
- app-tao-video/client/src/main.tsx
- app-tao-video/client/src/theme.css
- app-tao-video/client/tsconfig.json
- app-tao-video/drizzle/0001_initial.sql
- app-tao-video/drizzle/0002_app_state_jobs_trash_snapshots.sql
- app-tao-video/drizzle/0003_auto_progress.sql
- app-tao-video/drizzle/0004_drop_snapshots_table.sql
- app-tao-video/drizzle/meta/_journal.json
- app-tao-video/package.json
- app-tao-video/server/src/actions.ts
- app-tao-video/server/src/priv/core.ts
- app-tao-video/server/src/priv/handlers-jobs.ts
- app-tao-video/server/src/priv/handlers-media.ts
- app-tao-video/server/src/priv/handlers-preview.ts
- app-tao-video/server/src/priv/handlers-projects.ts
- app-tao-video/server/src/priv/media-library.ts
- app-tao-video/server/src/priv/motion.ts
- app-tao-video/server/src/priv/plan-normalize.ts
- app-tao-video/server/src/priv/projects.ts
- app-tao-video/server/src/privileged.ts
- app-tao-video/server/src/schema.ts
- app-tao-video/server/src/script-prompt.test.ts
- app-tao-video/server/src/script-prompt.ts
- app-tao-video/server/tsconfig.json
- app-tao-video/space.json
- app-tao-video/tsconfig.base.json
