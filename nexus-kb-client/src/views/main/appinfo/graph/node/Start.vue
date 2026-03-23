<style lang="less">
.kb-flow-node-start.n-collapse {
}
</style>

<template>
  <n-collapse class="kb-flow-node-start" :default-expanded-names="defaultExpandedNames" :on-update:expanded-names="onUpdateExpandedNames">
    <n-collapse-item title="输出" name="1">
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item v-for="attr in outputAttrs" :key="`${attr.nodeId}-${attr.attrId}`">
          <span>{{ attr.attrLbl }}</span>
          <n-tag size="small">{{ attr.dataTyp }}</n-tag>
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <!-- <n-collapse-item title="全局变量" name="2">
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item class="notnull">
          <span>应用ID</span>
          <n-tag size="small">string</n-tag>
        </n-list-item>
        <n-list-item>
          <span>对话ID</span>
          <n-tag size="small">string</n-tag>
        </n-list-item>
        <n-list-item>
          <span>用户ID</span>
          <n-tag size="small">string</n-tag>
        </n-list-item>
      </n-list>
    </n-collapse-item> -->
  </n-collapse>
</template>
<script>
  import { defineComponent, ref, watch, onMounted } from 'vue'
  import { useNode } from '../mixin/node'
  
  export default defineComponent({
    components: {
    },
    setup(props, context) {
      const { nodeData } = useNode()
      const attrs = nodeData['attrs'] || []
      const outputAttrs = attrs.filter(item => item.attrCls === 'opt')
      const onUpdateExpandedNames = () => {
        context.emit('on-resize')
      }
      return {
        onUpdateExpandedNames,
        defaultExpandedNames: ['1', '2', '3'],
        attrs, outputAttrs
      }
    }
  })
</script>
