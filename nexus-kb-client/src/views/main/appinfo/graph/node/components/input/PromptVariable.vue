<style lang="less">
.kb-flow-node-prompt-variable.n-collapse {
  .n-collapse-item {
    margin-top: 0;
    margin-left: 0;
    padding: 10px 10px 0 10px;
    border-width: 0;
    .n-collapse-item__header {
      padding-top: 0;
      .n-base-icon {
        svg {
          display: none;
        }
      }
    }
    .n-collapse-item__header-main {
      padding: 4px 0;
      .n-collapse-item-arrow {
        margin-right: 0;
        i {
          display: block;
          height: 4px;
          width: 14px;
          background-color: var(--primary-color);
          border-radius: var(--border-radius);
        }
      }
    }
    .n-collapse-item__content-wrapper .n-collapse-item__content-inner {
      padding-top: 0;
    }
    .n-thing {
      .n-thing-main {
        cursor: pointer;
        &:hover {
          background-color: var(--primary-color-opacity-5);
        }
        .n-thing-main__content {
          padding-left: 16px;
        }
      }
    }
  }
}
</style>

<template>
  <n-collapse class="kb-flow-node-prompt-variable" :default-expanded-names="variableOptions.map(item => item.value)">
    <n-collapse-item :title="item.label" :name="item.value" v-for="item in variableOptions" :key="item.value">
      <n-thing v-for="child in item.children" :key="child.value" @click="onVariableClick(item, child)">
        {{ child.label }}
      </n-thing>
    </n-collapse-item>
  </n-collapse>
</template>
<script>
  import { defineComponent, ref, watch, onMounted, nextTick } from 'vue'
  import { useNode } from '../../../mixin/node'
  
  export default defineComponent({
    components: {
    },
    props: {
      attr: Object,
    },
    setup(props, context) {
      let {ctx, node, nodeData, nodeElId} = useNode()
      const variableOptions = ref([])
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

      const onVariableClick = (item, child) => {
        context.emit('on-change', {
          value: child.value,
          label: item.label + '/' + child.label
        })
      }
      return {
        variableOptions,
        initVariableOptions, onVariableClick
      }
    }
  })
</script>
