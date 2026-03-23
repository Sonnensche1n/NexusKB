<style lang="less">
.kb-appinfo-flow {
  height: 100%;
  position: relative;
  border-left: 1px solid var(--divider-color);
  &-drawer {
    // .n-drawer-body-content-wrapper {
    //   padding: 0 !important;
    // }
  }
  &>.trigger {
    position: absolute;
    left: 12px;
    top: 90px;
    z-index: 1;
  }
  &>.header.n-thing {
    position: absolute;
    z-index: 1;
    padding: 24px 10px 0 10px;
    .n-thing-header {
      margin-bottom: 0;
      .n-thing-header__title {
        font-size: 14px;
        font-weight: 550;
      }
    }
    .n-thing-avatar {
      margin-top: 0;
      margin-right: 6px;
      .n-icon {
        font-size: 45px;
        color: var(--primary-color);
      }
    }
    .n-thing-main__description, .n-tag__content {
      font-size: 11px;
    }
    .n-thing-main__description {
      .save {
        cursor: pointer;
        margin-left: 4px;
        &:hover {
          color: var(--primary-color);
        }
      }
    }
  }
  &>.option.n-thing {
    position: absolute;
    right: 0;
    top: 0;
    padding: 24px 10px 0 10px;
    z-index: 1;
  }
  &>.graph {
    height: 100%;
  }
  &>.minimap {
    position: absolute;
    right: 10px;
    bottom: 10px;
    z-index: 1;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border-color);
    .x6-widget-minimap {
      background-color: var(--base-color);
      .x6-graph {
        box-shadow: none;
      }
      .x6-widget-minimap-viewport, .x6-widget-minimap-viewport-zoom {
        border-color: var(--primary-color);
      }
      .x6-widget-minimap-viewport-zoom {
        background-color: var(--base-color);
      }
    }
  }
}
</style>

