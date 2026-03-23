<style lang="less">
.kb-triplet-graph {
  height: 100%;
  position: relative;
  .graph {
    height: 100%;
  }
  .n-empty, .n-spin-body {
    position: absolute;
    top: 0;
    width: 100%;
    height: 100%;
  }
  &-contextmenu {
    background-color: var(--n-color) !important;
    .g6-contextmenu-ul {
      .g6-contextmenu-li {
        color: var(--text-color-base);
        &:hover {
          background-color: var(--n-color);
          opacity: 0.5;
        }
        &:last-child:hover {
          color: var(--error-color);
        }
      }
    }
  }
}
</style>

<template>
  <div class="kb-triplet-graph">
    <div ref="graphRef" class="graph"></div>
    <n-spin v-if="loading"/>
    <n-empty v-if="dataList.length === 0" />
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, onMounted } from 'vue'
  import { Graph } from '@antv/g6'
  import { useTheme } from '@/mixin/app'

  export default defineComponent({
    components: {
    },
    props: {
      reposId: {
        type: String,
        required: true
      },
      authEdit: {
        type: Boolean,
        default: false
      },
      dtsetId: {
        type: String,
        default: ''
      }
    },
    setup(props, context) {
      const { proxy, ctx } = getCurrentInstance()
      const graphRef = ref()
      let graph = null // 使用ref接收graph会卡死
      const { themeOverrides } = useTheme()
      const reposId = props.reposId
      const dtsetId = props.dtsetId
      const authEdit = props.authEdit
      const loading = ref(false)
      const dataList = ref([])
      
      const initGraph = () => {
        return new Graph({
          container: graphRef.value,
          autoResize: true,
          node: {
            type: 'circle',
            style: {
              halo: true,
              haloStrokeOpacity: 0.2,
              haloLineWidth: 20,
              stroke: themeOverrides.value.common.primaryColorOpacity3,
              lineWidth: 10,
              fill: themeOverrides.value.common.primaryColor,
              size: 50,
              labelText: (d) => d.label,
              iconFontFamily: 'iconfont-kb',
              iconText: '\ue696', // unicode: &#xe696;
              labelFill: themeOverrides.value.common.primaryColor
            },
            state: {
              highlight: {
                fill: themeOverrides.value.common.primaryColorHover,
                halo: true,
                haloStrokeOpacity: 0.2,
                haloLineWidth: 20,
                stroke: themeOverrides.value.common.primaryColorOpacity3,
                lineWidth: 10,
              },
              dim: {
                fill: themeOverrides.value.common.primaryColorOpacity5,
              },
            },
          },
          edge: {
            type: 'quadratic',
            style: {
              stroke: themeOverrides.value.common.primaryColorOpacity5,
              labelText: (d) => d.label,
              endArrow: true,
              endArrowSize: 5,
              labelFill: themeOverrides.value.common.primaryColor
            },
            state: {
              highlight: {
                stroke: themeOverrides.value.common.primaryColorHover,
                lineWidth: 1
              },
            },
          },
          layout: {
            type: 'force-atlas2',
            preventOverlap: true,
            kr: 350
          },
          behaviors: [
            'drag-element', 'zoom-canvas', 'drag-canvas', 'hover-element',
            {
              type: 'hover-activate',
              enable: (event) => event.targetType === 'node',
              degree: 1, // 高亮临近节点.
              state: 'highlight',
              inactiveState: 'dim',
              onHover: (event) => {
                event.view.setCursor('pointer');
              },
              onHoverEnd: (event) => {
                event.view.setCursor('default');
              },
            },
          ],
          plugins: [
            {
              type: 'contextmenu',
              trigger: 'contextmenu', // 'click' or 'contextmenu'
              className: 'kb-triplet-graph-contextmenu',
              onClick: (value, target, current) => {
                if (!current) {
                  return
                }
                let id = current.id
                let triplet = dataList.value.find(item => item.tpltId === id)
                console.log(triplet)
                if (!triplet) {
                  return
                }
                if (value === 'edit') {
                  context.emit('on-edit-triplet', triplet)
                } else if (value === 'delete') {
                  context.emit('on-remove-triplet', triplet)
                }
              },
              getItems: () => {
                return authEdit ? [
                  { name: '编辑', value: 'edit' },
                  { name: '删除', value: 'delete' },
                ] : []
              },
              enable: (e) => e.targetType === 'edge',
            },
          ],
        })
      }

      const initGraphData = () => {
        let nodes = []
        let edges = []
        dataList.value.forEach(item => {
          let subject = item.tpltSbjct
          let predicate = item.tpltPrdct
          let object = item.tpltObjct
          if (!nodes.find(n => n.id === subject)) {
            nodes.push({
              id: subject,
              label: subject,
              size: 20
            })
          }
          if (!nodes.find(n => n.id === object)) {
            nodes.push({
              id: object,
              label: object,
              size: 20
            })
          }
          edges.push({
            id: item.tpltId,
            source: subject,
            target: object,
            label: predicate
          })
        })
        graph.setData({
          nodes,
          edges
        })
        graph.render()
      }

      const onInitDta = () => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.get('/knb/dataset/triplet/' + dtsetId).then(res => {
            dataList.value = res.data || []
            initGraphData()
            loading.value = false
          }).catch(err => {
            console.error(err)
            loading.value = false
          })
        }
      }
      onInitDta()

      onMounted(() => {
        graph = initGraph()
        graph.render()
      })
      
      const removeGraphData = (ids) => {
        graph.removeData(ids)
      }
      const updateGraphData = (data) => {
      }
      return {
        graphRef,
        loading,
        dataList,
        authEdit,
        onInitDta,
        removeGraphData, updateGraphData
      }
    }
  })
</script>
