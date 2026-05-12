<template>
    <div style="max-width: 500px; margin: auto;">
      <h2>提交邮件内容</h2>
  
      <textarea
        v-model="emailBody"
        placeholder="在这里粘贴邮件内容..."
        rows="8"
        style="width: 100%;"
      ></textarea>
  
      <br />
  
      <button :disabled="loading" @click="submitEmail">
        {{ loading ? "提交中..." : "提交" }}
      </button>
      <button :disabled="loading" @click="getEmail">
        {{ loading ? "提交中..." : "获取邮件" }}
      </button>
      <div v-if="error" style="color: red; margin-top: 10px;">
        {{ error }}
      </div>
  
      <div v-if="result" style="margin-top: 20px;">
        <h3>解析结果：</h3>
        <pre>{{ result }}</pre>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import axios from "axios";
  
  // 响应式数据
  const emailBody = ref("");
  const result = ref(null);
  const loading = ref(false);
  const error = ref(null);
  
  // 提交方法
  const submitEmail = async () => {
    if (!emailBody.value.trim()) {
      error.value = "请输入邮件内容";
      return;
    }
  
    error.value = null;
    result.value = null;
    loading.value = true;
  
    try {
      const res = await axios.post(
        "http://127.0.0.1/api/parse_email/",
        { email_body: emailBody.value }
      );
      result.value = res.data;
    } catch (err) {
      console.error(err);
      error.value = "提交失败，请检查后端服务";
    } finally {
      loading.value = false;
    }
  };
  
  const getEmail = async () => {
    error.value = null;
    result.value = null;
    loading.value = true;
  
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/parse_email/")
      
    } catch (err) {
      console.error(err);
      error.value = "提交失败，请检查后端服务";
    } finally {
      loading.value = false;
    }
  };
  </script>