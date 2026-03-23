<style lang="less">
.kb-flow-nodes.n-tabs {
  .n-tabs-nav--segment-type {
    padding: 10px;
  }
  .n-tab-pane {
    padding: 0 10px;
  }
  .n-list-item {
    cursor: pointer;
    padding-left: 10px;
    padding-right: 10px;

    .n-thing-avatar-header-wrapper {
      align-items: center;
      .n-thing-avatar {
        padding: 8px;
        margin-right: 8px;
        border-radius: 10px;
        background-color: var(--primary-color);
        display: flex;
        .n-icon {
          font-size: 18px;
          color: #fff;
        }
      }
      .n-thing-header {
        margin-bottom: 0;
      }
    }
    
    &:hover {
      background-color: var(--n-color-hover);
    }
  }
}
</style>

<template>
  <n-tabs class="kb-flow-nodes" type="segment" animated>
    <n-tab-pane name="node" tab="节点">
      <n-list :show-divider="false">
        <n-list-item v-for="node in nodes" :key="`${node.ndfId}`">
          <n-popover trigger="hover" placement="right">
            <template #trigger>
              <n-thing @mousedown="startDragToGraph(node, $event)">
                <template #avatar>
                  <n-icon :class="node.ndfIcon || 'iconfont-kb icon-llm'" />
                </template>
                <template #header>
                  {{ node.ndfNm }}
                </template>
              </n-thing>
            </template>
            <span>{{ node.ndfDesc || node.ndfNm }}</span>
          </n-popover>
        </n-list-item>
      </n-list>
      <n-empty v-if="nodes.length === 0"/>
    </n-tab-pane>
    <n-tab-pane name="tool" tab="工具">
      <n-list :show-divider="false">
        <n-list-item v-for="node in tools" :key="`${node.ndfId}`">
          <n-popover trigger="hover" placement="right">
            <template #trigger>
              <n-thing @mousedown="startDragToGraph(node, $event)">
                <template #avatar>
                  <n-icon :class="node.ndfIcon || 'iconfont-kb icon-llm'" />
                </template>
                <template #header>
                  {{ node.ndfNm }}
                </template>
              </n-thing>
            </template>
            <span>{{ node.ndfDesc || node.ndfNm }}</span>
          </n-popover>
        </n-list-item>
      </n-list>
      <n-empty v-if="tools.length === 0"/>
    </n-tab-pane>
  </n-tabs>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed } from 'vue'
  import { Dnd } from '@antv/x6-plugin-dnd'
  import { uuid, isEmpty } from '@/libs/tools'
  import { createGraphNode } from './graph/utils'

  export default defineComponent({
    components: {
    },
    props: {
      graph: Object,
      appId: String
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const nodeDefList = ref([])
      const graph = props.graph
      const appId = props.appId
      const initNodeDefList = () => { // 从后台获取
        proxy.$api.get(`/agt/app/flow/node/defines`).then(res => {
          nodeDefList.value = res.data || {}
        }).catch(err => {
          console.error(err)
        })
      }
      initNodeDefList()

      const nodes = computed(() => {
        return nodeDefList.value.filter(node => node.ndfCls === 'node')
      })
      const tools = computed(() => {
        return nodeDefList.value.filter(node => node.ndfCls === 'tool')
      })

      // 生成节点初始化ports
      const createNodeAttrsAndPorts = (nodeId, ndfData) => {
        let attrsDef = ndfData['attrs'] || []
        let attrs = []
        let attrMap = {}
        attrsDef.forEach(def => {
          let attrSrcs = (def['attrSrc'] || '').split(',')
          let valSrc = ''
          if (attrSrcs.length > 0) {
            valSrc = attrSrcs[0]
          }
          let attr = {
            nodeId, appId, attrId: def.attrId, attrVal: def['dftVal'] || '', valSrc, ...def
          }
          attrs.push(attr)
          attrMap[def.attrId] = attr
        })

        let incoming = Number(ndfData['incoming'] || 0)
        let outgoing = Number(ndfData['outgoing'] || 0)
        let ports = []
        if (isNaN(incoming)) { // 不是数字而是属性的id，port应该是根据某个参数动态增减的
          incoming = ndfData['incoming']
          let attr = attrMap[incoming] // 值必须是数组的json字符串
          if (attr) {
            try {
              if (!isEmpty(attr.attrVal)) {
                let vals = JSON.parse(attr.attrVal)
                vals.forEach(val => {
                  ports.push({ portId: uuid(), appId, portTyp: 'incoming', nodeId, attrId: incoming, attrVal: val })
                })
              }
            } catch (err) {
              console.error(err)
            }
          }
        } else {
          for (let i = 0; i < incoming; i++) {
            ports.push({ portId: uuid(), appId, portTyp: 'incoming', nodeId })
          }
        }
        if (isNaN(outgoing)) { // 不是数字，port应该是根据某个参数动态增减的
          outgoing = ndfData['outgoing']
          let attr = attrMap[outgoing] // 值必须是数组的json字符串
          if (attr) {
            try {
              if (!isEmpty(attr.attrVal)) {
                let vals = JSON.parse(attr.attrVal)
                vals.forEach(val => {
                  ports.push({ portId: uuid(), appId, portTyp: 'outgoing', nodeId, attrId: incoming, attrVal: val })
                })
              }
            } catch (err) {
              console.error(err)
            }
          }
        } else {
          for (let i = 0; i < outgoing; i++) {
            ports.push({ portId: uuid(), appId, portTyp: 'outgoing', nodeId })
          }
        }
        return {
          attrs, ports
        }
      }

      const startDragToGraph = (ndfData, e) => {
        let nodeId = uuid()
        const { attrs, ports } = createNodeAttrsAndPorts(nodeId, ndfData)
        let nodeData = {
          nodeId,
          appId,
          ndfId: ndfData['ndfId'],
          nodeDef: ndfData,
          nodeNm: ndfData.ndfNm, nodeDesc: ndfData.ndfDesc,
          posX: 0, posY: 0,
          width: ndfData['width'] || 300,
          // 节点变量
          ports,
          attrs // 节点变量
        }
        
        const node = graph.createNode(createGraphNode(nodeData))
        const dnd = new Dnd({
          target: graph,
          getDragNode() {
            // 这里返回一个新的节点作为拖拽节点
            return graph.createNode({
              width: ndfData['width'] || 300,
              height: 60,
              shape: 'rect',
              label: ndfData.ndfNm,
              attrs: {
                body: {
                  stroke: '#EFEFF5',
                  strokeWidth: 1,
                  rx: 10,
                  ry: 10
                },
              },
            })
          },
          getDropNode: () => node.clone({ keepId: true }),
          // ☆拖拽结束时，验证节点是否可以放置到目标画布中。
          validateNode: (n, e) => {
            const {x, y} = n.store.data.position // 这是位置
            nodeData.posX = x
            nodeData.posY = y
            node.data.posX = x
            node.data.posY = y
          }
        })
        dnd.start(node, e)
      }
      return {
        nodeDefList, nodes, tools,
        startDragToGraph
      }
    }
  })
</script>
