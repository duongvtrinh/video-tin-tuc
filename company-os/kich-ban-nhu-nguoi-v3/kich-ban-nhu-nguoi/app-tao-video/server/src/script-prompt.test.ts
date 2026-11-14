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
    expect(base).toContain("Tối đa 1 câu hỏi trong toàn bài");
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

describe("buildScriptPrompt — giọng người viết (đợt 11/11, SCRIPT_DOCTRINE.md)", () => {
  test("có người kể một giọng, viết cho tai nghe", () => {
    expect(base).toContain("người kể chuyện");
    expect(base).toContain("MỘT giọng kể xuyên suốt");
    expect(base).toContain("để người ta NGHE");
  });

  test("buộc chọn và cắt dữ kiện trước khi viết, cho phép tính suy ra từ dữ kiện", () => {
    expect(base).toContain("dữ kiện nào BỎ");
    expect(base).toContain("không cần dùng hết dữ kiện");
    expect(base).toContain("phép tính phải đúng");
    expect(base).toContain("sẽ nói thẳng trong lời kể");
  });

  test("câu mở đầu (CEO 12/11/2026): 13 dạng, tuyệt đối không số liệu/ngày tháng", () => {
    expect(base).toContain("câu ĐẦU TIÊN của bài là một trong 13 dạng");
    for (const k of ["tuyên bố gây sốc", "câu hỏi dẫn dắt câu chuyện", "câu hỏi đặt vấn đề", "câu nói suy ngẫm", "câu khẳng định mô tả cả nội dung", "nghịch lý bằng lời", "hình ảnh lạ", "lời nhân chứng trích nguyên văn", "lời hứa bị phá", "điều ai cũng tưởng", "người xem trong tình huống", "người trả giá", "đính chính tin đang lan truyền"]) {
      expect(base).toContain(k);
    }
    expect(base).toContain("TUYỆT ĐỐI không có số liệu, không có ngày tháng");
    expect(base).toContain("Từ câu thứ 2 mới đưa cảnh/sự kiện cụ thể");
    // luật cũ đòi câu đầu có con số/tên riêng đã bị gỡ
    expect(base).not.toContain("có con số hoặc tên riêng cụ thể");
    expect(base).not.toContain("kèm xung đột và quy mô bằng con số mạnh nhất trong dữ kiện (hook 0-3 giây đầu). Câu đầu");
  });

  test("tiêu đề luận điểm là mệnh đề cụ thể", () => {
    expect(base).toContain("mệnh đề cụ thể có số hoặc động từ");
    expect(base).toContain("không phải nhãn chủ đề");
  });

  test("vòng mở: treo bằng câu khẳng định có thông tin, chỉ treo điều sẽ trả", () => {
    expect(base).toContain("Vòng mở");
    expect(base).toContain("câu khẳng định có thông tin");
    expect(base).toContain("Chỉ treo điều mà dữ kiện sẽ trả");
  });

  test("luật viết cho tai: nhịp câu, số cuối câu, động từ chủ động, chi tiết thay tính từ", () => {
    expect(base).toContain("tối đa 28");
    expect(base).toContain("Xen câu rất ngắn");
    expect(base).toContain("đặt CUỐI câu");
    expect(base).toContain("Tối đa 2-3 con số mỗi câu");
    expect(base).toContain("Động từ chủ động");
    expect(base).toContain("Chi tiết thay tính từ");
    expect(base).toContain("Để sự thật tự gây cảm xúc");
  });

  test("xưng hô và dấu câu an toàn cho TTS", () => {
    expect(base).toContain("Không xưng 'tôi'");
    expect(base).toContain("hôm nay chúng ta");
    expect(base).toContain("Không ngoặc đơn, gạch dài, chấm phẩy, markdown");
  });

  test("cấm theo CHỨC NĂNG, đủ 9 lớp, cấm thay bằng từ đồng nghĩa", () => {
    expect(base).toContain("theo CHỨC NĂNG chứ không chỉ theo cụm");
    expect(base).toContain("đừng thay bằng từ đồng nghĩa");
    for (const n of ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)"]) {
      expect(base).toContain(n);
    }
    expect(base).toContain("'Nhưng câu chuyện chưa dừng lại ở đó'");
    expect(base).toContain("'Qua đó có thể thấy'");
    expect(base).toContain("'đóng vai trò'");
  });

  test("ví dụ chỉ minh họa hình thức, không chép nội dung", () => {
    expect(base).toContain("chỉ minh họa HÌNH THỨC");
    expect(base).toContain("Tuyệt đối không chép lại nội dung");
  });

  test("tự kiểm: thử thay sự kiện, xóa câu thừa; dữ kiện mỏng thì viết ngắn", () => {
    expect(base).toContain("thử thay sự kiện này bằng một sự kiện khác");
    expect(base).toContain("Dữ kiện mỏng thì viết ngắn");
  });

  test("giữ nguyên thứ tự các khối: dữ kiện → cấu trúc → viết cho tai → mẫu cấm → độ dài", () => {
    const order = [
      base.indexOf("SỰ KIỆN ĐÃ KIỂM CHỨNG"),
      base.indexOf("Cấu trúc bắt buộc"),
      base.indexOf("Viết cho tai nghe:"),
      base.indexOf("CẤM các mẫu rỗng"),
      base.indexOf("GỢI Ý ĐỘ DÀI"),
      base.indexOf("Chỉ trả về toàn văn kịch bản"),
    ];
    for (let i = 0; i < order.length; i++) {
      expect(order[i]).toBeGreaterThan(-1);
      if (i > 0) expect(order[i]).toBeGreaterThan(order[i - 1]);
    }
  });
});