<template>
  <div :id="id" class="kb-appinfo-flow">
    <n-button class="trigger" strong circle type="primary" @click="nodesShow = !nodesShow">
      <template #icon>
        <n-icon class="iconfont icon-plus" />
      </template>
    </n-button>
    <n-drawer content-class="kb-appinfo-flow-drawer" v-model:show="nodesShow" :show-mask="false" display-directive="show" :width="300" placement="left" :to="`#${id}`"
      :trap-focus="false" :block-scroll="false" >
      <n-drawer-content title="">
        <nodes :graph="graph" :appId="appId" />
      </n-drawer-content>
    </n-drawer>
    <n-drawer content-class="kb-appinfo-flow-drawer" v-model:show="publishShow" :show-mask="false" :width="300" placement="right" :to="`#${id}`"
      :trap-focus="false" :block-scroll="false" >
      <n-drawer-content title="">
        <release :appId="appId" />
      </n-drawer-content>
    </n-drawer>
    <n-drawer content-class="kb-appinfo-flow-drawer" v-model:show="debugShow" :show-mask="false" width="80%" placement="right" :to="`#${id}`"
      :trap-focus="false" :block-scroll="false" >
      <n-drawer-content title="">
        <debug :appId="appId" :graph="graph" />
      </n-drawer-content>
    </n-drawer>
    <n-drawer v-model:show="settingShow" width="70%" placement="right">
      <n-drawer-content>
        <template #header>
          <n-icon class="iconfont icon-settings"></n-icon>
          设置
        </template>
        <setting :appId="appId" :appInfo="appInfo" />
      </n-drawer-content>
    </n-drawer>
    <n-thing class="header">
      <template #avatar>
        <n-icon class="iconfont-kb icon-workspace" />
      </template>
      <template #header>
        {{ appInfo.appNm }}
      </template>
      <template #description>
        <n-tag size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'transparent', textColor: 'var(--primary-color)'}">
          <n-badge dot color='var(--primary-color)'/>&nbsp;{{ APPINFO_RELEASE_STATUS[appInfo.appSts]?.label }}
        </n-tag>
        <span class="save" title="点击保存" @click="saveWorkflow" v-if="authEdit">
          <template v-if="saveTime" >已保存 <n-time :time="saveTime" format="HH:mm" /></template>
          <template v-else>点击保存</template>
        </span>
      </template>
    </n-thing>
    <n-thing class="option">
      <n-space>
        <n-button tertiary circle title="设置" @click="settingShow = !settingShow">
          <template #icon>
            <n-icon class="iconfont icon-settings" />
          </template>
        </n-button>
        <n-button tertiary circle title="发布记录" @click="publishShow = !publishShow">
          <template #icon>
            <n-icon class="iconfont icon-avtimer" />
          </template>
        </n-button>
        <n-button @click="debugShow = !debugShow" v-if="authEdit">
          <template #icon>
            <n-icon class="iconfont icon-play" />
          </template>
          调试
        </n-button>
        <n-button type="primary" @click="publishWorkflow" v-if="authEdit">
          <template #icon>
            <n-icon class="iconfont icon-send" />
          </template>
          发布
        </n-button>
      </n-space>
    </n-thing>
    <div ref="graphRef" class="graph"></div>
    <div ref="minimapRef" class="minimap"></div>
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, onMounted, onBeforeUnmount, computed } from 'vue'
  import { Graph, NodeView } from '@antv/x6'
  import { MiniMap } from '@antv/x6-plugin-minimap'
  import { register } from '@antv/x6-vue-shape'
  import { useDialog, useMessage } from 'naive-ui'
  import { random, uuid } from '@/libs/tools'
  import { dialogCreate, dialogConfirm, renderIconfontIcon } from '@/libs/utils'
  import { APPINFO_RELEASE_STATUS } from '@/libs/enum'
  import { flow_node_shape, createGraphNode, createGraphEdge } from './graph/utils'
  import Nodes from './Nodes.vue'
  import Release from './Release.vue'
  import Node from './graph/Node.vue'
  import Debug from './Debug.vue'
  import Setting from './Setting.vue'

  register({
    shape: flow_node_shape,
    component: Node,
  })

  class SimpleNodeView extends NodeView {
    renderMarkup() {
      return this.renderJSONMarkup({
        tagName: 'rect',
        selector: 'body',
      })
    }
    update() {
      super.update({
        body: {
          refWidth: '100%',
          refHeight: '100%',
          fill: 'var(--border-color)',
        },
      })
    }
  }

  export default defineComponent({
    components: {
      Nodes, Release, Debug, Setting
    },
    props: {
      appId: String
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const appId = props.appId
      const id = `F${random(true, 4)}`
      const appInfo = ref({})
      const graphRef = ref(null)
      const minimapRef = ref(null)
      const graph = ref()
      const nodesShow = ref(false)
      const publishShow = ref(false)
      const debugShow = ref(false)
      const settingShow = ref(false)
      const saveEnabled = ref(false)
      const authEdit = computed(() => appInfo.value['optAuth'] === 'alter')

      // 工作流节点列表
      const nodeDataList = ref([])
      const nodeEdgeList = ref([])

      const initAppInfo = () => {
        proxy.$api.get(`/agt/app/${appId}`).then(res => {
          appInfo.value = res.data
        }).catch(err => {
          console.error(err)
        })
      }
      initAppInfo()
      // 从后台获取工作流的配置数据，再初始化画布
      const initFlowData = () => {
        proxy.$api.get(`/agt/app/flow/node/datas/${appId}`).then(res => {
          const { nodes, edges } = res.data || {}
          nodeDataList.value = nodes || []
          nodeEdgeList.value = edges || []
          initGraphData()
        }).catch(err => {
          console.error(err)
        })
      }

      initFlowData()

      const initGraph = () => {
        return new Graph({
          container: graphRef.value,
          autoResize: true,
          panning: true,
          mousewheel: {
            enabled: true,
          },
          connecting: {
            snap: true,
            highlight: true,
            allowBlank: false,
            allowNode: false,
            allowLoop: false,
            allowMulti: true,
            createEdge: function ({sourceCell, sourceView, sourceMagnet}) {
              let edgeData = {
                edgeId: uuid(), srcId: sourceCell.id, tgtId: '', srcPortId: '', tgtPortId: ''
              }
              return this.createEdge(createGraphEdge(edgeData))
            },
            validateConnection: function(args) {
              let sourceCell = args.sourceCell
              let sourcePortId = args.sourcePort
              let sourcePort = sourceCell.port.ports.find(port => port.id === sourcePortId)
              let sourcePortGroup = sourcePort.group
              if (sourcePort && sourcePortGroup.indexOf('outgoing') === -1) { // 输出端口才能连线
                return false
              }
              if (sourcePortGroup === 'outgoing2') {
                let fs = this.getOutgoingEdges(sourceCell).filter(edge => edge.source.port === sourcePortId && edge.target.port)
                return fs.length === 0
              }
              let fs = this.getOutgoingEdges(sourceCell).filter(edge => edge.source.cell === sourceCell.id && edge.target.cell)
              if (fs.length > 0) {
                return false
              }
              return true
            }
          },
          grid: {
            visible: true,
            type: 'dot',
            args: [
              {
                color: 'var(--border-color)', // 主网格线颜色
                thickness: 0.5 // 主网格线宽度
              }
            ]
          }
        })
      }
      const initGraphData = () => {
        let nodeMap = {}
        nodeDataList.value.forEach(nodeData => {
          let node = createGraphNode(nodeData)
          graph.value.addNode(node)
          nodeMap[nodeData['nodeId']] = node
        })
        nodeEdgeList.value.forEach(edgeData => {
          let edge = createGraphEdge(edgeData, nodeMap)
          if (edge) {
            graph.value.addEdge(edge)
          }
        })
        // graph.value.centerContent()
        initTimer()
      }
      const registerGraphEvent = () => {
        graph.value.on('node:moved', ({ e, x, y, node, view }) => {
          node.data['posX'] = x
          node.data['posY'] = y
        })
        graph.value.on('node:added', ({ node, index, options }) => {
        })
        graph.value.on('edge:added', ({ edge, index, options }) => {
        })
        graph.value.on('edge:connected', ({ isNew, edge }) => {
          if (!isNew) {
            return
          }
          let edgeData = edge.data || {}
          if (edgeData['tgtId']) {
            return
          }
          let srcId = edge.source.cell
          let srcPortId = edge.source.port
          let tgtId = edge.target.cell
          if (!tgtId) {
            return
          }
          let tgtPortId = edge.target.port
          edgeData['appId'] = appId
          edgeData['srcId'] = srcId
          edgeData['srcPortId'] = srcPortId
          edgeData['tgtId'] = tgtId
          edgeData['tgtPortId'] = tgtPortId
          edge.prop('data', edgeData)
        })
        graph.value.on('edge:mouseenter', ({ cell }) => {
          cell.addTools([
            {
              name: 'button-remove',
              args: { distance: '50%' },
            },
          ])
        })
        graph.value.on('edge:mouseleave', ({ cell }) => {
          if (cell.hasTool('button-remove')) {
            cell.removeTool('button-remove')
          }
        })
        graph.value.on('node:mouseenter', ({ cell }) => {
          // if (cell.data.ndfId === 'start') {
          //   return
          // }
          cell.addTools([
            {
              name: 'button-remove',
              args: { x: '100%' }
            },
          ])
        })
        graph.value.on('node:mouseleave', ({ cell }) => {
          if (cell.hasTool('button-remove')) {
            cell.removeTool('button-remove')
          }
        })
        graph.value.on('cell:change:*', ({ key }) => {
          if (key === 'tools' || key === 'size') {
            return
          }
          saveEnabled.value = true
        })
      }
      onMounted(() => {
        graph.value = initGraph()
        graph.value.use(
          new MiniMap({
            container: minimapRef.value,
            width: 200,
            height: 124,
            graphOptions: {
              createCellView(cell) {
                if (cell.isEdge()) {
                  return null
                }
                if (cell.isNode()) {
                  return SimpleNodeView
                }
              },
            },
          })
        )
        registerGraphEvent()
      })
      
      const saveTime = ref('')
      // 保存工作流
      const saveWorkflow = (e) => {
        if (!authEdit.value) {
          return
        }
        let nodes = graph.value.getNodes()
        let edges = graph.value.getEdges()
        if (nodes.length == 0) {
          return message.error('请添加节点')
        }
        if (!e) {
          if (!saveEnabled.value) {
            return
          }
        }
        let nodeDatas = nodes.map(node => {
          const { x, y } = node.store.data.position
          node.data['posX'] = x
          node.data['posY'] = y
          return node.data
        })
        let edgeDatas = edges.map(edge => edge.data)
        proxy.$api.post(`/agt/app/flow/save/${appId}`, { nodes: nodeDatas, edges: edgeDatas }).then(res => {
          saveTime.value = Date.now()
          saveEnabled.value = false
        }).catch(err => {
          console.error(err)
        })
      }

      // 发布应用
      const publishWorkflow = () => {
        dialogConfirm(dialog, {
          title: '发布确认',
          content: '确定发布该应用的版本吗？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.post(`/agt/app/release/${appId}`).then(res => {
              appInfo.value['appSts'] = res.data['appSts']
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        })
      }

      const timer = ref(null)
      const initTimer = () => {
        // 60秒自动保存一次
        timer.value = setInterval(() => {
          saveWorkflow()
        }, 1000 * 60)
      }
      onBeforeUnmount(() => {
        if (timer.value) {
          clearInterval(timer.value)
        }
      })

      return {
        id,
        appInfo, APPINFO_RELEASE_STATUS,
        nodesShow, publishShow, debugShow, settingShow, authEdit,
        graphRef, graph, minimapRef,
        saveWorkflow, publishWorkflow,
        saveTime
      }
    }
  })
</script>
