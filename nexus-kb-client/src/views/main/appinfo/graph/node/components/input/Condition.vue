<style lang="less">
.kb-flow-node-condition {
  width: 100%;
  .n-card {
    box-shadow: var(--box-shadow-1);
    margin-bottom: 10px;
    .n-card-header {
      .n-card-header__main {
        font-size: var(--n-font-size);
        .n-button {
          margin-left: 8px;
          .n-icon {
            transform: scale(1.5);
          }
        }
      }
      .n-card-header__extra {
        display: none;
      }
    }
    &:hover {
      .n-card-header__extra {
        display: block;
      }
    }
    .n-card__footer {
      text-align: center;
    }
  }
}
</style>

<template>
  <div class="kb-flow-node-condition" @mousedown.stop="" @mousemove.stop="">
    <n-card :ref="element.key" v-for="element in attrVals_" :key="element.key" :bordered="false" :header-style="`padding: 10px 10px ${element.typ === 'else' ? '10px' : '0'} 10px;`" content-style="padding: 10px;" footer-style="padding: 0 10px 10px 10px;">
      <template #header>
        <span>{{ element.typ.toUpperCase() }}</span>
        <n-button text title="并且" v-if="element.comb === 'and'" @click="element['comb'] = 'or'">
          <n-icon class="iconfont-kb icon-and" />
        </n-button>
        <n-button text title="或者" v-if="element.comb === 'or'" @click="element['comb'] = 'and'">
          <n-icon class="iconfont-kb icon-or" />
        </n-button>
      </template>
      <template #header-extra>
        <n-button size="small" text type="error" title="删除" @click="() => {
          attrVals = attrVals.filter(val => val.key !== element.key)
        }">
          <n-icon class="iconfont icon-delete" />
        </n-button>
      </template>
      <n-space vertical>
        <n-input-group v-for="(item, index) in element.items" :key="`${element.key}-${index}`">
          <variable :attr="item" valueKey="var" />
          <n-select v-model:value="item.symbol" size="small" placeholder="选择条件" :options="options" :on-update:value="(value) => {
            item.symbol = value
            if (value === 'null' || value === 'nnull') {
              item.val = ''
            }
          }" />
          <n-input v-model:value="item.val" size="small" placeholder="输入值" :disabled="item.symbol === 'null' || item.symbol === 'nnull'" />
          <n-button size="small" @click="() => {
            element['items'].splice(index, 1)
          }"><n-icon class="iconfont icon-minus" /></n-button>
        </n-input-group>
      </n-space>
      <template #footer>
        <n-button size="small" @click="() => {
          if (!element['items']) element['items'] = []
          element['items'].push({ var: '', symbol: '', val: '' })
        }"><n-icon class="iconfont icon-plus" />&nbsp;添加条件</n-button>
      </template>
    </n-card>
    <n-card title="ELSE" :ref="attrValElse?.key" :bordered="false" header-style="padding: 10px;"></n-card>
    <p style="text-align: center;">
      <n-button size="small" @click="() => {
        attrVals.push({ key: uuid(), typ: 'else if', comb: 'and', items: [{ var: '', symbol: 'eq', val: '' }] })
      }"><n-icon class="iconfont icon-plus" />&nbsp;添加分支</n-button>
    </p>
  </div>
</template>
<script>
  import { defineComponent, ref, watch, computed, onMounted, nextTick } from 'vue'
  import { uuid, isEmpty } from '@/libs/tools'
  import { NODE_ATTR_CONDITION_TYPE } from '@/libs/enum'
  import { map2Options } from '@/libs/utils'
  import { useNode } from '../../../mixin/node'
  import Variable from './Variable.vue'
  import { getElementOffset } from '../../../utils'


  // 条件分支  IF ELSE IF ELSE
  export default defineComponent({
    components: {
      Variable
    },
    props: {
      attr: Object,
    },
    setup(props, context) {
      let { ctx, node, nodeData, nodeElId, resizeNode } = useNode()
      let appId = nodeData['appId']
      let attr = props['attr']
      // const conditions = [
      //   { key: 'id1', typ: 'if', comb: 'or', items: [ // type: if, else if, else    comb: or, and
      //     { var: '', symbol: 'eq', val: '10' } // symbol 为空，不为空，等于，不等于，包含，不包含，开始为，结束为，大于，大于等于，小于，小于等于，长度等于，长度不等于，长度大于，长度大于等于，长度小于，长度小于等于
      //   ] },
      //   { key: 'id2', typ: 'else if', comb: 'and', items: [ // type: if, else if, else    comb: or, and
      //     { var: '', symbol: 'eq', val: '10' } // symbol 为空，不为空，等于，不等于，包含，不包含，开始为，结束为，大于，大于等于，小于，小于等于，长度等于，长度不等于，长度大于，长度大于等于，长度小于，长度小于等于
      //   ] },
      //   { key: 'id3', typ: 'else' }
      // ]
      let attrVal = ref(attr.attrVal || '') // [ { key: 'id1', typ: 'if', comb: 'or', items: [ { var: '', symbol: 'eq', val: '10' } ] } ]
      let attrVals = ref([])
      try {
        if (!isEmpty(attrVal.value)) {
          attrVals.value = JSON.parse(attrVal.value)
        }
      } catch (error) {
        console.error(error)
      }

      if (attrVals.value.length === 0) {
        attrVals.value = [
          { key: uuid(), typ: 'if', comb: 'and', items: [{ var: '', symbol: 'eq', val: '' }] },
          { key: uuid(), typ: 'else' }
        ]
      }

      const attrVals_ = computed(() => {
        return attrVals.value.filter(val => val.typ !== 'else')
      })
      const attrValElse = computed(() => {
        return attrVals.value.find(val => val.typ === 'else')
      })

      watch(attrVal, (newVal) => {
        attr['attrVal'] = newVal
      })

      watch(attrVals, (newVals) => {
        if (newVals.length > 0) {
          attrVals.value[0]['typ'] = 'if'
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

      // ({ portId: uuid(), portTyp: 'incoming', nodeId, attrId: incoming, valkey: val, y: 0 }
      // 新增和删除都需要重新设置 port 才行
      const setPortsOffset = () => {
        let parent = document.getElementById(nodeElId)
        let offsetTopMap = {}
        let clientHeightMap = {}
        for (const valKey in ctx.$refs) {
          if (ctx.$refs.hasOwnProperty(valKey)) {
            if (!ctx.$refs[valKey]) {
              continue
            }
            let el = ctx.$refs[valKey][0]?.$el
            if (!el) {
              el = ctx.$refs[valKey]?.$el
            }
            if (el) {
              clientHeightMap[valKey] = el.clientHeight
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
            let h = clientHeightMap[portValKey]
            let y = offsetTopMap[portValKey] + h / 2
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
          let h = clientHeightMap[valKey]
          let y = offsetTopMap[valKey] + h / 2
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

      return {
        options: map2Options(NODE_ATTR_CONDITION_TYPE),
        uuid, attrVals_, attrValElse, attrVals
      }
    }
  })
</script>
