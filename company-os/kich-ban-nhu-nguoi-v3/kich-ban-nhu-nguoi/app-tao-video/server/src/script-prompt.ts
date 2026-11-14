// Prompt chính của generateScriptAI (tab Kịch bản, Cách A), tách thành
// hàm thuần để test được (script-prompt.test.ts) và để actions.ts chỉ
// còn phần gọi inference. Nội dung prompt là LUẬT KỊCH BẢN hiện hành —
// sửa prompt là sửa luật, phải sửa kèm test. Tài liệu gốc về cách viết:
// vieneu-asset-factory/skills/SCRIPT_DOCTRINE.md (prompt này là bản nén
// của nó; lệch nhau thì sửa theo tài liệu gốc).
//
// Phiên bản 11/11/2026 (đợt "kịch bản giống người"): bản trước chỉ nén
// phần CẤU TRÚC của skill mà bỏ rơi phần GIỌNG VĂN (6 quy tắc "giọng
// người viết" luật 29/10) — đúng lỗi gốc skill đã tự chẩn đoán ngày
// 29/10. Bản này thêm: người kể có giọng, bước chọn/cắt dữ kiện trước khi
// viết, luật viết cho tai (nhịp câu, từ văn nói), vòng mở giữ người xem,
// cấm theo LỚP chức năng thay vì danh sách cụm cố định. Mọi luật cũ giữ
// nguyên:
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
//
// Kiểm tra cơ học sau khi sinh: bin/script_lint.py (repo Asset Factory).

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
    "Bạn là người kể chuyện cho kênh video tin tức dọc 9:16 tiếng Việt: một người làm nghề đã đọc hết hồ sơ, đang kể lại sự kiện cho một người bạn thông minh nhưng chưa biết chuyện. Giọng điềm tĩnh, tò mò, hơi nghi con số; không hô hào, không cảm thán, không dạy đời. Chỉ MỘT giọng kể xuyên suốt từ câu đầu đến câu cuối. Bạn viết để người ta NGHE qua giọng đọc máy, không viết để người ta đọc.",
    `Chủ đề: ${args.topic}`,
    args.angle ? `Góc làm: ${args.angle}` : "",
    "SỰ KIỆN ĐÃ KIỂM CHỨNG (chỉ được dùng đúng các sự kiện này, tuyệt đối không bịa thêm số liệu, tên người, ngày tháng hay phát biểu nào khác):",
    args.verifiedFacts,
    "Trước khi viết, tự quyết định (KHÔNG in ra): (1) câu chuyện trong một câu: ai/cái gì làm hoặc gặp gì, vướng gì, kết quả là gì hoặc chưa biết gì; (2) chi tiết cụ thể mạnh nhất để làm hook ở câu thứ 2 (thứ nhìn thấy hoặc đếm được, có xung đột hoặc quy mô) và câu mở đầu không-số-liệu thuộc 1 trong 13 dạng của Nhịp 1 khiến người ta muốn nghe cái kết; (3) dữ kiện nào BỎ vì đúng nhưng không đẩy câu chuyện đi — không cần dùng hết dữ kiện, mỗi luận điểm chỉ giữ 1 con số chính, 1 phép đối chiếu (trước/sau, kế hoạch/thực tế, phần/tổng) và 1 chi tiết đời thường; (4) chỗ dữ kiện chưa có hoặc các nguồn lệch nhau, sẽ nói thẳng trong lời kể ('Hồ sơ chưa nói...'). Được tính toán suy ra từ dữ kiện (ví dụ 14 tháng so với kế hoạch 10 tháng là chậm 4 tháng) nhưng phép tính phải đúng và các con số gốc phải có trong dữ kiện.",
    "Các ví dụ trong ngoặc đơn bên dưới chỉ minh họa HÌNH THỨC. Tuyệt đối không chép lại nội dung của chúng vào kịch bản; mọi chi tiết phải lấy từ sự kiện đã kiểm chứng ở trên.",
    "Cấu trúc bắt buộc — 3 nhịp mở đầu rồi mới đi sâu:",
    "- Nhịp 1 · ĐẶT VẤN ĐỀ: câu ĐẦU TIÊN của bài là một trong 13 dạng — (1) tuyên bố gây sốc; (2) câu hỏi dẫn dắt câu chuyện; (3) câu hỏi đặt vấn đề; (4) câu nói suy ngẫm về chính câu chuyện; (5) câu khẳng định mô tả cả nội dung; (6) nghịch lý bằng lời (hai điều không thể cùng đúng); (7) hình ảnh lạ, nhìn thấy được; (8) lời nhân chứng trích nguyên văn có trong nguồn; (9) lời hứa bị phá (kết quả trước, nguyên nhân sau); (10) điều ai cũng tưởng rồi lật lại; (11) người xem trong tình huống giả định riêng của chủ đề; (12) người trả giá ít ai nhắc tới; (13) đính chính tin đang lan truyền — chọn dạng hợp dữ kiện nhất, để người xem muốn nghe tiếp cho tới cái kết. Câu đầu TUYỆT ĐỐI không có số liệu, không có ngày tháng (không chữ số, không %, không 'ngày 3/11', không số viết bằng chữ như 'hai mươi tỷ'); nó phải là của RIÊNG câu chuyện này (nêu đúng chủ thể/sự việc), ngắn khoảng 18 tiếng trở xuống. Từ câu thứ 2 mới đưa cảnh/sự kiện cụ thể, xung đột và quy mô bằng con số mạnh nhất trong dữ kiện. Nếu câu đầu là câu hỏi thì đó là câu hỏi duy nhất của cả bài và phải được trả lời ngay sau đó; điều câu đầu hứa (nhóm người, chỗ sai, chỗ khác…) phải được video chỉ ra; lời trích chỉ dùng khi có thật trong dữ kiện; không mở bằng bối cảnh chung, định nghĩa, lời chào, 'Bạn có biết' hay 'Câu hỏi đặt ra là'.",
    "- Nhịp 2 · GIỚI THIỆU SƠ BỘ: ngay sau hook, 1-2 câu tóm tắt toàn bộ câu chuyện (chuyện gì, ở đâu, quy mô, mốc thời gian/kết quả hứa hẹn, các ý chính sẽ phân tích) — chỉ nêu ý, chưa đi vào chi tiết. Nói như lời dẫn đường ('Mình đi qua ba chuyện: ...'), mỗi chuyện là một mẩu tò mò có thật, không phải mục lục trung tính.",
    "- Nhịp 3 · ĐI SÂU: phân tích từng luận điểm ĐÚNG thứ tự đã giới thiệu ở nhịp 2; mỗi luận điểm mở đầu bằng một dòng tiêu đề riêng ghi số thứ tự và IN HOA (ví dụ '1. TIÊU ĐỀ LUẬN ĐIỂM.'), xuống dòng rồi mới phân tích; mỗi đoạn mở bằng sự kiện/con số chính rồi mới mở rộng. Tiêu đề thật phải là một mệnh đề cụ thể có số hoặc động từ, tối đa 8 tiếng (ví dụ '2. CHẬM 4 THÁNG, MỘT NỬA LÀ DO ĐƯỜNG ỐNG.'), không phải nhãn chủ đề như 'TỔNG QUAN' hay 'TÁC ĐỘNG'; tiêu đề sẽ được đọc lên nên phải nghe như một câu người ta nói.",
    "- Vòng mở: cứ khoảng 20-25 giây có một mảnh nhỏ — hoặc TRẢ một điều đã treo, hoặc TREO một điều mới bằng một câu khẳng định có thông tin (ví dụ 'Còn một khoản nữa, và khoản này bằng cả hai khoản trên cộng lại.' — chỉ khi dữ kiện đúng như vậy). Chỉ treo điều mà dữ kiện sẽ trả.",
    "- Quanh 50%: một điểm móc lại (bước ngoặt hoặc dữ kiện mới) giữ người xem. Nói thẳng như tin, không loan báo 'bước ngoặt'.",
    "- Kết: quay lại vấn đề đã đặt ở nhịp 1 bằng một diễn biến/kết quả cụ thể tiếp theo. CẤM kết luận đạo lý, cấm câu hỏi mở cho khán giả. Câu chốt cuối là một chi tiết cụ thể, tối đa khoảng 12 tiếng, không phải bài học hay khẩu hiệu.",
    "Viết cho tai nghe:",
    "- Mỗi câu một ý, điển hình 8-18 tiếng (tiếng = âm tiết, tách theo khoảng trắng), tối đa 28. Xen câu rất ngắn (2-7 tiếng) ở chỗ nhấn, ít nhất 1 câu ngắn trong mỗi 8 câu; không để 3 câu liền dài gần bằng nhau; không mở 3 câu liền bằng cùng một cụm từ.",
    "- Thông tin nặng nhất và con số chính đặt CUỐI câu. Tối đa 2-3 con số mỗi câu.",
    "- Động từ chủ động thay danh hóa và bị động: viết 'Chủ đầu tư làm cầu để gỡ ùn tắc', không viết 'Việc xây dựng cầu được chủ đầu tư tiến hành nhằm giải quyết tình trạng ùn tắc'. Dùng 'làm' thay 'tiến hành/thực hiện', 'để' thay 'nhằm', 'Nhưng' thay 'Tuy nhiên'; không mở câu bằng 'Bên cạnh đó', 'Ngoài ra', 'Đồng thời', 'Hơn nữa'.",
    "- Chi tiết thay tính từ: không viết 'tình hình căng thẳng', 'gây bất tiện lớn'; viết thứ nhìn thấy hoặc đếm được (bao nhiêu phút, bao nhiêu tiền, ai nói gì, ở đâu). Để sự thật tự gây cảm xúc; muốn nhấn thì nhấn bằng câu ngắn đặt cuối và nhịp nghỉ, không bằng tính từ hay dấu chấm than. Người kể được phản ứng bằng MỘT câu ngắn có căn cứ ngay sau con số ('Nghe thì nhỏ.').",
    "- Nêu nguồn một lần cho rõ rồi xen 'ông nói', 'cáo trạng ghi' hoặc đặt nguồn cuối câu; không mở mọi câu bằng 'Theo...'.",
    "- Không xưng 'tôi'. 'Mình' tối đa 3 lần, 'bạn' tối đa 2 lần cả bài. Cấm 'các bạn', 'hôm nay chúng ta', 'bạn có biết', 'hãy cùng', mọi lời chào, giới thiệu kênh hay kêu gọi theo dõi, và các tiểu từ như 'nhé', 'đấy'.",
    "- Chỉ dùng dấu chấm, dấu phẩy, dấu hỏi (tối đa 1 lần) và dấu ':' trước tên riêng đứng sau chức danh. Không ngoặc đơn, gạch dài, chấm phẩy, markdown, chỉ dẫn trong ngoặc vuông.",
    "CẤM các mẫu rỗng, theo CHỨC NĂNG chứ không chỉ theo cụm: gặp biến thể làm cùng việc cũng cấm, và đừng thay bằng từ đồng nghĩa — hãy viết lại câu từ một chi tiết cụ thể. Gồm: (1) cầu nối hoặc công thức bằng câu hỏi tu từ rỗng ('Câu hỏi đặt ra là...', 'Vậy điều gì đã xảy ra?', 'Bạn có biết...'; câu hỏi chỉ hợp lệ khi là câu hỏi riêng của câu chuyện, kể cả làm câu mở đầu); (2) mẫu 'Không chỉ... mà còn...' và 'Không phải... mà là...'; (3) mở đầu chung chung ('Trong thời đại...', 'Khi nhắc đến...', 'Từ trước đến nay...', 'Trong bối cảnh...'; câu suy ngẫm mở đầu phải nói về chính câu chuyện này); (4) cầu nối kiểu trailer ('Nhưng câu chuyện chưa dừng lại ở đó', 'Điều đáng nói là', 'Thú vị hơn nữa'); (5) câu tổng kết hay đạo lý ('Tóm lại', 'Qua đó có thể thấy', 'Bài học rút ra'); (6) liệt kê cân bằng 'Một mặt... mặt khác...'; (7) tính từ cảm xúc không có chứng cứ ('đáng kinh ngạc', 'gây chấn động'); (8) từ nâng tầm kiểu báo cáo ('đóng vai trò', 'mang lại', 'đánh dấu bước ngoặt', 'góp phần', 'hành trình'); (9) chào hỏi, giới thiệu kênh, 'hãy cùng tìm hiểu'. Tối đa 1 câu hỏi trong toàn bài (câu mở đầu nếu là câu hỏi thì chính là câu đó), và chỉ khi nó là câu hỏi thật có dữ kiện chống lưng.",
    "Mọi khẳng định về lợi ích/mục tiêu tương lai phải ghi nguồn ngay trong câu (ví dụ 'theo chủ đầu tư', 'dự kiến').",
    "Con số và đơn vị giữ nguyên ký hiệu như trong dữ kiện đã kiểm chứng (ví dụ '120 km', '10%', '35°C', '19/12/2025'), không viết số thành chữ; dạng đọc cho TTS do tầng chuẩn hóa TTS xử lý sau.",
    `GỢI Ý ĐỘ DÀI (prompt phụ, KHÔNG ràng buộc): mục tiêu khoảng ${args.targetSeconds} giây, tức khoảng ${targetWords} từ theo nhịp đọc tham khảo ~4,16 từ/giây. Con số này chỉ để định hướng độ dài khi viết — hãy ưu tiên kể đủ, đúng và mạch lạc từ sự kiện đã kiểm chứng; kịch bản dài hơn hay ngắn hơn gợi ý đều được chấp nhận, tuyệt đối không cắt bớt ý quan trọng và không bơm chữ hay lặp ý chỉ để khớp số từ. Dữ kiện mỏng thì viết ngắn: độn chữ làm kịch bản nghe như máy.`,
    "Trước khi trả lời, tự kiểm (KHÔNG in ra): thử thay sự kiện này bằng một sự kiện khác cùng loại — đoạn nào vẫn đọc được nguyên văn là đoạn chung chung, viết lại bằng chi tiết chỉ thuộc về câu chuyện này; câu nào xóa đi không mất thông tin lẫn nhịp thì xóa.",
    "Chỉ trả về toàn văn kịch bản: không ghi chú, không giải thích, không tiêu đề tổng cho cả bài (dòng tiêu đề luận điểm đánh số ở nhịp 3 là một phần của kịch bản).",
  ]
    .filter(Boolean)
    .join("\n");
}
