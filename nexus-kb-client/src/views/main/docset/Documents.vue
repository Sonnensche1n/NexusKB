<style lang="less">
.kb-docset-docs.n-layout {
  height: 100%;
  // border-left: 1px solid var(--border-color);
  .n-layout-sider {
    border-right: 1px solid var(--border-color);
    .n-scrollbar-container {
      padding: 20px 24px;
    }
    .title {
      font-size: 18px;
      font-weight: 600;
      padding-bottom: 20px;
      .n-icon {
        font-size: 22px;
        margin-right: 4px;
        position: relative;
        top: 2px;
        color: var(--primary-color);
      }
    }
    .option {
      display: flex;
      justify-content: center;
    }
    .tree.n-tree {
      .n-tree-node {
        padding: 4px 0;
      }
      .n-tree-node.n-tree-node--selected {
        .n-icon,.n-tree-node-content__text {
          color: var(--primary-color);
        }
      }
      .n-tree-node-switcher {
        width: 18px !important;
      }
      .n-tree-node-content {
        padding-left: 0;
        .n-tree-node-content__text {
          border-bottom: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .n-tree-node-content__prefix {
          margin-right: 4px;
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
  }
  .content.n-layout-content {
    position: relative;
    .option {
      position: absolute;
      left: 24px;
      top: 20px;
      z-index: 2;
    }
    .child-nav {
      position: absolute;
      top: 95px;
      left: 20px;
      .n-timeline-item-content {
        .n-timeline-item-content__content {
          cursor: pointer;
          &:hover {
            color: var(--primary-color);
          }
        }
        .n-timeline-item-content__meta {
          margin-bottom: 10px;
        }
      }
    }
    .prev, .next {
      opacity: 0.3;
      .n-float-button {
        margin-top: -20px;
      }
      &:hover {
        opacity: 1;
      }
    }
  }
}
</style>

<template>
  <n-layout class="kb-docset-docs" has-sider>
    <n-layout-sider :native-scrollbar="false">
      <div class="title">
        <n-icon class="iconfont-kb icon-docset"></n-icon>文档列表({{ documentList.length }})
      </div>
      <n-button-group class="option" v-if="authEdit">
        <n-button round @click="addDocument">
          <template #icon>
            <n-icon class="iconfont icon-pluscircle"></n-icon>
          </template>
          新文档
        </n-button>
      </n-button-group>
      <n-tree class="tree" block-line block-node :style="`${authEdit ? 'margin-top: 20px;' : ''}`"
        :data="treeData"
        :selected-keys="selectedDocIds"
        :expanded-keys="expandedDocIds"
        key-field="docId"
        label-field="docTtl"
        children-field="children"
        :render-prefix="renderTreeItemPrefix"
        :render-suffix="renderTreeItemSuffix"
        :cancelable="false"
        selectable
        :on-update:selected-keys="onSelectedKeysChange"
        :on-update:expanded-keys="onExpandedKeysChange"
      />
    </n-layout-sider>
    <n-layout-content class="content">
      <p class="option" v-if="authEdit">
        <n-button-group v-if="editMode">
          <n-button round @click="editMode = false" :loading="saving">
            <template #icon>
              <n-icon class="iconfont icon-undovariant"></n-icon>
            </template>退出
          </n-button>
          <n-button round @click="saveContent" :loading="saving">
            <template #icon>
              <n-icon class="iconfont icon-contentsave"></n-icon>
            </template>保存
          </n-button>
        </n-button-group>
        <n-button-group v-else>
          <n-button round @click="editMode = true">
            <template #icon>
              <n-icon class="iconfont icon-tableedit"></n-icon>
            </template>编辑
          </n-button>
        </n-button-group>
      </p>
      <template v-if="selectedDocId">
        <template v-if="editMode">
          <document-editor ref="editorRef" :docId="selectedDocId" :key="`${selectedDocId}-editor`" />
        </template>
        <template v-else>
          <document-viewer :docId="selectedDocId" :key="`${selectedDocId}-viewer`" @on-empty-content="childNavShow = true" />
          <n-timeline class="child-nav" v-if="childNavShow">
            <n-timeline-item v-for="doc in selectedDocChildList" :key="doc.docId">
            <span @click="onChildClick(doc)">{{ doc.docTtl }}</span>
            <template #icon>
              <n-icon class="iconfont-kb icon-document" />
            </template>
            <template #footer>
              <n-time :time="new Date()" :to="new Date(doc.updTm)" type="relative" />
            </template>
            </n-timeline-item>
          </n-timeline>
        </template>
      </template>
      <n-float-button v-if="prevDoc" :title="prevDoc.docTtl" class="prev" @click="onChildClick(prevDoc)" position="absolute" top="50%" left="10px">
        <n-icon class="iconfont icon-arrowleft" />
      </n-float-button>
      <n-float-button v-if="nextDoc" :title="nextDoc.docTtl" class="next" @click="onChildClick(nextDoc)" position="absolute" top="50%" right="10px">
        <n-icon class="iconfont icon-arrowright" />
      </n-float-button>
    </n-layout-content>
  </n-layout>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { NDropdown, NIcon, useDialog, useMessage } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { copyProp } from '@/libs/tools'
  import EventBus from '@/libs/eventbus'
  import DocumentForm from './form/DocumentForm.vue'
  import DocumentViewer from './form/DocumentViewer.vue'
  import DocumentEditor from './form/DocumentEditor.vue'
  import Setting from './Setting.vue'
  import DocumentToDatasetForm from './form/DocumentToDatasetForm.vue'
  import { useDocument } from './mixin/document'

  export default defineComponent({
    components: {
      DocumentViewer, DocumentEditor, Setting
    },
    props: {
      /** 文档集ID */
      setId: {
        type: String,
        required: true
      },
      docsetInfo: {
        type: Object
      }
    },
    setup(props) {
      const router = useRouter()
      const route = useRoute()
      const { proxy, ctx } = getCurrentInstance()
      const dialog = useDialog()
      const message = useMessage()
      const setId = props.setId || route.query.id
      const docsetInfo = props.docsetInfo
      const authEdit = computed(() => docsetInfo['optAuth'] === 'alter')
      const editMode = ref(false)
      const selectedDocIds = ref([])
      const expandedDocIds = ref([])
      const selectedDocId = computed(() => selectedDocIds.value[0] || '')
      const editorRef = ref(null)
      const saving = ref(false)
      const { documentList, treeData, renderTreeItemPrefix } = useDocument()
      const selectedDocChildList = computed(() => documentList.value.filter(d => d.docPid === selectedDocId.value))
      const childNavShow = ref(false)
      const prevDoc = ref(null)
      const nextDoc = ref(null)

      watch(treeData, (list) => {
        if (selectedDocIds.value.length === 0 && list.length > 0) {
          selectedDocIds.value = [list[0].docId]
        }
      })
 
      watch(selectedDocId, (id) => {
        prevDoc.value = null
        nextDoc.value = null
        let selectedDoc = documentList.value.find(d => d.docId === id)
        if (!selectedDoc) {
          return
        }
        let docPid = selectedDoc.docPid
        let siblings = documentList.value.filter(d => d.docPid === docPid)
        if (siblings.length > 1) {
          let i = siblings.findIndex(d => d.docId === id)
          if (i > 0) {
            prevDoc.value = siblings[i - 1]
          }
          if (i < siblings.length - 1) {
            nextDoc.value = siblings[i + 1]
          }
        }
      })

      const onSelectedKeysChange = (keys) => {
        selectedDocIds.value = keys
        childNavShow.value = false
      }
      const onExpandedKeysChange = (keys) => {
        expandedDocIds.value = keys
      }

      const addDocument = (p) => {
        let docPid = p.docId // 如果不为空则是创建子文档
        dialogCreate(dialog, {
          title: `新增${docPid ? '子' : ''}文档`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-document', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            data.setId = setId
            data['docPid'] = docPid
            proxy.$api.post('/doc/document', data).then(res => {
              let doc = res.data || {}
              documentList.value.push(doc)
              selectedDocIds.value = [doc.docId]
              let docPath = doc.docPath || ''
              if (docPid) {
                let paths = docPath.split('/')
                expandedDocIds.value = paths.slice(1, paths.length - 1)
              }
              setTimeout(() => {
                editMode.value = true
              }, 100)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
            })
          }
        }, DocumentForm, {
        })
      }
      const saveContent = () => {
        saving.value = true
        editorRef.value.saveContent().then(res => {
          saving.value = false
          editMode.value = false
        }).catch(() => {
          saving.value = false
        })
      }
      const docOptions = [
        {
          label: '发布',
          key: 'tokb',
          icon: () => renderIconfontIcon('iconfont icon-send'),
          label: () => {
            return h('span', {
              title: '发布到知识库'
            }, '发布')
          }
        },
        {
          label: '新增',
          key: 'child',
          icon: () => renderIconfontIcon('iconfont icon-filedocumentbox'),
          label: () => {
            return h('span', {
              title: '新增子文档'
            }, '新增')
          }
        },
        {
          label: '编辑',
          key: 'edit',
          icon: () => renderIconfontIcon('iconfont icon-pencil')
        },
        {
          label: '删除',
          key: 'delete',
          icon: () => renderIconfontIcon('iconfont icon-delete')
        }
      ]
      const renderTreeItemSuffix = ({ option }) => {
        if (!authEdit.value) {
          return h('span')
        }
        return h(
          NDropdown,
          {
            options: docOptions,
            onSelect: (key) => {
              onDocOptionSelect(key, option)
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
      const onDocOptionSelect = (key, doc) => {
        if (key === 'tokb') { // 发布到知识库
          dialogCreate(dialog, {
            title: `请选择知识库`,
            style: 'width: 40%;',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-team', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              if (!data) {
                return false
              }
              dialog.loading = true
              proxy.$api.post('/doc/document/to/dataset', {
                docId: doc.docId,
                reposId: data
              }).then(res => {
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
            }
          }, DocumentToDatasetForm, {
            docId: doc.docId
          })
        } else if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改文档`,
            style: 'width: 40%;',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-doc1', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/doc/document', data).then(res => {
                copyProp(doc, data)
                EventBus.emit('on-document-update', data)
              }).catch(err => {
                console.error(err)
              })
              dialog.destroy()
            }
          }, DocumentForm, {
            doc
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该文档么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/doc/document/' + doc.docId).then(res => {
                documentList.value = documentList.value.filter(item => item.docId !== doc.docId)
                if (selectedDocId.value === doc.docId) {
                  selectedDocIds.value = [documentList.value[0]?.docId]
                }
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
              return false
            }
          })
        } else if (key === 'child') {
          addDocument(doc)
        }
      }
      const onChildClick = (doc) => {
        selectedDocIds.value = [doc.docId]
        let docPath = doc.docPath || ''
        let paths = docPath.split('/')
        expandedDocIds.value = paths.slice(1, paths.length - 1)
      }
      return {
        authEdit,
        setId,
        editorRef,
        docsetInfo,
        editMode, saving, childNavShow, prevDoc, nextDoc,
        selectedDocId, documentList, treeData, selectedDocIds, expandedDocIds, selectedDocChildList,
        renderTreeItemPrefix, renderTreeItemSuffix, onSelectedKeysChange, onExpandedKeysChange,
        docOptions,
        addDocument, onDocOptionSelect, saveContent, onChildClick
      }
    }
  })
</script>
