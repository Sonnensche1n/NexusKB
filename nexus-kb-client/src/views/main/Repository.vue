<style lang="less">
.kb-repos {
  height: 100%;
  .n-card-header {
    .n-card-header__main {
      font-weight: 600;
      display: flex;
      align-items: center;
      .n-icon {
        font-size: 22px;
        // position: relative;
        // top: 1.5px;
        margin-right: 4px;
        color: var(--primary-color);
      }
    }
    .n-card-header__extra {
      .n-button {
        margin-left: 10px;
      }
    }
  }
}
</style>

<template>
  <n-card class="kb-repos" :bordered="false">
    <template #header>
      <n-icon class="iconfont-kb icon-knowledge"></n-icon>我的知识库
    </template>
    <template #header-extra>
      <n-input v-model:value="inputValue" placeholder="输入知识库名称搜索" autofocus :on-input="onInputChange">
        <template #prefix>
          <n-icon class="iconfont icon-magnify"></n-icon>
        </template>
      </n-input>
      <n-button type="primary" @click="addForm"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新建</n-button>
    </template>
    <card-list :dataList="repositoryList" idKey="reposId" titleKey="reposNm" descKey="reposDesc" defaultDesc="该知识库还没有介绍~"
      @on-option-select="onOptionSelect" @on-item-click="turnToDetail"
    />
    <n-empty v-if="repositoryList.length === 0">
      <template #extra>
        <n-button type="primary" @click="addForm"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新建</n-button>
      </template>
    </n-empty>
  </n-card>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { isEmpty, localSave } from '@/libs/tools'
  import { CURRENT_REPOS_ID_KEY } from '@/libs/enum'
  import CardList from '@/views/main/components/CardList.vue'
  import RepositoryForm from './repository/form/RepositoryForm.vue'

  export default defineComponent({
    components: {
      CardList
    },
    setup() {
      const dialog = useDialog()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const sourceRepositoryList = ref([])
      const repositoryList = ref([])
      const inputValue = ref('')
      const initData = () => {
        proxy.$api.post('/knb/repository/my/list').then(res => {
          sourceRepositoryList.value = res.data || []
          repositoryList.value = sourceRepositoryList.value
        }).catch(err => {
          console.error(err)
        })
      }
      initData()
      const addForm = () => {
        dialogCreate(dialog, {
          title: `新增知识库`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/knb/repository', data).then(res => {
              initData()
            }).catch(err => {
              console.error(err)
            })
            dialog.destroy()
          }
        }, RepositoryForm, {
        })
      }
      const onOptionSelect = (key, repos) => {
        if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改知识库`,
            style: 'width: 50%;',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/knb/repository', data).then(res => {
                initData()
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
            }
          }, RepositoryForm, {
            repository: repos
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该知识库么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/knb/repository/' + repos.reposId).then(res => {
                initData()
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
              return false
            }
          })
        }
      }
      const onInputChange = _.debounce((value) => {
        if (isEmpty(value)) {
          repositoryList.value = sourceRepositoryList.value
          return
        }
        repositoryList.value = sourceRepositoryList.value.filter(item => {
          return (item.reposNm.toLowerCase()).indexOf(value.toLowerCase()) > -1
        })
      }, 500)
      const turnToDetail = (reposId) => {
        localSave(CURRENT_REPOS_ID_KEY, reposId)
        router.push(`/main/repository/detail?id=${reposId}`)
      }
      return {
        inputValue,
        repositoryList,
        addForm, onOptionSelect,
        onInputChange, turnToDetail
      }
    }
  })
</script>
