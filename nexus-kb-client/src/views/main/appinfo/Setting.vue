<style lang="less">
.kb-app-setting {
  .n-list {
    .n-list-item {
      margin-top: 10px;
      border: 1px solid var(--n-border-color);
      .n-input--textarea {
        .n-input-wrapper {
          width: 100%;
        }
      }
    }
    .n-list-item:first-child {
      margin-top: 0;
    }
  }
  .value {
    height: 34px;
    line-height: 34px;
  }
  .input {
    display: none;
  }
  .edit {
    .value {
      display: none;
    }
    .input {
      display: block;
    }
  }
}
</style>

<template>
  <div class="kb-app-setting">
    <n-list hoverable :show-divider="false">
      <n-list-item :class="editAppNm?'edit':''">
        <template #suffix>
          <n-button v-if="editAppNm" @click="onEditReposNm">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editAppNm = !editAppNm">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="名称">
          <div class="value">{{ appInfo.appNm }}</div>
          <n-input class="input" v-model:value="appNm" placeholder="请输入应用名称"/>
        </n-thing>
      </n-list-item>
      <n-list-item :class="editAppDesc?'edit':''">
        <template #suffix>
          <n-button v-if="editAppDesc" @click="onEditAppDesc">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editAppDesc = !editAppDesc">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="介绍">
          <n-ellipsis class="value" :line-clamp="1" :tooltip="{ width: '400px' }">
            {{ appInfo.appIntd || '这个应用还没有介绍~' }}
          </n-ellipsis>
          <n-input class="input" v-model:value="appIntd" type="textarea" placeholder="请输入应用介绍"
          :autosize="{
            minRows: 3,
            maxRows: 5
          }"/>
        </n-thing>
      </n-list-item>
    </n-list>
  </div>
</template>
<script>
  import { defineComponent, ref, watch, getCurrentInstance } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { isEmpty } from '@/libs/tools'
  import { map2Options } from '@/libs/utils'
  import { COMMON_AUTH_RANGE_TYPE } from '@/libs/enum'
  import ResourceTeam from '@/views/main/components/resource/ResourceTeam.vue'
  import ResourceCoppl from '@/views/main/components/resource/ResourceCoppl.vue'

  export default defineComponent({
    components: {
      ResourceTeam, ResourceCoppl
    },
    props: {
      appId: {
        type: String,
        required: true
      },
      appInfo: {
        type: Object
      }
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const appId = props.appId
      const appInfo = props.appInfo
      const authEdit = computed(() => appInfo['optAuth'] === 'alter')
      const appNm = ref(appInfo.appNm)
      const appIntd = ref(appInfo.appIntd)
      const authRang = ref(appInfo.authRang)
      const authRangOptions = ref(map2Options(COMMON_AUTH_RANGE_TYPE))

      const editAppNm = ref(false)
      const onEditReposNm = () => {
        if (isEmpty(appNm.value)) {
          message.error('必须输入应用名称')
          return
        }
        if (appNm.value === appInfo.appNm) {
          editAppNm.value = false
          return
        }
        proxy.$api.put('/agt/app/name', { appId, appNm: appNm.value }).then(res => {
          appInfo.appNm = appNm.value
          editAppNm.value = false
        }).catch(err => {
          console.error(err)
          editAppNm.value = false
        })
      }

      const editAppDesc = ref(false)
      const onEditAppDesc = () => {
        if (isEmpty(appIntd.value)) {
          message.error('必须输入应用介绍')
          return
        }
        if (appIntd.value === appInfo.appIntd) {
          editAppDesc.value = false
          return
        }
        proxy.$api.put('/agt/app/desc', { appId, appIntd: appIntd.value }).then(res => {
          editAppDesc.value = false
          appInfo.appIntd = appIntd.value
        }).catch(err => {
          console.error(err)
          editAppDesc.value = false
        })
      }
      const onAuthRangChange = (rang) => {
        proxy.$api.put('/agt/app/auth/range', { appId, authRang: rang }).then(res => {
          appInfo.authRang = rang
        }).catch(err => {
          console.error(err)
        })
      }

      watch(authRang, (newRang, oldRang) => {
        if (!oldRang) {
          return
        }
        onAuthRangChange(newRang)
      })

      return {
        authEdit,
        appInfo,
        appNm, editAppNm, onEditReposNm,
        appIntd, editAppDesc, onEditAppDesc,
        authRang, authRangOptions
      }
    }
  })
</script>
