// Handlers job nền: khởi chạy (setsid + runner python), poll trạng thái theo file + nhịp tim, hủy theo nhóm tiến trình.
// Chỉ privileged.ts import file này; kiểu tham số/kết quả lấy thẳng từ
// contract tương ứng (ArgsOf/ResOf) để handler không lệch contract.
import type { Factory } from "@space/privileged";
import type { z } from "@hatch/space-sdk";

type ArgsOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["request"]>;
type ResOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["response"]>;

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { FACTORY, PY3, projDir, readJson, withPlanWriteLock, writeJson } from "./core";
import { buildGenImageJobs, jobFiles, stepCommand } from "./projects";

export async function startJob({ jobId, projectId, step, force }: ArgsOf<"startJob">): Promise<ResOf<"startJob">> {
    if (step === "render") {
      // Keep the previous preview's md5 so a later check can prove the file changed.
      const preview = join(projDir(projectId), `export/${projectId}_preview.mp4`);
      if (existsSync(preview)) {
        const md5 = createHash("md5").update(readFileSync(preview)).digest("hex");
        const files = jobFiles(projectId, jobId);
        writeFileSync(files.status.replace(".json", ".prevmd5"), md5);
      }
    }
    let note = "";
    if (step === "genimages") {
      // A22 (05/11/2026): buildGenImageJobs bỏ qua cảnh đã có ảnh thật —
      // ghi rõ cảnh bị bỏ qua vào note của job để việc bỏ qua không lặng lẽ.
      // B39 (06/11/2026, lệnh CEO, lựa chọn A): bọc lời gọi trong
      // withPlanWriteLock như pickMedia/generateAiMedia — buildGenImageJobs
      // đọc–sửa–ghi plan, trước đây đứng ngoài quy ước khóa.
      const { count: n, skipped } = await withPlanWriteLock(projectId, () =>
        buildGenImageJobs(projectId),
      );
      note = `${n} job ảnh` + (skipped.length ? ` · Bỏ qua: ${skipped.join("; ")}` : "");
      if (n === 0) {
        // B22 (05/11/2026, lệnh CEO, lựa chọn A): không có job thì vẫn
        // ghi file status/log để lần poll sau ra "done" thay vì "error"
        // ma — trước đây return sớm không ghi gì, pollJob đọc fallback
        // {running:false, exitCode:null} rồi reconcileJob ghi DB thành
        // error với log trống, ghi đè cả thông báo đúng ban đầu.
        const logTail = skipped.length ? `Không có job ảnh mới. ${skipped.join("; ")}` : "Không có cảnh nào trong plan để tạo ảnh.";
        const files0 = jobFiles(projectId, jobId);
        writeFileSync(files0.log, logTail + "\n", "utf8");
        writeJson(files0.status, { running: false, exitCode: 0, step, note });
        return { logTail };
      }
    }
    const cmd = stepCommand(projectId, step, force);
    const files = jobFiles(projectId, jobId);
    writeFileSync(files.log, "", "utf8");
    writeJson(files.status, { running: true, exitCode: null, step, note });
    // The privileged executor process exits right after this handler returns,
    // and anything still in its session dies with it. So the real work runs
    // under setsid via a tiny wrapper that streams output to the log file and
    // writes the final status file itself. The wrapper also rewrites the
    // status file with a heartbeat ("beat") every ~10s while the child runs:
    // pid liveness alone is not proof of life after a host reboot (the pid
    // can be reused by an unrelated process), a stale heartbeat is. The
    // runner file is refreshed whenever its content differs, so fixes here
    // reach projects that already have an older runner on disk.
    const runnerPath = join(FACTORY, ".app-runner.py");
    const runnerSrc = [
      "import json, os, subprocess, sys, time",
      "status_path, log_path = sys.argv[1], sys.argv[2]",
      "cmd = sys.argv[3:]",
      "def write_status(payload):",
      "    tmp = status_path + '.tmp'",
      "    with open(tmp, 'w', encoding='utf-8') as f:",
      "        json.dump(payload, f)",
      "    os.replace(tmp, status_path)",
      "base = {'pid': os.getpid(), 'childPid': None, 'startedAt': int(time.time())}",
      "write_status(dict(base, running=True, exitCode=None, beat=int(time.time())))",
      "env = dict(os.environ)",
      "env['PYTHONUNBUFFERED'] = '1'",
      "with open(log_path, 'ab', buffering=0) as log:",
      "    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)",
      "    base['childPid'] = proc.pid",
      "    while proc.poll() is None:",
      "        write_status(dict(base, running=True, exitCode=None, beat=int(time.time())))",
      "        time.sleep(10)",
      "    rc = proc.returncode",
      "write_status(dict(base, running=False, exitCode=rc, beat=int(time.time())))",
      "",
    ].join("\n");
    let runnerCurrent = "";
    try {
      runnerCurrent = readFileSync(runnerPath, "utf8");
    } catch {
      runnerCurrent = "";
    }
    if (runnerCurrent !== runnerSrc) {
      writeFileSync(runnerPath, runnerSrc, "utf8");
    }
    const launcher = spawn(
      "setsid",
      [PY3, runnerPath, files.status, files.log, ...cmd],
      { detached: true, stdio: "ignore" },
    );
    launcher.on("error", () => {
      writeFileSync(files.log, "Không khởi động được tiến trình nền.", "utf8");
      writeJson(files.status, { running: false, exitCode: -1, step, note });
    });
    launcher.unref();
    return { logTail: note };
  }

