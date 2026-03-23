import { ref, getCurrentInstance, defineProps, computed } from 'vue'
import { NIcon } from 'naive-ui'
import { useRoute } from 'vue-router'

export const useDocument = () => {
  const { proxy, ctx } = getCurrentInstance()
  const route = useRoute()
  const setId = ctx._.props.setId || route.query.id
  const documentList = ref([])
  function generateTreeData(dcmtList, pid = '') {
    let tree = []
    for (let i = 0; i < dcmtList.length; i++) {
      const item = dcmtList[i]
      if ((item.docPid || '') === pid) {
        const children = generateTreeData(dcmtList, item.docId)
        if (children.length) {
          item.children = children
        } else {
          delete item.children
        }
        tree.push(item)
      }
    }
    return tree
  }
  const initDocumentList = () => {
    return proxy.$api.post(`/doc/document/list/${setId}`).then(res => {
      documentList.value = res.data
    }).catch(err => {
      console.error(err)
    })
  }

  initDocumentList()

  const treeData = computed(() => {
    let list = documentList.value // 不能删除这一行
    return generateTreeData(list)
  })

  return {
    documentList,
    treeData, initDocumentList,
    renderTreeItemPrefix: () => h(NIcon, {
      class: `iconfont-kb icon-document`
    })
  }
}
