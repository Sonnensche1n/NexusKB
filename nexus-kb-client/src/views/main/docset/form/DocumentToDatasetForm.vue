<style lang="less">
.kb-doc-tokb {
  display: flex;
  padding: 24px 0;
  .n-select:first-child {
    .n-base-selection {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
  }
  .n-select:last-child {
    margin-left: -1px;
    .n-base-selection {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
  }
}
</style>

<template>
  <div class="kb-doc-tokb">
    <n-select
      v-model:value="selectedReposId"
      filterable
      placeholder="输入知识库名称搜索"
      label-field="reposNm"
      value-field="reposId"
      :options="reposList"
      :loading="loading"
      clearable
      :clear-filter-after-select="true"
    />
  </div>
</template>
<script>
  import { defineComponent, ref, reactive, getCurrentInstance, h } from 'vue'
  import { NTag, NBadge, useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, map2Options } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import _ from 'lodash'
  export default defineComponent({
    components: {
    },
    props: {
      docId: {
        type: String,
        required: true
      }
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const docId = props.docId
      const dialog = useDialog()
      const loading = ref(false)
      const reposList = ref([])
      const selectedReposId = ref()
      const onInitDocumentDatasetList = () => {
        proxy.$api.get('/doc/document/reposid/list/' + docId).then(res => {
          let list = res.data || []
          if (list.length > 0) {
            selectedReposId.value = list[0]
          }
        }).catch(err => {
          console.error(err)
        })
      }
      onInitDocumentDatasetList()
      const onIniteReposList = () => {
        loading.value = true
        proxy.$api.post('/knb/repository/my/list').then(res => {
          reposList.value = res.data || []
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }
      onIniteReposList()
      const ok = () => {
        if (isEmpty(selectedReposId.value)) {
          return
        }
        return selectedReposId.value
      }
      return {
        loading, selectedReposId, reposList,
        ok
      }
    }
  })
</script>
