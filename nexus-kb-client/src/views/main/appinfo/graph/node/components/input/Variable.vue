<style lang="less">
.kb-flow-node-variable {

}
</style>

<template>
  <n-cascader class="kb-flow-node-variable" size="small" clearable check-strategy="child"
    v-model:value="attr[valueKey]"
    placeholder="请选择引用变量"
    expand-trigger="hover"
    :options="variableOptions"
    :on-update:show="initVariableOptions"
  />
</template>
<script>
  import { defineComponent, ref, watch, onMounted, nextTick } from 'vue'
  import { useNode } from '../../../mixin/node'
  
  export default defineComponent({
    components: {
    },
    props: {
      attr: Object,
      valueKey: {
        type: String,
        default: 'attrVal'
      }
    },
    setup(props, context) {
      let {ctx, node, nodeData, nodeElId} = useNode()
      let attr = props['attr']
      let variableOptions = ref([])
      // todo 当边被删除时，需要判断引用的变量是否有source节点的属性，有的话需要清空，暂时不管
      const initVariableOptions = () => {
        variableOptions.value = []
        let nodes = node._model.graph.getPredecessors(node).reverse() // 获取所有前序节点
        nodes.forEach(nd => {
          let ndData = nd.data
          variableOptions.value.push({
            value: ndData.nodeId,
            label: ndData.nodeNm,
            children: (ndData.attrs || []).map(attr => { // 需要过滤掉不同的数据类型，暂时不管
              return {
                value: `${ndData.nodeId}/${attr.attrKey}`,
                label: attr.attrLbl
              }
            })
          })
        })
      }
      initVariableOptions()
      return {
        variableOptions,
        initVariableOptions
      }
    }
  })
</script>
