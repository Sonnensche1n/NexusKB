<style lang="less">
.kb-application {
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
  <n-card class="kb-application" :bordered="false">
    <template #header>
      <n-icon class="iconfont-kb icon-workspace"></n-icon>我的应用库
    </template>
    <template #header-extra>
      <n-input v-model:value="inputValue" placeholder="输入应用名称搜索" autofocus :on-input="onInputChange">
        <template #prefix>
          <n-icon class="iconfont icon-magnify"></n-icon>
        </template>
      </n-input>
      <n-button type="primary" @click="addForm"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;新建</n-button>
    </template>
    <card-list :dataList="appList" idKey="appId" titleKey="appNm" descKey="appIntd" defaultDesc="该应用还没有介绍~"
      @on-option-select="onOptionSelect" @on-item-click="turnToDetail"
    />
    <n-empty v-if="appList.length === 0">
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
  import { isEmpty } from '@/libs/tools'
  import CardList from '@/views/main/components/CardList.vue'
  import AppInfoForm from './appinfo/form/AppInfoForm.vue'

  export default defineComponent({
    components: {
      CardList
    },
    setup() {
      const dialog = useDialog()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
      const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const sourceAppList = ref([])
      const appList = ref([])
      const inputValue = ref('')
      const initData = () => {
        proxy.$api.post('/agt/app/my/list').then(res => {
          sourceAppList.value = res.data || []
          appList.value = sourceAppList.value
        }).catch(err => {
          console.error(err)
        })
      }
      initData()
      const addForm = () => {
        dialogCreate(dialog, {
          title: `新增应用`,
          style: 'width: 50%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-app1', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/agt/app', data).then(res => {
              initData()
            }).catch(err => {
              console.error(err)
            })
            dialog.destroy()
          }
        }, AppInfoForm, {
        })
      }
      const onOptionSelect = (key, app) => {
        if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改应用`,
            style: 'width: 50%;',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-app1', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/agt/app', data).then(res => {
                initData()
              }).catch(err => {
                console.error(err)
              })
              dialog.destroy()
            }
          }, AppInfoForm, {
            app
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该应用么？',
            type: 'warning',
            loading: false,
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/agt/app/' + app.appId).then(res => {
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
          appList.value = sourceAppList.value
          return
        }
        appList.value = sourceAppList.value.filter(item => {
          return (item.appNm.toLowerCase()).indexOf(value.toLowerCase()) > -1
        })
      }, 500)
      const turnToDetail = (setId) => {
        router.push(`/main/appinfo/detail?id=${setId}`)
      }
      return {
        inputValue,
        appList,
        addForm, onOptionSelect,
        onInputChange, turnToDetail
      }
    }
  })
</script>
