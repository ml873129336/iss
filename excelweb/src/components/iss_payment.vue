<template>
  <div class="container">
    <h1>付款单生成系统</h1>

    <!-- 科力普 -->
    <div class="card">
      <div class="title">科力普付款单</div>

      <div class="form-item">
        <label>金额：</label>
        <input v-model="colipuAmount" placeholder="不填自动读取邮件" />
      </div>

      <button @click="handleColipu" :disabled="loading">
        {{ loading ? "生成中..." : "下载 Excel" }}
      </button>
    </div>

    <!-- 电信 -->
    <div class="card">
      <div class="title">电信付款单</div>

      <div class="form-item">
        <label>金额：</label>
        <input v-model="dianxinAmount" placeholder="请输入金额" />
      </div>

      <button @click="preview" :disabled="loading">
        {{ loading ? "生成中..." : "生成预览" }}
      </button>

      <div v-if="previewImg">
        <h3>预览</h3>

        <img
          :src="'data:image/png;base64,' + previewImg"
          style="width: 500px; border: 1px solid #ccc"
        />

        <br /><br />

        <button @click="download">确认下载</button>
        <button @click="sendEmail" style="margin-left: 10px;">
          发送邮件
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import {
  downloadColipu,
  downloadDianxin,
  previewDianxin,
  sendDianxinEmail,
} from "@/api/payment";

// ======================
// 状态
// ======================
const colipuAmount = ref("");
const dianxinAmount = ref("");
const loading = ref(false);
const previewImg = ref("");


// ======================
// 通用下载
// ======================
const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
};


// ======================
// 科力普下载
// ======================
const handleColipu = async () => {
  if (!colipuAmount.value) {
    alert("金额可不填（自动读取邮件）");
  }

  try {
    loading.value = true;

    const res = await downloadColipu(colipuAmount.value);
    downloadFile(res.data, "colipu.xlsx");

  } catch (e) {
    alert("科力普下载失败：" + (e.response?.data?.msg || e));
  } finally {
    loading.value = false;
  }
};


// ======================
// 电信 - 预览
// ======================
const preview = async () => {
  if (!dianxinAmount.value) {
    alert("请输入金额");
    return;
  }

  try {
    loading.value = true;

    const res = await previewDianxin(dianxinAmount.value,"dianxin");
    previewImg.value = res.data.preview;

  } catch (e) {
    alert("预览失败：" + (e.response?.data?.msg || e));
  } finally {
    loading.value = false;
  }
};


// ======================
// 电信 - 下载
// ======================
const download = async () => {
  try {
    loading.value = true;

    const res = await downloadDianxin(dianxinAmount.value);
    downloadFile(res.data, "dianxin.xlsx");

  } catch (e) {
    alert("下载失败：" + (e.response?.data?.msg || e));
  } finally {
    loading.value = false;
  }
};


// ======================
// 电信 - 发邮件
// ======================
const sendEmail = async () => {
  if (!dianxinAmount.value) {
    alert("请输入金额");
    return;
  }

  const email = "peter.mo@iss-gf.com";
  if (!email) return;

  try {
    loading.value = true;

    await sendDianxinEmail(dianxinAmount.value, email);
    alert("邮件已发送");

  } catch (e) {
    alert("发送失败：" + (e.response?.data?.msg || e));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  padding: 40px;
  max-width: 600px;
}

h1 {
  margin-bottom: 30px;
}

.card {
  border: 1px solid #ddd;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
}

.form-item {
  margin-bottom: 10px;
}

input {
  width: 100%;
  padding: 6px;
  margin-top: 5px;
}

button {
  padding: 8px 16px;
  cursor: pointer;
}
</style>