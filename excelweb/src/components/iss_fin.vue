<template>
  <div class="upload-container">
    <el-upload
      ref="uploadRef"
      v-model:file-list="fileList"
      class="upload-demo"
      action="#"
      multiple
      :auto-upload="false"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :limit="10"
      :on-exceed="handleExceed"
    >
      <template #trigger>
        <el-button type="primary">选择文件</el-button>
      </template>

      <template #tip>
        <div class="el-upload__tip">
          支持上传多个文件
        </div>
      </template>
    </el-upload>

    <el-button 
      class="mt-4" 
      type="success" 
      @click="submitUpload"
      :disabled="fileList.length === 0"
    >
      开始上传
    </el-button>

    <el-progress 
      v-if="uploading"
      :percentage="progressPercent" 
      :status="uploadStatus"
      class="mt-4"
    />

    <el-button 
      class="mt-4" 
      type="success" 
      @click="submitUpload1"
      
    >
      开始上传2
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const fileList = ref([])
const uploading = ref(false)
const progressPercent = ref(0)
const uploadStatus = ref('')

const handleChange = (file, files) => {
  // 验证文件大小
  fileList.value = files
}

const handleRemove = (file, files) => {
  fileList.value = files
}

const handleExceed = () => {
  ElMessage.warning('最多只能上传 10 个文件')
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  progressPercent.value = 0
  uploadStatus.value = ''

  const formData = new FormData()
  fileList.value.forEach(file => {
    formData.append('files', file.raw)
  })

  try {
    // 192.168.18.22
    //127.0.0.1
    const response = await axios.post('http://127.0.0.1:8000/api/iss_fin/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob',
      onUploadProgress: progressEvent => {
        progressPercent.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
      
    })

  

    uploadStatus.value = 'success'
    ElNotification({
      title: '成功',
      message: '文件上传成功',
      type: 'success'
    })
    fileList.value = []
    downloadFile(response.data, response.headers, "处理结果.xlsx")

  } catch (error) {
    uploadStatus.value = 'exception'
    ElNotification({
      title: '错误',
      message: '文件上传失败',
      type: 'error'
    })
    console.error('上传错误:', error)
  } finally {
    uploading.value = false
  }
}

const submitUpload1 = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  progressPercent.value = 0
  uploadStatus.value = ''

  const formData = new FormData()
  fileList.value.forEach(file => {
    formData.append('files', file.raw)
  })

  try {
    // 192.168.18.22
    //127.0.0.1
    const response = await axios.post('http://127.0.0.1:8000/api/iss_fin1/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob',
      onUploadProgress: progressEvent => {
        progressPercent.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
      
    })

  

    uploadStatus.value = 'success'
    ElNotification({
      title: '成功',
      message: '文件上传成功',
      type: 'success'
    })
    fileList.value = []
    downloadFile(response.data, response.headers, "处理结果.xlsx")

  } catch (error) {
    uploadStatus.value = 'exception'
    ElNotification({
      title: '错误',
      message: '文件上传失败',
      type: 'error'
    })
    console.error('上传错误:', error)
  } finally {
    uploading.value = false
  }
}

const fetchAttachments = async () => {
  try {
    const response = await axios.get('http://192.168.18.22:8000/api/iss_fin/')

    downloadFile(response.data.body, response.headers, "处理结果.xlsx")

    }
  catch (error) {
    ElMessage.error("获取附件失败")
    console.error(error)
  }
}


const downloadFile = (data, headers, defaultFilename = "下载文件.xlsx") => {
  // 创建 Blob
  const blob = new Blob([data], { type: headers['content-type'] })

  // 解析文件名
  let filename = defaultFilename
  const disposition = headers['content-disposition']
  if (disposition) {
    const filenameRegex = /filename\*=UTF-8''([^;]+)|filename="?([^"]+)"?/i
    const matches = filenameRegex.exec(disposition)
    if (matches) {
      filename = decodeURIComponent(matches[1] || matches[2])
    }
  }

  // 生成下载链接
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // 释放内存
  setTimeout(() => window.URL.revokeObjectURL(url), 100)
}

</script>

<style scoped>
.upload-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.mt-4 {
  margin-top: 16px;
}

.upload-demo {
  width: 100%;
}
</style>