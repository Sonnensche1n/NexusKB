<style lang="less">
.kb-flow-node-classify {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  .n-input .n-input-wrapper {
    padding-left: 4px;
    padding-right: 4px;
    .n-input__suffix {
      display: none;
    }
    &:hover {
      .n-input__suffix {
        display: block;
      }
    }
  }
}
</style>

<template>
  <div class="kb-flow-node-classify">
    <n-input v-for="(val, index) in attrVals" :key="`${attr.attrId}-${val.key}`" :ref="val.key" v-model:value="val.value" type="text" size="small" :placeholder="`输入分类${index + 1}`">
      <template #prefix>
        <n-tag size="small" :color="tagColor">分类{{ index + 1 }}</n-tag>
      </template>
      <template #suffix>
        <n-button size="small" text type="error" title="删除">
          <n-icon class="iconfont icon-delete" @click="removeClassify(val.key)" />
        </n-button>
      </template>
    </n-input>
    <n-button size="small" @click="addClassify"><n-icon class="iconfont icon-plus" />&nbsp;添加分类</n-button>
  </div>
</template>
<script>
  import { defineComponent, ref, watch, computed, onMounted, nextTick } from 'vue'
  import { uuid, isEmpty } from '@/libs/tools'
  import { useNode } from '../../../mixin/node'
  import { getElementOffset } from '../../../utils'
  
  export default defineComponent({
    components: {
    },
    props: {
      attr: Object,
    },
    setup(props, context) {
      let {ctx, node, nodeData, nodeElId, resizeNode} = useNode()
      let appId = nodeData['appId']
      let attr = props['attr']
      let attrVal = ref(attr.attrVal || '') // '[{key": "classid1", "value": "分类1"},{"key": "classid2", "value": "分类2"},{"key": "classid3", "value": "分类3"}]'
      let attrVals = ref([])
      try {
        if (!isEmpty(attrVal.value)) {
          attrVals.value = JSON.parse(attrVal.value)
        }
      } catch (error) {
        console.error(error)
      }
      watch(attrVal, (newVal) => {
        attr['attrVal'] = newVal
      })
      watch(attrVals, (newVals) => {
        if (newVals.length > 0) {
          attrVal.value = JSON.stringify(newVals)
        } else {
          attrVal.value = ''
        }
        nextTick(() => {
          setTimeout(() => {
            setPortsOffset()
          }, 150)
        })
        resizeNode()
      }, {
        deep: true
      })
      // ({ portId: uuid(), portTyp: 'incoming', nodeId, attrId: incoming, valKey: val, y: 0 }
      
      // 新增和删除都需要重新设置 port 才行
      const setPortsOffset = () => {
        let parent = document.getElementById(nodeElId)
        let offsetTopMap = {}
        for (const valKey in ctx.$refs) {
          if (ctx.$refs.hasOwnProperty(valKey)) {
            if (!ctx.$refs[valKey]) {
              continue
            }
            let el = ctx.$refs[valKey][0]?.$el
            if (el) {
              let offset = getElementOffset(el, parent)
              offsetTopMap[valKey] = offset.top
            }
          }
        }
        let nodePorts = nodeData.ports?.filter(item => item.portTyp === 'outgoing' && item.valKey)
        let valKeys = attrVals.value.map(val => val.key)
        let portValKeys = nodePorts.map(item => item.valKey)
        let deletedKeys = []
        nodePorts.forEach(item => {
          let portValKey = item.valKey
          if (!valKeys.includes(portValKey)) { // 已经被删除
            deletedKeys.push(item.portId)
            return
          }
          if (offsetTopMap[portValKey]) {
            let y = offsetTopMap[portValKey] + 15
            if (item.posY !== y) {
              item.posY = y
              node.setPortProp(item.portId, 'args', { y })
            }
          }
        })
        if (deletedKeys.length > 0) {
          node.removePorts(deletedKeys)
          nodeData.ports = nodeData.ports.filter(item => {
            return !deletedKeys.includes(item.portId)
          })
        }
        let newPorts = []
        // 新增的port
        valKeys.filter(valKey => !portValKeys.includes(valKey)).forEach(valKey => {
          let y = offsetTopMap[valKey] + 14
          newPorts.push({ portId: uuid(), appId, portTyp: 'outgoing', nodeId: nodeData['nodeId'], attrId: attr.attrId, valKey, posY: y })
        })
        if (newPorts.length > 0) {
          nodeData.ports.push(...newPorts)
          newPorts.forEach(port => {
            node.addPort({
              group: 'outgoing2',
              id: port['portId'],
              data: port,
              args: {
                y: port.posY || 0
              }
            })
          })
        }
      }
      onMounted(() => {
        nextTick(() => {
          setTimeout(() => {
            setPortsOffset()
          }, 150)
        })
      })
      const addClassify = () => {
        attrVals.value.push({
          key: uuid(), value: ''
        })
      }
      const removeClassify = (key) => {
        attrVals.value = attrVals.value.filter(val => val.key !== key) // 还需要删除节点的port
      }
      return {
        tagColor: {color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'},
        attrVals,
        addClassify, removeClassify
      }
    }
  })
</script>
