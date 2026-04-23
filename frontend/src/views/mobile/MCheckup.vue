<template>
  <div class="m-checkup">
    <section class="hero-card">
      <p class="hero-eyebrow">Medical Archive</p>
      <h2 class="hero-title">我的体检报告</h2>
      <p class="hero-subtitle">{{ heroSubtitle }}</p>
    </section>

    <section class="upload-entry">
      <button class="upload-entry-btn" @click="openUploadSheet()">
        导入体检报告
      </button>
    </section>

    <section v-if="groupedCheckups.length" class="year-list">
      <article class="year-section" v-for="yearGroup in groupedCheckups" :key="yearGroup.year">
        <header class="year-header">
          <h3 class="year-title">{{ yearGroup.year }} 年</h3>
          <span class="year-count">{{ yearGroup.items.length }} 次体检</span>
        </header>

        <div class="year-grid">
          <article class="checkup-card" v-for="c in yearGroup.items" :key="c.id">
            <header class="checkup-header">
              <div>
                <p class="checkup-title">第 {{ c.sequence }} 次体检</p>
                <p class="checkup-date">{{ formatDate(c.check_date) }}</p>
              </div>
              <span class="state-tag" :class="{ pending: !(c.report_file_url || c.report_file) }">
                {{ c.report_file_url || c.report_file ? "已上传" : "待上传" }}
              </span>
            </header>

            <div class="checkup-hospital" v-if="c.hospital">{{ c.hospital }}</div>

            <div class="checkup-grid">
              <div class="cg-item" v-if="c.blood_pressure">
                <span class="cg-lbl">血压</span>
                <span class="cg-val">{{ c.blood_pressure }}</span>
              </div>
              <div class="cg-item" v-if="c.heart_rate">
                <span class="cg-lbl">心率</span>
                <span class="cg-val">{{ c.heart_rate }}</span>
              </div>
              <div class="cg-item" v-if="c.blood_sugar">
                <span class="cg-lbl">血糖</span>
                <span class="cg-val">{{ c.blood_sugar }}</span>
              </div>
              <div class="cg-item" v-if="c.height">
                <span class="cg-lbl">身高</span>
                <span class="cg-val">{{ c.height }}cm</span>
              </div>
              <div class="cg-item" v-if="c.weight">
                <span class="cg-lbl">体重</span>
                <span class="cg-val">{{ c.weight }}kg</span>
              </div>
            </div>

            <div class="report-preview" v-if="isImage(c)">
              <img :src="getReportUrl(c)" alt="体检报告" />
            </div>
            <div class="report-link" v-else-if="getReportUrl(c)">
              <a :href="getReportUrl(c)" target="_blank" rel="noopener">查看已上传报告</a>
            </div>

            <div class="upload-actions">
              <button class="upload-btn secondary" @click="openUploadSheet(c)">
                {{ getReportUrl(c) ? "更换报告" : "补传报告" }}
              </button>
            </div>
          </article>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <p class="empty-title">暂无体检记录</p>
      <p class="empty-subtitle">先导入一份体检报告，并选择对应的年度和次数。</p>
    </section>

    <el-dialog
      v-model="uploadDialogVisible"
      title="导入体检报告"
      width="92%"
      class="upload-dialog"
      @closed="resetUploadDraft"
    >
      <div class="sheet-form">
        <div class="field-row">
          <label>年度</label>
          <input v-model.number="uploadDraft.year" type="number" min="2020" />
        </div>
        <div class="field-row">
          <label>第几次</label>
          <select v-model.number="uploadDraft.sequence">
            <option :value="1">第1次体检</option>
            <option :value="2">第2次体检</option>
          </select>
        </div>
        <div class="field-row">
          <label>体检日期</label>
          <input v-model="uploadDraft.check_date" type="date" />
        </div>
      </div>

      <div v-if="matchedCheckup" class="matched-tip">
        已匹配到 {{ matchedCheckup.year }} 年第 {{ matchedCheckup.sequence }} 次体检，上传后会替换该记录的报告。
      </div>
      <div v-else class="matched-tip pending">
        当前组合还没有记录，上传后会自动创建该次体检记录。
      </div>

      <template #footer>
        <button class="sheet-btn ghost" @click="uploadDialogVisible = false">取消</button>
        <button class="sheet-btn" :disabled="uploading" @click="pickFile('dialog')">
          {{ uploading ? '上传中...' : '选择图片或PDF' }}
        </button>
      </template>
    </el-dialog>

    <input
      class="hidden-input"
      type="file"
      accept="image/*,application/pdf"
      capture="environment"
      :ref="el => bindFileInput(el, 'dialog')"
      @change="onFileChange($event)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import request from "@/utils/request";

