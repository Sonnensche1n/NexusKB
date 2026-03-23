<style lang="less">
.kb-dataset-catalog {
  padding-right: 18px;
  .n-tree {
    .n-tree-node {
      padding: 4px 10px;
    }
    .n-tree-node.n-tree-node--selected {
      .n-icon,.n-tree-node-content__text {
        color: var(--primary-color);
      }
    }
    .n-tree-node-switcher.n-tree-node-switcher--expanded {
      transform: none;
    }
    .n-tree-node-content {
      .n-tree-node-content__text {
        border-bottom: 0;
      }
      .n-tree-node-content__suffix {
        visibility: hidden;
      }
      &:hover {
        .n-tree-node-content__suffix {
          visibility: visible;
        }
      }
    }
  }
  .kb-add-catalog {
    text-align: center;
    margin-bottom: 10px;
  }
}
</style>

<template>
  <div class="kb-dataset-catalog">
    <div class="kb-add-catalog" v-if="authEdit">
      <n-button v-if="catalogList.length === 0" round @click="onAddCatalog({}, false)"><n-icon class="iconfont-kb icon-add-catalog"></n-icon>&nbsp;新目录</n-button>
    </div>
    <n-tree 
      block-line
      :data="treeData"
      :selected-keys="selectedCtlgIds"
      :expanded-keys="expandedCtlgIds"
      key-field="ctlgId"
      label-field="ctlgNm"
      children-field="children"
      :render-prefix="renderTreeItemPrefix"
      :render-suffix="renderTreeItemSuffix"
      :cancelable="false"
      selectable
      expand-on-click
      :draggable="authEdit"
      :on-update:selected-keys="onSelectedKeysChange"
      :on-update:expanded-keys="onExpandedKeysChange"
      :on-drop="onCatalogDrop"
    />
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed, watch } from 'vue'
  import { NIcon, NDropdown, useMessage, useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { deepCopy } from '@/libs/tools'
  import CatalogForm from './CatalogForm.vue'
  import { useCatalog } from './mixin/catalog'

  export default defineComponent({
    components: {
    },
    props: {
      reposId: String,
      authEdit: Boolean
    },
    setup(props, context) {
      const dialog = useDialog()
      const message = useMessage()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const reposId = props.reposId
      const authEdit = props.authEdit
      const { catalogList, treeData, initCatalogList, renderTreeItemPrefix, findCatalogAndIndex } = useCatalog()
      const selectedCtlgIds = ref([''])
      const expandedCtlgIds = ref([])
      context.emit('on-selected-change', '')

      const onSelectedKeysChange = (keys) => {
        selectedCtlgIds.value = keys
      }
      watch(selectedCtlgIds, (keys) => {
        context.emit('on-selected-change', keys[0])
      })
      const onExpandedKeysChange = (keys) => {
        expandedCtlgIds.value = keys
      }

      const treeItemOptions = ref([
        {
          label: '同级',
          key: 'addbro',
          icon: () => renderIconfontIcon('iconfont-kb icon-add-catalog'),
          disabled: !authEdit
        },
        {
          label: '子级',
          key: 'addchild',
          icon: () => renderIconfontIcon('iconfont-kb icon-add-catalog1'),
          disabled: !authEdit
        },
        {
          label: '编辑',
          key: 'edit',
          icon: () => renderIconfontIcon('iconfont icon-pencil'),
          disabled: !authEdit
        },
        {
          label: '删除',
          key: 'delete',
          icon: () => renderIconfontIcon('iconfont icon-delete'),
          disabled: !authEdit
        }
      ])

      const onAddCatalog = (row, child=false) => {
        dialogCreate(dialog, {
          title: `新增${child ? '子' : '同级'}目录`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            data.reposId = reposId
            if (child) {
              data.ctlgPid = row.ctlgId
            } else {
              data.ctlgPid = row.ctlgPid
            }
            proxy.$api.post('/knb/dataset/catalog', data).then(async res => {
              await initCatalogList()
              selectedCtlgIds.value = [res.data.ctlgId]
              if (res.data.ctlgPid) {
                expandedCtlgIds.value = [res.data.ctlgPid]
              }
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, CatalogForm, {
        })
      }

      const onEditCatalog = (row) => {
        dialogCreate(dialog, {
          title: `修改目录`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.put('/knb/dataset/catalog', data).then(res => {
              row.ctlgNm = data.ctlgNm
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, CatalogForm, {
          catalog: row
        })
      }
      const onRemoveCatalog = (row) => {
        dialogConfirm(dialog, {
          title: '删除确认',
          content: '删除后目录不可恢复',
          type: 'warning',
          loading: false,
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/knb/dataset/catalog/' + row.ctlgId).then(res => {
              initCatalogList()
              if (row.ctlgId === selectedCtlgIds.value[0]) {
                selectedCtlgIds.value = ['']
              }
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }

      const renderTreeItemSuffix = ({ option }) => {
        let ctlgId = option.ctlgId
        if (!ctlgId) {
          return h('span')
        }
        return h(
          NDropdown,
          {
            options: treeItemOptions.value,
            onSelect: (key) => {
              switch (key) {
                case 'addbro':
                  onAddCatalog(option, false)
                  break
                case 'addchild':
                  onAddCatalog(option, true)
                  break
                case 'edit':
                  onEditCatalog(option)
                  break
                case 'delete':
                  onRemoveCatalog(option)
                  break
              }
            }
          },
          h(
            NIcon,
            {
              class: 'iconfont icon-dotshorizontal'
            }
          )
        )
      }


      const reorderList = (siblings, resorts = []) => {
        siblings.forEach((item, index) => {
          let order = item.ctlgOdr
          if (order === index) {
            return
          }
          if (resorts.findIndex(r => r.ctlgId === item.ctlgId) > -1) {
            return
          }
          resorts.push({
            ctlgId: item.ctlgId,
            ctlgOdr: index
          })
        })
      }

      const onCatalogDrop = ({ node, dragNode, dropPosition }) => {
        if (!dragNode.ctlgId) { // 全部数据集目录不处理
          message.warning('此目录不能移动位置')
          return
        }
        if (!node.ctlgId) {
          message.warning('不能移动到这个位置')
          return
        }
        if (dropPosition === 'inside') {
          // 暂时只支持同级排序
          return
        }
        // dropPosition:after before[拖到第一个节点之前]
        let ctlgId = dragNode.ctlgId
        let ctlgPid = dragNode.ctlgPid // 可能是空
        // 找到同级目录
        const [dragCatalog, dragIndex] = findCatalogAndIndex(ctlgId, ctlgPid)
        catalogList.value.splice(dragIndex, 1)

        ctlgId = node.ctlgId
        ctlgPid = node.ctlgPid
        const [catalog, index] = findCatalogAndIndex(ctlgId, ctlgPid)

        if (dropPosition === 'before') {
          catalogList.value.splice(index, 0, dragCatalog)
        } else if (dropPosition === 'after') {
          catalogList.value.splice(index + 1, 0, dragCatalog)
        }

        let resorts = []
        let siblings = catalogList.value.filter(item => item.ctlgPid === dragCatalog.ctlgPid)
        reorderList(siblings, resorts)
        siblings = catalogList.value.filter(item => item.ctlgPid === catalog.ctlgPid)
        reorderList(siblings, resorts)
        proxy.$api.put('/knb/dataset/catalog/sort', resorts)
      }
      return {
        catalogList, treeData, selectedCtlgIds, expandedCtlgIds,
        renderTreeItemSuffix,
        renderTreeItemPrefix,
        onSelectedKeysChange,
        onExpandedKeysChange,
        onAddCatalog, onCatalogDrop
      }
    }
  })
</script>