// Test cho prompt generateScriptAI (giai đoạn 3 đợt riêng, 03/11 — mục
// "test prompt" còn thiếu của đợt 4 giai đoạn). Chạy: `bun test` trong
// thư mục gốc của artifact (hoặc `bun test server/src/script-prompt.test.ts`).
// Mỗi assert gắn với một luật kịch bản hiện hành; prompt lệch luật là
// test đỏ, không phải "chấp nhận được".

import { describe, expect, test } from "bun:test";
import { buildScriptPrompt } from "./script-prompt";

const FACTS =
  "Ngày 3/11, cầu X tại Hà Nội thông xe sau 14 tháng thi công; tổng vốn 120 tỷ đồng; theo chủ đầu tư, dự kiến giảm 30% ùn tắc giờ cao điểm.";
const base = buildScriptPrompt({
  topic: "Thông xe cầu X tại Hà Nội",
  verifiedFacts: FACTS,
  angle: "",
  targetSeconds: 180,
});

describe("buildScriptPrompt — dữ kiện đầu vào", () => {
  test("nhúng nguyên văn chủ đề và sự kiện đã kiểm chứng", () => {
    expect(base).toContain("Chủ đề: Thông xe cầu X tại Hà Nội");
    expect(base).toContain(FACTS);
    expect(base).toContain("tuyệt đối không bịa thêm số liệu");
  });

  test("có góc làm thì ghi dòng Góc làm, không có thì bỏ hẳn dòng đó", () => {
    const withAngle = buildScriptPrompt({
      topic: "T",
      verifiedFacts: FACTS,
      angle: "Tác động tới người đi làm",
      targetSeconds: 180,
    });
    expect(withAngle).toContain("Góc làm: Tác động tới người đi làm");
    expect(base).not.toContain("Góc làm:");
  });
});

describe("buildScriptPrompt — cấu trúc 3 nhịp (luật 31/10)", () => {
  test("đủ 3 nhịp theo đúng thứ tự Đặt vấn đề → Giới thiệu sơ bộ → Đi sâu", () => {
    const i1 = base.indexOf("Nhịp 1 · ĐẶT VẤN ĐỀ");
    const i2 = base.indexOf("Nhịp 2 · GIỚI THIỆU SƠ BỘ");
    const i3 = base.indexOf("Nhịp 3 · ĐI SÂU");
    expect(i1).toBeGreaterThan(-1);
    expect(i2).toBeGreaterThan(i1);
    expect(i3).toBeGreaterThan(i2);
  });

  test("nhịp 2 chỉ tóm tắt, nhịp 3 đi sâu ĐÚNG thứ tự đã giới thiệu", () => {
    expect(base).toContain("chỉ nêu ý, chưa đi vào chi tiết");
    expect(base).toContain("ĐÚNG thứ tự đã giới thiệu ở nhịp 2");
  });

  test("có điểm móc lại quanh 50%", () => {
    expect(base).toContain("Quanh 50%: một điểm móc lại");
  });

  test("kết là diễn biến cụ thể, cấm kết luận đạo lý và câu hỏi mở", () => {
    expect(base).toContain("bằng một diễn biến/kết quả cụ thể tiếp theo");
    expect(base).toContain("CẤM kết luận đạo lý, cấm câu hỏi mở cho khán giả");
  });
});

describe("buildScriptPrompt — hình thức luận điểm và mẫu cấm", () => {
  test("tiêu đề luận điểm đánh số + IN HOA trên dòng riêng", () => {
    expect(base).toContain("ghi số thứ tự và IN HOA");
    expect(base).toContain("'1. TIÊU ĐỀ LUẬN ĐIỂM.'");
  });

  test("cấm mẫu rỗng và giới hạn 1 câu hỏi tu từ (human-script rule 29/10)", () => {
    expect(base).toContain("CẤM các mẫu rỗng");
    expect(base).toContain("mẫu 'Không chỉ... mà còn...'");
    expect(base).toContain("Tối đa 1 câu hỏi tu từ trong toàn bài");
  });

  test("khẳng định tương lai phải ghi nguồn trong câu", () => {
    expect(base).toContain("phải ghi nguồn ngay trong câu");
    expect(base).toContain("'theo chủ đầu tư'");
  });

  test("số và đơn vị giữ ký hiệu, không viết thành chữ", () => {
    expect(base).toContain("giữ nguyên ký hiệu");
    expect(base).toContain("không viết số thành chữ");
    expect(base).toContain("'10%'");
    expect(base).toContain("'35°C'");
  });

  test("chỉ trả về toàn văn kịch bản, không ghi chú/giải thích", () => {
    expect(base).toContain("Chỉ trả về toàn văn kịch bản");
  });
});

describe("buildScriptPrompt — mục tiêu thời lượng chỉ là gợi ý (luật CEO 03/11)", () => {
  test("có đoạn GỢI Ý ĐỘ DÀI ghi rõ prompt phụ, KHÔNG ràng buộc", () => {
    expect(base).toContain("GỢI Ý ĐỘ DÀI (prompt phụ, KHÔNG ràng buộc)");
    expect(base).toContain("không bơm chữ hay lặp ý chỉ để khớp số từ");
    expect(base).toContain("không cắt bớt ý quan trọng");
  });

  test("không còn dung sai phần trăm kiểu ±10% ở bất cứ đâu", () => {
    expect(base).not.toContain("±");
    expect(base).not.toContain("dung sai");
  });

  test("số từ dự tính = giây mục tiêu × 4,16 (làm tròn)", () => {
    // 180 × 4,16 = 748,8 → 749 từ; 240 × 4,16 = 998,4 → 998 từ.
    expect(base).toContain("khoảng 180 giây, tức khoảng 749 từ");
    const p240 = buildScriptPrompt({
      topic: "T",
      verifiedFacts: FACTS,
      angle: "",
      targetSeconds: 240,
    });
    expect(p240).toContain("khoảng 240 giây, tức khoảng 998 từ");
  });
});
