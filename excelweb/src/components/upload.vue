<template>
  <div>
    <input type="file" ref="fileInput" @change="onFileChange" accept=".xls,.xlsx" />
    <el-button type="primary" @click="uploadFile">上传 Excel</el-button>
    <el-button type="primary" @click="send_email">发送邮件</el-button>

    <el-select v-model="selectedDept" placeholder="选择部门" clearable style="width: 200px;" @change="filterData">
      <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
    </el-select> 

    <el-table v-if="tableData.length" :data="tableData" style="margin-top: 20px; width: 100%" stripe border>
      <el-table-column 
        v-for="(value, key) in tableData[0]"
        
        :key="key"
        :prop="key"
        :label="key"
        :width="key === '总结' ? 300 : 150"
        >
      <template #default="scope">
          <span v-html="highlightText(scope.row[key])"></span>
        </template>
      
      
      </el-table-column>

    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const fileInput = ref(null)
const selectedFile = ref(null)
const tableData = ref([])
const keyword = "缺卡"

const highlightText = (str) => {
  const reg = new RegExp(keyword, "g")
  return str.replace(reg, `<span style="color: red;">${keyword}</span>`)
}

const filterData = async () => {
  let url = "/api/attendance/";
  if (selectedDept.value) {
    url += `?dept=${encodeURIComponent(selectedDept.value)}`;
  }
  const res = await axios.get(url);
  tableData.value = res.data;
};


const onFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const send_email =async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/send_files/")
    ElMessage.success(res.data.msg)
  } catch (err) {
    ElMessage.error("发送失败: " + (err.response?.data?.error || err.message))
  }
}

const uploadFile = () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择一个 Excel 文件')
    return
  }

  // 校验文件类型
  const fileType = selectedFile.value.type
  if (
    fileType !== "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" &&
    fileType !== "application/vnd.ms-excel"
  ) {
    ElMessage.error('只能上传 Excel 文件')
    return
  }

  // 构造 FormData
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  // 发送 POST 请求
  axios.post('http://127.0.0.1:8000/api/upload-excel/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
    .then(res => {
      if (res.data.data) {
        tableData.value = res.data.data
        ElMessage.success('上传成功')
      } else {
        ElMessage.error(res.data.message || '上传失败')
      }
    })
    .catch(err => {
      ElMessage.error('上传出错')
      console.error(err)
    })
}
</script>