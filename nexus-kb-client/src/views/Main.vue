<style lang="less">
@import url('./main.less');
</style>

<template>
  <n-layout has-sider class="kb-main">
    <n-layout-sider :class="`kb-main-sider kb-navi-${naviType}`" content-style="padding: 10px;" width="100" collapse-mode="transform" :collapsed-width="0" show-trigger="bar">
      <div class="kb-logo">
        <logo />
      </div>
      <n-menu class="kb-main-menu" collapsed
        v-model:value="activeKey"
        :options="menuOptions"
        responsive
        :on-update:value="onMenuUpdate"
      />
      <div class="kb-main-option">
        <n-button text class="theme" @click="onThemeTypeChange" :title="`切换${themeType === 'dark' ? '浅': '深'}色主题`">
          <n-icon :class="`iconfont-kb icon-${themeType === 'dark' ? 'moon': 'sun'}`" />
        </n-button>
      </div>
    </n-layout-sider>
    <n-layout-content>
      <router-view />
    </n-layout-content>
  </n-layout>
</template>
<script>
  import { defineComponent, onBeforeUnmount, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog } from 'naive-ui'
  import { renderIconfontIcon } from '@/libs/utils'
  import { localRead, localSave } from '@/libs/tools'
  import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
  import { useTheme } from '@/mixin/app'
  import EventBus from '@/libs/eventbus'
  import useUserStore from '@/store/user'
  import Logo from '@/components/Logo.vue'

  const menuOptions = [
    {
      label: '对 话',
      key: 'chat',
      icon: () => renderIconfontIcon('iconfont-kb icon-chat')
    },
    {
      label: '搜 索',
      key: 'search',
      icon: () => renderIconfontIcon('iconfont-kb icon-search2')
    },
    {
      label: '知识库',
      key: 'repository',
      icon: () => renderIconfontIcon('iconfont-kb icon-knowledge')
    },
    {
      label: '文档库',
      key: 'docset',
      icon: () => renderIconfontIcon('iconfont-kb icon-docset')
    },
    {
      label: '设 置',
      key: 'setting',
      icon: () => renderIconfontIcon('iconfont-kb icon-setting2')
    }
  ]

  export default defineComponent({
    components: {
      Logo
    },
    setup() {
      const router = useRouter()
      const userStore = useUserStore()
      const dialog = useDialog()
      const { naviType } = useTheme()
      const getKeyByPath = (path) => {
        const currentPaths = path.split('/')
        return currentPaths.find(item => menuOptions.map(menu => menu.key).includes(item))
      }
      const activeKey = ref(getKeyByPath(router.currentRoute.value.path))
      const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE) // light, dark
      const onThemeTypeChange = (type) => {
        if (typeof type === 'string') {
          themeType.value = type
          return
        }
        if (themeType.value === 'dark') {
          themeType.value = 'light'
        } else {
          themeType.value = 'dark'
        }
      }
      watch(themeType, (newTheme, oldTheme)=>{
        localSave(THEME_TYPE_KEY, newTheme)
        EventBus.emit('on-theme-type-change', newTheme)
      })

      watch(() => router.currentRoute.value, (newRouter) => {
        let key = getKeyByPath(newRouter.path)
        activeKey.value = key
      }, { immediate: true })

      const onMenuUpdate = (key) => {
        activeKey.value = key
        let path = '/'
        if (key === 'chat') {
          path = '/main/chat'
        } else if (key === 'repository') {
          path = '/main/repository'
        } else if (key === 'setting') {
          path = '/main/setting'
        } else if (key === 'search') {
          path = '/main/search'
        } else if (key === 'docset') {
          path = '/main/docset'
        } else if (key === 'appinfo') {
          path = '/main/appinfo'
        }
        router.push({
          path
        })
      }

      const synth = window.speechSynthesis
      const speech = new SpeechSynthesisUtterance()
      speech.lang = 'zh-CN' // 使用的语言:中文
      speech.volume = 1 // 声音音量：1
      speech.rate = 1 // 语速：1
      speech.pitch = 1 // 音高：1
      speech.onend = () => {
        EventBus.emit('on-speech-onend')
      }

      const onSpeechOn = (text) => {
        onSpeechOff()
        speech.text = text // 文字内容: 如果能播放出声音 那可真是泰裤辣！
        synth.speak(speech) // 播放
      }
      const onSpeechOff = () => {
        EventBus.emit('on-speech-onend')
        speech.text = ''
        synth.cancel(speech)
      }

      EventBus.on('on-speech-on', onSpeechOn)
      EventBus.on('on-speech-off', onSpeechOff)
      EventBus.on('on-theme-type-change', onThemeTypeChange)
      onBeforeUnmount(() => {
        EventBus.off('on-speech-on', onSpeechOn)
        EventBus.off('on-speech-off', onSpeechOff)
        EventBus.off('on-theme-type-change', onThemeTypeChange)
      })
      return {
        themeType, naviType,
        activeKey,
        menuOptions,
        onMenuUpdate, onThemeTypeChange
      }
    }
  })
</script>
