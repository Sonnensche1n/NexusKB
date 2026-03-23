<style lang="less">
.kb-dataset-chunk {
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
  .n-spin-body {
    position: absolute;
    left: 50%;
    top: 50%;
    margin-left: -17px;
    margin-top: -17px;
  }
  .n-card {
    .n-card-header {
      padding: 10px;
      font-size: 12px;
      span {
        color: var(--primary-color);
        padding: 2px 4px;
        border: 1px solid var(--primary-color);
        background-color: var(--primary-color-opacity-5);
        border-radius: var(--border-radius);
      }
    }
    .n-card__content {
      cursor: pointer;
      padding-bottom: 0;
      .n-ellipsis {
        height: 135px;
      }
    }
    .n-card__action {
      padding: 6px 10px;
      background-color: initial;
      font-size: 12px;
      display: flex;
      justify-content: space-between;
      .n-icon {
        position: relative;
        top: 1px;
      }
      .delete.n-button {
        color: var(--error-color);
        visibility: hidden;
        &:hover {
          color: var(--error-color-hover);
        }
      }
    }
    &:hover {
      .n-card__action {
        .delete.n-button {
          visibility: visible;
        }
      }
    }
  }
  .n-pagination {
    margin-top: 12px;
    justify-content: flex-end;
  }
}
</style>

<template>
  <n-scrollbar class="kb-dataset-chunk">
    <div class="kb-dataset-chunk-header">
      <div></div>
      <div class="option">
        <n-input v-model:value="inputValue" placeholder="输入内容搜索" autofocus :on-input="onInputChange">
          <template #prefix>
            <n-icon class="iconfont icon-magnify"></n-icon>
          </template>
        </n-input>
        <!-- <n-button v-if="authEdit" type="primary" @click="onAddQA"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新增</n-button> -->
      </div>
    </div>
    <n-grid :x-gap="20" :y-gap="20" :cols="4">
      <n-gi v-for="chunk in chunkList" :key="chunk.chkId">
        <n-card hoverable embedded @click="onEditChunk(chunk)">
          <template #header>
            <span>#{{ chunk.chkSeq }}</span>
          </template>
          <n-ellipsis :line-clamp="6" :tooltip="false" :title="chunk.chkCntnt">
            {{ chunk.chkCntnt }}
          </n-ellipsis>
          <template #action>
            <span>
              <n-icon class="iconfont-kb icon-text" />{{ countText(chunk.chkCntnt) }}
            </span>
            <n-button v-if="authEdit" quaternary size="tiny" class="delete" @click.stop="e => deleteChunk(chunk, e)" title="删除"><n-icon class="iconfont icon-delete"></n-icon></n-button>
          </template>
        </n-card>
      </n-gi>
    </n-grid>
    <n-spin v-if="loading" />
    <n-empty v-if="chunkList.length === 0"/>
    <n-pagination v-if="chunkList.length > 0" v-model:page="pagination.page" :page-count="pagination.pageCount" :page-size="pagination.pageSize" :on-update:page="initChunkList" />
  </n-scrollbar>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useDialog } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import ChunkForm from './ChunkForm.vue'

  export default defineComponent({
    components: {
    },
    props: {
      dtsetId: String,
      dtsetNm: String,
      authEdit: Boolean
    },
    setup(props, context) {
      const dialog = useDialog()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const inputValue = ref('')
      const chunkList = ref([])
      const loading = ref(false)
      const pagination = reactive({
        page: 1,
        pageCount: 1,
        pageSize: 12,
        itemCount: 0
      })
      const initChunkList = (pageNum) => {
        loading.value = true
        proxy.$api.post('/knb/dataset/chunk/page', {
          datasetChunk: {
            dtsetId: props.dtsetId, chkCntnt: inputValue.value
          },
          pageBase: {
            pageNum, pageSize: pagination.pageSize
          }
        }).then(res => {
          loading.value = false
          chunkList.value = res.data || []
          pagination.page = pageNum
          pagination.pageCount = res.pages
          pagination.itemCount = res.total
        }).catch(err => {
          loading.value = false
          console.error(err)
        })
      }
      initChunkList()

      const onInputChange = _.debounce((value) => {
        initChunkList(1)
      }, 500)
      
      const onTurnBack = () => {
        context.emit('on-turn-back')
      }
      const countText = (text = '') => {
        text = text.replace(/\n|\r/gi, '')
        return text.length
      }

      const onEditChunk = (chunk) => {
        if (!props.authEdit) return
        dialogCreate(dialog, {
          title: `编辑内容`,
          style: 'width: 70%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-dataset1', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.put('/knb/dataset/chunk/content', data).then(res => {
              chunk.chkCntnt = data.chkCntnt
              chunk.chkAsst = data.chkAsst
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, ChunkForm, {
          chunk
        })
      }
      const deleteChunk = (chunk) => {
        dialogConfirm(dialog, {
          title: '删除',
          content: '确定删除该分段么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/knb/dataset/chunk/' + chunk.chkId).then(res => {
              initChunkList(pagination.page)
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
        pagination, chunkList, inputValue, loading,
        onTurnBack, initChunkList, countText, onEditChunk, deleteChunk, onInputChange
      }
    }
  })
</script>
