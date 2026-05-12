<template>
  <el-dialog v-model="visible" :title="form.id ? '编辑资产' : '新增资产'" width="600px" @close="handleDialogClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      
      <el-form-item label="类别" prop="category">
        <el-select v-model="form.category" placeholder="选择类别">
          <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="型号" prop="description">
        <el-select v-model="form.description" placeholder="选择型号">
          <el-option v-for="item in DescriptionOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="SN" prop="serial_number">
        <el-input v-model="form.serial_number" placeholder="请输入序列号" />
      </el-form-item>


      <el-form-item label="使用人" prop="user_id">
        <el-select v-model="form.user_id" placeholder="选择员工" filterable>
          <el-option v-for="emp in employees" :key="emp.id" :label="emp.name" :value="emp.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-select v-model="form.status" placeholder="选择状态">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="采购日期" prop="purchase_date">
        <el-date-picker v-model="form.purchase_date" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>

      

      <el-form-item label="备注">
        <el-input type="textarea" v-model="form.remark" />
      </el-form-item>

      <el-form-item label="文件">
        <el-upload
          class="upload-demo"
          :file-list="fileList"
          :on-change="handleFileChange"
          :on-remove="handleRemove"
          :limit="1"
          :auto-upload="false"
          accept=".csv"
          :show-file-list="true"
>
          <el-button type="primary">选择文件</el-button>
        </el-upload>
      </el-form-item>
      
    </el-form>

    

    

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

// 接收父组件传参
const props = defineProps({
  visible: Boolean,
  asset: Object,
});
const emit = defineEmits(["update:visible", "saved"]);

const visible = ref(props.visible);
watch(() => props.visible, (v) => (visible.value = v));
watch(visible, (v) => emit("update:visible", v));

const API_EMPLOYEES = "http://127.0.0.1:8000/api/assert_manager/employees/"
const API_ASSET = "http://127.0.0.1:8000/api/assert_manager/assets/"
const formRef = ref();
const form = ref({});
const employees = ref([]);

const statusOptions = [
  { value: "in_use", label: "在用" },
  { value: "idle", label: "闲置" },
  { value: "repair", label: "维修中" },
  { value: "scrapped", label: "报废" },
];

const categoryOptions = [
  { value: "laptop", label: "笔记本" },
  { value: "desktop", label: "台式机" },
  { value: "monitor", label: "显示器" },
  { value: "printer", label: "打印机" },
];

const DescriptionOptions = [
  { value: "thinkpad14", label: "Thinkpad丨 ThinkBook 14丨 I5-1135G7 丨512-SSD 丨 14" }
  
];

const rules = {
  category: [{ required: true, message: "请选择类别", trigger: "change" }],
  user_id: [{ required: true, message: "请选择使用人", trigger: "change" }],
};

const fileList = ref([]);

const handleFileChange = (file,fileListRaw) => {
  fileList.value = fileListRaw.slice(-1);
  form.value.file = file.raw; // ✅ 保存到 form
};

const handleRemove = () => {
  fileList.value = [];
  form.value.file = null;
};

// 监听传入的资产
watch(
  () => props.asset,
  (newAsset) => {
    form.value = newAsset
      ? { ...newAsset,user_id: newAsset.user?.id || null }
      : { id: null, category: "laptop", user: null,serial_number:"", status: "idle", remark: "" };

    if (newAsset?.file_url) {
      fileList.value = [
        {
          name: newAsset.file_name , // 可以根据后台返回的文件名
          url: newAsset.file_url,
        },
      ];
      form.value.file = null; // 这里不覆盖原文件，只显示
    } else {
      fileList.value = [];
      form.value.file = null;
    }
  },
  { immediate: true }
);

// 获取员工列表
const fetchEmployees = async () => {
  const res = await axios.get(API_EMPLOYEES);
  employees.value = res.data;
};

// 保存资产
const save = async () => {
  try {
    await formRef.value.validate();

    // 1️⃣ 构造 FormData
    const formData = new FormData();

    for (const key in form.value) {
      if (key !== "file" && form.value[key] !== undefined) {
        formData.append(key, form.value[key]);
      }
    }

    // 如果有文件字段（假设绑定在 form.value.file）
    if (form.value.file instanceof File) {
      formData.append("file", form.value.file);
    }

    // 2️⃣ 判断是创建还是更新
    if (form.value.id) {
      await axios.put(`${API_ASSET}${form.value.id}/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      ElMessage.success("资产更新成功");
    } else {
      await axios.post(API_ASSET, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      ElMessage.success("资产创建成功");
    }

    emit("saved");
    close();
  } catch (err) {
    console.error("保存失败：", err.response?.data || err);
    ElMessage.error(err.response?.data?.detail || "保存失败");
  }
};

const handleDialogClose = () => {
  fileList.value = [];
  form.value.file = null;
  formRef.value?.clearValidate();
};

const close = () => {
  visible.value = false;
  handleDialogClose();
};

onMounted(fetchEmployees);
</script>
