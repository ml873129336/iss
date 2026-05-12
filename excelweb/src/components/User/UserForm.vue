<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
    <el-form-item label="Name" prop="name">
      <el-input v-model="form.name" />
    </el-form-item>

    <el-form-item label="ID" prop="employee_id">
      <el-input v-model="form.employee_id"  type="number" placeholder="请输入ID"/>
    </el-form-item>


    <el-form-item label="Department" prop="department">
      <el-select v-model="form.department" placeholder="选择部门">
        <el-option
          v-for="d in departments"
          :key="d.id"
          :label="d.name"
          :value="d.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="Title" prop="position">
      <el-select v-model="form.position">
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
    </el-form-item>

    <el-form-item label="City" prop="city">
      <el-select v-model="form.city">
        <el-option label="Shanghai" value="SHA" />
        <el-option label="Ningbo" value="NGB" />
        <el-option label="Shenzhen" value="SZX" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="报道日期" prop="onboard_date">
      <el-date-picker
        v-model="form.onboard_date"
        type="date"
        placeholder="请选择日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
      />
    </el-form-item>

    <el-form-item label="Manager" prop="reporting_line">
      <el-select v-model="form.reporting_line" placeholder="主管">
        <el-option
          v-for="d in manager"
          :key="d.id"
          :label="d.name"
          :value="d.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" :disabled="!isFormValid" @click="save">保存</el-button>
      <el-button @click="cancelForm">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>

import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_EMPLOYEES = 'http://127.0.0.1:8000/api/assert_manager/employees/'
const API_DEPARTMENTS = 'http://127.0.0.1:8000/api/assert_manager/departments/'

const rules = {
  name: [
    { required: true, message: '姓名不能为空', trigger: 'blur' }
  ],
  employee_id: [
    { required: true, message: '员工号不能为空', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '员工号必须是6位数字', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '部门不能为空', trigger: 'change' },
  ],
  city: [
    { required: true, message: '城市不能为空', trigger: 'change' },
  ],
  position: [
    { required: true, message: '职位不能为空', trigger: 'change' },
    
  ],
  onboard_date: [
    { required: true, message: '入职日期不能为空', trigger: 'change' },
    
  ],
  reporting_line: [
    { required: true, message: '主管不能为空', trigger: 'change' },
    
  ]
  
}



const props = defineProps({
  formData: Object,
})
const emit = defineEmits(['saved', 'cancel'])

const form = ref({ name: '', city:'',employee_id:'',position:'',department: '', reporting_line: '',onboard_date:''})
const departments = ref([])
const manager = ref([])
const formRef = ref()
const isFormValid = ref(false)


const clearForm = () => {
  Object.keys(form.value).forEach(key => form.value[key] = key === 'id' ? null : '')
  formRef.value?.resetFields()
  formRef.value?.clearValidate()
}




onMounted(async () => {
  const res = await axios.get(API_DEPARTMENTS)
  const res1 = await axios.get(API_EMPLOYEES)
  departments.value = res.data
  manager.value = res1.data
})

watch(
  () => props.formData,
  
  async (newVal) => {
    await nextTick()
    if(newVal){
      form.value = newVal ? { ...newVal } : { name: '', city:'',employee_id:'',position:'',department: '', reporting_line: '' ,onboard_date:''}
    } else {
      clearForm()
    }
  
    formRef.value?.clearValidate()
  },
  { immediate: true }
)

// 实时验证表单，控制保存按钮
watch(
  form,
  () => {
    if (formRef.value) {
      formRef.value.validate(valid => {
        isFormValid.value = valid
      })
    }
  },
  { deep: true, immediate: true }
)


const save = async () => {
  try {
     if (form.value.id) {
      await axios.put(`${API_EMPLOYEES}${form.value.id}/`, form.value)
      ElMessage.success('修改成功')
      
    } else {
      console.log(form.value)
      await axios.post(API_EMPLOYEES, form.value)
      ElMessage.success('新增成功')
      
    }
    emit('saved')
    emit('cancel')
    clearForm()

  } catch(err){
    ElMessage.error('保存失败，请检查输入内容')

  }
 
}

const cancelForm = () => {
  clearForm()
  emit('cancel')
}

defineExpose({
  resetFields: clearForm
})

</script>

<style scoped>
/* 可选样式 */
</style>
