<style lang="less">
</style>

<template>
  <div>
    <div class="option" v-if="authEdit">
      <n-button @click="onCopplRela"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;添加协作者</n-button>
    </div>
    <n-data-table style="margin-top: 10px;" :loading="loading" :columns="reposCopplColumns" :data="reposCopplList" />
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { NButton, NIcon, useDialog, useMessage } from 'naive-ui'
  import { dialogCreate, dialogConfirm, renderIconfontIcon } from '@/libs/utils'
  import RelaCoppl from './RelaCoppl.vue'

  export default defineComponent({
    components: {
    },
    props: {
      rscId: {
        type: String,
        required: true
      },
      rscTyp: {
        type: String,
        required: true
      },
      authEdit: {
        type: Boolean
      }
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const rscId = props.rscId
      const rscTyp = props.rscTyp
      const authEdit = props.authEdit

      const loading = ref(false)
      const reposCopplColumns = [
        { title: '名称', key: 'nkNm', fixed: 'left' },
        { title: '操作', key: 'option', align: 'center', width: 120, render(row) {
          return h(
            NButton,
            {
              quaternary: true,
              title: '移除协作者',
              disabled: !authEdit,
              onClick: () => {
                onRemoveCoppl(row)
              }
            },
            {
              default: () => {
                return [
                  h(
                    NIcon,
                    {
                      class: 'iconfont icon-delete'
                    }
                  )
                ]
              }
            })
          }
        }
      ]
      const reposCopplList = ref([])
      const onInitCopplList = () => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.post('/sys/resource/coppl/list', {
            rscId
          }).then(res => {
            reposCopplList.value = res.data || []
            loading.value = false
          }).catch(err => {
            console.error(err)
            loading.value = false
          })
        }
      }
      onInitCopplList()
      const onCopplRela = () => {
        dialogCreate(dialog, {
          title: `添加协作者`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-user', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            if (!data || data.length === 0) {
              return
            }
            proxy.$api.post('/sys/resource/coppl/rela', data).then(res => {
              onInitCopplList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, RelaCoppl, {
          rscId, rscTyp
        })
      }
      const onRemoveCoppl = (row) => {
        dialogConfirm(dialog, {
          title: '删除',
          content: '确定移除该协作者么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/sys/resource/coppl/' + row.rscId + '/' + row.userId).then(res => {
              onInitCopplList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }

      return {
        authEdit,
        loading, reposCopplColumns, reposCopplList, onCopplRela
      }
    }
  })
</script>
