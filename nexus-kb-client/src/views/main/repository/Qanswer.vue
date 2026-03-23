<style lang="less">
.kb-qanswer {
  height: 100%;
  &-header {
    padding-bottom: 10px;
    display: flex;
    justify-content: space-between;
    .title {
      font-size: 18px;
      font-weight: 600;
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
      .n-button {
        margin-left: 10px;
      }
    }
  }
  .n-data-table {
    height: calc(100% - 45px) !important;
    .n-data-table-wrapper, .n-data-table-base-table {
      height: 100%;
    }
  }
}
</style>

<template>
  <div class="kb-qanswer">
    <div class="kb-qanswer-header">
      <div class="title">
        <n-icon class="iconfont-kb icon-qa"></n-icon>Q&A({{ pagination.itemCount }})
      </div>
      <div class="option">
        <n-input v-model:value="inputValue" placeholder="输入问题搜索" autofocus :on-input="onInputChange">
          <template #prefix>
            <n-icon class="iconfont icon-magnify"></n-icon>
          </template>
        </n-input>
        <n-button v-if="authEdit" type="primary" @click="onAddQA"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新增</n-button>
      </div>
    </div>
    <n-data-table
      remote
      :loading="loading"
      :columns="columns"
      :data="questDataList"
      :pagination="pagination"
      @update:page="onInitQuestDataList"
    />
  </div>
</template>
<script>
  import { defineComponent, ref, computed, getCurrentInstance, h } from 'vue'
  import { NDataTable, NButton, NIcon, NInput, NDropdown, useDialog } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import QanswerForm from './form/QanswerForm.vue'

  export default defineComponent({
    components: {
      NDataTable, NButton, NIcon, NInput
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
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const reposId = props.reposId
      const dtsetId = props.dtsetId
      const authEdit = props.authEdit
      const dialog = useDialog()
      const loading = ref(false)
      const questDataList = ref([])
      const inputValue = ref('')
      const pagination = reactive({
        page: 1,
        pageCount: 1,
        pageSize: 10,
        prefix ({ itemCount }) {
          return `总数 ${itemCount}`
        }
      })

      const onInitQuestDataList = (pageNum) => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.post('/knb/repository/quest/page', {
            reposQuest: {
              reposId, dtsetId: props.dtsetId, qstQuest: inputValue.value
            },
            pageBase: {
              pageNum, pageSize: pagination.pageSize
            }
          }).then(res => {
            questDataList.value = res.data || []
            pagination.page = pageNum
            pagination.pageCount = res.pages
            pagination.itemCount = res.total
            loading.value = false
          }).catch(err => {
            console.error(err)
            loading.value = false
          })
        }
      }
      onInitQuestDataList()
      const onInputChange = _.debounce((value) => {
        onInitQuestDataList(1)
      }, 500)

      const onAddQA = () => {
        dialogCreate(dialog, {
          title: `新增Q&A`,
          style: 'width: 70%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-qa', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            data.reposId = reposId
            data.dtsetId = dtsetId // 可能是空的
            data.qstSrc = 'hm' // 人工
            dialog.loading = true
            proxy.$api.post('/knb/repository/quest', data).then(res => {
              onInitQuestDataList(pagination.page)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        }, QanswerForm, {
        })
      }

      const onEditQA = (row) => {
        dialogCreate(dialog, {
          title: `修改Q&A`,
          style: 'width: 70%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-qa', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            dialog.loading = true
            proxy.$api.put('/knb/repository/quest', data).then(res => {
              row.qstQuest = data.qstQuest
              row.qstAswr = data.qstAswr
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, QanswerForm, {
          quest: row
        })
      }
      const onRemoveQA = (row) => {
        dialogConfirm(dialog, {
          title: '删除确认',
          content: '确定删除该问答对么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/knb/repository/quest/' + row.qstId).then(res => {
              onInitQuestDataList(pagination.page)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }
      const rowOptions = ref([
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
      return {
        loading,
        questDataList,
        authEdit,
        inputValue,
        pagination,
        columns: [
          { title: '问题', key: 'qstQuest', minWidth: 300, fixed: 'left' },
          { title: '答案', key: 'qstAswr', minWidth: 300 },
          { title: '操作', key: 'option', align: 'center', width: 120, render(row) {
            return h(
              NDropdown,
              {
                options: rowOptions.value,
                onSelect: (key) => {
                  switch (key) {
                    case 'edit':
                      onEditQA(row)
                      break
                    case 'delete':
                      onRemoveQA(row)
                      break
                  }
                }
              },
              h(
                NButton,
                {
                  size: 'small', secondary: true, type: 'primary'
                },
                h(
                  NIcon,
                  {
                    class: 'iconfont icon-dotshorizontal'
                  }
                )
              )
            )}
          }
        ],
        onInitQuestDataList, onInputChange, onAddQA
      }
    }
  })
</script>
