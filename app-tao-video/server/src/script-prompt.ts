// Prompt chính của generateScriptAI (tab Kịch bản, Cách A), tách thành
// hàm thuần để test được (script-prompt.test.ts) và để actions.ts chỉ
// còn phần gọi inference. Nội dung prompt là LUẬT KỊCH BẢN hiện hành —
// sửa prompt là sửa luật, phải sửa kèm test:
//
// - Cấu trúc 3 nhịp mở đầu (luật COO 31/10): ĐẶT VẤN ĐỀ → GIỚI THIỆU SƠ
//   BỘ (1 cảnh tóm tắt toàn bộ, đúng thứ tự sẽ đi sâu) → ĐI SÂU đúng thứ
//   tự đã giới thiệu; kết quay lại vấn đề mở đầu bằng diễn biến cụ thể,
//   CẤM kết luận đạo lý và câu hỏi mở.
// - Tiêu đề luận điểm: dòng riêng, đánh số + IN HOA (luật 30/10 — cấm
//   dạng #1/#2/#3 trong kịch bản).
// - Cấm mẫu rỗng của human-script rule 29/10: hook tu từ sáo rỗng,
//   "Không chỉ... mà còn...", mở đầu chung chung kiểu trailer, tính từ
//   cảm xúc không chứng cứ; tối đa 1 câu hỏi tu từ có dữ kiện chống lưng.
// - Khẳng định tương lai phải ghi nguồn ngay trong câu.
// - Số/đơn vị giữ ký hiệu (%, °C, km...), không viết thành chữ — tầng
//   chuẩn hóa TTS xử lý dạng đọc sau.
// - "Mục tiêu thời lượng" CHỈ là prompt phụ gợi ý (luật CEO 03/11): hệ
//   số ~4,16 từ/giây đổi giây mục tiêu thành số từ dự tính để định
//   hướng độ dài; KHÔNG dung sai phần trăm, không cắt/bơm chữ cho khớp,
//   không kiểm tra đạt/không đạt ở bất kỳ khâu nào.

export interface ScriptPromptArgs {
  topic: string;
  verifiedFacts: string;
  angle: string;
  targetSeconds: number;
}

export function buildScriptPrompt(args: ScriptPromptArgs): string {
  // Số từ dự tính từ giây mục tiêu — chỉ để AI định hướng độ dài.
  const targetWords = Math.round(args.targetSeconds * 4.16);
  return [
    "Bạn là biên kịch video tin tức dọc 9:16 tiếng Việt cho kênh phân tích sự kiện.",
    `Chủ đề: ${args.topic}`,
    args.angle ? `Góc làm: ${args.angle}` : "",
    "SỰ KIỆN ĐÃ KIỂM CHỨNG (chỉ được dùng đúng các sự kiện này, tuyệt đối không bịa thêm số liệu, tên người, ngày tháng hay phát biểu nào khác):",
    args.verifiedFacts,
    "Cấu trúc bắt buộc — 3 nhịp mở đầu rồi mới đi sâu:",
    "- Nhịp 1 · ĐẶT VẤN ĐỀ: mở bằng một cảnh/sự kiện cụ thể kèm xung đột và quy mô bằng con số mạnh nhất trong dữ kiện (hook 0-3 giây đầu).",
    "- Nhịp 2 · GIỚI THIỆU SƠ BỘ: ngay sau hook, 1-2 câu tóm tắt toàn bộ câu chuyện (chuyện gì, ở đâu, quy mô, mốc thời gian/kết quả hứa hẹn, các ý chính sẽ phân tích) — chỉ nêu ý, chưa đi vào chi tiết.",
    "- Nhịp 3 · ĐI SÂU: phân tích từng luận điểm ĐÚNG thứ tự đã giới thiệu ở nhịp 2; mỗi luận điểm mở đầu bằng một dòng tiêu đề riêng ghi số thứ tự và IN HOA (ví dụ '1. TIÊU ĐỀ LUẬN ĐIỂM.'), xuống dòng rồi mới phân tích; mỗi đoạn mở bằng sự kiện/con số chính rồi mới mở rộng.",
    "- Quanh 50%: một điểm móc lại (bước ngoặt hoặc dữ kiện mới) giữ người xem.",
    "- Kết: quay lại vấn đề đã đặt ở nhịp 1 bằng một diễn biến/kết quả cụ thể tiếp theo. CẤM kết luận đạo lý, cấm câu hỏi mở cho khán giả.",
    "CẤM các mẫu rỗng: hook tu từ sáo rỗng, mẫu 'Không chỉ... mà còn...', mở đầu chung chung kiểu trailer, tính từ cảm xúc không có chứng cứ. Tối đa 1 câu hỏi tu từ trong toàn bài, và chỉ khi nó là câu hỏi thật có dữ kiện chống lưng.",
    "Mọi khẳng định về lợi ích/mục tiêu tương lai phải ghi nguồn ngay trong câu (ví dụ 'theo chủ đầu tư', 'dự kiến').",
    "Con số và đơn vị giữ nguyên ký hiệu như trong dữ kiện đã kiểm chứng (ví dụ '120 km', '10%', '35°C', '19/12/2025'), không viết số thành chữ; dạng đọc cho TTS do tầng chuẩn hóa TTS xử lý sau.",
    `GỢI Ý ĐỘ DÀI (prompt phụ, KHÔNG ràng buộc): mục tiêu khoảng ${args.targetSeconds} giây, tức khoảng ${targetWords} từ theo nhịp đọc tham khảo ~4,16 từ/giây. Con số này chỉ để định hướng độ dài khi viết — hãy ưu tiên kể đủ, đúng và mạch lạc từ sự kiện đã kiểm chứng; kịch bản dài hơn hay ngắn hơn gợi ý đều được chấp nhận, tuyệt đối không cắt bớt ý quan trọng và không bơm chữ hay lặp ý chỉ để khớp số từ.`,
    "Chỉ trả về toàn văn kịch bản: không ghi chú, không giải thích, không tiêu đề tổng cho cả bài (dòng tiêu đề luận điểm đánh số ở nhịp 3 là một phần của kịch bản).",
  ]
    .filter(Boolean)
    .join("\n");
}
