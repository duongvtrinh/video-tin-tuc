import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

// App-side state only. Project content itself lives in the repo filesystem
// (~/workspace/vieneu-asset-factory/projects/<pid>/) and is read live through
// privileged handlers — it is never duplicated into this database.

export const jobs = sqliteTable("jobs", {
  id: text("id").primaryKey(),
  projectId: text("project_id").notNull(),
  step: text("step").notNull(),
  status: text("status", { enum: ["running", "done", "error", "cancelled"] })
    .notNull()
    .default("running"),
  startedAt: integer("started_at").notNull(),
  finishedAt: integer("finished_at"),
  exitCode: integer("exit_code"),
  logTail: text("log_tail").notNull().default(""),
  note: text("note").notNull().default(""),
});

export const trash = sqliteTable("trash", {
  projectId: text("project_id").primaryKey(),
  name: text("name").notNull().default(""),
  deletedAt: integer("deleted_at").notNull(),
});

// 12B (05/11/2026) + B34 (06/11/2026, lệnh CEO, lựa chọn A): bảng
// snapshots DB đã gỡ khỏi schema — không code nào đọc/ghi nó (snapshot
// thật nằm trong .snapshots/ của project, xem handlers-projects.ts).
// Migration 0002 vẫn tạo bảng này trong DB hiện có nên KHÔNG sửa file
// migration đã áp dụng; migration 0004 DROP TABLE snapshots dọn sạch
// DB khi áp dụng (chỉ xóa bảng DB — tính năng snapshot file giữ nguyên).

// Tiến độ của panel "Tạo video tự động" (10 bước) lưu xuống server theo
// project: đóng/mở lại app vẫn thấy đúng bước đã xong, bước lỗi và các
// mục cần xử lý tay, thay vì chỉ sống trong bộ nhớ trang như trước.
export const autoProgress = sqliteTable("auto_progress", {
  projectId: text("project_id").primaryKey(),
  statuses: text("statuses").notNull().default("{}"),
  messages: text("messages").notNull().default("[]"),
  needsManual: text("needs_manual").notNull().default("[]"),
  updatedAt: integer("updated_at").notNull().default(0),
});