const checkups = ref([]);
const fileInputs = ref({});
const uploading = ref(false);
const uploadDialogVisible = ref(false);

const now = new Date();
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
const uploadDraft = ref({
  year: now.getFullYear(),
  sequence: 1,
  check_date: today,
});

const heroSubtitle = computed(() => {
  if (!checkups.value.length) return "上传后可在管理端同步查看图片报告。";
  return `共 ${checkups.value.length} 条体检记录，可按年份和次数补传报告。`;
});

const groupedCheckups = computed(() => {
  const groups = new Map();
  checkups.value.forEach(item => {
    const year = Number(item.year);
    if (!groups.has(year)) groups.set(year, []);
    groups.get(year).push(item);
  });
  return Array.from(groups.entries())
    .sort((a, b) => b[0] - a[0])
    .map(([year, items]) => ({
      year,
      items: items.slice().sort((a, b) => Number(a.sequence) - Number(b.sequence)),
    }));
});

const matchedCheckup = computed(() =>
  checkups.value.find(item => item.year === Number(uploadDraft.value.year) && item.sequence === Number(uploadDraft.value.sequence)) || null
);

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}.${m}.${day}`;
}

function bindFileInput(el, key) {
  if (el) fileInputs.value[key] = el;
}

function pickFile(key) {
  if (uploading.value) return;
  fileInputs.value[key]?.click();
}

function getReportUrl(c) {
  return c?.report_file_url || c?.report_file || "";
}

function isImage(c) {
  const url = (getReportUrl(c) || "").toLowerCase();
  return [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".heic"].some(ext => url.includes(ext));
}

async function loadMyCheckups() {
  checkups.value = await request.get("/checkup/my/");
}

function openUploadSheet(checkup = null) {
  if (checkup) {
    uploadDraft.value = {
      year: Number(checkup.year),
      sequence: Number(checkup.sequence),
      check_date: checkup.check_date || today,
    };
  } else {
    uploadDraft.value = {
      year: now.getFullYear(),
      sequence: 1,
      check_date: today,
    };
  }
  uploadDialogVisible.value = true;
}

function resetUploadDraft() {
  uploadDraft.value = {
    year: now.getFullYear(),
    sequence: 1,
    check_date: today,
  };
}

async function onFileChange(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (uploading.value) return;

  if (!uploadDraft.value.year || !uploadDraft.value.sequence || !uploadDraft.value.check_date) {
    ElMessage.warning("请先选择年度、第几次和体检日期");
    event.target.value = "";
    return;
  }

  const formData = new FormData();
  formData.append("report_file", file);
  formData.append("year", String(uploadDraft.value.year));
  formData.append("sequence", String(uploadDraft.value.sequence));
  formData.append("check_date", uploadDraft.value.check_date);

  if (matchedCheckup.value?.id) {
    formData.append("checkup_id", String(matchedCheckup.value.id));
  }

  try {
    uploading.value = true;
    await request.post("/checkup/my-upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    ElMessage.success(matchedCheckup.value ? "体检报告已更新" : "体检报告已导入");
    uploadDialogVisible.value = false;
    await loadMyCheckups();
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
}

onMounted(async () => {
  await loadMyCheckups();
});
</script>

<style scoped>
.m-checkup {
  --bg: #f5f5f7;
  --card: #fff;
  --text-main: #111111;
  --text-sub: #6e6e73;
  --line: rgba(0, 0, 0, 0.08);
  min-height: calc(100vh - 64px);
  padding: 16px;
  background:
    radial-gradient(120% 70% at 15% -5%, rgba(0, 122, 255, 0.08), transparent 55%),
    radial-gradient(90% 60% at 95% 0%, rgba(16, 185, 129, 0.08), transparent 55%),
    var(--bg);
}

.hero-card {
  background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
}

.hero-eyebrow {
  margin: 0 0 4px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8a8a8e;
}

.hero-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--text-main);
}

.hero-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--text-sub);
}

.upload-entry {
  margin-bottom: 14px;
}

.upload-entry-btn {
  display: block;
  width: 100%;
  background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 14px 16px;
  color: #007aff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.05);
}

.upload-btn,
.sheet-btn {
  border: none;
  border-radius: 12px;
  padding: 11px 14px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #0a84ff, #0071e3);
}

.year-list {
  display: grid;
  gap: 14px;
}

.year-section {
  background: transparent;
}

.year-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 0 4px;
}

.year-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.year-count {
  font-size: 12px;
  color: var(--text-sub);
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.checkup-card {
  padding: 14px;
  background: var(--card);
  border-radius: 18px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.05);
  min-width: 0;
}

.checkup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.checkup-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.checkup-date {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-sub);
}

.state-tag {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: #0a7d3f;
  background: rgba(10, 125, 63, 0.12);
}

.checkup-hospital {
  font-size: 13px;
  color: var(--text-sub);
  margin-bottom: 10px;
}

.checkup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}

.cg-item {
  background: #fbfbfc;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 8px 9px;
}

.cg-lbl {
  display: block;
  font-size: 11px;
  color: var(--text-sub);
}

.cg-val {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin-top: 4px;
}

.report-preview {
  margin-top: 6px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--line);
  background: #fafafa;
  aspect-ratio: 4 / 5;
}

.report-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.upload-actions {
  margin-top: 10px;
}

.upload-btn.secondary {
  width: 100%;
  background: #f2f2f7;
  color: #111111;
}

.sheet-btn {
  width: calc(50% - 6px);
}

.sheet-btn.ghost {
  background: #f2f2f7;
  color: #111111;
}

:deep(.upload-dialog .el-dialog__footer) {
  display: flex;
  gap: 12px;
}

@media (max-width: 640px) {
  .year-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 390px) {
  .year-grid {
    grid-template-columns: 1fr;
  }
}

.state-tag.pending {
  color: #d97706;
  background: rgba(217, 119, 6, 0.12);
}

.report-link a {
  color: #007aff;
  text-decoration: none;
  font-size: 14px;
}

.hidden-input {
  display: none;
}

.empty-state {
  border-radius: 20px;
  padding: 20px 16px;
  background: #fff;
  border: 1px dashed rgba(0, 0, 0, 0.16);
}

.empty-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.empty-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-sub);
}

.sheet-form {
  display: grid;
  gap: 10px;
}

.field-row {
  display: grid;
  grid-template-columns: 72px 1fr;
  align-items: center;
  gap: 8px;
}

.field-row label {
  font-size: 13px;
  color: var(--text-sub);
}

.field-row input,
.field-row select {
  height: 38px;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0 10px;
  background: #fff;
  color: var(--text-main);
}

.matched-tip {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(10, 125, 63, 0.08);
  color: #0a7d3f;
  font-size: 13px;
  line-height: 1.6;
}

.matched-tip.pending {
  background: rgba(217, 119, 6, 0.1);
  color: #b45309;
}

:deep(.upload-dialog .el-dialog) {
  border-radius: 22px;
}
</style>
