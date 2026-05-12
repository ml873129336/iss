<template>
  <div class="p-6">
    <!-- 搜索栏 -->
    <el-card class="mb-4">
      <div class="flex gap-3">
        <el-input
          v-model="search"
          placeholder="搜索资产名称"
          clearable
          style="width: 200px"
        />
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 150px">
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button type="primary" @click="fetchAssets">搜索</el-button>
        <el-button type="success" @click="openForm()">新增资产</el-button>
        <el-upload
          :http-request="uploadExcel"
          accept=".xlsx,.xls"
          :show-file-list="false"
        >
          <el-button type="warning">导入 Excel</el-button>
        </el-upload>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <el-table :data="assets" stripe>
        <el-table-column prop="category_display" label="类别" width="120" />
        <el-table-column prop="description_display" label="描述" width="400" />
        <el-table-column prop="serial_number" label="S/N" width="200" />
        <el-table-column prop="user.name" label="使用人" width="160" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="{
                in_use: 'success',
                idle: 'info',
                repair: 'warning',
                scrapped: 'danger'
              }[row.status]"
            >
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="采购日期" width="140" />

        <el-table-column label="附件" width="160">
        <template #default="{ row }">
          <a
            v-if="row.file_url"
            :href="row.file_url"
            target="_blank"
            style="color:#409EFF;text-decoration:none"
          >
            下载文件
          </a>
          <span v-else>无</span>
        </template>
      </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" @click="openForm(row)">编辑</el-button>
              <el-popconfirm title="确定删除该资产吗？" @confirm="deleteAsset(row.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

    <!-- 引入表单组件 -->
    <AssetForm
      v-model:visible="dialogVisible"
      :asset="editingAsset"
      @saved="fetchAssets"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";
import AssetForm from "./AssetForm.vue";

const assets = ref([]);
const dialogVisible = ref(false);
const editingAsset = ref(null);
const search = ref("");
const statusFilter = ref("");

const statusMap = {
  in_use: "在用",
  idle: "闲置",
  repair: "维修中",
  scrapped: "报废",
};

const statusOptions = Object.entries(statusMap).map(([value, label]) => ({
  value,
  label,
}));

// 获取资产列表
const fetchAssets = async () => {
  const res = await axios.get("http://127.0.0.1:8000/api/assert_manager/assets/", {
    params: { search: search.value, status: statusFilter.value },
  });
  assets.value = res.data;
};

// 删除资产
const deleteAsset = async (id) => {
  await axios.delete(`http://127.0.0.1:8000/api/assert_manager/assets/${id}/`);
  ElMessage.success("删除成功");
  fetchAssets();
};

// 打开新增/编辑弹窗
const openForm = (asset = null) => {
  editingAsset.value = asset ? { ...asset } : null;
  dialogVisible.value = true;
};

const uploadExcel = async (options) => {
  const file = options.file; // Element Plus 传来的文件对象
  const form = new FormData();
  form.append("file", file);

  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/api/assert_manager/assets/upload_excel/",
      form,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );

    // 提示成功
    ElMessage.success(`导入完成，成功 ${res.data.created.length} 条，失败 ${res.data.errors.length} 条`);

    // 如果有失败，打印到控制台查看
    if (res.data.errors.length) console.error(res.data.errors);

    // 刷新资产列表
    fetchAssets();

  } catch (error) {
    console.error(error);
    ElMessage.error("Excel 导入失败，请检查文件格式或数据");
  }
};



onMounted(fetchAssets);
</script>
