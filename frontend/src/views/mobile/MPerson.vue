<template>
  <div class="ds-person">
    <div class="page-header">
      <button class="back-btn" @click="handleBack" aria-label="返回">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="page-title">{{ currentTitle }}</h1>
    </div>

    <div v-if="!activePanel" class="settings-list">
      <button class="settings-item" @click="router.push('/m/account')">
        <div class="item-copy">
          <span class="item-title">{{ t('accountManagement') }}</span>
          <span class="item-desc">{{ t('accountTip') }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>

      <button class="settings-item" @click="openPanel('language')">
        <div class="item-copy">
          <span class="item-title">{{ t('interfaceLanguage') }}</span>
          <span class="item-desc">{{ currentLanguageLabel }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>

      <button class="settings-item" @click="openPanel('appearance')">
        <div class="item-copy">
          <span class="item-title">{{ t('appearanceMode') }}</span>
          <span class="item-desc">{{ currentAppearanceLabel }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>

      <button class="settings-item" @click="openPanel('fontScale')">
        <div class="item-copy">
          <span class="item-title">{{ t('textSize') }}</span>
          <span class="item-desc">{{ currentFontScaleLabel }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>

      <button class="settings-item" @click="restoreDefaults">
        <div class="item-copy">
          <span class="item-title">{{ t('restoreDefaults') }}</span>
          <span class="item-desc">{{ t('resetTip') }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>

      <button v-if="isAuthed" class="settings-item danger" @click="handleLogout">
        <div class="item-copy">
          <span class="item-title">{{ t('logout') }}</span>
          <span class="item-desc">{{ t('logoutTip') }}</span>
        </div>
        <el-icon class="item-arrow"><ArrowRight /></el-icon>
      </button>
    </div>

    <div v-else class="panel-card">
      <div class="panel-caption">{{ t('currentChoice') }}</div>
      <p class="panel-desc">{{ panelDescription }}</p>

      <div class="option-list">
        <button
          v-for="item in currentOptions"
          :key="item.value"
          class="option-row"
          :class="{ active: currentValue === item.value }"
          @click="updatePreference(activePanel, item.value)"
        >
          <div class="item-copy">
            <span class="item-title">{{ item.label }}</span>
            <span class="item-desc">{{ item.desc }}</span>
          </div>
          <span v-if="currentValue === item.value" class="checkmark">✓</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getPreferences, resetPreferences, savePreferences } from '@/utils/preferences'
import { useMobileI18n } from '@/utils/mobileI18n'

const router = useRouter()
const route = useRoute()
const refreshAuth = inject('refreshAuth', () => {})
const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))
const preferences = ref(getPreferences())
const { t } = useMobileI18n()

const activePanel = computed(() => {
  const panel = route.query.panel
  return ['language', 'appearance', 'fontScale'].includes(panel) ? panel : ''
})

const languageOptions = computed(() => ([
  { value: 'zh-CN', label: t('languageZh'), desc: t('languageZhDesc') },
  { value: 'en-US', label: t('languageEn'), desc: t('languageEnDesc') },
  { value: 'yue-Hans-CN', label: t('languageYue'), desc: t('languageYueDesc') },
]))

const appearanceOptions = computed(() => ([
  { value: 'light', label: t('appearanceLight'), desc: t('appearanceLightDesc') },
  { value: 'warm', label: t('appearanceWarm'), desc: t('appearanceWarmDesc') },
  { value: 'contrast', label: t('appearanceContrast'), desc: t('appearanceContrastDesc') },
]))

const fontScaleOptions = computed(() => ([
  { value: 'default', label: t('fontDefault'), desc: t('fontDefaultDesc') },
  { value: 'large', label: t('fontLarge'), desc: t('fontLargeDesc') },
  { value: 'extra-large', label: t('fontExtraLarge'), desc: t('fontExtraLargeDesc') },
]))

const panelMeta = computed(() => ({
  language: {
    title: t('interfaceLanguage'),
    desc: t('chooseLanguage'),
    options: languageOptions.value,
    value: preferences.value.language,
  },
  appearance: {
    title: t('appearanceMode'),
    desc: t('chooseAppearance'),
    options: appearanceOptions.value,
    value: preferences.value.appearance,
  },
  fontScale: {
    title: t('textSize'),
    desc: t('chooseTextSize'),
    options: fontScaleOptions.value,
    value: preferences.value.fontScale,
  },
}))

const currentTitle = computed(() => activePanel.value ? panelMeta.value[activePanel.value].title : t('settings'))
const panelDescription = computed(() => activePanel.value ? panelMeta.value[activePanel.value].desc : '')
const currentOptions = computed(() => activePanel.value ? panelMeta.value[activePanel.value].options : [])
const currentValue = computed(() => activePanel.value ? panelMeta.value[activePanel.value].value : '')

const currentLanguageLabel = computed(() =>
  languageOptions.value.find(item => item.value === preferences.value.language)?.label || t('languageZh')
)
const currentAppearanceLabel = computed(() =>
  appearanceOptions.value.find(item => item.value === preferences.value.appearance)?.label || t('appearanceLight')
)
const currentFontScaleLabel = computed(() =>
  fontScaleOptions.value.find(item => item.value === preferences.value.fontScale)?.label || t('fontDefault')
)

function openPanel(panel) {
  router.push({ path: '/m/settings', query: { panel } })
}

function handleBack() {
  if (activePanel.value) {
    router.push('/m/settings')
    return
  }
  router.push('/m/chat')
}

function updatePreference(key, value) {
  preferences.value = savePreferences({
    ...preferences.value,
    [key]: value,
  })
  ElMessage.success(t('saved'))
}

function restoreDefaults() {
  preferences.value = resetPreferences()
  ElMessage.success(t('resetDone'))
}

function handleLogout() {
  localStorage.removeItem('elder_token')
  localStorage.removeItem('token')
  refreshAuth()
  router.push('/m/settings')
}
</script>

<style scoped>
.ds-person {
  min-height: calc(100vh - 64px);
  padding: 16px;
  background:
    radial-gradient(120% 70% at 15% -5%, rgba(0, 122, 255, 0.08), transparent 55%),
    radial-gradient(90% 60% at 95% 0%, rgba(16, 185, 129, 0.08), transparent 55%),
    #f5f5f7;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  color: #1d1d1f;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  cursor: pointer;
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: #111111;
}

.settings-list,
.panel-card {
  background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 22px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.settings-item,
.option-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  padding: 15px 18px;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: transparent;
  cursor: pointer;
}

.settings-item:last-child,
.option-row:last-child {
  border-bottom: none;
}

.settings-item:active,
.option-row:active {
  background: rgba(242, 242, 247, 0.9);
}

.item-copy {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #111111;
}

.item-desc {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  line-height: 1.5;
  color: #6e6e73;
}

.item-arrow {
  color: #8a8a8e;
  font-size: 15px;
}

.danger .item-title,
.danger .item-arrow {
  color: #d70015;
}

.panel-card {
  padding: 12px 0 0;
}

.panel-caption {
  padding: 0 18px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #8a8a8e;
  text-transform: uppercase;
}

.panel-desc {
  margin: 8px 0 14px;
  padding: 0 18px;
  font-size: 14px;
  color: #6e6e73;
}

.checkmark {
  font-size: 17px;
  font-weight: 700;
  color: #007aff;
}

.option-row.active {
  background: #f5f9ff;
}
</style>
