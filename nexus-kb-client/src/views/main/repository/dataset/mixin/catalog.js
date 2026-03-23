import { ref, getCurrentInstance, defineProps, computed } from 'vue'
import { NIcon } from 'naive-ui'

export const useCatalog = () => {
  const { proxy, ctx } = getCurrentInstance()
  const reposId = ctx._.props.reposId // ctx.reposId 这样打包过后找不到属性
  const catalogList = ref([])
  const defaultTreeItem = {
    ctlgId: '',
    ctlgNm: '全部数据集',
    ctlgPid: ''
  }
  function generateTreeData(ctlgList, pid = '') {
    let tree = []
    for (let i = 0; i < ctlgList.length; i++) {
      const item = ctlgList[i]
      if ((item.ctlgPid || '') === pid) {
        const children = generateTreeData(ctlgList, item.ctlgId)
        if (children.length) {
          item.children = children
        }
        tree.push(item)
      }
    }
    return tree
  }
  const initCatalogList = () => {
    return proxy.$api.post('/knb/dataset/catalog/list', {
      reposId
    }).then(res => {
      catalogList.value = res.data
    }).catch(err => {
      console.error(err)
    })
  }

  initCatalogList()

  const treeData = computed(() => {
    return [defaultTreeItem, ...generateTreeData(catalogList.value)]
  })

  // 找到同级目录节点与索引
  function findCatalogAndIndex(ctlgId, ctlgPid) {
    let catalog = {}, index = -1
    for(let i = 0; i < catalogList.value.length; i++) {
      let item = catalogList.value[i]
      if(item.ctlgId === ctlgId) {
        catalog = item
        index = i
      }
    }
    return [catalog, index]
  }

  return {
    catalogList,
    treeData, initCatalogList,
    findCatalogAndIndex,
    renderTreeItemPrefix: () => h(NIcon, {
      class: `iconfont-kb icon-catalog`
    })
  }
}
