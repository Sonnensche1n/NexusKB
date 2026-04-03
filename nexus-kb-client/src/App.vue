<style lang="less">
@import url('./window.less');
.n-config-provider, .kb-app {
  height: 100%;
}
</style>

<template>
  <n-config-provider :theme="themeType" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-el tag="div" id="kb-app" :class="`kb-app ${themeType.name}`" :key="`kb-app-${key}`">
      <div v-if="isTauri" data-tauri-drag-region class="window-titlebar">
        <div class="window-titlebar-button" @click="appWindow?.minimize()" title="最小化"></div>
        <div class="window-titlebar-button" @click="appWindow?.toggleMaximize()" title="最大化"></div>
        <div class="window-titlebar-button" @click="appWindow?.close()" title="关闭"></div>
      </div>
      <n-dialog-provider>
        <n-message-provider>
          <router-view />
          <m-n-d />
        </n-message-provider>
      </n-dialog-provider>
    </n-el>
  </n-config-provider>
</template>
<script>
  import { invoke } from '@tauri-apps/api/core'
  import { Window } from '@tauri-apps/api/window'
  import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow'
  import { defineComponent, getCurrentInstance, ref } from 'vue'
  import { useTheme } from '@/mixin/app'
  import MND from './components/MND.vue'
  
  export default defineComponent({
    components: {
      MND
    },
    setup() {
      const { proxy, ctx } = getCurrentInstance()
      const {themeOverrides, themeType, zhCN, dateZhCN} = useTheme()
      const key = ref(0)
      
      // 判断是否在 Tauri 环境中运行
      const isTauri = typeof window !== 'undefined' && window.__TAURI__ !== undefined
      
      let appWindow = null
      
      if (isTauri) {
        const appWebview = getCurrentWebviewWindow()
        appWebview.listen('on-server-started', (event) => {
          console.log(event.payload)
          key.value = 1
        })
        appWindow = new Window('main')
      }
      
      return {
        key,
        themeOverrides, themeType, zhCN, dateZhCN,
        appWindow,
        isTauri
      }
    }
  })
</script>
