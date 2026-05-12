import axios from "axios";

const request = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 100000,
});


// =========================
// 科力普（保持 GET 下载）
// =========================
export function downloadColipu(amount) {
  return request({
    url: "/it_payment_colipu/",
    method: "get",
    params: amount ? { amount } : {},
    responseType: "blob",
  });
}


// =========================
// 电信 - 下载 Excel
// =========================
export function downloadDianxin(amount) {
  return request({
    url: "/payment_download/",
    method: "post",
    data: { company },
    responseType: "blob", // ✅ 下载必须 blob
  });
}


// =========================
// 电信 - 预览图片
// =========================
export function previewDianxin(amount) {
  return request({
    url: "/payment_preview/",
    method: "post",
    data: { company, amount },
  });
}


// =========================
// 电信 - 发邮件
// =========================
export function sendDianxinEmail(amount, email) {
  return request({
    url: "/payment_send_email/",
    method: "post",
    data: {
      email,
       company,
    }
      
});
}