export async function pollJob({ jobId, projectId }: ArgsOf<"pollJob">): Promise<ResOf<"pollJob">> {
    const files = jobFiles(projectId, jobId);
    const status = readJson<{ running?: boolean; exitCode?: number | null; pid?: number; beat?: number }>(
      files.status,
      { running: false, exitCode: null },
    );
    let logTail = "";
    try {
      logTail = readFileSync(files.log, "utf8").slice(-4000);
    } catch {
      logTail = "";
    }
    let running = status.running === true;
    let exitCode = typeof status.exitCode === "number" ? status.exitCode : null;
    const markDead = () => {
      // The runner died without writing its final status (host reboot,
      // killed process): report the job as finished-with-error instead of
      // leaving it "running" forever.
      running = false;
      exitCode = exitCode ?? -1;
      if (!logTail) {
        logTail =
          "Tiến trình nền đã kết thúc bất thường (không ghi được trạng thái cuối — máy chủ có thể đã khởi động lại hoặc tiến trình bị tắt giữa chừng).";
      }
    };
    if (running && typeof status.pid !== "number") {
      // Legacy status without a pid: fall back to file age — a live runner
      // rewrites this file at start, so an old "running" file means it died.
      try {
        if (Date.now() - statSync(files.status).mtimeMs > 120_000) markDead();
      } catch {
        markDead();
      }
    }
    if (running && typeof status.pid === "number") {
      let alive = true;
      try {
        process.kill(status.pid, 0);
      } catch {
        alive = false;
      }
      if (!alive) {
        markDead();
      } else if (
        typeof status.beat === "number" &&
        Date.now() / 1000 - status.beat > 180
      ) {
        // The pid answers but the runner's heartbeat stopped long ago: after
        // a host reboot the pid can belong to an unrelated process, or the
        // runner is wedged. Either way this job is not progressing.
        markDead();
      }
    }
    return { running, exitCode, logTail };
  }

export async function cancelJob({ jobId, projectId }: ArgsOf<"cancelJob">): Promise<ResOf<"cancelJob">> {
    const files = jobFiles(projectId, jobId);
    const status = readJson<{ running?: boolean; pid?: number; childPid?: number }>(
      files.status,
      { running: false },
    );
    let cancelled = false;
    if (status.running === true && typeof status.pid === "number") {
      // The runner runs under setsid, so its pid is the process-group
      // leader: signalling the group stops the child (ffmpeg/python) too,
      // not just the wrapper.
      try {
        process.kill(-status.pid, "SIGTERM");
        cancelled = true;
      } catch {
        try {
          process.kill(status.pid, "SIGTERM");
          cancelled = true;
        } catch {
          cancelled = false;
        }
      }
      if (typeof status.childPid === "number") {
        try {
          process.kill(status.childPid, "SIGTERM");
        } catch {
          /* child already gone */
        }
      }
    }
    if (cancelled) {
      writeFileSync(files.log, "\n[app] Job đã bị hủy theo yêu cầu.\n", {
        flag: "a",
      });
      writeJson(files.status, {
        running: false,
        exitCode: -2,
        pid: typeof status.pid === "number" ? status.pid : null,
        cancelled: true,
      });
    }
    return { cancelled };
  }
