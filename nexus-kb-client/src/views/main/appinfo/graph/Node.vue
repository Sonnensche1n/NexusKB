<style lang="less">
@import url('./node/style.less');
</style>

<template>
  <n-config-provider :theme="themeType" :theme-overrides="themeOverrides">
    <n-dialog-provider>
      <n-message-provider>
        <n-card :id="nodeElId" ref="nodeRef" class="kb-flow-node" hoverable header-style="padding: 0;" content-style="padding: 0;" :style="{ width: `${nodeData['width'] || 300}px` }">
          <template #header>
            <n-thing>
              <template #avatar>
                <n-icon :class="nodeData.nodeDef.ndfIcon || 'iconfont-kb icon-llm'" />
              </template>
              <template #header>
                {{ nodeData['nodeNm'] }}
              </template>
              <template #default>
                {{ nodeData['nodeDesc'] }}
              </template>
            </n-thing>
            <waves :themeType="themeType" />
          </template>
          <content @on-resize="resizeNode" />
        </n-card>
      </n-message-provider>
    </n-dialog-provider>
  </n-config-provider>
</template>
<script>
  import { defineComponent, ref, onMounted, nextTick } from 'vue'
  import { useTheme } from '@/mixin/app'
  import Content from './node/Content.vue'
  import { useNode } from './mixin/node'
  import Waves from './Waves.vue'
  
  export default defineComponent({
    components: {
      Content, Waves
    },
    setup() {
      const {themeOverrides, themeType} = useTheme()
      const nodeRef = ref()
      const {node, nodeData, nodeElId, resizeNode} = useNode()
      onMounted(() => {
        resizeNode()
      })
      return {
        themeOverrides, themeType,
        nodeRef,
        nodeData, nodeElId,
        defaultExpandedNames: ['1', '2', '3'],
        resizeNode
      }
    }
  })
</script>
