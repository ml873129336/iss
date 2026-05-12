<template>
  <div class="p-4">
    <!-- 搜索栏 -->
    <el-input
      v-model="search"
      placeholder="搜索用户名或部门"
      class="mb-4 w-60"
      clearable
      @clear="fetchUsers"
      @keyup.enter="fetchUsers"
    />


    <div class="button-row">
      <el-button type="primary" @click="{clearFormData(); openForm(null)}">新增用户</el-button>
      <el-upload
        :show-file-list="false"
        :http-request="uploadExcel"
        accept=".xls,.xlsx .csv"
      >
        <el-button type="success">导入 Excel</el-button>
      </el-upload>
    </div>
    

    <!-- 用户表格 -->
    <el-table :data="filteredUsers" stripe class="mt-4" style="width: 100%">
      <el-table-column prop="name" label="Name" width="100" />
      <el-table-column prop="employee_id" label="ID" width="100" />
      <el-table-column label="Department" width="200" >
        <template #default="{ row }">
          {{ getDepartmentName(row.department) }}
        </template>
      </el-table-column>
      <el-table-column prop="mail" label="Mail" width="160" />
      <el-table-column prop="city" label="City" width="100" />
      <el-table-column prop="position" label="Title" width="160" />
      <el-table-column prop="reporting_line" label="Manager" width="100" />
      <el-table-column label="操作" width="300">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openForm(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteUser(row.id)">删除</el-button>
          <el-button type="success" size="small" @click="sendOnboardingEmail(row)">发送邮件</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 用户表单弹窗 -->
    <el-dialog v-model="showForm" title="用户信息" width="500px" @close="clearFormData">
      <UserForm ref="userformRef" :formData="editData" @saved="fetchUsers" @cancel="showForm = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted,nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import UserForm from './UserForm.vue'
import axios from 'axios'

const users = ref([])
const departments = ref([])
const search = ref('')
const showForm = ref(false)
const editData = ref(null)
const userformRef = ref(null)

onMounted(async () => {
  await fetchDepartments()
  await fetchUsers()
})

const fetchUsers = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/assert_manager/employees/')
    users.value = res.data
  } catch (err) {
    console.error("获取员工失败", err)
  }
  
}

const fetchDepartments = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/assert_manager/departments/')
    departments.value = res.data
  } catch (err) {
    console.error('获取部门失败', err)
  }
}

const deleteUser = async (id) => {
  ElMessageBox.confirm('确认删除该用户吗？', '警告', { type: 'warning' })
    .then(async () => {
      await axios.delete(`http://127.0.0.1:8000/api/assert_manager/employees/${id}/`)
      ElMessage.success('删除成功')
      fetchUsers()
    })
    .catch(() => {})
}

const sendmail = async() =>{


}



const openForm = (user) => {
  editData.value = user ? { ...user } : null
  showForm.value = true
}

const filteredUsers = computed(() =>
  users.value.filter(u =>
    u.name.includes(search.value) || (u.department_name || '').includes(search.value)
  )
)
const getDepartmentName = (deptId) => {
  const dept = departments.value.find(d => d.id === deptId)
  return dept ? dept.name : ''
}

const clearFormData = async () => {
  editData.value = null
  await nextTick() // 确保子组件已更新
  userformRef.value?.resetFields()

  
}

const sendOnboardingEmail = async (user) => {
  try {
    await axios.post(`http://127.0.0.1:8000/api/assert_manager/employees/${user.id}/send_onboarding_email/`);
    ElMessage.success(`入职邮件已发送给 ${user.name}`);
  } catch (err) {
    console.error("发送邮件失败", err);
    ElMessage.error(`发送邮件失败：${err.response?.data?.detail || err.message}`);
  }
}

const uploadExcel = async (option) => {
  const formData = new FormData()
  formData.append('file', option.file)

  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/api/assert_manager/employees/import_excel/',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    ElMessage.success('Excel 导入成功')
    fetchUsers() // 刷新表格
  } catch (err) {
    console.error('导入失败', err)
    ElMessage.error('导入失败：' + (err.response?.data?.detail || err.message))
  }
}

</script>


<style scoped>
  .button-row {
    display: flex;      /* 水平排列 */
    gap: 10px;          /* 间距 */
    margin-bottom: 16px;/* 底部空隙 */
    align-items: center;/* 垂直居中 */
  }
</style>