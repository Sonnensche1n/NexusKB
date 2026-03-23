import { ref, onBeforeUnmount, computed } from 'vue'
import { darkTheme, lightTheme } from 'naive-ui'
import { zhCN, dateZhCN } from 'naive-ui'
import { THEME_TYPE_KEY, THEME_COLOR_KEY, DEFAULT_THEME_TYPE, DEFAULT_THEME_COLOR, TEME_NAVIGATION_KEY, DEFAULT_THEME_NAVIGATION } from '@/libs/enum'
import { localRead, modifyColorAlpha, similarColors } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
export const useTheme = () => {
  const primaryColor = ref(localRead(THEME_COLOR_KEY) || DEFAULT_THEME_COLOR)
  const themeOverrides = computed(() => {
    let colors = similarColors(primaryColor.value, 3, 50)
    return {
      common: {
        primaryColor: primaryColor.value,
        primaryColorHover: colors[0],
        primaryColorPressed: colors[1],
        primaryColorSuppl: colors[2],
        primaryColorOpacity1: modifyColorAlpha(primaryColor.value, 0.82),
        primaryColorOpacity2: modifyColorAlpha(primaryColor.value, 0.72),
        primaryColorOpacity3: modifyColorAlpha(primaryColor.value, 0.38),
        primaryColorOpacity4: modifyColorAlpha(primaryColor.value, 0.24),
        primaryColorOpacity5: modifyColorAlpha(primaryColor.value, 0.18)
      }
    }
  })
  const themeType = ref(null)
  const onThemeTypeChange = (type) => {
    if (type === 'dark') {
      themeType.value = darkTheme
    } else {
      themeType.value = lightTheme
    }
  }
  onThemeTypeChange(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)

  const naviType = ref(localRead(TEME_NAVIGATION_KEY) || DEFAULT_THEME_NAVIGATION)
  const onNaviTypeChange = (type) => {
    naviType.value = type
  }

  const onThemeColorChange = (color) => {
    primaryColor.value = color
  }
  EventBus.on('on-theme-type-change', onThemeTypeChange)
  EventBus.on('on-theme-color-change', onThemeColorChange)
  EventBus.on('on-theme-navigation-change', onNaviTypeChange)
  onBeforeUnmount(() => {
    EventBus.off('on-theme-type-change', onThemeTypeChange)
    EventBus.off('on-theme-color-change', onThemeColorChange)
    EventBus.off('on-theme-navigation-change', onNaviTypeChange)
  })
  return {
    themeOverrides, themeType, naviType, zhCN, dateZhCN
  }
}
