<template>
  <div class="m-history">
    <section class="hero-card">
      <p class="hero-eyebrow">Health Journal</p>
      <h2 class="hero-title">我的健康记录</h2>
      <p class="hero-subtitle">{{ heroSubtitle }}</p>
    </section>

    <section v-if="records.length" class="record-list">
      <article class="record-card" v-for="r in records" :key="r.id">
        <header class="record-head">
          <div class="record-date">{{ formatDate(r.date) }}</div>
          <span class="record-status" :class="{ warn: r.anomalies?.length }">
            {{ r.anomalies?.length ? "需关注" : "稳定" }}
          </span>
        </header>

        <div class="metric-grid">
          <div class="metric">
            <p class="metric-label">心跳</p>
            <p class="metric-value" :class="{ danger: isHigh(r.heart_rate, 120) || isLow(r.heart_rate, 50) }">
              {{ r.heart_rate ?? "—" }} <span class="metric-unit">次/分</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric-label">血氧</p>
            <p class="metric-value" :class="{ danger: isLow(r.blood_oxygen, 90) }">
              {{ r.blood_oxygen ?? "—" }} <span class="metric-unit">%</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric-label">血压</p>
            <p class="metric-value" :class="{ danger: isHigh(r.systolic_bp, 160) }">
              {{ r.systolic_bp ?? "—" }}/{{ r.diastolic_bp ?? "—" }} <span class="metric-unit">mmHg</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric-label">体温</p>
            <p class="metric-value" :class="{ danger: isHigh(r.temperature, 37.5) }">
              {{ r.temperature ?? "—" }} <span class="metric-unit">℃</span>
            </p>
          </div>
        </div>

        <p v-if="r.feeling" class="feeling">今日感受：{{ r.feeling }}</p>
        <div class="anomalies" v-if="r.anomalies?.length">
          <span class="anomaly-chip" v-for="a in r.anomalies" :key="a">{{ a }}</span>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <div class="empty-dot"></div>
      <p class="empty-title">暂无健康记录</p>
      <p class="empty-subtitle">完成一次健康填报后，这里会自动展示。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import request from "@/utils/request";

const records = ref([]);
const isHigh = (v, max) => v != null && Number(v) > max;
const isLow = (v, min) => v != null && Number(v) < min;

const heroSubtitle = computed(() => {
  if (!records.value.length) return "还没有数据，先去填写今日健康数据吧。";
  const latest = records.value[0]?.date || "";
  return `最近一次更新：${formatDate(latest)}`;
});

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}.${m}.${day}`;
}

onMounted(async () => {
  records.value = await request.get("/health/my-history/");
});
</script>

<style scoped>
.m-history {
  --bg: #f5f5f7;
  --card: #ffffff;
  --text-main: #111111;
  --text-sub: #6e6e73;
  --line: rgba(0, 0, 0, 0.08);
  --danger: #d70015;
  --ok: #0a7d3f;
  min-height: calc(100vh - 64px);
  padding: 16px;
  background:
    radial-gradient(120% 70% at 15% -5%, rgba(10, 125, 63, 0.08), transparent 55%),
    radial-gradient(90% 60% at 95% 0%, rgba(0, 122, 255, 0.06), transparent 55%),
    var(--bg);
}

.hero-card {
  background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px 18px 16px;
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

.record-list {
  display: grid;
  gap: 12px;
}

.record-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 14px;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.05);
}

.record-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.record-date {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.record-status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ok);
  background: rgba(10, 125, 63, 0.1);
}

.record-status.warn {
  color: var(--danger);
  background: rgba(215, 0, 21, 0.1);
}

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.metric {
  padding: 10px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: #fbfbfc;
}

.metric-label {
  margin: 0 0 6px;
  font-size: 12px;
  color: var(--text-sub);
}

.metric-value {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.1;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.metric-value.danger {
  color: var(--danger);
}

.metric-unit {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-sub);
  margin-left: 2px;
}

.feeling {
  margin: 12px 0 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f2f2f7;
  color: #3a3a3c;
  font-size: 14px;
}

.anomalies {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.anomaly-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 600;
  color: var(--danger);
  background: rgba(215, 0, 21, 0.1);
}

.empty-state {
  margin-top: 12px;
  border-radius: 20px;
  padding: 28px 16px;
  text-align: center;
  background: #ffffff;
  border: 1px dashed rgba(0, 0, 0, 0.14);
}

.empty-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin: 0 auto 12px;
  background: #c7c7cc;
}

.empty-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.empty-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-sub);
}
</style>
