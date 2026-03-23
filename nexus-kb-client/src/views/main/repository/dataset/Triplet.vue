<style lang="less">
.kb-triplet {
  height: 100%;
  &-header {
    padding-bottom: 10px;
    display: flex;
    justify-content: space-between;
    .option {
      display: flex;
      .n-button {
        margin-left: 10px;
      }
    }
  }
  &-content {
    height: calc(100% - 45px);
    .n-data-table {
      .n-data-table-wrapper, .n-data-table-base-table {
        height: 100%;
      }
    }
  }
}
</style>

<template>
  <div class="kb-triplet">
    <div class="kb-triplet-header">
      <div class="title">
        <n-button-group>
          <n-button :type="showType === 'graph' ? 'primary': 'default'" @click="showType = 'graph'">
            <template #icon>
              <n-icon class="iconfont-kb icon-triplet" />
            </template>
          </n-button>
          <n-button :type="showType === 'table' ? 'primary': 'default'" @click="showType = 'table'">
            <template #icon>
              <n-icon class="iconfont icon-table" />
            </template>
          </n-button>
        </n-button-group>
      </div>
      <div class="option">
        <n-input v-model:value="subjectValue" placeholder="输入主语搜索" autofocus :on-input="onInputChange" v-if="showType === 'table'">
          <template #prefix>
            <n-icon class="iconfont icon-magnify"></n-icon>
          </template>
        </n-input>
        <n-button v-if="authEdit" type="primary" @click="onAddTriplet"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新增</n-button>
      </div>
    </div>
    <div class="kb-triplet-content">
      <keep-alive>
        <triplet-table ref="tableRef" v-if="showType === 'table'" :reposId="reposId" :authEdit="authEdit" :dtsetId="dtsetId" @on-edit-triplet="onEditTriplet" @on-remove-triplet="onRemoveTriplet" />
        <triplet-graph ref="graphRef" v-else :reposId="reposId" :authEdit="authEdit" :dtsetId="dtsetId" @on-edit-triplet="onEditTriplet" @on-remove-triplet="onRemoveTriplet" />
      </keep-alive>
    </div>
  </div>
</template>
<script>
  import { defineComponent, ref, computed, getCurrentInstance, h } from 'vue'
  import { NButton, NIcon, NDropdown, useDialog } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import TripletTable from './TripletTable.vue'
  import TripletGraph from './TripletGraph.vue'
  import TripletForm from './TripletForm.vue'

  export default defineComponent({
    components: {
      TripletTable, TripletGraph
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
      const tableRef = ref()
      const graphRef = ref()
      const showType = ref('graph')
      const tripletDataList = ref([])
      const subjectValue = ref('')

      const onInitDta = (pageNum) => {
        if (showType.value === 'table') {
          tableRef.value.onInitDta(pageNum, { subject: subjectValue.value })
        } else if (showType.value === 'graph') {
          graphRef.value.onInitDta({ subject: subjectValue.value })
        }
      }
      const onInputChange = _.debounce((value) => {
        onInitDta(1)
      }, 500)

      const onAddTriplet = () => {
        dialogCreate(dialog, {
          title: `新增关系`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-triplet1', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            data.reposId = reposId
            data.dtsetId = dtsetId // 可能是空的
            data.tpltSrc = 'hm' // 人工
            dialog.loading = true
            proxy.$api.post('/knb/dataset/triplet', data).then(res => {
              onInitDta(1)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        }, TripletForm, {
        })
      }

      const onEditTriplet = (row) => {
        dialogCreate(dialog, {
          title: `修改关系`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-triplet1', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            dialog.loading = true
            proxy.$api.put('/knb/dataset/triplet', data).then(res => {
              row.tpltSbjct = data.tpltSbjct
              row.tpltPrdct = data.tpltPrdct
              row.tpltPrdct = data.tpltPrdct
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, TripletForm, {
          triplet: row
        })
      }
      const onRemoveTriplet = (row) => {
        dialogConfirm(dialog, {
          title: '删除确认',
          content: '确定删除该图谱么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/knb/dataset/triplet/' + row.tpltId).then(res => {
              onInitDta()
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
        tableRef, graphRef,
        showType,
        tripletDataList,
        authEdit,
        subjectValue,
        onInitDta, onInputChange, onAddTriplet, onEditTriplet, onRemoveTriplet
      }
    }
  })
</script>
