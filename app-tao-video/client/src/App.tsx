// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { ProjectList } from "./components/ProjectList";
import { ProjectView } from "./components/ProjectView";
import { SafeAreaTopScrim } from "@hatch/space-sdk/client";
import { useState } from "react";

export function App() {
  const [openId, setOpenId] = useState<string | null>(null);
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <SafeAreaTopScrim />
      {openId ? (
        <ProjectView projectId={openId} onBack={() => setOpenId(null)} />
      ) : (
        <ProjectList onOpen={(id) => setOpenId(id)} />
      )}
    </div>
  );
}
