<style lang="less">
</style>

<template>
  <n-form
    ref="formVm"
    label-placement="left"
    label-width="auto"
    :model="formData"
    require-mark-placement="right-hanging"
  >
    <n-form-item label="主题" path="theme">
      <n-radio-group v-model:value="formData.theme" name="radiobuttongroup1">
        <n-radio-button key="light" value="light" label="浅色主题" />
        <n-radio-button key="dark" value="dark" label="深色主题" />
      </n-radio-group>
    </n-form-item>
    <n-form-item label="颜色" path="color">
      <n-color-picker v-model:value="formData.color" :show-alpha="false" style="width: 170px;" :swatches="['#2587F7', '#6E21FF', '#832203', '#389E3E', '#AC4A20', '#D57F3F', '#FF6452', '#FF6E0B']" />
    </n-form-item>
    <n-form-item label="导航" path="navigation">
      <n-radio-group v-model:value="formData.navigation" name="radiobuttongroup2">
        <n-radio-button key="default" value="default" label="默认背景" />
        <n-radio-button key="primary" value="primary" label="主题背景" />
      </n-radio-group>
    </n-form-item>
  </n-form>
</template>
<script>
  import { defineComponent, ref, reactive, onBeforeMount, watch } from 'vue'
  import { localRead, localSave } from '@/libs/tools'
  import EventBus from '@/libs/eventbus'
  import { THEME_TYPE_KEY, THEME_COLOR_KEY, DEFAULT_THEME_TYPE, DEFAULT_THEME_COLOR, TEME_NAVIGATION_KEY, DEFAULT_THEME_NAVIGATION } from '@/libs/enum'
  export default defineComponent({
    components: {
    },
    data() {
      return {
      }
    },
    setup() {
      const formVm = ref(null)
      const formData = reactive({
        theme: localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE , // light, dark
        color: localRead(THEME_COLOR_KEY) || DEFAULT_THEME_COLOR,
        navigation: localRead(TEME_NAVIGATION_KEY) || DEFAULT_THEME_NAVIGATION
      })
      onBeforeMount(() => {})
      watch(() => formData.theme, (newTheme, oldTheme)=>{
        localSave(THEME_TYPE_KEY, newTheme)
        EventBus.emit('on-theme-type-change', newTheme)
      })
      watch(() => formData.color, (newColor, oldColor)=>{
        localSave(THEME_COLOR_KEY, newColor)
        EventBus.emit('on-theme-color-change', newColor)
      })
      watch(() => formData.navigation, (newNavi, oldNavi)=>{
        localSave(TEME_NAVIGATION_KEY, newNavi)
        EventBus.emit('on-theme-navigation-change', newNavi)
      })
      return {
        formVm,
        formData
      }
    }
  })
</script>
