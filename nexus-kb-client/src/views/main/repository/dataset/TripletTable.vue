<style lang="less">
</style>

<template>
  <n-data-table
    remote
    :loading="loading"
    :columns="columns"
    :data="dataList"
    :pagination="pagination"
    @update:page="onInitDta"
  />
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, h } from 'vue'
  import { NButton, NIcon, NDropdown } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon } from '@/libs/utils'

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
      const reposId = props.reposId
      const dtsetId = props.dtsetId
      const authEdit = props.authEdit
      const loading = ref(false)
      const dataList = ref([])
      const pagination = reactive({
        page: 1,
        pageCount: 1,
        pageSize: 10,
        prefix ({ itemCount }) {
          return `总数 ${itemCount}`
        }
      })

      const onInitDta = (pageNum = pagination.page, values = { subject: '' }) => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.post('/knb/dataset/triplet/page', {
            datasetTriplet: {
              reposId, dtsetId, tpltSbjct: values.subject
            },
            pageBase: {
              pageNum, pageSize: pagination.pageSize
            }
          }).then(res => {
            dataList.value = res.data || []
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
      onInitDta(1)

      const onEditTriplet = (row) => {
        context.emit('on-edit-triplet', row)
      }
      const onRemoveTriplet = (row) => {
        context.emit('on-remove-triplet', row)
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
        pagination,
        dataList,
        authEdit,
        columns: [
          { title: '主语', key: 'tpltSbjct' },
          { title: '谓语', key: 'tpltPrdct' },
          { title: '宾语', key: 'tpltObjct' },
          { title: '操作', key: 'option', align: 'center', width: 120, render(row) {
            return h(
              NDropdown,
              {
                options: rowOptions.value,
                onSelect: (key) => {
                  switch (key) {
                    case 'edit':
                      onEditTriplet(row)
                      break
                    case 'delete':
                      onRemoveTriplet(row)
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
        onInitDta
      }
    }
  })
</script>
