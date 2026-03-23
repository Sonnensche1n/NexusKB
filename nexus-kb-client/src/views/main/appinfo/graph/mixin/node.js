import { getCurrentInstance, inject, watch } from 'vue'

export const useNode = () => {
  const { proxy, ctx } = getCurrentInstance()
  const node = inject('getNode')()
  const nodeData = node.data
  const nodeElId = 'EL' + nodeData['nodeId']
  const resizeNode = () => {
    nextTick(() => {
      setTimeout(() => {
        const el = document.getElementById(nodeElId)
        if (el) {
          const width = el.clientWidth
          const height = el.clientHeight
          node.resize(width, height)
        }
      }, 100)
    })
  }
  return {
    proxy,
    ctx,
    node,
    nodeData,
    nodeElId,
    resizeNode
  }
}
